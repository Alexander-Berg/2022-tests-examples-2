# coding: utf8
import re
import os
import time
import bson
import pymongo
import logging
import sandbox.common.errors as errors
import sandbox.common.types.misc as ctm
import sandbox.common.types.client as ctc
import sandbox.projects.gencfg.mongo as mongo
import sandbox.projects.gencfg.helpers as helpers
import sandbox.projects.gencfg.environment as environment

from sandbox import sdk2
from datetime import datetime, timedelta
from sandbox.common.errors import TaskFailure
from sandbox.projects.resource_types import CONFIG_BUILD_LOGS, GENCFG_DB_CACHE


AUTHOR_RE = re.compile('.*committed by (?P<author>[A-Za-z0-9_.-]+).*')


def function_logger(func):
    """
    Count time executing func and logging exceptions to context
    """

    def wrapper(self, *args, **kwargs):
        s = time.time()
        try:
            result = func(self, *args, **kwargs)
        except Exception as e:
            self.Context.broken_goals += '[{}] {}: {}\n'.format(func.__name__, type(e).__name__, e)
            raise
        self.print_info('[TIME] {} {}'.format(func.__name__, time.time() - s))
        return result
    return wrapper


class TestConfigGenerator2(sdk2.Task):
    """ Run gen.sh and update db """

    MONGO_SETTINGS = {
        'uri': ','.join([
            'myt0-4012.search.yandex.net:27017',
            'myt0-4019.search.yandex.net:27017',
            'sas1-6063.search.yandex.net:27017',
            'sas1-6136.search.yandex.net:27017',
            'vla1-3984.search.yandex.net:27017',
        ]),
        'replicaset': 'heartbeat_mongodb_c',
        'read_preference': pymongo.ReadPreference.PRIMARY
    }

    class Requirements(sdk2.Task.Requirements):
        ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, 10 * 1024, None)
        client_tags = ctc.Tag.CUSTOM_GENCFG_BUILD

    class Parameters(sdk2.Task.Parameters):
        mongo_db = sdk2.parameters.String(
            'Mongo DB',
            required=True,
            default='topology_commits'
        )
        mongo_collection = sdk2.parameters.String(
            'Mongo Collection',
            required=True,
            default='commits'
        )
        revision = sdk2.parameters.Integer(
            'Revison',
            required=False
        )
        gencfg_option = sdk2.parameters.String(
            'Gencfg option (<empty>, run_check, precommit)',
            default='run_checks'
        )
        retry_count = sdk2.parameters.Integer(
            'Count retry after TEMPORARY',
            default=3
        )
        dry_run = sdk2.parameters.Bool(
            'Run without populate/import',
            required=True,
            default=True
        )
        update_commit_info = sdk2.parameters.Bool(
            'Update commit info in mongo',
            required=True,
            default=False
        )
        use_last_resources = sdk2.parameters.Bool(
            'Use last released resources',
            required=True,
            default=False
        )

    class Context(sdk2.Task.Context):
        broken_goals = ''
        diff_builder_result = ''
        exceptions = []
        executions_count = 0
        commit_author = None

    # LOGGING

    @staticmethod
    def set_log(info):
        logging.info('[{}] USER_LOG: {}'.format(
            datetime.now().strftime('%H:%M:%S'),
            info
        ))

    def print_info(self, info):
        self.set_info('{}'.format(info))
        self.set_log('{}'.format(info))

    # MONGO

    @staticmethod
    def db_get_collection(mongo_db, mongo_collection):
        collection = pymongo.MongoReplicaSetClient(
            TestConfigGenerator2.MONGO_SETTINGS['uri'],
            connectTimeoutMS=5000,
            replicaSet=TestConfigGenerator2.MONGO_SETTINGS['replicaset'],
            w='majority',
            wtimeout=15000,
            read_preference=TestConfigGenerator2.MONGO_SETTINGS['read_preference']
        )[mongo_db][mongo_collection]
        return collection

    def db_find_one(self, query, collection=None):
        collection = collection or self.collection
        request = collection.find(query).sort(
            '$natural', pymongo.ASCENDING
        ).limit(1)
        request = request[0] if request.count() else None
        return request

    def db_update_one(self, query, updates, collection=None):
        collection = collection or self.collection
        collection.update_one(
            query,
            {"$set": updates},
            upsert=True
        )

    # PATHS

    def get_trunk_path(self):
        return self.ramdrive.path / 'trunk'

    def get_prev_trunk_path(self):
        return self.ramdrive.path / 'prev_trunk'

    # BACKGROUND QUEUE

    def add_background_task(self, raise_on_fail, task_func, fargs, fkwargs):
        self.background_tasks.append({
            'name': task_func.__name__,
            'process': task_func(*fargs, **fkwargs),
            'raise_on_fail': raise_on_fail
        })

    def on_execute(self):
        self.Context.executions_count += 1
        self.Context.commit_author = 'None'

        try:
            self.background_tasks = []
            self.collection = self.db_get_collection(self.Parameters.mongo_db, self.Parameters.mongo_collection)
            self.gencfg = environment.GencfgEnvironment(self, self.Parameters.revision, self.get_trunk_path())
            self.gencfg_prev = environment.GencfgEnvironment(
                self, self.Parameters.revision - 1, self.get_prev_trunk_path()
            )

            self.prepare_gencfg_paths()
            self.install_gencfg()
            self.run_precalc_caches()
            self.run_diffbuilder_process()
            self.run_background_processes()
            self.run_checks_gencfg()
            self.populate_gencfg_trunk_if_needed()
            self.sync_hosts_info_with_mongo()
            self.wait_background_gencfg_tasks()
            self.clean_gencfg_trunk()
        except TaskFailure:
            raise
        except Exception as e:
            if self.Context.executions_count >= self.Parameters.retry_count:
                raise
            self.set_log('Task will be restarted because catch exception {}: {}'.format(type(e).__name__, e))
            raise errors.TemporaryError(str(e))

    def on_finish(self, prev_status, status):
        collection = self.db_get_collection(self.Parameters.mongo_db, self.Parameters.mongo_collection)
        if str(status) == 'SUCCESS':
            self.set_task_status_mongo(True, collection)
        else:
            self.set_task_status_mongo(False, collection)

    def on_break(self, prev_status, status):
        collection = self.db_get_collection(self.Parameters.mongo_db, self.Parameters.mongo_collection)
        self.set_task_status_mongo(False, collection)

    @function_logger
    def run_precalc_caches(self):
        self.gencfg.run_process(['./utils/common/precalc_caches.py', '--no-nanny', '--no-configs'], 'precalc_caches')

    @function_logger
    def prepare_gencfg_paths(self):
        """
        Checkout gencfg on select revision,
        gencfg on pre-select revision and
        get commit author
        """
        self.gencfg.prepare()
        self.gencfg_prev.prepare()
        self.Context.commit_author = self.get_commit_author(self.Parameters.revision)

    @function_logger
    def install_gencfg(self):
        """
        Download *.so and install python virtual envionments
        """
        self.gencfg.install(self.Parameters.use_last_resources)

    @function_logger
    def run_checks_gencfg(self):
        """
        Run ./gen.sh run_checks for check gencfg
        """
        try:
            self.gencfg.gen_sh(self.Parameters.gencfg_option)
        except Exception as e:
            self.save_exceptions(os.path.join(self.gencfg.src_root, 'build'))
            raise TaskFailure('[{}] {}'.format(type(e).__name__, e))
        finally:
            self.gencfg.create_resource(CONFIG_BUILD_LOGS, os.path.join(self.gencfg.src_root, 'build'), 'build')
            times = helpers.get_bin_time_output(os.path.join(str(self.log_path()), 'gen_sh.err.log'))
            self.print_info('[TIME] run_checks_gencfg_user {}'.format(times.get('user', 0)))
        self.gencfg.create_resource(GENCFG_DB_CACHE, os.path.join(self.gencfg.db_root, 'cache'), 'generator_cache')

    def run_diffbuilder_process(self):
        self.add_background_task(
            raise_on_fail=False,
            task_func=self.gencfg.diffbuilder,
            fargs=(),
            fkwargs={'gencfg_prev_path': self.gencfg_prev.src_root, 'background': True}
        )

    @helpers.disable_in_dry_run
    def run_background_processes(self):
        """
        Check skip dict and run:
            fill gencfg api
            fill clickhouse
            update host based firewall
        """
        commit = self.get_commit_from_mongo(self.Parameters.revision)

        if not commit['skip']['mongo']:
            self.add_background_task(
                raise_on_fail=True,
                task_func=self.gencfg.populate_gencfg_trunk,
                fargs=(),
                fkwargs={'background': True}
            )

        # Export slb names
        self.add_background_task(
            raise_on_fail=True,
            task_func=self.gencfg.run_process,
            fargs=(),
            fkwargs={'cmd': ['./utils/mongo/export_slbs.py'], 'log_name': 'export_slbs', 'background': True}
        )

    @helpers.disable_in_dry_run
    def populate_gencfg_trunk_if_needed(self):
        """
        Check the absence of the field test_passed and run fill gencfg api
        """
        commit = self.get_commit_from_mongo(self.Parameters.revision)

        # If skip mongo is set but commit not checked
        if commit['skip']['mongo'] and 'test_passed' not in commit:
            self.add_background_task(
                raise_on_fail=True,
                task_func=self.gencfg.populate_gencfg_trunk,
                fargs=(),
                fkwargs={'background': True}
            )

    @helpers.disable_in_dry_run
    def sync_hosts_info_with_mongo(self):
        self.add_background_task(
            raise_on_fail=False,
            task_func=self.gencfg.sync_hosts_info_with_mongo,
            fargs=(),
            fkwargs={'section': 'hosts_to_groups', 'background': True}
        )
        self.add_background_task(
            raise_on_fail=False,
            task_func=self.gencfg.sync_hosts_info_with_mongo,
            fargs=(),
            fkwargs={'section': 'hosts_to_hardware', 'background': True}
        )

    @function_logger
    def wait_background_gencfg_tasks(self):
        """
        Waits for tasks to complete and validates their code
        """
        for task in self.background_tasks:
            exitcode = task['process'].wait()
            if exitcode and task['raise_on_fail']:
                self.Context.exceptions = []
                self.save_exceptions()
                raise Exception('Task `{}` finished with exit code {}'.format(task['name'], exitcode))

        if not os.path.exists(str(self.log_path('diffbuilder.out.log'))):
            self.Context.diff_builder_result = 'Diffbuilder file not found'
            return

        with open(str(self.log_path('diffbuilder.out.log')), 'r') as diffbuilder_out:
            self.Context.diff_builder_result = diffbuilder_out.read()

    def set_task_status_mongo(self, success, collection=None):
        if not self.Parameters.update_commit_info:
            return

        commit = str(self.Parameters.revision)
        doc = {
            'author': self.Context.commit_author,
            'test_passed': success,
            'task_id': str(self.id),
            'status': 'tested'
        }
        self.db_update_one({'commit': commit}, doc, collection)

    def get_commit_author(self, revision):
        author = 'None'
        output = self.gencfg.log(revision)

        try:
            author = output[0]['author']
            match = AUTHOR_RE.match(output[0]['msg'])
            if match:
                author = match.group('author')
        except Exception as e:
            self.print_info('[EXCEPTION] get_commit_author: {}: {}'.format(type(e).__name__, str(e)))

        return author

    def get_commit_from_mongo(self, revision):
        commit = self.db_find_one({'commit': str(revision)})

        if not commit:
            commit = {}

        if 'skip' not in commit:
            commit['skip'] = {'mongo': False, 'clickhouse': False, 'hbf': False}

        return commit

    def _get_oldest_gencfg_trunk_commit(self, commit, leave_last_n=100, max_time_delta=timedelta(hours=7)):
        count = 0
        old_record = bson.ObjectId.from_datetime(datetime.utcnow() - max_time_delta)
        logging.debug('old record: %s', old_record)
        for record in self.db_get_collection(self.Parameters.mongo_db, 'commits').find(
            {
                'test_passed': True,
                'commit': {'$lt': str(commit)}
            },
            sort=[('commit', -1)]
        ):
            count += 1
            if record['_id'] < old_record and count >= leave_last_n:
                return record['commit']

    @helpers.disable_in_dry_run
    def clean_gencfg_trunk(self):
        commit = self.Parameters.revision
        oldest_commit = self._get_oldest_gencfg_trunk_commit(commit)
        logging.info('clean gencfg_trunk: commit < %s', oldest_commit)

        for attempt in range(3):
            try:
                # gencfg_trunk_v1
                gencfg_trunk = mongo.get_collection(self.Parameters.mongo_db, 'gencfg_trunk', mongo.HEARTBEAT_C)
                gencfg_trunk.remove({'commit': {'$lt': int(oldest_commit)}})

                # gencfg_trunk_v2
                gencfg_trunk_v2 = mongo.get_collection(self.Parameters.mongo_db, 'gencfg_trunk', mongo.HEARTBEAT_D)
                gencfg_trunk_v2.remove({'commit': {'$lt': int(oldest_commit)}})
                return
            except Exception:
                time.sleep(1)
        else:
            raise Exception('Failed to remove commits older than <{}> from mongo'.format(oldest_commit))

    def save_exceptions(self, log_dir=None):
        helpers.print_errors_to_info(self, log_dir or self.log_path(), 2)
        self.Context.exceptions = helpers.get_list_errors(log_dir or self.log_path(), 2)
