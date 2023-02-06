# coding=utf-8
import datetime

from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import retries
from sandbox.projects.metrika.utils.parameters import PackageVersion
from sandbox.projects.metrika.java import metrika_java_test_stand_create
from sandbox.sdk2 import parameters


class ClickHouseB2BTestStandCreate(metrika_java_test_stand_create.MetrikaJavaTestStandCreate):
    """
    Создание тестового стенда java демонов Метрики для приемки CH (то же самое + CaaS)
    """
    name = 'CLICKHOUSE_B2B_TEST_STAND_CREATE'

    class Parameters(metrika_java_test_stand_create.MetrikaJavaTestStandCreate.Parameters):
        caas_parent = parameters.String(
            'CaaS parent name', required=True, default='days-32_sample-4',
            description='Имя родительского инстанса, который содержит срез тестовых данных'
        )
        clickhouse_version = PackageVersion(
            'ClickHouse стабильная версия', required=True, package='clickhouse-server', host_group='mtgiga',
            description='Референсная версия ClickHouse, по умолчанию берётся с mtgiga'
        )

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        self.create_caas_instance()
        super(ClickHouseB2BTestStandCreate, self).on_execute()

    @retries(3)
    def create_caas_instance(self):
        caas = self.maas_provider.get_caas_client()
        caas.delete_all_instances_by_name(self.stage_name)
        parent_id = caas.get_latest_instance_by_name(self.Parameters.caas_parent).id

        instance = self.maas_provider.get_caas_client()
        instance.create(name=self.stage_name, parent_id=parent_id, ttl=int(datetime.timedelta(weeks=2).total_seconds()), version_tag=self.Parameters.clickhouse_version, memory_limit=96)
        self.Context.caas_clickhouse_port = instance.ports['clickhouse_http']
        self.Context.caas_host = instance.host

    def create_bishop_environment(self):
        from metrika.pylib.bishop import Bishop
        super(ClickHouseB2BTestStandCreate, self).create_bishop_environment()

        bishop_client = Bishop(token=self.Parameters.bishop_token.value())
        bishop_client.variable.create(name='CLICKHOUSE_HOST', value=self.Context.caas_host, environment=self.Context.bishop_environment, variable_type='string')
        bishop_client.variable.create(name='CLICKHOUSE_PORT', value=self.Context.caas_clickhouse_port, environment=self.Context.bishop_environment, variable_type='string')
