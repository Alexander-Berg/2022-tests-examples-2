# coding=utf-8
import logging
from datetime import datetime, timedelta
from time import sleep, mktime

from requests import HTTPError
from six.moves import urllib

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.utils import CommonParameters, conductor, settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.parameters import PackageVersion, choices, TrackerIssue
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask

DAEMONS = {
    'mtgiga-test': ('web-giga-writer', True),  # (name, bigrt)
    'mtmobgiga-test': ('app-giga-writer', True)
}


@with_parents
class ClickhouseTestQueuesProcessing(PipelineBaseTask, BaseConsoleMixin):
    SLEEP = 30
    DELAY_THRESHOLD = 100

    class Parameters(CommonParameters):
        description = 'Тест разгребания очереди с КХ'

        kill_timeout = 4 * 60 * 60

        ticket = TrackerIssue()

        cgroup = sdk2.parameters.String('Кондукторная группа', required=True, choices=choices(sorted(DAEMONS)))

        clickhouse_version = PackageVersion('Версия ClickHouse', required=True, package='clickhouse-server')

        ch_config_version = PackageVersion('Версия конфига КХ', required=True, package='clickhouse-server-metrika', host_group='mtgiga-test')

        sleep_time = sdk2.parameters.Integer('Время остановки демона (минуты)', required=True, default=5)

        timeout = sdk2.parameters.Integer('Таймаут на разгребание очереди (минуты)', required=True, default=180)

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_save(self):
        self.Parameters.description = 'Тест разгребания очереди с КХ {} на {}'.format(self.Parameters.clickhouse_version, self.Parameters.cgroup)

    def create_stages(self):
        return [
            (self.install_packages, 'Установка пакетов'),
            (self.daemons_stop, 'Остановка демона'),
            (self.sleep, 'Ожидание'),
            (self.daemons_start, 'Запуск демона'),
            (self.wait_queues, 'Разгребание очереди'),
        ]

    @property
    def deploy_api(self):
        from metrika.pylib.deploy.client import DeployAPI
        return DeployAPI(token=sdk2.yav.Secret(settings.yav_uuid).data()['deploy-token'])

    @property
    def daemon(self):
        return DAEMONS[self.Parameters.cgroup][0]

    @property
    def bigrt(self):
        return DAEMONS[self.Parameters.cgroup][1]

    @property
    def stage_id(self):
        return '{}-testing'.format(self.daemon)

    def install_packages(self):
        from metrika.pylib.mtapi.packages import PackagesAPI
        mtapi = PackagesAPI()
        mtapi._verify = False

        conductor_client = conductor.Conductor(self)
        with self.memoize_stage.tickets(commit_on_entrance=False):
            workflows = {
                'clickhouse': {
                    'clickhouse-client': self.Parameters.clickhouse_version,
                    'clickhouse-common-static': self.Parameters.clickhouse_version,
                    'clickhouse-server': self.Parameters.clickhouse_version,
                },
                'clickhouse-server-metrika': {
                    'clickhouse-server-metrika': self.Parameters.ch_config_version,
                }
            }

            self.Context.conductor_tickets = []
            for workflow, packages in workflows.items():
                for package, version in list(packages.items()):
                    if mtapi.pkg_version_per_group(self.Parameters.cgroup, package) == version:
                        self.comment('На {} уже установлен пакет {}={}'.format(self.Parameters.cgroup, package, version))
                        packages.pop(package)

                if packages:
                    self.Context.conductor_tickets.append(
                        conductor_client.create_conductor_ticket(
                            packages, self.Context.issue_key, no_autoinstall=True, branch='testing',
                            deploy_groups=[('metrika', workflow, self.Parameters.cgroup)]
                        )
                    )
                    self.comment('Кондукторный тикет {0}: <a href=\"https://c.yandex-team.ru/tickets/{1}\">{1}</a>'.format(
                        ', '.join(sorted(packages)), self.Context.conductor_tickets[-1]
                    ))

        if self.Context.conductor_tickets:
            conductor_client.wait_conductor_tickets(self.Context.conductor_tickets)

    def _get_workload(self, spec):
        workloads = (
            spec['deploy_units'][self.daemon]
            ['multi_cluster_replica_set']['replica_set']
            ['pod_template_spec']['spec']
            ['pod_agent_payload']['spec']
            ['workloads']
        )
        for workload in workloads:
            if workload['id'] == self.daemon:
                break
        else:
            raise Exception('Workload {} not found for stage {}'.format(self.daemon, self.stage_id))
        return workload

    def daemons_stop(self):
        from yt.wrapper import yson

        with self.memoize_stage_global.stop_daemon(commit_on_entrance=False):
            spec = self.deploy_api.stage.get_stage_specification(self.stage_id)
            self.Context.revision = spec['revision']

            workload = self._get_workload(spec)
            self.Context.workload_spec = yson.dumps({
                'liveness_check': workload['liveness_check'],
                'readiness_check': workload['readiness_check'],
                'command_line': workload['start']['command_line'],
            })
            workload['liveness_check'] = {}
            workload['readiness_check'] = {}
            workload['start']['command_line'] = 'tail -f /dev/null'
            spec['revision_info']['description'] = 'Остановка {} для тестировния прогрузки SB#{}'.format(self.daemon, self.id)

            self.comment('Останавливаем <a href="https://deploy.yandex-team.ru/stage/{0}">{0}</a>'.format(self.stage_id))
            self.Context.stop_revision = self.deploy_api.stage.update_stage_specification(self.stage_id, spec)

        self.deploy_api.stage.wait_for_ready(self.stage_id, self.Context.stop_revision, timeout=15 * 60)

    def sleep(self):
        # c commit_on_entrance чтобы можно было остановить задачу и после запуска пойти дальше
        with self.memoize_stage.wait:
            self.comment('Спим {} min'.format(self.Parameters.sleep_time))
            sleep(self.Parameters.sleep_time * 60)

    def daemons_start(self):
        from yt.wrapper import yson

        with self.memoize_stage_global.start_daemon(commit_on_entrance=False):
            spec = self.deploy_api.stage.get_stage_specification(self.stage_id)

            workload = self._get_workload(spec)
            workload_spec = yson.loads(self.Context.workload_spec)
            workload['liveness_check'] = workload_spec['liveness_check']
            workload['readiness_check'] = workload_spec['readiness_check']
            workload['start']['command_line'] = workload_spec['command_line']

            spec['revision_info']['description'] = 'Запуск {} после тестировния прогрузки SB#{} (Revert to changes from revision {})'.format(
                self.daemon, self.id, self.Context.revision
            )
            self.comment('Запускаем <a href="https://deploy.yandex-team.ru/stage/{0}">{0}</a>'.format(self.stage_id))
            self.Context.reload_start = mktime(datetime.now().timetuple())
            self.Context.start_revision = self.deploy_api.stage.update_stage_specification(self.stage_id, spec)

        self.deploy_api.stage.wait_for_ready(self.stage_id, self.Context.start_revision, timeout=15 * 60)

    def wait_queues(self):
        from metrika.pylib.solomon import SolomonClient

        solomon = SolomonClient(token=sdk2.yav.Secret(settings.yav_uuid).data()['solomon-token'])
        if not self.bigrt:
            solomon_kwargs = dict(
                cluster='metrika-daemon-queues-test',
                service='metrika-daemon-queues',
                metric='delay', layer='total',
                daemon=self.daemon, queue='total'
            )
        else:
            solomon_kwargs = dict(
                cluster='daemon-queues',
                service='daemon-queues',
                host='testing',
                metric='delay', shard='total',
                daemon=self.daemon, queue='total'
            )

        if not self.Context.start_time:
            try:
                data = solomon.data('metrika', self.Context.reload_start, datetime.now(), **solomon_kwargs)[0]
            except HTTPError as e:
                self.comment(e.response.text)
                raise
            logging.debug(data)
            max_from_reload = max(zip(data['timestamps'], data['values']), key=lambda x: x[1])
            self.Context.start_time = max_from_reload[0] / 1000
            self.Context.start_value = max_from_reload[1]
            self.comment('Разгребаем очередь <a href="https://solomon.yandex-team.ru/?{}">{}</a>'.format(
                urllib.parse.urlencode(dict(project='metrika', graph='auto', **solomon_kwargs)),
                self.daemon
            ))

        while True:
            sleep(self.SLEEP)
            end = datetime.now()
            try:
                data = solomon.data('metrika', self.Context.start_time + 1, end, **solomon_kwargs)[0]
            except HTTPError as e:
                self.comment(e.response.text)
                raise
            logging.debug(data)
            for timestamp, value in zip(data['timestamps'], data['values']):
                if value < self.DELAY_THRESHOLD:
                    end_value = value
                    end_time = datetime.fromtimestamp(timestamp / 1000)
                    break
            else:
                start = end + timedelta(seconds=1)
                seconds_passed = int((start - datetime.fromtimestamp(self.Context.start_time)).total_seconds())
                logging.debug('{} / {} sec'.format(seconds_passed, self.Parameters.timeout * 60))
                if seconds_passed > self.Parameters.timeout * 60:
                    raise Exception('За {} min отставание не стало меньше {} sec'.format(self.Parameters.timeout, self.DELAY_THRESHOLD))
                continue
            break

        start_time = datetime.fromtimestamp(self.Context.start_time)
        result = (
            '{}\n'
            'Старт: {} sec [{}]\n'
            'Конец: {} sec [{}]\n'
            'Скорость: {:.2f} sec отставания в минуту'.format(
                self.Parameters.description,
                self.Context.start_value, start_time.isoformat(),
                int(end_value), end_time.isoformat(),
                (self.Context.start_value - end_value) / ((end_time - start_time).total_seconds() / 60)
            )
        )

        self.comment(result)
        if self.Parameters.ticket:
            self.st_client.issues[self.Parameters.ticket].comments.create(text=result)
