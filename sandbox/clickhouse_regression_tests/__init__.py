# coding=utf-8
from datetime import timedelta

from sandbox import sdk2
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.utils.parameters import PackageVersion
from sandbox.projects.metrika.admins.clickhouse.utils import build_clickhouse_docker_images
from sandbox.projects.metrika.core.metrika_core_arcadia_tests_run import MetrikaCoreArcadiaTestsRun
from sandbox.projects.metrika.utils import CommonParameters, settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.maas import MaasProvider
from sandbox.projects.metrika.utils.parameters import TrackerIssue, ArcadiaURL, DataCenterParameters
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask


@with_parents
class ClickhouseRegressionTests(PipelineBaseTask):
    class Parameters(CommonParameters):
        description = 'Регрессионные тесты КХ'

        arcadia_url = ArcadiaURL('URL Аркадии', required=True)
        ticket = TrackerIssue()

        use_existing_caas = sdk2.parameters.Bool('Использовать существующий инстанс в СaaS')

        with use_existing_caas.value[True]:
            caas_instance_id = sdk2.parameters.Integer('Идентификатор инстанса в CaaS', required=True)

        with use_existing_caas.value[False]:
            caas_instance_name = sdk2.parameters.String('Имя инстанса в CaaS', required=True, default='ch-regression-tests')

            clickhouse_version = PackageVersion(
                'Версия ClickHouse', required=True, package='clickhouse-client', host_group='mtgiga',
                description='Версия ClickHouse для родительского инстанса. По умолчанию берётся с mtgiga'
            )

            ch_config_version = PackageVersion(
                'Версия конфига КХ', required=True, package='clickhouse-server-metrika', host_group='mtgiga',
                description='Версия конфига КХ для родительского инстанса. По умолчанию берётся версия пакета clickhouse-server-metrika с mtgiga'
            )

            yt_dictionaries_version = PackageVersion(
                'Версия словарей YT', required=True, package='yandex-clickhouse-dictionary-yt', host_group='mtgiga',
                description='Версия yt-словарей для родительского инстанса. По умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga'
            )

        data_center_params = DataCenterParameters()

        bishop_token = sdk2.parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                        description="Секрет с токеном для доступа к bishop")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_save(self):
        if not self.Parameters.use_existing_caas:
            self.Parameters.description = 'Регрессионные тесты КХ ' + self.Parameters.clickhouse_version

    def create_stages(self):
        return [
            (self.build_ch, 'Сборка образа КХ'),
            (self.create_caas_instance, 'Создание стенда'),
            (self.tests, 'Тесты'),
            (self.delete_caas_instance, 'Удаление стенда'),
        ]

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value(), self.Parameters.data_center)

    def build_ch(self):
        if not self.Parameters.use_existing_caas:
            build_clickhouse_docker_images(self, (self.Parameters.clickhouse_version, self.Parameters.ch_config_version, self.Parameters.yt_dictionaries_version))

    def create_caas_instance(self):
        caas = self.maas_provider.get_caas_client()

        if self.Parameters.use_existing_caas:
            caas.id = self.Parameters.caas_instance_id
        else:
            parent_id = self.maas_provider.get_caas_client().get_latest_instance_by_name('days-32_sample-4').id

            caas = self.maas_provider.get_caas_client()

            caas.create(
                name='{name}:{id}'.format(name=self.Parameters.caas_instance_name, id=self.id),
                parent_id=parent_id,
                ttl=int(timedelta(days=30).total_seconds()), memory_limit=96,
                version_tag=self.Context.caas_yt_versions[-1]
            )

        caas.get_status()

        self.Context.caas_id = caas.id
        self.Context.ch_host = caas.host
        self.Context.ch_port = caas.ports['clickhouse_http']

        self.set_info('Инстанс CaaS {id}: {host}:{port}'.format(id=self.Context.caas_id, host=self.Context.ch_host, port=self.Context.ch_port))

    def tests(self):
        params = dict(
            description='Регрессионные тесты КХ ' + self.Context.caas_yt_versions[-1],
            checkout_arcadia_from_url=self.Parameters.arcadia_url.format(author=self.author, ticket=self.Parameters.ticket),
            targets='metrika/admin/python/clickhouse_regression_tests',
            test_params='host={} port={}'.format(self.Context.ch_host, self.Context.ch_port),
            env_vars="METRIKA_VAULT_TOKEN='$(vault:value:{}:{})'".format(settings.owner, settings.yav_token),
            definition_flags='-DSB',
            fail_task_on_test_failure=True,
        )
        if self.Parameters.ticket:
            params.update(
                report_startrek=True,
                issue_key=self.Parameters.ticket
            )
        self.run_subtasks([(MetrikaCoreArcadiaTestsRun, params)])

    def delete_caas_instance(self):
        caas = self.maas_provider.get_caas_client()
        caas.id = self.Context.caas_id
        caas.delete()
        self.set_info('Инстанс CaaS {id} удален'.format(id=self.Context.caas_id))
