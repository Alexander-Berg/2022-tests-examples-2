# -*- coding: utf-8 -*-

import os
import time

import requests

from sandbox import sdk2

from sandbox.common.types.client import Tag
from sandbox.common.types.task import Semaphores, Status
from sandbox.sandboxsdk.environments import PipEnvironment
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sdk2.helpers import subprocess as sp


class AURORA_PARSER_TEST_ARCHIVE(sdk2.Resource):
    """
        Archive containing parser for Aurora tests.
    """
    releasable = False
    any_arch = False
    parser_type = sdk2.Attributes.String("Parser type", required=True, default="scraper")


class AuroraBinary(sdk2.Resource):
    releasable = False
    any_arch = False


class TestAuroraBundle(sdk2.Task):

    TEST_TASK_NAMES = ['sandbox_test_scraper', 'sandbox_test_graph', 'sandbox_test_parser',
                       'sandbox_test_join_robot_base']

    SERVICE_TASK_NAMES = ['executions_creator', 'output_collector', 'graph_scheduler',
                          'download_watcher', 'yt_parser_launcher']

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 20 * 60  # 20 minutes
        aurora_binary = sdk2.parameters.Resource(
            'aurora_binary_id',
            resource_type=AuroraBinary,
            required=True
        )

    class Requirements(sdk2.Requirements):
        environments = [
            PipEnvironment('requests'),
        ]
        client_tags = (Tag.LINUX_XENIAL | Tag.LINUX_BIONIC) & Tag.PORTOD
        semaphores = Semaphores(
            acquires=[
                Semaphores.Acquire(name='test_aurora_mongo_base')
            ],
        )
        disk_space = 2 * 1024  # 2 GB

    @staticmethod
    def fail(message, *args, **kwargs):
        raise SandboxTaskFailureError(message.format(*args, **kwargs))

    def on_break(self, prev_status, status):
        if status == Status.TIMEOUT:
            raise SandboxTaskFailureError('TestAuroraBundle was timeouted.')

    def on_execute(self):

        def check(func, *args, **kwargs):
            try:
                r = func(*args, **kwargs)
            except Exception as e:
                self.fail('Exception during request = {}', e.message)

            if not r.ok:
                self.fail('Reason = {}, Code = {}\n{}', r.reason, r.status_code, r.content)
            return r

        def __create_environment():
            aurora_processes_environment = os.environ.copy()
            aurora_processes_environment['AURORA_CONFIG'] = 'sandbox_test'
            aurora_processes_environment['LOAD_ANIMALS_TOKENS'] = 'yes'
            aurora_processes_environment['PATH'] = ':'.join([
                os.path.join(os.getcwd(), 'bin'),
                os.environ.get('PATH', '')
            ])
            return aurora_processes_environment

        def __setup(pl_master, pl_scheduler, pl_metaworker):

            def get_parser_resource(parser_type):
                resource = sdk2.Resource.find(
                    resource_type=AURORA_PARSER_TEST_ARCHIVE,
                    attrs=dict(parser_type=parser_type)
                ).order(-sdk2.Resource.id).first()
                resource_tar_path = str(sdk2.ResourceData(resource).path)
                resource_tar = open(resource_tar_path, 'rb')
                return resource_tar.read()

            def construct_parser(name, parser_type, command, config=None):
                parser = {
                    'name': name,
                    'client': 'mighty_tester',
                    'project': 'test_it_all',
                    'owner': 'sandbox_test',
                    'timeout': '1380',
                    'schedule': '0 0 * * *',
                    'parser_type': parser_type,
                    'command': command,
                    'storage': 'hahn',
                    'storage_path': 'TestAuroraBundle_output',
                    'queue': 'default',
                    'monitor_every_execution': 'true',
                    'monitoring_field': '["stdout", "valid"]',
                    'monitoring_threshold': '[0.7, 0.7]',
                    'data_format': 'json',
                    'output_type': 'columnar_strict',
                    'cache_enabled': 'true',
                    'language': 'python 2.7.11',
                    'force_random_user_agent': 'false',
                    'proxy_region': 'RU',
                    'daa_enabled': 'true',
                    'proxy_type': 'animals',
                    'monitoring_alert_enabled': 'false',
                }

                if config:
                    parser.update(config)

                return parser

            aurora_path = str(sdk2.ResourceData(self.Parameters.aurora_binary).path)
            if not os.path.exists('./aurora'):
                os.symlink(aurora_path, './aurora')

            aurora_processes_environment = __create_environment()

            animals_auth_tokens = sdk2.Vault.data('AURORA_ANIMALS_AUTH_TOKENS')
            open('animals_auth_tokens', 'w').write(animals_auth_tokens)

            secrets = sdk2.Vault.data('AURORA_TEST_SECRETS')
            open('aurora.conf', 'w').write(secrets)

            pl_cli_cleanup = sdk2.helpers.ProcessLog(self, logger='cli.cleanup')
            try:
                cli_return_code = sp.Popen(
                    [aurora_path, '--patch-path', 'aurora.conf', 'cleanup-db'],
                    shell=False,
                    stdout=pl_cli_cleanup.stdout,
                    stderr=sp.STDOUT,
                    env=aurora_processes_environment
                ).wait()
                if cli_return_code != 0:
                    self.fail('aurora-cli failed to execute')
            finally:
                pl_cli_cleanup.close()

            sp.Popen(
                [aurora_path, 'nameserver', '--storage', 'sql:pyro_nameserver.sqlite'],
                shell=False, stdout=pl_metaworker.stdout, stderr=sp.STDOUT
            )

            master = sp.Popen(
                [aurora_path, '--patch-path', 'aurora.conf', 'master'],
                shell=False, env=aurora_processes_environment, stdout=pl_master.stdout, stderr=sp.STDOUT
            )

            scheduler = sp.Popen(
                [aurora_path, '--patch-path', 'aurora.conf', 'scheduler'],
                shell=False, env=aurora_processes_environment, stdout=pl_scheduler.stdout, stderr=sp.STDOUT
            )

            time.sleep(10)  # wait a bit, let him create all collections in MongoDB

            if master.poll() is not None:
                self.fail('master failed to start')
            if scheduler.poll() is not None:
                self.fail('scheduler failed to start')

            metaworker = sp.Popen(
                [aurora_path, '--patch-path', 'aurora.conf', 'metaworker-master'],
                shell=False,
                env=aurora_processes_environment,
                stdout=pl_metaworker.stdout,
                stderr=sp.STDOUT
            )

            time.sleep(1)  # wait a bit just in case

            if metaworker.poll() is not None:
                self.fail('aurora-metaworker failed to start')

            scraper_data = get_parser_resource('scraper')
            scraper = construct_parser(
                name='sandbox_test_scraper',
                parser_type='scraper',
                command='python script.py'
            )

            graph_data = get_parser_resource('execution_graph')
            graph_config = {
                'step_one_command': 'python generate_urls.py',
                'step_one_use_builtins': 'false',
                'merge_step_type': 'default'
            }
            execution_graph = construct_parser(
                name='sandbox_test_graph',
                parser_type='execution_graph',
                command='python get_titles.py',
                config=graph_config
            )

            join_robot_base_data = get_parser_resource('join_robot_base')
            join_robot_base_config = {
                'step_one_command': '//home/aurora/tests_data/join_robot_base_input',
                'step_one_use_builtins': 'true',
                'join_robot_base': 'true',
                'host': 'https://1xsis.host',
                'merge_step_type': 'default'
            }
            join_robot_base = construct_parser(
                name='sandbox_test_join_robot_base',
                parser_type='execution_graph',
                command='python parser.py',
                config=join_robot_base_config
            )

            parser_data = get_parser_resource('parser')
            parser_config = {
                'host': 'http://example.com',
                'url_pattern': '.*',
                'custom_source_url_table': '//home/aurora/tests_data/example_com',
                'source_url_table': 'custom',
                'threads_count': 25,
                'urls_limit': 0,
                'merge_step_type': 'default'
            }
            parser = construct_parser(
                name='sandbox_test_parser',
                parser_type='parser',
                command='python parser.py',
                config=parser_config
            )

            check(requests.post, 'http://localhost:18375/api/v1/task', scraper,
                  files={'files_python_code_tar_gz': scraper_data})
            check(requests.post, 'http://localhost:18375/api/v1/task', execution_graph,
                  files={'files_python_code_tar_gz': graph_data})
            check(requests.post, 'http://localhost:18375/api/v1/task', join_robot_base,
                  files={'files_python_code_tar_gz': join_robot_base_data})
            check(requests.post, 'http://localhost:18375/api/v1/task', parser,
                  files={'files_python_code_tar_gz': parser_data})

            for task_name in self.SERVICE_TASK_NAMES + self.TEST_TASK_NAMES:
                check(requests.get,
                      'http://localhost:18375/api/v1/task/' + task_name + '/force_execute')

            return master, scheduler, metaworker

        def __run_test(metaworker):
            failed_tasks = []
            tests_finished = False
            service_tasks_count = len(self.SERVICE_TASK_NAMES)
            tasks_to_watch = self.SERVICE_TASK_NAMES + self.TEST_TASK_NAMES
            task_count = len(tasks_to_watch)
            while True:
                if metaworker.poll() is not None:
                    self.fail('aurora-metaworker stopped abruptly.')

                for task_name in tasks_to_watch:
                    r = check(requests.get, 'http://localhost:18375/api/v2/tasks/{}'.format(task_name)).json()

                    task_status = r['data']['status']
                    if task_status == 'FAILED':
                        failed_tasks.append(r['data'])
                        if task_name in self.SERVICE_TASK_NAMES:
                            tests_finished = True
                            break
                        elif task_name in self.TEST_TASK_NAMES:
                            tasks_to_watch.remove(task_name)
                    elif task_name in self.TEST_TASK_NAMES and task_status == 'SUCCESS':
                        tasks_to_watch.remove(task_name)

                    if len(tasks_to_watch) == service_tasks_count:
                        tests_finished = True
                        break

                if tests_finished:
                    break

                # wait more
                time.sleep(1)

            return failed_tasks, task_count

        def __cleanup(master, scheduler, metaworker, failed_tasks, task_count):

            if not failed_tasks:
                for task_name in self.TEST_TASK_NAMES:
                    check(requests.delete, 'http://localhost:18375/api/v1/task/' + task_name)

            master.send_signal(2)
            scheduler.send_signal(2)
            metaworker.send_signal(2)

            master_code = master.wait(timeout=10)
            scheduler_code = scheduler.wait(timeout=30)

            metaworker_code = metaworker.wait()

            failed_list = []
            for failed_task in failed_tasks:
                for execution in failed_task[u'executions']:
                    if execution[u'status'] == u'FAILED':
                        failed_task_name = 'Failed task name: ' + execution[u'name']
                        failed_list.extend([failed_task_name, execution[u'worker'].get('stderr', '')])

            failed_string = '\n'.join(failed_list)

            if len(failed_tasks) > 0:
                self.fail('{} of {} tasks have failed to execute: {}', len(failed_tasks), task_count, failed_string)

            if master_code:
                self.fail('master exited with code {}', master_code)

            if scheduler_code:
                self.fail('scheduler exited with code {}', scheduler_code)

            if metaworker_code:
                self.fail('aurora-metaworker exited with code {}', metaworker_code)

        pl_master = sdk2.helpers.ProcessLog(self, logger='master')
        pl_scheduler = sdk2.helpers.ProcessLog(self, logger='scheduler')
        pl_metaworker = sdk2.helpers.ProcessLog(self, logger='metaworker')

        try:
            master, scheduler, metaworker = __setup(pl_master, pl_scheduler, pl_metaworker)
            failed_tasks, task_count = __run_test(metaworker)
            __cleanup(master, scheduler, metaworker, failed_tasks, task_count)
        finally:
            pl_metaworker.close()
            pl_scheduler.close()
            pl_master.close()
