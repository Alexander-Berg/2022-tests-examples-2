# -*- coding: utf-8 -*-

import json
import logging
import time
import urllib2
import os.path

from sandbox import sdk2

from sandbox.sandboxsdk import ssh
from sandbox.sandboxsdk.svn import Arcadia

import sandbox.common.types.misc as ctm

from sandbox.projects.common.nanny import nanny
from sandbox.projects.resource_types.releasers import experiment_releasers


DEFAULT_ARCADIA_PATH = '/web/report/data/flags/experiments/'

ARCADIA_KEY_OWNER = 'AB-TESTING'
ARCADIA_KEY_NAME = 'robot-eksperimentus-ssh'
ARCADIA_USER = 'robot-eksperimentus'


class AbtAliasJson(sdk2.Resource):
    '''
    Experiments aliases for Report (see. USEREXP-4992)
    '''
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus']


class AbtAliasJsonUpdate(nanny.ReleaseToNannyTask2, sdk2.Task):
    '''
    Update alias.json resource for Report
    '''

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        alias_json_url = sdk2.parameters.String('alias.json URL',
                                                default='http://ab.yandex-team.ru/alias.json',
                                                required=True)

        arcadia_commit_url = sdk2.parameters.ArcadiaUrl('svn path to commit alias.json on release',
                                                        default_value=Arcadia.trunk_url() + DEFAULT_ARCADIA_PATH,
                                                        required=False)

    class Context(sdk2.Task.Context):
        version = 'none'
        ts_created = 'none'

    def _commit_to_arcadia(self):
        logging.info('trying to commit alias.json...')

        if not self.Parameters.arcadia_commit_url:
            logging.info('no url specified - no need to commit')
            return

        checkout_dir = str(self.path('arcadia'))

        logging.info('checkouting Arcadia to {}...'.format(checkout_dir))
        Arcadia.checkout(self.Parameters.arcadia_commit_url, checkout_dir)

        alias_json_resource = sdk2.Resource['ABT_ALIAS_JSON'].find(task=self).first()
        alias_json_resource_data = sdk2.ResourceData(alias_json_resource)
        alias_json_path = str(alias_json_resource_data.path)
        logging.info('loading the resource from {}...'.format(alias_json_path))
        alias_json_content = json.load(open(alias_json_path))
        alias_json_pretty = json.dumps(alias_json_content, indent=4)
        new_alias_json_path = os.path.join(checkout_dir, 'alias.json')
        logging.info('saving pretty copy of the resource to {}...'.format(new_alias_json_path))
        with open(new_alias_json_path, 'w') as f:
            f.write(alias_json_pretty)

        logging.info('committing to Arcadia...')
        try:
            with ssh.Key(self, key_owner=ARCADIA_KEY_OWNER, key_name=ARCADIA_KEY_NAME):
                Arcadia.commit(
                    checkout_dir,
                    'SERP-1: alias.json updated to the version #{}_{}'.format(self.Context.version, self.Context.ts_created),
                    user=ARCADIA_USER
                )
        except Exception, e:
            logging.error(u'something wrong while commiting: {}'.format(unicode(e)))
        else:
            logging.info('successfully committed')

    def on_release(self, additional_parameters):
        logging.info('alias.json releasing...')
        version = self.Context.version
        ts_created = self.Context.ts_created
        comment = 'Update alias.json to version #{}_{}'.format(version, ts_created)
        logging.debug('COMMENT = {}'.format(comment))
        additional_parameters['release_subject'] = comment
        nanny.ReleaseToNannyTask2.on_release(self, additional_parameters)

        self._commit_to_arcadia()

    def _download_alias_json(self):
        url = self.Parameters.alias_json_url
        logging.info('fetching alias.json from url {}'.format(url))
        for i in xrange(1, 11):
            logging.info('fetch attempt {}'.format(i))
            try:
                return urllib2.urlopen(url).read()
            except urllib2.URLError as e:
                logging.warning('error: {}'.format(str(e)))
            time.sleep(10)
        raise Exception('FAILED to fetch alias.json')

    def on_execute(self):
        alias_json_content = self._download_alias_json()

        alias_json_meta = json.loads(alias_json_content)['meta']
        version = alias_json_meta.get('version', 'none')
        ts_created = alias_json_meta.get('ts_created', 'none')
        self.Context.version = version
        self.Context.ts_created = ts_created
        logging.info('alias.json version #{}_{}'.format(version, ts_created))

        logging.info('creating resource...')
        resource = sdk2.ResourceData(AbtAliasJson(
            self, 'alias_json_{}_{}'.format(version, ts_created), 'alias.json'
        ))
        resource.path.write_bytes(alias_json_content)

        logging.info('making resource ready...')
        resource.ready()
