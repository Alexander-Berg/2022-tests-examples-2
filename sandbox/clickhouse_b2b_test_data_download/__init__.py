# coding=utf-8
import logging
import random
import re
from copy import deepcopy
from datetime import datetime, timedelta
from itertools import chain, izip_longest
from urllib import quote_plus

import requests
from requests.packages.urllib3.util.retry import Retry

from sandbox import sdk2
from sandbox.common.errors import TaskError, TemporaryError
from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_data_download.default_data_sources import DATA_SOURCES
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_data_download.state import State
from sandbox.projects.metrika.admins.clickhouse.utils import build_clickhouse_docker_images
from sandbox.projects.metrika.utils import CommonParameters
from sandbox.projects.metrika.utils import parameters, settings
from sandbox.projects.metrika.utils.auth import MdbAuth
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.maas import MaasProvider
from sandbox.projects.metrika.utils.parameters import hide, DataCenterParameters
from sandbox.projects.metrika.utils.mixins.juggler_reporter import JugglerReporterMixin
from sandbox.projects.metrika.utils.parameters import PackageVersion
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask

INSERT_TEMPLATE = "INSERT INTO {database}.{table} FORMAT JSONEachRow"

META_DB = 'caas'
CREATE_DATABASE_TEMPLATE = 'CREATE DATABASE IF NOT EXISTS {database}'

META_TABLE = "metadata"
CREATE_META_TABLE = "CREATE TABLE IF NOT EXISTS {database}.{table} (StartDate Date, FinishDate Date) ENGINE=Log".format(database=META_DB, table=META_TABLE)

TASK_TABLE = 'loadings'
STATE_TABLE = 'state'
ALTERS_TABLE = 'alters'

CREATE_TASK_TABLE = "CREATE TABLE IF NOT EXISTS `{database}`.`{table}` " \
                    "(EventTime DateTime, SandboxTaskId UInt32, Seq UInt32, CreateQuery String, RemoteExpr String, DateColumn String, TargetDatabase String, TargetTable String" \
                    ", RemoteDatabase String, RemoteTable String) ENGINE=Log"
CREATE_STATE_TABLE = "CREATE TABLE IF NOT EXISTS `{database}`.`{table}` " \
                     "(EventTime DateTime, SandboxTaskId UInt32, Seq UInt32, Duration UInt32) ENGINE=Log"
CREATE_ALTERS_TABLE = "CREATE TABLE IF NOT EXISTS `{database}`.`{table}` (EventTime DateTime, SandboxTaskId UInt32, AlterText String) ENGINE=Log"
SELECT_TASK = "SELECT CreateQuery, RemoteExpr, DateColumn, TargetDatabase, TargetTable, RemoteDatabase, RemoteTable, Seq FROM `{database}`.`{task_table}` " \
              "WHERE Seq NOT IN (SELECT Seq FROM `{database}`.`{state_table}`) ORDER BY Seq LIMIT 1"

INSERT_SELECT_TEMPLATE = "INSERT INTO `{database}`.`{table}` SELECT * FROM {remote_type}('{remotes}', `{remote_database}`.`{remote_table}`, '{user}', '{password}') " \
                         "{sample_fragment} {where_fragment}"

DROP_TABLE_TEMPLATE = 'DROP TABLE IF EXISTS `{database}`.`{table}`'

# TODO - перенести в DATA_SOURCES
UNSAMPLED_TABLES = set([
    ('offline_conv_calls_log_storage', 'offline_calls_log'),
    ('offline_conv_calls_log_storage', 'offline_calls_log_v2'),
    ('offline_conv_calls_log_storage', 'offline_calls_log_v3'),
    ('feriat', 'alexkuk_hosts'),
    ('expenses', 'expenses'),
    ('cdp', 'clients'),
    ('cdp', 'orders'),
    ('merge', '.inner.pub_rows_uniques'),
])

CUSTOM_SAMPLES = {
    ('mobile', 'client_events'): 1e-5,
}

MAX_ITERATIONS = 20
BATCH_INSERT_SELECT_SIZE = 50

DTF = '%Y-%m-%d'
DTF_TS = '%Y-%m-%d %H:%M:%S'

MERGE_PARSER_REGEX = re.compile(r"^.*Merge\('?(?P<database>.+?)'?, '(?P<regex>.*?)'.*$")
REPLICATED_ENGINE_PARSER_REGEX = re.compile(r"^(?P<head>^.*)Replicated(?P<engine>.+?\()'.+?', '.+?'(?:, )?(?P<params>.*)$")
VIEW_PARSER_REGEX = re.compile(r"^.*FROM (?P<dbtable>.+?)( .*)?$")
DISTRIBUTED_PARSER_REGEX = re.compile(r"^Distributed\('?(?P<cluster>.+?)'?, '?(?P<database>.*?)'?, '?(?P<table>.*?)'?(, (?P<sharding_key>.*?))?\)$")
BUFFER_PARSER_REGEX = re.compile(r"^Buffer\('?(?P<database>.*?)'?, '?(?P<table>.*?)'?,.*?\)$")

CREATE_TABLE_RE = re.compile(r'CREATE TABLE (?P<database>.*?)\.(?P<table>.*?)\s')
DISTRIBUTED_TABLE_RE = re.compile(r"Distributed\('?(?P<cluster>.+?)'?, '?(?P<database>.*?)'?, '?(?P<table>.*?)'?(?P<rest>[,)])")
BUFFER_TABLE_RE = re.compile(r"Buffer\('?(?P<database>.*?)'?, '?(?P<table>.*?)'?,")

logger_loadings = logging.getLogger('create_loadings_task')
logger_caas = logging.getLogger('caas')


@with_parents
class ClickHouseB2BTestDataDownload(PipelineBaseTask, JugglerReporterMixin):
    name = 'CLICKHOUSE_B2B_TEST_DATA_DOWNLOAD'

    @property
    def juggler_host(self):
        return self.pipeline_state.caas_host

    @property
    def juggler_service(self):
        return "caas_{}".format(self.pipeline_state.instance_name)

    def _juggler_predicate(self, status):
        return self.Parameters.is_report_to_juggler

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Parameters(CommonParameters):
        kill_timeout = 48 * 60 * 60  # a lot of hours

        container = parameters.LastPeasantContainerResource('Environment container resource', required=True)

        with sdk2.parameters.Group('Источник данных') as data_source_group:
            sample_rate = sdk2.parameters.Float('Коэффициент семплирования', required=True, default=0.0001)

            custom_data_sources = sdk2.parameters.Bool("Переопределить источники данных", required=True, default=False,
                                                       description='Полезно совместно с явным указанием инстанса для доливки каких либо данных и отладки.')
            with custom_data_sources.value[True]:
                data_sources = sdk2.parameters.JSON('Источники данных', required=True, default=DATA_SOURCES)

            data_window_size = sdk2.parameters.Integer('Период данных в днях', required=True, default=32,
                                                       description='Количество дней данных, которые нужно выгрузить')

            with sdk2.parameters.RadioGroup("Начальная дата") as start_date:
                start_date.values.relative = start_date.Value("Относительная", default=True)
                start_date.values.absolute = start_date.Value("Абсолютная")

            with start_date.value["relative"]:
                start_date_relative = sdk2.parameters.Integer('Сколько дней отступить в прошлое', required=True, default=1,
                                                              description='На сколько дней в прошлое отстоит день, после последнего дня выгрузки. '
                                                                          'Нужно для того, что при запуске из шедулера параметры остаются фиксированными')

            with start_date.value["absolute"]:
                start_date_absolute = sdk2.parameters.String('Начальный день в прошлом, в формате YYYY-MM-DD', required=True, default=(datetime.now() - timedelta(1)).strftime(DTF),
                                                             description='Дата в прошлом дня, после последнего дня выгрузки')

        with sdk2.parameters.Group('Приёмник данных') as data_destination_group:
            data_center_params = DataCenterParameters()
            with sdk2.parameters.RadioGroup("Инстанс в СaaS") as caas_instance:
                caas_instance.values.exists = caas_instance.Value("Уже создан")
                caas_instance.values.create = caas_instance.Value("Создать новый", default=True)

            with caas_instance.value["exists"]:
                caas_instance_id = sdk2.parameters.Integer("Идентификатор инстанса в CaaS", required=True,
                                                           description="Идентификатор инстанса в CaaS, который уже создан и не является родительским. Полезно для доливки данных в ручном режиме.")

            with caas_instance.value["create"]:
                caas_instance_name = sdk2.parameters.String("Имя инстанса в CaaS", required=True, default="days-32_sample-4")

                # doesn'\t refresh in scheduler, refresh manually in code
                with sdk2.parameters.RadioGroup("Версия ClickHouse") as clickhouse_version:
                    clickhouse_version.values.stable = clickhouse_version.Value("Стабильная с mtgiga")
                    clickhouse_version.values.custom = clickhouse_version.Value("Явно заданная", default=True)

                with clickhouse_version.value["custom"]:
                    custom_clickhouse_version = PackageVersion("Версия ClickHouse", required=True, package="clickhouse-client", host_group="mtgiga",
                                                               description="Версия ClickHouse для родительского инстанса. По умолчанию берётся с mtgiga")

                with sdk2.parameters.RadioGroup("Версия словарей YT") as yt_dictionaries_version:
                    yt_dictionaries_version.values.stable = yt_dictionaries_version.Value("Стабильная с mtgiga")
                    yt_dictionaries_version.values.custom = yt_dictionaries_version.Value("Явно заданная", default=True)

                with yt_dictionaries_version.value["custom"]:
                    custom_yt_dictionaries_version = PackageVersion("Версия словарей YT", required=True, package="yandex-clickhouse-dictionary-yt", host_group="mtgiga",
                                                                    description="Версия yt-словарей для родительского инстанса. "
                                                                                "По умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga")

                with sdk2.parameters.RadioGroup("Версия конфига КХ") as ch_config_version:
                    ch_config_version.values.stable = ch_config_version.Value("Стабильная с mtgiga")
                    ch_config_version.values.custom = ch_config_version.Value("Явно заданная", default=True)

                with ch_config_version.value["custom"]:
                    custom_ch_config_version = PackageVersion("Версия конфига КХ", required=True, package="clickhouse-server-metrika", host_group="mtgiga",
                                                              description="Версия конфига КХ для родительского инстанса. "
                                                                          "По умолчанию берётся версия пакета clickhouse-server-metrika с mtgiga")

                caas_ttl = sdk2.parameters.Integer('CaaS ttl, days', required=True, default=365)
                force_update = sdk2.parameters.Bool('Force update', required=True, default=False,
                                                    description="Если True, то перед загрузкой новых данных будет удалён более свежий инстанс, если у него нет дочерних. "
                                                                "Это случай, когда новые данные ещё не использовались в тестах.")

            apply_alters = sdk2.parameters.Bool('Применить альтеры', required=True, default=False,
                                                description="Если True, то после загрузки данных будут применены указанные альтеры.")

            with apply_alters.value[True]:
                alters = sdk2.parameters.List("Альтеры", required=True, description='Будут выполнены после заливки данных.')

        with sdk2.parameters.Group('Секреты') as secrets_group:
            ch_user = sdk2.parameters.String('ClickHouse user', required=True, default='robot-metrika-ch-test')
            ch_password = sdk2.parameters.Vault('ClickHouse password', required=True, default='METRIKA:robot-metrika-ch-test')
            bishop_token = sdk2.parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                            description="Секрет с токеном для доступа к bishop")

        is_report_to_juggler = sdk2.parameters.Bool("Отправлять ли событие в Juggler", required=True, default_value=False,
                                                    description="Должно быть выставлено, если запуск производится регулярный, например, из шедулера.")

        _binary = hide(binary_task.binary_release_parameters_list(stable=True))

    class Context(PipelineBaseTask.Context):
        pipeline_state = State().state

    def create_stages(self):
        return [
            (self.create_caas_instance, "Родительский инстанс"),
            (self.create_download_plan, "План загрузки данных"),
            (self.download_data, "Загрузка данных"),
        ]

    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.getLogger("scenario")
        return self._logger

    @property
    def _session(self):
        try:
            return self.__session
        except AttributeError:
            self.__session = requests.session()
            self.__session.mount("http", requests.adapters.HTTPAdapter(max_retries=Retry(total=20, backoff_factor=1)))
            self.__session.verify = False
        return self.__session

    @property
    def _caas_session(self):
        try:
            return self.__caas_session
        except AttributeError:
            self.__caas_session = requests.session()
            self.__caas_session.auth = MdbAuth(self.Parameters.ch_user, self._ch_password)
            self.__caas_session.mount("http", requests.adapters.HTTPAdapter(max_retries=Retry(total=20, method_whitelist=frozenset(['POST']), status_forcelist=(500, 502, 504), backoff_factor=1)))
            self.__caas_session.verify = False
        return self.__caas_session

    @property
    def _ch_session(self):
        try:
            return self.__ch_session
        except AttributeError:
            self.__ch_session = requests.session()
            self.__ch_session.auth = MdbAuth(self.Parameters.ch_user, self._ch_password)
            adapter = requests.adapters.HTTPAdapter(max_retries=Retry(total=2, method_whitelist=frozenset(['GET']), status_forcelist=(500, 502, 504), backoff_factor=1))
            self.__ch_session.mount("http", adapter)
            self.__ch_session.mount("https", adapter)
            self.__ch_session.verify = False
        return self.__ch_session

    @property
    def _ch_password(self):
        try:
            return self.__ch_password
        except AttributeError:
            self.__ch_password = self.Parameters.ch_password.data()
        return self.__ch_password

    def _get_cluster_hosts(self, cluster):
        from metrika.pylib.mtapi.cluster import ClusterAPI
        hosts = self.pipeline_state.cluster_hosts.get(cluster)
        if not hosts:
            cluster_api = ClusterAPI()
            cluster_api._verify = False
            hosts = cluster_api.list.fqdn(group=cluster, environment='production', dc_name="!man")
            self.pipeline_state.cluster_hosts[cluster] = hosts
            return hosts
        else:
            return hosts

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value(), self.Parameters.data_center)

    def create_caas_instance(self):
        if self.Parameters.caas_instance == "exists":
            # 1. проверить, если не парент
            #   1.1 Если имя подпадает под r'^(.*):inprogress:\d+$' - то продолжаем загрузку - выделить базовое имя, переименовать с тем что бы число в конце было номером данной задачи.
            #   1.2 Если не подпадает - то всё имя - базовое, переименовать, продолжаем загрузку
            # 2. Если парент
            #   2.1 Имя сохранить - будет базовое имя.
            #   2.2 Переименовать добавлением суффикса ":obsolete"
            #   2.3 Создать дочерний, назвать с суффиксом и заливать данные в него
            logger_caas.info("Не создаём инстанс, будет использоваться {id}".format(id=self.Parameters.caas_instance_id))

            maas_instance = self._create_maas_client(self.Parameters.caas_instance_id)
            maas_instance.get_status()
            instance_name = maas_instance.properties.get("name", "") if maas_instance.properties is not None else ""
            logger_caas.info("Имя инстанса: '{name}'".format(name=instance_name))
            if maas_instance.status == 'active':
                name_regex = re.compile(r"^(?P<name>.+?):inprogress:\d+$")
                match = name_regex.search(instance_name)
                if match:
                    base_name = match.group("name")
                    maas_instance.update(name="{name}:inprogress:{id}".format(name=base_name, id=self.id))
                    self.pipeline_state.instance_name = base_name
                else:
                    maas_instance.update(name="{name}:inprogress:{id}".format(name=instance_name, id=self.id))
                    self.pipeline_state.instance_name = instance_name
                self._set_instance_id(maas_instance.id)
                self.set_info("Переиспользован инстанс {id}".format(id=maas_instance.id))
            elif maas_instance.status == 'parent':
                logger_caas.info("Инстанс - родительский. Будет создан новый инстанс, а имеющийся - переименован.")
                maas_instance.update(name="{name}:obsolete".format(name=instance_name))
                instance = self._create_maas_client()
                params = {
                    "parent_id": maas_instance.id,
                    "name": "{name}:inprogress:{id}".format(name=instance_name, id=self.id),
                    "ttl": int(timedelta(days=self.Parameters.caas_ttl).total_seconds()),
                    "version_tag": str(maas_instance.properties["version_tag"]),
                    "memory_limit": 60
                }
                instance.create(**params)
                self.pipeline_state.instance_name = instance_name
                self._set_instance_id(instance.id)
                self.set_info("Создан инстанс {id}".format(id=instance.id))
            else:
                raise TaskError("CaaS instance {id} in state {state}. Probably restart instance will make it active.".format(id=self.Parameters.caas_instance_id, state=maas_instance.status))
        else:
            with sdk2.helpers.ProgressMeter("Создаём инстанс для заливки данных"):
                logger_caas.info("Создаём инстанс для заливки данных")
                # все родительские инстансы отсортированы по убыванию даты создания, самый свежий - в начале
                instances = self._create_maas_client().list()
                parents = sorted(filter(lambda item: item.get("name") == str(self.Parameters.caas_instance_name), instances), key=lambda item: item["created_at"], reverse=True)
                logger_caas.debug("Parents: {}".format(parents))

                if len(parents) > 2:
                    raise TaskError(
                        "Обнаружено {count} родительских инстансов с имененм {name}. Удалите лишнее и перезапустите.".format(count=len(parents), name=self.Parameters.caas_instance_name))
                elif len(parents) == 2:
                    # нужно удалить тот, что страрее, если у него нет дочерних, либо тот, что новее, если у него нет дочерних и поставлена галка.
                    # если дочерние есть у обоих - это ошибка - raise TaskError, можно будет перезапустить
                    children_0 = filter(lambda item: item.get("parent_id") == parents[0]["id"], instances)
                    children_1 = filter(lambda item: item.get("parent_id") == parents[1]["id"], instances)
                    logger_caas.debug("Childern 0: {}".format(children_0))
                    logger_caas.debug("Childern 1: {}".format(children_1))
                    if len(children_1) == 0:
                        # удалим тот что в parents[1]
                        self._create_maas_client(parents[1]["id"]).delete()
                    elif len(children_0) == 0:
                        if self.Parameters.force_update:
                            # удалим тот, что в parents[0]
                            self._create_maas_client(parents[0]["id"]).delete()
                        else:
                            raise TaskError("Дочерние инстансы отсутствуют у более свежего родительского инстанса {parent_id}, но принудительного обновления не указано. "
                                            "Его можно удалить вручную и перезапустить задачу.".format(parent_id=parents[0]["id"]))

                # тут можно создавать
                instance = self._create_instance(self.Parameters.caas_instance_name)
                self.pipeline_state.instance_name = self.Parameters.caas_instance_name
                self._set_instance_id(instance.id)
                self.set_info("Создан инстанс {id}".format(id=instance.id))

        # на выходе отсюда созданный инстанс с имененм <caas_instance_name>:inprogress:<task_id>

    def _create_instance(self, base_name):
        # получить версию, если явно не задана.
        from metrika.pylib.mtapi.packages import PackagesAPI
        packages_api = PackagesAPI()
        packages_api._verify = False

        version = packages_api.pkg_version_per_group("mtgiga", "clickhouse-client") if \
            self.Parameters.clickhouse_version == "stable" else \
            self.Parameters.custom_clickhouse_version
        logger_caas.info("ClickHouse version: {}".format(version))

        version_yt_dict = packages_api.pkg_version_per_group("mtgiga", "yandex-clickhouse-dictionary-yt") if \
            self.Parameters.yt_dictionaries_version == "stable" else \
            self.Parameters.custom_yt_dictionaries_version

        ch_config_version = packages_api.pkg_version_per_group("mtgiga", "clickhouse-server-metrika") if \
            self.Parameters.ch_config_version == "stable" else \
            self.Parameters.custom_ch_config_version
        logger_caas.info("YT Dictionaries version: {}".format(version_yt_dict))

        # переиспользуем логику из пайплайна тестирования.

        build_clickhouse_docker_images(self, (version, ch_config_version, version_yt_dict))

        instance = self._create_maas_client()
        params = {
            "name": "{name}:inprogress:{id}".format(name=base_name, id=self.id),
            "ttl": int(timedelta(days=self.Parameters.caas_ttl).total_seconds()),
            "version_tag": self.Context.caas_yt_versions[0],
            "memory_limit": 60
        }
        instance.create(**params)

        return instance

    def create_download_plan(self):
        # Здесь записываются данные в таблицу метаданных, если ещё не
        # анализирируется задание на загрузку и записывается в таблицу состояния, записываются альтеры
        with sdk2.helpers.ProgressMeter("Создаём задания на загрузку данных"):
            self._store_metadata()
            self._create_state()
            self._create_loadings()

        self.set_info("Задания на загрузку данных созданы")

    def download_data(self):
        # загрузка данных осуществляется по заданию - то, что в параметре self.Parameters.data_sources или по умолчанию
        # из задания формируется список действий для загрузки, действие - создание таблицы и загрузка в неё данных
        # данные загружаются последовательно - таблица за таблицей
        # успешно загруженное записывается в метатаблицу для того, что бы можно было продолжить загрузку после аварийного прерывания либо этой же задачей, либо другой, но с указанием
        # уже созданного инстанса в CaaS.

        # здесь только выполняется загрузка по плану из таблицы.
        # все исключения являются TemporaryError, что бы максимально автоматизированно выполнить загрузку данных

        self._process_loadings()

        if self.Parameters.apply_alters:
            self._apply_alters()

        # Переименовываем
        self._create_maas_client(self.pipeline_state.instance_id).update(name=self.pipeline_state.instance_name)
        # на выходе отсюда - созданный инстанс с имененм <caas_instance_name>

        self.set_info("Все задания на загрузку данных выполнены")

    def _create_maas_client(self, instance_id=None):
        instance = self.maas_provider.get_caas_client()
        instance.id = instance_id
        return instance

    def _set_instance_id(self, caas_instance_id):
        self.pipeline_state.instance_id = caas_instance_id
        instance = self._create_maas_client(caas_instance_id)
        instance.get_status()
        self.pipeline_state.caas_host = instance.host
        self.pipeline_state.instance_ports = instance.ports
        self.pipeline_state.instance_uri = "http://{host}:{port}".format(host=self.pipeline_state.caas_host, port=instance.ports["clickhouse_http"])
        # На случай таймаута Sandbox-задачи принудительно сохраним контекст
        self.Context.save()

    def _execute_non_query(self, query, data=None, json=None, params=None):
        """
        :param query: запрос для исполнения
        :param data: данные в виде строки, в том числе с переводами строк
        :param json: данные в виде словаря, они будут сериализованы в json
        :return:
        """
        logging.debug("Execute non query: {query}\ndata={data}\njson={json}".format(query=query, data=data, json=json))
        resp = self._caas_session.post(self.pipeline_state.instance_uri + "/?query=" + quote_plus(query), data=data, json=json, params=params)
        logging.debug(resp.text)
        resp.raise_for_status()

    def _execute_query(self, query):
        logging.debug("Execute query: {}".format(query))
        resp = self._caas_session.post(self.pipeline_state.instance_uri + "/?query=" + quote_plus(query + " FORMAT JSON"))
        logging.debug(resp.text)
        resp.raise_for_status()
        return resp.json().get("data")

    def _execute_query_on_hosts(self, hosts, query, predicate=None):
        logging.debug("Execute query on hosts. {}".format(query))
        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            host = random.choice(hosts)
            logging.debug("Selected host: {}".format(host))
            try:
                protocol, port = ('https', 8443) if host.endswith('db.yandex.net') else ('http', 8123)
                resp = self._ch_session.get(
                    "{protocol}://{host}:{port}/?query=".format(protocol=protocol, host=host, port=port) +
                    quote_plus("{query} FORMAT JSON".format(query=query))
                )
                logging.debug(resp.text)
                resp.raise_for_status()
                result = resp.json().get("data")
                if predicate:
                    if predicate(result):
                        return result
                    else:
                        logging.warning("Предикат вернул False, продолжаем перебирать хосты.")
                else:
                    return result
            except:
                logging.warning("Ошибка при выполнении запроса.", exc_info=True)

        # пришли сюда, значит всё плохо
        raise TaskError("Предпринято попыток: {iterations}. Успешно выполнить запрос не удалось.".format(iterations=MAX_ITERATIONS))

    def _store_metadata(self):
        logger_loadings.info("Store metadata")
        self._execute_non_query(CREATE_DATABASE_TEMPLATE.format(database=META_DB))
        self._execute_non_query(CREATE_META_TABLE)
        dates = self._execute_query("SELECT * FROM {db}.{table} LIMIT 1".format(db=META_DB, table=META_TABLE))
        if dates:
            logger_loadings.info("Обнаружены даты предыдущей попытки загрузки - используем их. {}".format(dates[0]))
            self.pipeline_state.dates = dates[0]
        else:
            now = datetime.now()
            start_date = now - timedelta(days=self.Parameters.start_date_relative) if self.Parameters.start_date == "relative" else datetime.strptime(self.Parameters.start_date_absolute, DTF)
            finish_date = start_date - timedelta(days=self.Parameters.data_window_size)
            self.pipeline_state.dates = {'StartDate': finish_date.strftime(DTF), 'FinishDate': start_date.strftime(DTF)}
            logger_loadings.info("Даты загрузки: {}".format(self.pipeline_state.dates))
            self._execute_non_query(INSERT_TEMPLATE.format(database=META_DB, table=META_TABLE), json=self.pipeline_state.dates)
        self.pipeline_state.datetimes = {name: str(datetime.strptime(date, '%Y-%m-%d')) for name, date in self.pipeline_state.dates.items()}

    def _create_state(self):
        logger_loadings.info("Create state")
        self._execute_non_query(CREATE_DATABASE_TEMPLATE.format(database=META_DB))
        self._execute_non_query(CREATE_TASK_TABLE.format(database=META_DB, table=TASK_TABLE))
        self._execute_non_query(CREATE_STATE_TABLE.format(database=META_DB, table=STATE_TABLE))

    def _create_loadings(self):
        # анализирует задание и формирует список загрузок, вычёркивая те, о которых есть запись в таблице, что они уже были выполнены
        # выполняет DDL

        processed_tables = set()

        datasources = (self.Parameters.data_sources if self.Parameters.custom_data_sources else DATA_SOURCES)["sources"]

        for source in datasources:
            logger_loadings.info("================> Начинаем обработку источника данных {}".format(source))

            if source:
                hosts = self._get_cluster_hosts(source["cluster-mtapi"])
                self._create_loading_concrete(hosts, source, None, processed_tables, cluster=source["cluster-mtapi"])
            else:
                raise TaskError(source)

            logger_loadings.info("================> Завершена обработка источника данных {}".format(source))

    def _create_loading_concrete(self, hosts, source, remotes, processed_tables, cluster=None):
        logger_loadings.info("**************** Create loadings for '{database}'.'{table}' {remotes}".format(database=source['database'], table=source['table'], remotes=remotes))
        key = (source["database"], source["table"], remotes)
        if key in processed_tables:
            logger_loadings.info("Already processed.")
            return

        processed_tables.add(key)

        # Запрос выполняем на случайном хосте из hosts с двумя ретраями, если фейл - то берём другой хост из списка.
        # Общее количество попыток - 20
        # 1. Получим из system.tables следующие данные:
        #   engine
        #   engine_full
        #   create_table_query
        # 2. Далее возможны следующие варианты:
        #   2.1 'View' in engine:
        #       2.1.1 из определения вынуть таблицы
        #       2.1.2 рекурсивно обработать каждую таблицу
        #       2.1.3 добавить задание на создание этого view
        #  2.2 engine == 'Merge':
        #       2.2.1 извлечь регэксп из engine_full
        #       2.2.2 по регэкспу получить список таблиц и рекурсивно обработать каждую (select from system.tables)
        #       2.2.3 добавить задание на создание этой таблицы
        #  2.3 engine == 'Distributed':
        #       2.3.1 извлечь из engine_full имя кластера, имя бд и имя таблицы
        #       2.3.2 получить список хостов (select from system.clusters) по имени кластера
        #       2.3.3 рекурсивно обработать таблицу, но указав другой список хостов
        #       2.3.4 добавить задание на создание этой таблицы
        #  2.4 engine == 'MySQL'
        #       2.4.1 пропустить
        #  2.5 engine_full.startswith('Replicated') or engine.startswith('Replicated'):
        #       2.5.1 преобразовать create_table_query так, что бы превратить Replicated-движок в обычный
        #       2.5.2 добавить задание на создание этой таблицы
        #       2.5.3 добавить задание на загрузку данных в эту таблицу
        #  2.6 прочее
        #       2.6.1 добавить задание на создание этой таблицы
        #       2.6.2 добавить задание на загрузку данных в эту таблицу

        # задание на создание таблицы - выражение CREATE TABLE ....
        # задание на загрузку данных - имя бд, имя таблицы и список хостов, откуда брать данные

        # задание добавляется только если его там ещё нет

        # по ходу работы поддерживается set из строк <имя бд>.<имя таблицы>, которые уже обработаны, что бы не обрабатывать повторно
        table_meta_data = self._execute_query_on_hosts(hosts, "SELECT engine, engine_full, create_table_query FROM system.tables WHERE database = '{db}' AND name = '{table}'"
                                                       .format(db=source["database"], table=source["table"]), lambda rows: len(rows) == 1)[0]

        engine = table_meta_data["engine"]
        engine_full = table_meta_data["engine_full"]
        create = table_meta_data["create_table_query"]
        for part, replacement in source.get("format-create", {}).items():
            if part not in {'database', 'cluster', 'shard', 'replica'}:
                create = create.replace(part, replacement)
            else:
                create = create.replace('{' + part + '}', replacement)

        source['remote_database'] = source['database']
        source['remote_table'] = source['table']
        renames = source.get('renames', {}).get(cluster)
        if renames:
            logging.debug('RENAMES %s', renames)
            source['remote_database'] = source['database']
            source['database'] = renames.get('databases', {}).get(source['database'], source['database'])
            source['table'] = renames.get('tables', {}).get(source['table'], source['table'])
            create = CREATE_TABLE_RE.sub(
                lambda m: 'CREATE TABLE {}.{} '.format(source['database'], source['table']),
                create
            )
            logging.debug('NEW CREATE %s', create)

        if 'View' in engine:
            if not source.get('metadata-only'):
                match = VIEW_PARSER_REGEX.search(create)
                if match:
                    (database, table) = [s.strip("'") for s in match.group('dbtable').split('.')]
                    sub_source = deepcopy(source)
                    sub_source["database"] = database
                    sub_source["table"] = table
                    self._create_loading_concrete(hosts, sub_source, remotes, processed_tables)
                else:
                    logging.fatal("Ошибка парсинга View: {}".format(create))
                    raise TaskError(create)
            self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
        elif 'Merge' == engine:
            if not source.get('metadata-only'):
                # override merge engine
                match = MERGE_PARSER_REGEX.search(engine_full)
                if match:
                    tables_meta_data = self._execute_query_on_hosts(hosts, "SELECT database, name FROM system.tables WHERE database = '{database}' AND match(name, '{pattern}')".format(
                        database=match.group("database"), pattern=source["override-merge"] if "override-merge" in source else match.group("regex")))
                    for table_meta_data in tables_meta_data:
                        sub_source = deepcopy(source)
                        sub_source["database"] = table_meta_data["database"]
                        sub_source["table"] = table_meta_data["name"]
                        self._create_loading_concrete(hosts, sub_source, remotes, processed_tables)
                else:
                    logging.fatal("Ошибка парсинга Merge: {}".format(create))
                    raise TaskError(create)
            self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
        elif 'Distributed' == engine:
            if not source.get('metadata-only'):
                match = DISTRIBUTED_PARSER_REGEX.search(engine_full)
                if match:
                    engine_cluster = source["override-cluster"] if "override-cluster" in source else match.group("cluster")
                    renames = source.get('renames', {}).get(engine_cluster)
                    if renames:
                        logging.debug('DISTR RENAMES %s', renames)
                        create = DISTRIBUTED_TABLE_RE.sub(
                            lambda m: "Distributed('{}', '{}', '{}'{}".format(
                                m.group('cluster'),
                                renames.get('databases', {}).get(m.group('database'), m.group('database')),
                                renames.get('tables', {}).get(m.group('table'), m.group('table')),
                                m.group('rest'),
                            ),
                            create
                        )
                        logging.debug('NEW CREATE %s', create)

                    # сконструировать remotes и прокинуть, используется в Replicated
                    cluster_definition = self._execute_query_on_hosts(
                        hosts,
                        "SELECT groupArray(concat(host_name, ':', toString(port))) as replicas, groupArray(host_name) as sub_hosts FROM system.clusters "
                        "WHERE cluster='{cluster}' GROUP BY shard_num ORDER BY shard_num".format(cluster=engine_cluster)
                    )
                    # [[i for i in row if i is not None] for row in list(izip_longest(*[iter(r)]*9))]
                    # сгруппировать их по нескольку шардов, возможно будет быстрее
                    shard_groups = [[i for i in row if i is not None] for row in list(izip_longest(*[iter(cluster_definition)] * BATCH_INSERT_SELECT_SIZE))]
                    for shard_group in shard_groups:
                        cluster_remotes = ",".join(["{" + "|".join([replica for replica in shard["replicas"]]) + "}" for shard in shard_group])
                        sub_hosts = list(chain.from_iterable([shard["sub_hosts"] for shard in shard_group]))
                        sub_source = deepcopy(source)
                        sub_source["database"] = match.group("database")
                        sub_source["table"] = match.group("table")
                        override_cluster = source.get("override-subcluster", source.get("override-cluster"))
                        if override_cluster:
                            sub_source["override-cluster"] = override_cluster
                        self._create_loading_concrete(sub_hosts, sub_source, cluster_remotes, processed_tables, cluster=engine_cluster)
                else:
                    logging.fatal("Ошибка парсинга Distributed: {}".format(create))
                    raise TaskError(create)
            self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
        elif 'MySQL' == engine:
            self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
        elif engine.startswith('Replicated'):
            if not remotes and not source.get('metadata-only'):
                logging.fatal("Для движка с данными не задан remotes - что-то пошло не так")
                raise TaskError("No remotes\n{}".format(create))
            match = REPLICATED_ENGINE_PARSER_REGEX.search(create)
            if match:
                create_rewrite = "{head}{engine}{params}".format(head=match.group("head"), engine=match.group("engine"), params=match.group("params"))
                self._add_task(source["database"], source["table"], create_rewrite, remote_database=source['remote_database'], remote_table=source['remote_table'])
                if not source.get('metadata-only'):
                    self._add_task(source["database"], source["table"], None, remotes, source["date-column"], remote_database=source['remote_database'], remote_table=source['remote_table'])
            else:
                logging.fatal("Ошибка парсинга Replicated: {}".format(create))
                raise TaskError(create)
        elif 'MergeTree' == engine:
            if not source.get('metadata-only'):
                if not remotes:
                    logging.fatal("Для движка с данными не задан remotes - что-то пошло не так")
                    raise TaskError("No remotes\n{}".format(create))
                self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
                self._add_task(source["database"], source["table"], None, remotes, source["date-column"], remote_database=source['remote_database'], remote_table=source['remote_table'])
            else:
                logging.fatal("Похоже, что нужно реализовать вычисление remotes на основе переданного сюда кластера.")
                raise TaskError(create)
        elif 'Log' == engine:
            if not source.get('metadata-only'):
                # Для этого случая предполагаем, что каждый из hosts содержит эту таблицу в одинаковом виде, сформируем remotes из них
                artificial_remotes = "{" + "|".join(["{host}:9000".format(host=replica) for replica in hosts]) + "}"
                self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
                self._add_task(source["database"], source["table"], None, artificial_remotes, source["date-column"], remote_database=source['remote_database'], remote_table=source['remote_table'])
            else:
                logging.fatal("Похоже, что нужно реализовать вычисление remotes на основе переданного сюда кластера.")
                raise TaskError(create)
        elif 'Buffer' == engine:
            if not source.get('metadata-only'):
                match = BUFFER_PARSER_REGEX.search(engine_full)
                if match:
                    renames = source.get('renames', {}).get(cluster)
                    if renames:
                        logging.debug('BUFFER RENAMES %s', renames)
                        create = BUFFER_TABLE_RE.sub(
                            lambda m: "Buffer('{}', '{}',".format(
                                renames.get('databases', {}).get(m.group('database'), m.group('database')),
                                renames.get('tables', {}).get(m.group('table'), m.group('table')),
                            ),
                            create
                        )
                        logging.debug('NEW CREATE %s', create)

                    sub_source = deepcopy(source)
                    sub_source["database"] = match.group("database")
                    sub_source["table"] = match.group("table")
                    override_cluster = source.get("override-subcluster", source.get("override-cluster"))
                    if override_cluster:
                        sub_source["override-cluster"] = override_cluster
                    self._create_loading_concrete(hosts, sub_source, remotes, processed_tables, cluster=cluster)
                else:
                    logging.fatal("Ошибка парсинга Distributed: {}".format(create))
                    raise TaskError(create)
            self._add_task(source["database"], source["table"], create, remote_database=source['remote_database'], remote_table=source['remote_table'])
        else:
            logging.warning("Что-то новенькое.")
            raise TaskError(create)

    def _add_task(self, target_database, target_table, query, remotes=None, datecolumn=None, remote_database=None, remote_table=None):
        """
        :param target_database: целевая БД
        :param target_table: целевая таблица
        :param query: create table или иной DDL - обязательно должен быть
        :param remotes: первый агрумент для функции remote (..), откуда брать данные, если не задано, то данные не заливаются, напрмер, это View или Merge
        :return:
        """
        rows = self._execute_query(
            "SELECT COUNT() as count FROM {database}.{table} WHERE TargetDatabase='{target_database}' AND TargetTable='{target_table}' AND RemoteExpr='{remote_expr}'".format(
                database=META_DB, table=TASK_TABLE,
                target_database=target_database,
                target_table=target_table,
                remote_expr=remotes if remotes else ""))
        if int(rows[0]["count"]) > 0:
            logging.warning("Пропускаем задание для {target_database}.{target_table} {remote_expr}".format(target_database=target_database, target_table=target_table, remote_expr=remotes))
        else:
            self._execute_non_query(INSERT_TEMPLATE.format(database=META_DB, table=TASK_TABLE),
                                    json={'EventTime': datetime.now().strftime(DTF_TS),
                                          'SandboxTaskId': self.id,
                                          'Seq': self._execute_query("SELECT plus(max(Seq),1) AS next FROM {database}.{table}".format(database=META_DB, table=TASK_TABLE))[0].get("next"),
                                          'CreateQuery': query if query else "",
                                          'TargetDatabase': target_database,
                                          'TargetTable': target_table,
                                          'RemoteDatabase': remote_database or target_database,
                                          'RemoteTable': remote_table or target_table,
                                          'RemoteExpr': remotes if remotes else "",
                                          'DateColumn': datecolumn if datecolumn else ""})

    def _get_next_loading(self):
        rows = self._execute_query(SELECT_TASK.format(database=META_DB, task_table=TASK_TABLE, state_table=STATE_TABLE))
        if rows:
            return rows[0]
        else:
            return None

    def _get_total_loadings(self):
        return int(self._execute_query("SELECT max(Seq) AS max FROM {database}.{table}".format(database=META_DB, table=TASK_TABLE))[0].get("max"))

    def _process_loadings(self):
        # обрабатываем задания последовательно, делая запись о том, что оно выполнено.
        # Вначале делаем CREATE DATABASE IF NOT EXISTS
        # DROP TABLE IF EXITS, CREATE query, если нужно insert select
        total = self._get_total_loadings()
        with sdk2.helpers.ProgressMeter("Выполняется задание", maxval=total) as progress:
            while True:
                loading = self._get_next_loading()
                if loading:
                    seq = int(loading["Seq"])
                    progress.value = seq
                    progress.add(0)
                    logging.info("================> Начинаем выполнение задания: {seq} из {total} - прогресс {ratio:.2%}".format(seq=seq, total=total, ratio=float(seq) / total))
                    logging.debug("{}".format(loading))
                    try:
                        # 0. выполнить DDL запросы
                        # 1. Нужно как-то угадать колонку с датами, на которую будет наложено условие. Возможно это лучше будет заменить на явную настройку.
                        # 2. Проверить, действительно ли эта колонка содержит разные даты, по которым можно наложить условие.
                        # 4. Выполнить insert select

                        start_ts = datetime.now()

                        if loading["CreateQuery"]:
                            self._execute_non_query(CREATE_DATABASE_TEMPLATE.format(database=loading["TargetDatabase"]))
                            self._execute_non_query(DROP_TABLE_TEMPLATE.format(database=loading["TargetDatabase"], table=loading["TargetTable"]))
                            self._execute_non_query(query="", data=loading["CreateQuery"])

                        if loading["RemoteExpr"]:
                            # производим загрузку данных
                            if loading["DateColumn"]:
                                dates_condition = "WHERE {column} >= '{StartDate}' AND {column} < '{FinishDate}'".format(
                                    column=loading["DateColumn"],
                                    **(self.pipeline_state.datetimes if 'time' in loading["DateColumn"].lower() else self.pipeline_state.dates)
                                )
                            else:
                                dates_condition = ""
                            sample = (
                                "SAMPLE " + str(CUSTOM_SAMPLES.get((loading["TargetDatabase"], loading["TargetTable"]), self.Parameters.sample_rate))
                                if (loading["TargetDatabase"], loading["TargetTable"]) not in UNSAMPLED_TABLES
                                else ""
                            )

                            self._execute_non_query(
                                query="",
                                data=INSERT_SELECT_TEMPLATE.format(
                                    database=loading["TargetDatabase"], table=loading["TargetTable"], remotes=loading["RemoteExpr"],
                                    remote_database=loading["RemoteDatabase"], remote_table=loading["RemoteTable"],
                                    user=self.Parameters.ch_user, password=self._ch_password,
                                    sample_fragment=sample, where_fragment=dates_condition,
                                    remote_type='remoteSecure' if 'db.yandex.net' in loading["RemoteExpr"] else 'remote'
                                ),
                                params={
                                    'max_memory_usage': 10000000000 if 'db.yandex.net' in loading["RemoteExpr"] else 30000000000
                                }
                            )

                        finish_ts = datetime.now()

                        duration = (finish_ts - start_ts)

                        self._execute_non_query(INSERT_TEMPLATE.format(database=META_DB, table=STATE_TABLE),
                                                json={'EventTime': finish_ts.strftime(DTF_TS),
                                                      'SandboxTaskId': self.id,
                                                      'Seq': loading["Seq"],
                                                      'Duration': int(duration.total_seconds())})

                        logging.info("================> Завершаем выполнение. Длительность {}".format(duration))

                    except TaskError:
                        raise
                    except Exception as e:
                        logging.warning("Ошибка при выполнении задания. Выбрасываем, как Temporary", exc_info=True)
                        raise TemporaryError(e)
                else:
                    logging.info("Все задания выполнены.")
                    break

    def _apply_alters(self):
        # Последовательно применяем альтеры, делая запись о том, что они выполнены.
        self._execute_non_query(CREATE_ALTERS_TABLE.format(database=META_DB, table=ALTERS_TABLE))

        total = len(self.Parameters.alters)
        with sdk2.helpers.ProgressMeter("Применяются альтеры", maxval=total) as progress:
            for i in range(total):
                alter = self.Parameters.alters[i]
                seq = i + 1
                progress.value = seq
                progress.add(0)
                logging.info("================> Применяем альтер {seq} из {total} - прогресс {ratio:.2%}".format(seq=seq, total=total, ratio=float(seq) / total))
                logging.debug(alter)
                self._execute_non_query(alter)
                self._execute_non_query(INSERT_TEMPLATE.format(database=META_DB, table=ALTERS_TABLE),
                                        json={'EventTime': datetime.now().strftime(DTF_TS), 'SandboxTaskId': self.id, 'AlterText': alter})
                logging.info("================> Альтер успешно применен")
