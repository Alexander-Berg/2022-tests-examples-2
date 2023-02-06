import logging
import os
import re
import time
import yaml

from calendar import monthrange

from sandbox import sdk2
from sandbox.sandboxsdk import ssh
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.projects.common import task_env

DEFAULT_ARCADIA_PATH = '/quality/robots/ab_testing/experiments/'

ARCADIA_KEY_OWNER = 'AB-TESTING'
ARCADIA_KEY_NAME = 'sec-01dx1bdkxjy6h3yn85wfdbx3wp[ssh_key]'
ARCADIA_USER = 'robot-eksperimentus'

DAYS_DIR_CAPACITY = 8  # /2019/12/9-16/file


class AbtTestidsUpdate(sdk2.Task):
    """
    Commit testids.
    """

    class Requirements(task_env.TinyRequirements):
        ram = 4096

    class Parameters(sdk2.Task.Parameters):
        arcadia_commit_url = sdk2.parameters.ArcadiaUrl(
            'svn path to commit testids for testing',
            default_value=Arcadia.trunk_url() + DEFAULT_ARCADIA_PATH,
            required=False,
        )

        experiment_id = sdk2.parameters.String('experiment_id', required=True)
        testids_data = sdk2.parameters.JSON('testids_data', required=True)
        services = sdk2.parameters.List('services', required=True)
        flagsjson_id = sdk2.parameters.Integer("Flags.json id", required=False, default=0)

        with sdk2.parameters.Output():
            committed_revisions = sdk2.parameters.JSON('revisions for committed testids', default_value=[])
            commit_timestamp = sdk2.parameters.Integer('commit timestamp')

    def _get_submonth(self, day, last_day):
        part = (day - 1) / DAYS_DIR_CAPACITY
        first = part * DAYS_DIR_CAPACITY + 1
        last = min((part + 1) * DAYS_DIR_CAPACITY, last_day)
        return '-'.join(map(str, [first, last]))

    def _get_dir(self, checkout_dir):
        curtime = time.gmtime()
        dir_path = [
            str(curtime.tm_year),
            str(curtime.tm_mon),
            self._get_submonth(
                curtime.tm_mday,
                monthrange(curtime.tm_year, curtime.tm_mon)[1]
            ),
        ]

        full_path = os.path.join(*([checkout_dir] + dir_path))
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            return full_path, True
        return full_path, False

    def _get_data(self, testid, params, timestamp):
        return {'experiment_id': self.Parameters.experiment_id,
                'start_time': timestamp,
                'services': self.Parameters.services,
                'testid': testid,
                'flagsjson_id': self.Parameters.flagsjson_id,
                'params': params}

    def _commit_testid(self, testid, params, checkout_dir, dir_path, timestamp):
        Arcadia.update(checkout_dir, parents=True)
        file_path = os.path.join(dir_path, str(testid) + '.yaml')

        need_svn_add = False
        if not os.path.exists(file_path):
            need_svn_add = True
        new_data = self._get_data(testid, params, timestamp)

        logging.info('trying to write to the file {}...'.format(file_path))
        with open(file_path, 'w') as f:
            noalias_dumper = yaml.dumper.SafeDumper
            noalias_dumper.ignore_aliases = lambda self, new_data: True
            yaml.dump(new_data, f, default_flow_style=False, encoding='utf-8',
                      allow_unicode=True, Dumper=noalias_dumper)

        logging.info('committing to Arcadia...')
        with ssh.Key(self, key_owner=ARCADIA_KEY_OWNER, key_name=ARCADIA_KEY_NAME):
            if need_svn_add:
                Arcadia.add(file_path, parents=True)
            commit_output = Arcadia.commit(
                checkout_dir,
                'commit testid {} of {} for testing SKIP_CHECK'.format(testid, self.Parameters.experiment_id),
                user=ARCADIA_USER
            )

            committed_revision_match = re.findall(r"Committed revision ([0-9]+)", commit_output)
            if committed_revision_match:
                committed_revision = committed_revision_match[0]
                logging.info('committed testid {} with r{}'.format(testid, committed_revision))
                return {
                    'testid': testid,
                    'revision': int(committed_revision),
                    'params': params}
            else:
                logging.info('committed revision not found')
        logging.info('successfully committed')

    def _commit_to_arcadia(self):
        logging.info('trying to commit experiment {}...'.format(self.Parameters.experiment_id))

        if not self.Parameters.testids_data:
            logging.info('no testids to commit')
            return

        checkout_dir = str(self.path('arcadia'))
        logging.info('checking out Arcadia to {}...'.format(checkout_dir))
        Arcadia.checkout(self.Parameters.arcadia_commit_url, checkout_dir)
        dir_path, need_svn_add = self._get_dir(checkout_dir)
        timestamp = int(time.time())

        if need_svn_add:
            with ssh.Key(self, key_owner=ARCADIA_KEY_OWNER, key_name=ARCADIA_KEY_NAME):
                Arcadia.add(dir_path, parents=True)
                Arcadia.commit(checkout_dir, 'commit new dir for testing SKIP_CHECK', user=ARCADIA_USER)
            logging.info('successfully committed')

        self.Parameters.committed_revisions = [
            self._commit_testid(testid_info['testid'], testid_info['params'], checkout_dir, dir_path, timestamp)
            for testid_info in self.Parameters.testids_data
        ]
        if not self.Parameters.commit_timestamp:
            self.Parameters.commit_timestamp = timestamp

    def on_execute(self):
        self._commit_to_arcadia()
