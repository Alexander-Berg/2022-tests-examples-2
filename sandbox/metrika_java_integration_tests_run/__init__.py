# coding=utf-8
from __future__ import unicode_literals

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins.cosmos.cosmos_launcher import CosmosLauncher
from sandbox.projects.metrika.admins.cosmos.utils import ReportTtlParameters
from sandbox.projects.metrika.java.utils import get_host
from sandbox.projects.metrika.utils import CommonParameters, settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents, BaseMetrikaTask
from sandbox.projects.metrika.utils.parameters import ArcadiaURL, TrackerIssue


@with_parents
class MetrikaJavaIntegrationTestsRun(BaseMetrikaTask):
    class Parameters(CommonParameters):
        description = 'Запуск COSMOS_LAUNCHER'

        arcadia_url = ArcadiaURL(required=True)
        ticket = TrackerIssue()

        daemon = sdk2.parameters.String('Имя демона', required=True)
        version = sdk2.parameters.String('Версия демона', required=True)
        release = sdk2.parameters.String('Релиз в деплое для ожидания')
        stage = sdk2.parameters.String('Стейдж в деплое куда установлена версия демона', required=True, default='faced-testing')
        https = sdk2.parameters.Bool('Https', default=False)
        port = sdk2.parameters.Integer('Порт', required=True, default=8080)

        with sdk2.parameters.Group('Параметры COSMOS_LAUNCHER') as run:
            build_configuration = sdk2.parameters.JSON(
                'Конфигурация сборки',
                description='подстановки вычисляются автоматически',
                default={
                    '{daemon}/pom.xml': {
                        'schemas.server': '{host}'
                    }
                },
                required=True
            )

            run_configuration = sdk2.parameters.JSON(
                'Конфигурация прогона',
                description='подстановки вычисляются автоматически',
                default={
                    'metrika-2-api-integration': {
                        'api.testing': '{host}'
                    }
                },
                required=True
            )

            need_semaphore = sdk2.parameters.Bool('Необходимость семафора')

            report_ttl_params = ReportTtlParameters()

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def _format_recursive(self, d, substitutions):
        formatted_dict = {}
        for k, v in d.items():
            if isinstance(v, list):
                formatted_dict[k.format(**substitutions)] = [e.format(**substitutions) for e in v]
            elif isinstance(v, dict):
                formatted_dict[k.format(**substitutions)] = self._format_recursive(v, substitutions)
            else:
                formatted_dict[k.format(**substitutions)] = v.format(**substitutions)
        return formatted_dict

    def on_execute(self):
        from metrika.pylib.deploy.client import DeployAPI
        from metrika.pylib.mtapi.packages import PackagesAPI

        with self.memoize_stage['host'](commit_on_entrance=False):
            host = get_host(self.Parameters.stage)
            self.Context.host = 'http{proto}://{host}:{port}'.format(
                proto='s' if self.Parameters.https else '',
                host=host,
                port=self.Parameters.port
            )

        with self.memoize_stage['wait_release'](commit_on_entrance=False):
            if self.Parameters.release:
                deploy_api = DeployAPI(token=sdk2.yav.Secret(settings.yav_uuid).data()['deploy-token'])
                deploy_api.release.wait_for_closed(self.Parameters.release)

        with self.memoize_stage['check_version'](commit_on_entrance=False):
            version = PackagesAPI().pkg_version_from_deploy(self.Parameters.stage.rsplit('-', 1)[0], 'testing')
            if version != self.Parameters.version:
                raise Exception('Версия {} не установлена на {}'.format(self.Parameters.version, self.Parameters.stage))

        substitutions = dict(daemon=self.Parameters.daemon, host=self.Context.host)
        self.run_subtasks(
            (
                CosmosLauncher,
                dict(
                    description='Запуск интеграционных тестов {} из {}'.format(self.Parameters.daemon, self.Parameters.arcadia_url),
                    arcadia_path='metrika/java/tests',
                    vcs='arcadia',
                    arcadia_url=self.Parameters.arcadia_url,
                    report_startrek=bool(self.Parameters.ticket),
                    issue_key=self.Parameters.ticket,
                    fail_task_on_test_failure=True,
                    build_configuration=self._format_recursive(self.Parameters.build_configuration, substitutions),
                    packs_dirs=['{}/packs'.format(self.Parameters.daemon)],
                    run_configuration=self._format_recursive(self.Parameters.run_configuration, substitutions),
                    semaphore_name='COSMOS_LAUNCHER-{name}'.format(name=self.Parameters.daemon) if self.Parameters.need_semaphore else None,
                    report_ttl=self.Parameters.report_ttl
                )
            )
        )
