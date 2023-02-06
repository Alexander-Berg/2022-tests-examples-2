# coding=utf-8
import logging
from datetime import timedelta
from urllib import quote_plus

import datetime
import six
import yaml

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.common.types import resource as ctr
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika.admins.clickhouse.clickhouse_statbox_traf_queries_prepare import ClickHouseStatboxTrafQueriesPrepare
from sandbox.projects.metrika.admins.clickhouse.clickhouse_statbox_traf_tests_pipeline.state import State
from sandbox.projects.metrika.admins.clickhouse.clickhouse_statbox_traf_tests_run import ClickHouseStatboxTrafTestRun
from sandbox.projects.metrika.admins.clickhouse.utils import build_clickhouse_docker_images, create_caas_session
from sandbox.projects.metrika.admins.cosmos import utils as cosmos_utils
from sandbox.projects.metrika.core.metrika_core_dicts_upload import DictsReleaseResource
from sandbox.projects.metrika.utils import CommonParameters
from sandbox.projects.metrika.utils import parameters
from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.maas import VERSION_TAG, MaasProvider
from sandbox.projects.metrika.utils.parameters import ArcadiaURL, DataCenterParameters
from sandbox.projects.metrika.utils.parameters import PackageVersion
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask
from sandbox.projects.metrika.utils.pipeline.pipeline_errors import PipelineAbortError


class DictsTsvResource(sdk2.Resource):
    restart_policy = ctr.RestartPolicy.IGNORE


@with_parents
class ClickHouseStatboxTrafTestsPipeline(PipelineBaseTask):
    name = "CLICKHOUSE_STATBOX_TRAF_TESTS_PIPELINE"

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Context(PipelineBaseTask.Context):
        pipeline_state = State().state
        queries_task_id = []
        b2b_tests_task_id = []

    class Parameters(CommonParameters):
        description = 'B2B-тесты ClickHouse на запросах StatBox'

        arcadia_url = ArcadiaURL('URL Аркадии', required=True)

        container = parameters.LastPeasantContainerResource("Environment container resource", required=True)

        ch_dicts_resource = sdk2.parameters.Resource("Кастомные словари CH", resource_type=DictsReleaseResource)

        reporting = cosmos_utils.ReportStartrekParameters()

        with sdk2.parameters.Group("CaaS") as caas_group:
            data_center_params = DataCenterParameters()
            caas_parent = sdk2.parameters.String('CaaS parent name', required=True, default='days-32_sample-4',
                                                 description="Имя родительского инстанса, который содержит срез тестовых данных")
            caas_ttl = sdk2.parameters.Integer('TTL тестового стенда в сутках', required=True, default=2)

        with sdk2.parameters.Group("Запросы") as queries_group:
            force_pkg_version = sdk2.parameters.Bool("Задать явно версию пакета", required=True, default=False)
            with force_pkg_version.value[True]:
                pkg_version = sdk2.parameters.String("Версия пакета", required=True)

        with sdk2.parameters.Group("Пакеты") as packages_group:
            clickhouse_version_ref = PackageVersion("ClickHouse стабильная версия", required=True, package="clickhouse-client", host_group="mtgiga",
                                                    description="Референсная версия ClickHouse, по умолчанию берётся с mtgiga")
            clickhouse_version_test = PackageVersion("ClickHouse тестируемая версия", required=True, package="clickhouse-client", host_group="mtgiga",
                                                     description="Тестируемая версия ClickHouse, по умолчанию берётся с mtgiga")

            config_version_ref = PackageVersion("clickhouse-server-metrika стабильная версия", required=True, package="clickhouse-server-metrika", host_group="mtgiga",
                                                description="Референсная версия clickhouse-server-metrika, по умолчанию берётся с mtgiga")
            config_version_test = PackageVersion("clickhouse-server-metrika тестируемая версия", required=True, package="clickhouse-server-metrika", host_group="mtgiga",
                                                 description="Тестируемая версия clickhouse-server-metrika, по умолчанию берётся с mtgiga")

            yt_dictionaries_ref = PackageVersion("Словари YT стабильная версия", required=True, package="yandex-clickhouse-dictionary-yt", host_group="mtgiga",
                                                 description="Референсная версия yt-словарей, по умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga")
            yt_dictionaries_test = PackageVersion("Словари YT тестируемая версия", required=True, package="yandex-clickhouse-dictionary-yt", host_group="mtgiga",
                                                  description="Тестируемая версия yt-словарей, по умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga")

        with sdk2.parameters.Group("Настройки теста") as test_settings_group:
            tolerance = sdk2.parameters.Bool("Использовать сравнение с погрешностью", required=True, default=False,
                                             description="Если задано, то числа будут сравниваться с некоторой абсолютной погрешностью")
            with tolerance.value[True]:
                max_abs_diff = sdk2.parameters.Float("Максимальная абсолютная погрешность", required=False, default=0.01,
                                                     description="https://st.yandex-team.ru/METRIQA-2980#5c5ae04dc196de001fd25286")

        with sdk2.parameters.Group(label="Секреты") as secrets_group:
            ch_user = sdk2.parameters.String('ClickHouse user', required=True, default='robot-metrika-ch-test')
            ch_password = sdk2.parameters.YavSecret('ClickHouse password', required=True, default='{}#clickhouse-password'.format(settings.yav_uuid))
            bishop_token = sdk2.parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                            description="Секрет с токеном для доступа к bishop")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value(), self.Parameters.data_center)

    @property
    def _caas_session(self):
        try:
            return self.__caas_session
        except AttributeError:
            self.__caas_session = create_caas_session(self.Parameters.ch_user, self.Parameters.ch_password.data()[self.Parameters.ch_password.default_key])
        return self.__caas_session

    def _caas_client(self):
        return self.maas_provider.get_caas_client()

    def create_stages(self):
        return [
            (self.prepare_dicts, "Словари ClickHouse"),
            (self.prepare_docker_images, "Docker-образы ClickHouse"),
            (self.create_stand, "Создание тестового стенда"),
            (self.prepare_queries, "Тестовые запросы"),
            (self.run_tests, "Прогон тестов"),
            (self.delete_stand, "Удаление тестового стенда")
        ]

    def prepare_dicts(self):
        # TODO - тут происходит какой-то угар, это нужно переделать.
        # если не задано ch_dicts_resource - то всё нормально - используется то содержимое MaaS, что у нас есть
        # а вот если он задан (из таски релиза словарей https://a.yandex-team.ru/arc/trunk/arcadia/sandbox/projects/metrika/core/metrika_core_dicts_release/__init__.py?rev=r9365563#L140)
        # то начинается трэш и угар - из ресурса, который содержит sql-файлы словарей формируется ресурс с TSV-файлами словарей, котоырй передаётся
        # в CaaS при создании стенда.
        # нужно сделать так, что бы сюда сразу передавался ресурс, а формировался в пайплайне релиза словарей.
        from metrika.pylib.bishop import Bishop
        import pymysql
        if not self.Parameters.ch_dicts_resource:
            return

        stand_name = 'statbox-traf-test-{task_id}'.format(task_id=self.id)
        maas = self.maas_provider.get_maas_client()
        if not self.Context.maas_id:
            logging.debug('Creating MaaS stand %s', stand_name)
            parent = maas.get_latest_instance_by_name('vanilla-80')
            maas.create(name=stand_name, parent_id=parent.id, version_tag=VERSION_TAG, ttl=int(datetime.timedelta(days=3).total_seconds()))
            self.Context.maas_id = maas.id
        else:
            maas.id = self.Context.maas_id
            maas.get_status()

        bishop_client = Bishop(token=sdk2.yav.Secret(settings.yav_uuid).data()['bishop-token'])
        config = bishop_client.get_config('metrika-build-dictionary', 'metrika.sandbox.admin.production')[2]

        # HACK грязные хаки чтобы выцепить несекретное содержимое в шаблоне с секретами, до которых нет доступа
        yaml.add_multi_constructor('!', lambda loader, suffix, node: None)
        config = yaml.load(config)['dicts']

        dicts_info = {info['table']: dict(fields=info['fields'], name=name) for name, info in config.iteritems() if 'fields' in info}

        connection = pymysql.connect(
            host=maas.host, port=maas.ports['mysql'],
            user='stand', password=sdk2.yav.Secret('sec-01f2p6kyz96gzz6j8k0zjs9851').data()['stand'],
            use_unicode=True
        )
        with connection.cursor() as cursor:
            logging.debug('Creating database %s', stand_name)
            cursor.execute('DROP DATABASE IF EXISTS `{}`;'.format(stand_name))
            cursor.execute('CREATE DATABASE `{}`;'.format(stand_name))
            cursor.execute('USE `{}`;'.format(stand_name))

            sql_dicts_dir = sdk2.ResourceData(self.Parameters.ch_dicts_resource).path
            tsv_dicts_dir = self.path('wd', 'tsv_dicts')
            tsv_dicts_dir.mkdir(parents=True, exist_ok=True)

            for file in sql_dicts_dir.glob('*'):
                dict_name = file.stem
                if dict_name not in dicts_info:
                    logging.debug('Skipping %s', dict_name)
                    continue

                logging.debug('Creating and populating table %s', dict_name)

                for line in file.read_text(encoding='utf8').split(';\n'):
                    line = line.strip()
                    if line:
                        logging.debug(line)
                        cursor.execute(line)
                connection.commit()

                cursor.execute('SELECT {} FROM `{}`;'.format(', '.join(dicts_info[dict_name]['fields']), dict_name))
                tsv_dicts_dir.joinpath(dicts_info[dict_name]['name'] + '.txt').write_text(
                    '\n'.join('\t'.join(six.text_type(v) if v is not None else '' for v in line) for line in cursor.fetchall()),
                    encoding='utf8'
                )
            logging.debug('Deleting database %s', stand_name)
            cursor.execute('DROP DATABASE `{}`;'.format(stand_name))

        logging.debug('Deleting MaaS stand %s', stand_name)
        maas.delete()

        if list(tsv_dicts_dir.glob('*')):
            tsv_dicts_resource = DictsTsvResource(self, self.Parameters.ch_dicts_resource.description, tsv_dicts_dir.as_posix())
            sdk2.ResourceData(tsv_dicts_resource).ready()
            self.Context.tsv_dicts_resource_id = tsv_dicts_resource.id

    def prepare_docker_images(self):
        build_clickhouse_docker_images(
            self,
            [
                (self.Parameters.clickhouse_version_ref, self.Parameters.config_version_ref, self.Parameters.yt_dictionaries_ref),
                (self.Parameters.clickhouse_version_test, self.Parameters.config_version_test, self.Parameters.yt_dictionaries_test)
            ],
            without_merges=True
        )

    def _delete_caas_instance(self, id):
        logging.info("Удаляем инстанс {}".format(id))
        try:
            instance = self._caas_client()
            instance.id = id
            instance.delete()
        except:
            logging.info("Удалить инстанс CaaS {} не удалось.".format(id), exc_info=True)

    def create_stand(self):
        if self.pipeline_state.caas_id_test:
            logging.info("Найден ранее созданный инстанс: {}. Будет удалён.".format(self.pipeline_state.caas_id_test))
            self._delete_caas_instance(self.pipeline_state.caas_id_test)

        if self.pipeline_state.caas_id_ref:
            logging.info("Найден ранее созданный инстанс: {}. Будет удалён.".format(self.pipeline_state.caas_id_ref))
            self._delete_caas_instance(self.pipeline_state.caas_id_ref)

        logging.info("Получаем родительский инстанс {name}".format(name=self.Parameters.caas_parent))
        parent = self._caas_client().get_latest_instance_by_name(self.Parameters.caas_parent)
        logging.info("Получен родительский инстанс id: {id}".format(id=parent.id))

        logging.info("Создаём инстансы для родительского инстанса {}".format(parent.id))

        instance = self._caas_client()
        instance.create(name="statbox-traf-test-{task_id}".format(task_id=self.id),
                        parent_id=parent.id,
                        ttl=int(timedelta(days=self.Parameters.caas_ttl).total_seconds()),
                        version_tag=self.Context.caas_yt_no_merges_versions[1],
                        memory_limit=96,
                        resources=['{}:/opt/custom_dicts'.format(self.Context.tsv_dicts_resource_id)] if self.Context.tsv_dicts_resource_id else None)
        self.pipeline_state.caas_id_test = instance.id
        logging.info("Инстанс test: {}".format(self.pipeline_state.caas_id_test))

        instance = self._caas_client()
        instance.create(name="statbox-traf-ref-{task_id}".format(task_id=self.id),
                        parent_id=parent.id, ttl=int(timedelta(days=self.Parameters.caas_ttl).total_seconds()),
                        version_tag=self.Context.caas_yt_no_merges_versions[0],
                        memory_limit=96)
        self.pipeline_state.caas_id_ref = instance.id
        logging.info("Инстанс ref: {}".format(self.pipeline_state.caas_id_ref))

        query = "SELECT * FROM caas.metadata LIMIT 1"
        logging.debug("Execute query: {}".format(query))
        resp = self._caas_session.post("http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}".format(CLICKHOUSE_HOST=self.maas_provider.caas_host, CLICKHOUSE_PORT=instance.ports["clickhouse_http"]) +
                                       "/?query=" + quote_plus(query + " FORMAT JSON"))
        logging.debug(resp.text)
        resp.raise_for_status()
        data = resp.json().get("data")
        if data:
            self.pipeline_state.start_date = data[0]["StartDate"]
        else:
            raise PipelineAbortError("Родительский инстанс CaaS не содержит метаданных")

    def prepare_queries(self):
        params = {
            ClickHouseStatboxTrafQueriesPrepare.Parameters.date.name: self.pipeline_state.start_date,
        }
        if self.Parameters.force_pkg_version:
            params.update({
                ClickHouseStatboxTrafQueriesPrepare.Parameters.force_pkg_version.name: True,
                ClickHouseStatboxTrafQueriesPrepare.Parameters.pkg_version.name: self.Parameters.pkg_version
            })
        self.pipeline_state.queries_task_id = self.run_subtasks([(ClickHouseStatboxTrafQueriesPrepare, params)], self.Context.queries_task_id)[0]
        self.pipeline_state.queries_resource_id = sdk2.Task[self.pipeline_state.queries_task_id].Parameters.queries_resource.id

    def run_tests(self):
        test_instance = self._caas_client()
        test_instance.id = self.pipeline_state.caas_id_test
        test_instance.get_status()

        ref_instance = self._caas_client()
        ref_instance.id = self.pipeline_state.caas_id_ref
        ref_instance.get_status()

        params = {
            ClickHouseStatboxTrafTestRun.Parameters.vcs.name: "arcadia",
            ClickHouseStatboxTrafTestRun.Parameters.arcadia_url.name: self.Parameters.arcadia_url,
            ClickHouseStatboxTrafTestRun.Parameters.arcadia_path.name: "metrika/qa/clickhouse-statbox-tests",

            ClickHouseStatboxTrafTestRun.Parameters.queries.name: self.pipeline_state.queries_resource_id,
            ClickHouseStatboxTrafTestRun.Parameters.test_uri.name: "http://{host}:{port}".format(host=test_instance.host, port=test_instance.ports["clickhouse_http"]),
            ClickHouseStatboxTrafTestRun.Parameters.stable_uri.name: "http://{host}:{port}".format(host=ref_instance.host, port=ref_instance.ports["clickhouse_http"]),

            ClickHouseStatboxTrafTestRun.Parameters.report_startrek.name: self.Parameters.report_startrek,
            ClickHouseStatboxTrafTestRun.Parameters.issue_key.name: self.Parameters.issue_key,

            ClickHouseStatboxTrafTestRun.Parameters.fail_task_on_test_failure: True,
        }

        if self.Parameters.tolerance:
            params.update({
                ClickHouseStatboxTrafTestRun.Parameters.properties.name: {
                    "tolerance": "true",
                    "max.abs.diff": self.Parameters.max_abs_diff
                }
            })

        self.pipeline_state.b2b_tests_task_id = self.run_subtasks([(ClickHouseStatboxTrafTestRun, params)], self.Context.b2b_tests_task_id)[0]

        test_task = ClickHouseStatboxTrafTestRun[self.pipeline_state.b2b_tests_task_id]
        self.set_info('<a href="{link}/site/allure-maven-plugin/index.html">Протоколы тестов</a>'.format(link=sdk2.Resource[test_task.Parameters.report_resource.id].http_proxy), do_escape=False)

    def delete_stand(self):
        self._delete_caas_instance(self.pipeline_state.caas_id_test)
        self._delete_caas_instance(self.pipeline_state.caas_id_ref)
