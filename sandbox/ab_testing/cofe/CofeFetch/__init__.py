# coding: utf-8
import json
import logging
import os
import tarfile
import tempfile
import threading
import time
import shutil

from sandbox import sdk2
from sandbox.projects.ab_testing import (
    ABT_COFE_YA_PACKAGE,
    COFE_FETCH_RESULT,
)

from sandbox.sdk2 import paths

from sandbox.sdk2.helpers import subprocess as sp
from sandbox.projects.common import file_utils as fu
from sandbox.common.errors import TaskFailure

import sandbox.common.types.resource as ctr
import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn


class CofeFetch(sdk2.Task):
    """Cofe Fetch"""

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 10 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 24 * 60 * 60

        with sdk2.parameters.Group('Main settings') as main_settings:
            espresso = sdk2.parameters.Bool(
                'espresso',
                required=True,
                default=True,
            )

            project = sdk2.parameters.String(
                'project',
                required=True,
            )

            task_names = sdk2.parameters.List(
                'task names',
            )

            stage = sdk2.parameters.String(
                'stage',
                choices=[
                    ('preliminary', 'preliminary'),
                    ('main', 'main'),
                ],
                default=None,
            )

            period = sdk2.parameters.String(
                'period',
                required=True,
                choices=[
                    ('daily', 'daily'),
                    ('fast', 'fast'),
                ],
                default='daily',
            )

            dates = sdk2.parameters.String(
                'dates',
                required=True,
            )

            namespace = sdk2.parameters.String(
                'namespace',
            )

            backends = sdk2.parameters.List(
                'backends'
            )

            resources_mode = sdk2.parameters.String(
                'resources_mode',
                required=True,
                default='default',
                choices=[
                    ('default', 'default'),
                    ('static', 'static'),
                    ('dynamic', 'dynamic'),
                ]
            )

            format = sdk2.parameters.String(
                'format',
                required=True,
                default='ems',
                choices=[
                    ('ems', 'ems'),
                    ('json', 'json'),
                    ('table', 'table'),
                    ('table_color', 'table_color'),
                ]
            )

        with sdk2.parameters.Group('Slices settings') as slices_settings:
            slices_source = sdk2.parameters.String(
                'slices_source',
                required=True,
                default='config',
                choices=[
                    ('config', 'config'),
                    ('observations', 'observations'),
                ]
            )

            with slices_source.value['config']:
                config = sdk2.parameters.JSON(
                    'config',
                    default='{}',
                )

            with slices_source.value['observations']:
                observations = sdk2.parameters.List(
                    'observations',
                )

        with sdk2.parameters.Group('Solomon settings') as solomon_settings:
            solomon_send = sdk2.parameters.Bool(
                'solomon_send',
                required=True,
                default=False,
            )

            with solomon_send.value[True]:
                solomon_cluster = sdk2.parameters.String(
                    'solomon_cluster',
                    required=True,
                    default='production',
                    choices=[
                        ('production', 'production'),
                        ('testing', 'testing'),
                    ]
                )

                solomon_service = sdk2.parameters.String(
                    'solomon_service',
                    required=True,
                    default='',
                )

        with sdk2.parameters.Group('Additional settings') as additional_settings:
            engine = sdk2.parameters.String(
                'engine',
                default=None,
                choices=[
                    ('local', 'local'),
                    ('yt', 'yt'),
                    ('nile', 'nile'),
                ]
            )

            cofe_token = sdk2.parameters.Vault(
                'cofe token',
                description='\'name\' or \'owner:name\' for extracting from Vault',
                required=True
            )

            yt_pool = sdk2.parameters.String(
                'yt pool',
            )

            yt_proxy = sdk2.parameters.String(
                'yt proxy',
                required=True,
                default='hahn',
            )

            metric_picker_key = sdk2.parameters.String(
                'metric picker key',
            )

            cofe_package_resource = sdk2.parameters.LastReleasedResource(
                'cofe package released resource',
                resource_type=ABT_COFE_YA_PACKAGE,
                state=(ctr.State.READY,),
                required=False,
            )

            resources = sdk2.parameters.JSON(
                'resources',
                default='{}',
            )

    class Context(sdk2.Task.Context):
        command = list()
        progress = ''
        state = ''

    def _run_cmd(self, cmd, env=None, **kwargs):
        logging.debug('Run cmd=%s with env=%s', cmd, env)

        return sp.check_output(cmd, env=env, **kwargs)

    def _download_binaries(self, path_bin):
        logging.info('Downloading binaries to: %s', path_bin)

        path_tar = str(sdk2.ResourceData(self.Parameters.cofe_package_resource).path)

        logging.debug('Path to tar: %s', path_tar)

        with tarfile.open(path_tar) as tar:
            path_tmp = tempfile.mkdtemp()

            try:
                path_deb = None

                for member in tar.getmembers():
                    if member.name.endswith('.deb'):
                        logging.debug('Found deb-package in tar: %s', member.name)

                        path_deb = os.path.join(path_tmp, member.name)

                        logging.debug('Extracting deb-package as: %s', path_deb)

                        tar.extract(member, path_tmp)
                        break

                if path_deb is None:
                    raise TaskFailure('No deb package found in resource')

                cmd = ['dpkg', '-x', path_deb, path_bin]

                self._run_cmd(cmd)
            finally:
                shutil.rmtree(path_tmp)

    def on_execute(self):
        path_root = os.getcwd()
        path_bin = os.path.join(path_root, 'bin')

        logging.info('Preparing resources')

        self._download_binaries(path_bin)

        files = dict(
            cofe=os.path.join(path_bin, 'Berkanavt/ab_testing/bin/cofe'),
            token=os.path.join(path_root, 'token'),
            config=os.path.join(path_root, 'cfg.cfg'),
            result=os.path.join(path_root, 'RES.tmp'),
            progress=os.path.join(path_root, 'progress.txt'),
            state=os.path.join(path_root, 'state.json'),
            resources_json=os.path.join(path_root, 'resources.json'),
            log=os.path.join(paths.get_logs_folder(), 'cofe.log'),
        )

        logging.debug('Files: %s', files)

        logging.info('Saving cofe token')

        cofe_token = self.Parameters.cofe_token.data()

        with open(files['token'], 'w') as f:
            f.write(cofe_token)

        logging.info('Saving config')

        with open(files['config'], 'w') as f:
            json.dump(self.Parameters.config, f)

        logging.info('Saving resources')

        with open(files['resources_json'], 'w') as f:
            f.write(self.Parameters.resources)

        logging.info('Constructing env')

        env = {
            'YT_PREFIX': '//',
            'MR_RUNTIME': 'YT',
            'YT_PROXY': self.Parameters.yt_proxy,
            'YT_TOKEN_PATH': files['token'],
            'YQL_TOKEN_PATH': files['token'],
            'AB_TOKEN_PATH': files['token'],
            'ARCANUM_TOKEN_PATH': files['token'],
            'SOLOMON_TOKEN_PATH': files['token'],
        }

        if self.Parameters.yt_pool:
            env['YT_POOL'] = self.Parameters.yt_pool

        logging.info('Constructing cmd')

        cmd = [
            files['cofe'],
            'espresso' if self.Parameters.espresso else 'fetch',
            '-vv',
            '--log-file', files['log'],
            '--project', self.Parameters.project,
            '--dates', self.Parameters.dates,
            '--period', self.Parameters.period,
            '--result', files['result'],
            '--format', self.Parameters.format,
            '--progress-file', files['progress'],
            '--nile-monitor', 'simple',
            '--resources-mode', self.Parameters.resources_mode,
            '--use-yav',
        ]

        if self.Parameters.slices_source == 'config':
            assert self.Parameters.observations == [], 'observations must be empty when slices_source == \'config\''

            cmd.extend([
                '--config', files['config'],
            ])
        elif self.Parameters.slices_source == 'observations':
            assert self.Parameters.config == '{}', 'config must be empty when slices_source == \'observations\''

            cmd.extend([
                '--observations', ','.join(self.Parameters.observations),
            ])

        if self.Parameters.espresso:
            cmd.extend([
                '--status-file', files['state'],
            ])
            if json.loads(self.Parameters.resources):
                cmd.extend([
                    '--resources-json', files['resources_json'],
                ])

        if self.Parameters.stage:
            cmd.extend([
                '--stage', self.Parameters.stage,
            ])

        if self.Parameters.namespace:
            cmd.extend([
                '--namespace', self.Parameters.namespace,
            ])

        for backend in self.Parameters.backends:
            cmd.extend([
                '--backend', backend,
            ])

        for task_name in self.Parameters.task_names:
            cmd.extend([
                '--task', task_name,
            ])

        if self.Parameters.engine:
            cmd.extend([
                '--engine', self.Parameters.engine,
            ])

        if self.Parameters.metric_picker_key:
            cmd.extend([
                '--metric-picker-key', self.Parameters.metric_picker_key,
            ])

        if self.Parameters.solomon_send:
            if not self.Parameters.solomon_service:
                raise ValueError('solomon_service must be specified')

            cmd.extend([
                '--solomon-cluster', self.Parameters.solomon_cluster,
                '--solomon-service', self.Parameters.solomon_service,
            ])

        self.Context.command = list(cmd)
        self.Context.save()

        logging.info('Starting progress thread')

        progress_thread = ProgressThread(self, [
            {
                'file': files['progress'],
                'field': 'progress',
                'log': True,
            },
            {
                'file': files['state'],
                'field': 'state',
            },
        ])

        progress_thread.start()

        try:
            logging.info('Running cofe')
            self._run_cmd(cmd, env=env, stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            raise RuntimeError('cofe command {} failed with code {} and output:\n\n{}'.format(
                e.cmd, e.returncode, e.output,
            ))
        finally:
            logging.info('Stopping progress thread')
            progress_thread.stop()
            progress_thread.join()

        if not os.path.exists(files['result']):
            raise TaskFailure('Result file doesn\'t exist')

        logging.info('Creating resource')

        resource_data = sdk2.ResourceData(
            COFE_FETCH_RESULT(
                self, 'cofe result', files['result']
            )
        )
        resource_data.path.write_bytes(fu.read_file(files['result']))
        resource_data.ready()

        logging.info('Resource created')


class ProgressThread(threading.Thread):
    def __init__(self, task, data):
        super(ProgressThread, self).__init__()

        self._task = task
        self._data = data

        self._stop_event = threading.Event()

    def run(self):
        while True:
            try:
                self._handle()
            except Exception as e:
                logging.error('ERROR in progress thread: %s', e)
                return

            if self._stop_event.is_set():
                break

            time.sleep(5)

    def _handle(self):
        need_update = False

        for item in self._data:
            if not os.path.exists(item['file']):
                continue

            with open(item['file'], 'r') as f:
                value_new = f.read()

            value_old = getattr(self._task.Context, item['field'])

            if value_old == value_new:
                continue

            logging.debug('Update context field=\'{}\', value=\'{}\''.format(
                item['field'],
                value_new if item.get('log') else '...hidden...',
            ))

            setattr(self._task.Context, item['field'], value_new)

            need_update = True

        if need_update:
            logging.debug('Saving context')

            self._task.Context.save()

    def stop(self):
        self._stop_event.set()
