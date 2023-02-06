# coding=utf-8
import io
import logging

from datetime import datetime, timedelta

from sandbox import sdk2
from sandbox.common import fs
from sandbox.common.types.resource import RestartPolicy
from sandbox.common.utils import singleton_property
from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.java.metrika_lambda_test_data_prepare.state import State, Table, Query, File
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask
from sandbox.projects.metrika.utils.pipeline.pipeline_errors import PipelineAbortError
from sandbox.projects.metrika.utils import CommonParameters
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.sdk2.resource import Attributes

DTF = '%Y-%m-%d %H:%M:%S'

DTF_TABLE_NAME_INTRADAY = '%Y-%m-%dT%H:%M:%S'
DTF_TABLE_NAME_DAYLY = '%Y-%m-%d'

NOT_EXIST_PLACEHOLDER = "SRC doesn't exist"

DEFAULT_SAMPLES = {
    'visit-v2-log': 1e-4,
    'bs-dsp-log': 1e-4,
    'adfox-event-log': 1e-4,
    'bs-newsevent-log': 1e-4,
    "pbx-log": 1,
    "calltracking-log": 1,
    "offline-conversion-log": 1e-2,
    "crypta-matching": 1e-3
}

DEFAULT_DENOMINATOR = 10000000

INSERT_SELECT_TEMPLATE = """
PRAGMA AnsiInForEmptyOrNullableItemsCollections;

INSERT INTO `{dst}` WITH TRUNCATE
SELECT * FROM `{src}`
WHERE {condition};
"""


class MetrikaLambdaTestData(sdk2.resource.AbstractResource):
    restart_policy = RestartPolicy.IGNORE
    executable = False
    any_arch = True
    auto_backup = True
    start_date = Attributes.String("Start Date")
    finish_date = Attributes.String("Finish Date")


@with_parents
class MetrikaLambdaTestDataPrepare(PipelineBaseTask):
    """
    Подготавливает тестовые данные для тестирования Лямбды
    """

    class Parameters(CommonParameters):
        kill_timeout = 8 * 60 * 60  # a lot of hours
        with sdk2.parameters.Group("Назначение") as destination:
            yt_cluster = sdk2.parameters.String("YT cluster name", default="hahn", required=True)
            destination_path = sdk2.parameters.String("Базовый каталог назначения", required=True, default="//home/metrika/lambda-test-data")
            download_only = sdk2.parameters.Bool("Выгрузить подготовленные данные", required=True, default=False)
            with download_only.value[True]:
                destination_subdir = sdk2.parameters.String("Подкаталог в каталоге назначения", required=True)
            with download_only.value[False]:
                keep_tables = sdk2.parameters.Bool("Сохранить каталог назначения", required=True, default=False,
                                                   description="Если задано, то каталог назначения не будет удалён после успешного завершения задачи.")
                sample_rates = sdk2.parameters.Dict("Доля данных", required=True, default=DEFAULT_SAMPLES,
                                                    description="Доля данных, которая будте отобрана там, где применимо. Ключ - название вида таблиц.")
                max_parallel_operations = sdk2.parameters.Integer("Кол-во одновременных операций YT", required=True, default=30)
                max_parallel_queries = sdk2.parameters.Integer("Кол-во одновременных запросов YQL", required=True, default=15)
                relative_dates = sdk2.parameters.Bool("Относительные даты", required=True, default=True)
                with relative_dates.value[True]:
                    start_date_hours_back = sdk2.parameters.Integer("Начальная дата/время, часов назад", required=True, default=24,
                                                                    description="Начальная метка времени, за которую отбираются данные, часов назад")
                    finish_date_hours_back = sdk2.parameters.Integer("Конечная дата/время, часов назад", required=True, default=18,
                                                                     description="Конечная метка времени, за которую отбираются данные, часов назад")
                with relative_dates.value[False]:
                    start_date = sdk2.parameters.String("Начальная дата/время", required=True,
                                                        description="Начальная метка времени, за которую отбираются данные в формате YYYY-MM-DD HH:MM:SS")
                    finish_date = sdk2.parameters.String("Конечная дата/время", required=True,
                                                         description="Конечная дата/время, за которую отбираются данные в формате YYYY-MM-DD HH:MM:SS")
        with sdk2.parameters.Group("Секреты") as secrets:
            yt_token = sdk2.parameters.Vault("YT-токен", required=True, default="METRIKA:robot-metrika-test-yt")
            yql_token = sdk2.parameters.Vault("YQL-токен", required=True, default="METRIKA:robot-metrika-test-yql")
        with sdk2.parameters.Output():
            test_data = sdk2.parameters.Resource("Ресурс с тестовыми данными")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Context(PipelineBaseTask.Context):
        pipeline_state = State().state

    def on_before_timeout(self, seconds):
        self.Context.save()

    def create_stages(self):
        if self.Parameters.download_only:
            return [
                (self.initialize, "Подготовка"),
                (self.finalize, "Выгрузка")
            ]
        else:
            return [
                (self.initialize, "Подготовка"),
                (self.copy_files, "Копирование файлов"),
                (self.start_counters_job, "Копирование counters"),
                (self.wait_jobs, "Ожидание завершения YT-операций и YQL-запросов"),
                (self.start_visitlog_jobs, "Копирование Visit Log"),
                (self.wait_jobs, "Ожидание завершения YT-операций и YQL-запросов"),
                (self.start_other_jobs, "Копирование прочих логов"),
                (self.wait_jobs, "Ожидание завершения YT-операций и YQL-запросов"),
                (self.start_dictionaries_jobs, "Копирование словарей"),
                (self.wait_jobs, "Ожидание завершения YT-операций и YQL-запросов"),
                (self.finalize, "Выгрузка")
            ]

    def destination(self, *path):
        return self.path("export", *path)

    @singleton_property
    def yt_client(self):
        from yt.wrapper import YtClient
        return YtClient(proxy=self.Parameters.yt_cluster, token=self.Parameters.yt_token.data())

    @singleton_property
    def yql_client(self):
        from yql.api.v1.client import YqlClient
        return YqlClient(db=self.Parameters.yt_cluster, token=self.Parameters.yql_token.data())

    def initialize(self):
        now = datetime.now()
        if self.Parameters.relative_dates:
            start_date = now - timedelta(hours=self.Parameters.start_date_hours_back)
            start_date = start_date.replace(second=0, microsecond=0, minute=0)
            self.pipeline_state.start_date = start_date.strftime(DTF)
        else:
            self.pipeline_state.start_date = self.Parameters.start_date

        if self.Parameters.relative_dates:
            finish_date = now - timedelta(hours=self.Parameters.finish_date_hours_back)
            finish_date = finish_date.replace(second=0, microsecond=0, minute=0)
            self.pipeline_state.finish_date = finish_date.strftime(DTF)
        else:
            self.pipeline_state.finish_date = self.Parameters.finish_date

        from yt.wrapper import ypath_join
        if not self.Parameters.download_only:
            # создать каталог
            self.pipeline_state.destination_root = ypath_join(self.Parameters.destination_path, str(self.id))
            self.yt_client.create(path=self.pipeline_state.destination_root, type='map_node', recursive=True)
        else:
            self.pipeline_state.destination_root = ypath_join(self.Parameters.destination_path, str(self.Parameters.destination_subdir))

        logging.info("dst: {dst}".format(dst=self.pipeline_state.destination_root))
        self.set_info('Каталог для выгрузки тестовых данных: <a href="https://yt.yandex-team.ru/{db}/navigation?path={dst}">{dst}</a>'.format(
            db=self.Parameters.yt_cluster, dst=self.pipeline_state.destination_root), do_escape=False)

    def _get_tables(self):
        if self.Parameters.download_only:
            return list(self.yt_client.search(self.pipeline_state.destination_root, node_type=["table"]))
        else:
            return [table.dst for table in self.pipeline_state.tables] + [table.dst for table in self.pipeline_state.queries]

    def _get_files(self):
        if self.Parameters.download_only:
            return list(self.yt_client.search(self.pipeline_state.destination_root, node_type=["file"]))
        else:
            return [file.dst for file in self.pipeline_state.files]

    def finalize(self):
        # скачать все данные и сложить в ресурс
        with self.memoize_stage.create_resource(commit_on_entrance=False):
            fs.make_folder(self.destination().as_posix())
            tables = self._get_tables()
            files = self._get_files()
            with sdk2.helpers.ProgressMeter("Выгрузка из YT в ресурс", maxval=len(tables)) as progress:
                for table_path in tables:
                    logging.info("==> Exporting table {table}".format(table=table_path))

                    if table_path.startswith(self.pipeline_state.destination_root):
                        self._download_table_from_yt(table_path)
                    else:
                        logging.warning("Outside of destination root. Skipping.")

                    logging.info("==> Done.")
                    progress.add(1)

                for file_path in files:
                    logging.info("==> Exporting file {file}".format(file=file_path))

                    if file_path.startswith(self.pipeline_state.destination_root):
                        self._download_file_from_yt(file_path)
                    else:
                        logging.warning("Outside of destination root. Skipping.")

                    logging.info("==> Done.")
                    progress.add(1)

                self._create_map_node("home/metrika-lambda/testing/lambda/state")
                self._create_map_node("home/metrika-lambda/testing/lambda/visit_log_sorted_any")

                self.Parameters.test_data = MetrikaLambdaTestData(self, "Тестовые данные Лямбды",
                                                                  self.destination().as_posix(),
                                                                  start_date=self.pipeline_state.start_date,
                                                                  finish_date=self.pipeline_state.finish_date,
                                                                  ttl=365)

                sdk2.ResourceData(self.Parameters.test_data).ready()

        if not self.Parameters.download_only:
            with self.memoize_stage.clean_up(commit_on_entrance=False):
                if not self.Parameters.keep_tables:
                    self.yt_client.remove(self.pipeline_state.destination_root, recursive=True, force=False)
                    self.set_info("Каталог для выгрузки тестовых данных удалён.")
        else:
            self.set_info("Каталог для выгрузки тестовых данных сохранён.")

    def copy_files(self):
        self._copy_file("//home/crypta/public/udfs/stable/libcrypta_identifier_udf.so")

    def start_counters_job(self):
        from yt.wrapper import ypath_join

        self._copy_table_using_yql("//home/partner/page_metrica_counters")
        self._copy_table_using_yql("//home/adfox/owner_metrica_counters/owner_metrica_counters")
        self._copy_table_using_yql("//home/metrika/telephony_counters")
        self._copy_table_using_yql("//home/metrika-lambda/testing/lambda/offline_metrika_counters")
        self._copy_table_using_yql("//home/metrika-lambda/testing/lambda/telephony_metrika_counters")
        self._copy_table_using_yql("//home/metrika-lambda/testing/lambda/cdp_metrika_counters")
        self._copy_table_using_yql("//home/metrika/export/time_zones")

        self._copy_table_using_yql("//home/metrika/counters",
                                   condition_fragment=self._get_counters_condition_fragment())

        for table in [ypath_join("//home/metrika-lambda/testing/lambda/owner_metrica_counters", ts.strftime(DTF_TABLE_NAME_DAYLY)) for ts in self.get_dates(timedelta(days=1))]:
            self._copy_table_using_yql(table)

        for table in [ypath_join("//home/metrika-lambda/testing/lambda/page_metrica_counters", ts.strftime(DTF_TABLE_NAME_DAYLY)) for ts in self.get_dates(timedelta(days=1))]:
            self._copy_table_using_yql(table)

        for table in [ypath_join("//home/metrika-lambda/testing/lambda/crypta_matching/phone_md5", ts.strftime(DTF_TABLE_NAME_DAYLY)) for ts in self.get_dates(timedelta(days=1))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(crypta_id as String))",
                                       sample_type="crypta-matching")

        for table in [ypath_join("//home/metrika-lambda/testing/lambda/crypta_matching/phone_md5_extended", ts.strftime(DTF_TABLE_NAME_DAYLY)) for ts in self.get_dates(timedelta(days=1))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(yandexuid as String))",
                                       sample_type="crypta-matching")

    def start_visitlog_jobs(self):
        from yt.wrapper import ypath_join

        for table in [ypath_join("//logs/visit-v2-log/30min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=30))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(UserID as String))",
                                       sample_type="visit-v2-log",
                                       condition_fragment=self._get_visit_log_condition_fragment())

        for table in [ypath_join("//logs/visit-v2-private-log/30min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=30))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(UserID as String))",
                                       sample_type="visit-v2-log",
                                       condition_fragment=self._get_visit_log_condition_fragment())

        for table in [ypath_join("//logs/visit-v2-log/stream/5min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=5))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(UserID as String))",
                                       sample_type="visit-v2-log",
                                       condition_fragment=self._get_visit_log_condition_fragment())

        for table in [ypath_join("//logs/visit-v2-private-log/stream/5min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=5))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(UserID as String))",
                                       sample_type="visit-v2-log",
                                       condition_fragment=self._get_visit_log_condition_fragment())

    def start_other_jobs(self):
        from yt.wrapper import ypath_join

        for table in [ypath_join("//logs/bs-undodsp-log/1d", ts.strftime(DTF_TABLE_NAME_DAYLY)) for ts in self.get_dates(timedelta(days=1))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(uniqid)",
                                       sample_type="bs-dsp-log")

        for table in [ypath_join("//logs/bs-dsp-log/30min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=30))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(uniqid)",
                                       sample_type="bs-dsp-log")

        for table in [ypath_join("//logs/bs-dsp-checked-log/stream/5min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=5))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(uniqid)",
                                       sample_type="bs-dsp-log")

        for table in [ypath_join("//logs/adfox-event-log/1h", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(hours=1))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cast(ya_uid as String))",
                                       sample_type="adfox-event-log")

        for table in [ypath_join("//logs/bs-newsevent-log/1h", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(hours=1))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(uniqid)",
                                       sample_type="bs-newsevent-log")

        for table in [ypath_join("//home/telephony/pbx/metrika-cdr/prod/30m", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=30))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cdr_id)",
                                       sample_type="pbx-log")

        for table in [ypath_join("//home/logfeller/logs/telephony-metrica-cdr-prod/30min", ts.strftime(DTF_TABLE_NAME_INTRADAY)) for ts in self.get_dates(timedelta(minutes=30))]:
            self._copy_table_using_yql(table,
                                       sample_expr="Digest::MurMurHash(cdr_id)",
                                       sample_type="calltracking-log")

        for ts in self.get_dates(timedelta(minutes=30)):
            self._copy_table_using_yql(
                ypath_join("//home/metrika-lambda/production/lambda/offline_conversion_uploading_folder", ts.strftime(DTF_TABLE_NAME_INTRADAY)),
                dst_table=ypath_join("//home/metrika-lambda/testing/lambda/offline_conversion_uploading_folder", ts.strftime(DTF_TABLE_NAME_INTRADAY)),
                sample_expr="Digest::MurMurHash(ToBytes(Yson::Serialize(Yson::From((CounterID, UploadingID, IDType, ClientUserID, ClientID, YCLID, Goals_ID, Goals_EventTime)))))",
                sample_type="offline-conversion-log"
            )

    def start_dictionaries_jobs(self):
        counter_id_fragment = "counter_id in (select counter_id from `{destination_path}/home/metrika/counters`)" \
            .format(destination_path=self.pipeline_state.destination_root)
        self._copy_table_using_yql("//home/metrika/export/counters", condition_fragment=counter_id_fragment)
        self._copy_table_using_yql("//home/metrika/export/counter_options", condition_fragment=counter_id_fragment)

        campaign_id_fragment = "id in (select campaign_id from range(`{destination_path}/logs/adfox-event-log/1h`))" \
            .format(destination_path=self.pipeline_state.destination_root)
        self._copy_table_using_yql("//home/adfox/dictionaries/campaign", condition_fragment=campaign_id_fragment)

    def wait_jobs(self):
        logging.info("Checking YT-operation statuses and YQL-operations statuses")

        # Актуализируем состояния запущенных
        for table in [t for t in self.pipeline_state.tables if t.current_state == Table.IN_PROGRESS]:
            self._update_operation_status(table)
            self.Context.save()

        for table in [t for t in self.pipeline_state.queries if t.current_state == Query.IN_PROGRESS]:
            self._update_yql_status(table)
            self.Context.save()

        # Проверяем, есть ли зафейленные
        failed_yt = [t for t in self.pipeline_state.tables if t.current_state in (Table.FINISH_FAIL, Table.INTERNAL_ERROR)]
        failed_yql = [t for t in self.pipeline_state.queries if t.current_state in (Query.FINISH_FAIL, Query.INTERNAL_ERROR)]

        if failed_yt or failed_yql:
            message = []
            if failed_yt:
                message.append("YT operation(s) failed:")
                for t in failed_yt:
                    message.append(str(t.operation_id))
            if failed_yql:
                message.append("YQL queries failed:")
                for t in failed_yql:
                    message.append(str(t.operation_id))
            raise PipelineAbortError("\n".join(message))

        # Проверяем, сколько сейчас реально выполняется и если их меньше указанного количества - дозапускаем ещё необходимое количество
        num_running = len([t for t in self.pipeline_state.tables if t.current_state == Table.IN_PROGRESS])

        if num_running < self.Parameters.max_parallel_operations:
            num_to_launch = self.Parameters.max_parallel_operations - num_running
            for t in [t for t in self.pipeline_state.tables if t.current_state == Table.NOT_LAUNCHED][0:num_to_launch]:
                self._launch_operation(t)
                self._update_operation_status(t)
                self.Context.save()

        num_running_yql = len([t for t in self.pipeline_state.queries if t.current_state == Query.IN_PROGRESS])

        if num_running_yql < self.Parameters.max_parallel_queries:
            num_to_launch_yql = self.Parameters.max_parallel_queries - num_running_yql
            for t in [t for t in self.pipeline_state.queries if t.current_state == Query.NOT_LAUNCHED][0:num_to_launch_yql]:
                self._launch_query(t)
                self._update_yql_status(t)
                self.Context.save()

        if any([t.current_state in (Table.NOT_LAUNCHED, Table.IN_PROGRESS) for t in self.pipeline_state.tables]) or \
                any([t.current_state in (Query.NOT_LAUNCHED, Query.IN_PROGRESS) for t in self.pipeline_state.queries]):
            raise sdk2.WaitTime(60)

    def _get_visit_log_condition_fragment(self):
        return """(
    -- для yclid
    ((YCLID ?? CookieYCLID) > 0) or
    -- для dsp
    (Yson::GetLength(YANRaw_AdSessionID) > 0 and CounterID in (select cast(counter_id as UInt32) from `{destination_path}/home/partner/page_metrica_counters`)) or
    -- для adfox
    (Yson::GetLength(YANRaw_AdSessionID) > 0 and CounterID in (select cast(counter_id as UInt32) from `{destination_path}/home/adfox/owner_metrica_counters/owner_metrica_counters`)) or
    -- для офлайн конверсий
    (CounterID in (select CounterID from `{destination_path}/home/metrika-lambda/testing/lambda/offline_metrika_counters`)) or
    -- для телефонии
    (CounterID in (select CounterID from `{destination_path}/home/metrika-lambda/testing/lambda/telephony_metrika_counters`)) or
    -- для cdp
    (CounterID in (select CounterID from `{destination_path}/home/metrika-lambda/testing/lambda/cdp_metrika_counters`))
)""".format(destination_path=self.pipeline_state.destination_root)

    def _get_counters_condition_fragment(self):
        return """counter_id in (
    (select cast(counter_id as UInt32) as id from `//home/partner/page_metrica_counters`)
    union all
    (select cast(counter_id as UInt32) as id from `//home/adfox/owner_metrica_counters/owner_metrica_counters`)
    union all
    (select CounterID as id from `//home/metrika-lambda/testing/lambda/offline_metrika_counters`)
    union all
    (select CounterID as id from `//home/metrika-lambda/testing/lambda/telephony_metrika_counters`)
    union all
    (select CounterID as id from `//home/metrika-lambda/testing/lambda/cdp_metrika_counters`)
)"""

    def _start_yql_operation(self, src_table, dst_table, query):
        with self.memoize_stage[src_table](commit_on_entrance=False):
            dst_table = self._get_full_dst_path(src_table, dst_table)
            logging.info("Copy '{src}' -> '{dst}'".format(src=src_table, dst=dst_table))

            if self.yt_client.exists(src_table):
                self._create_dst_table(src_table, dst_table)

                table = Query()
                table.src = src_table
                table.dst = dst_table
                table.query = query
                table.current_state = Query.NOT_LAUNCHED
                self.pipeline_state.add_query(table)

                self.Context.save()
            else:
                logging.warning("Source table doesn't exist. Skip. {table}".format(table=src_table))

    def _get_full_dst_path(self, src_path, dst_path):
        from yt.wrapper import ypath_join, ypath_split
        dst_dir, dst_name = ypath_split(dst_path if dst_path is not None else src_path)
        dst_rel_dir = dst_dir[2:] if dst_dir.startswith("//") else dst_dir
        dst_path = ypath_join(self.pipeline_state.destination_root, dst_rel_dir, dst_name)
        return dst_path

    def _copy_table(self, src_table, dst_table=None, sample=None):
        with self.memoize_stage[src_table](commit_on_entrance=False):
            dst_table = self._get_full_dst_path(src_table, dst_table)
            logging.info("Copy with sampling {sample} '{src}' -> '{dst}'".format(sample=sample, src=src_table, dst=dst_table))

            if self.yt_client.exists(src_table):
                self._create_dst_table(src_table, dst_table)

                table = Table()
                table.src = src_table
                table.dst = dst_table
                table.sample = sample
                table.current_state = Table.NOT_LAUNCHED
                self.pipeline_state.add_table(self._update_operation_status(table))
                self.Context.save()
            else:
                logging.warning("Source table doesn't exist. Skip. {table}".format(table=src_table))

    def _create_dst_table(self, src_table, dst_table):
        from yt.wrapper import ypath_join
        attrs = self.yt_client.get(path=ypath_join(src_table, "@"))
        logging.debug("Source table attributes: {}".format(attrs))

        attrs = self._get_destination_table_attributes(attrs)

        logging.debug("Destination table attributes: {}".format(attrs))

        self.yt_client.create(path=dst_table, recursive=True, type='table', attributes=attrs)

    def _get_query_for_table(self, src_table, dst_table=None, sample_expr=None, sample_type=None, condition_fragment=None):
        dst_table = self._get_full_dst_path(src_table, dst_table)
        condition = ''
        if sample_expr is not None:
            sample = self.Parameters.sample_rates.get(sample_type, DEFAULT_SAMPLES[sample_type])
            condition += "{sample_expr} % {denominator} < {level}" \
                .format(sample_expr=sample_expr,
                        denominator=DEFAULT_DENOMINATOR,
                        level=DEFAULT_DENOMINATOR * float(sample))

        if condition_fragment is not None:
            if condition != '':
                condition += ' AND '
            condition += condition_fragment

        if condition == '':
            condition = 'true'

        return INSERT_SELECT_TEMPLATE.format(src=src_table, dst=dst_table, condition=condition)

    def _copy_table_using_yql(self, src_table, dst_table=None, sample_expr=None, sample_type=None, condition_fragment=None):
        self._start_yql_operation(src_table, dst_table, self._get_query_for_table(src_table, dst_table, sample_expr, sample_type, condition_fragment))

    def _copy_file(self, src_file, dst_file=None):
        with self.memoize_stage[src_file](commit_on_entrance=False):
            dst_file = self._get_full_dst_path(src_file, dst_file)
            logging.info("Copy '{src}' -> '{dst}'".format(src=src_file, dst=dst_file))

            if self.yt_client.exists(src_file):
                self.yt_client.copy(src_file, dst_file, recursive=True)

                file = File()
                file.src = src_file
                file.dst = dst_file
                self.pipeline_state.add_file(file)
                self.Context.save()
            else:
                logging.warning("Source file doesn't exist. Skip. {file}".format(file=src_file))

    def _get_destination_table_attributes(self, source_attrs):
        destination_attrs = dict()
        if "user_attribute_keys" in source_attrs:
            for k in source_attrs["user_attribute_keys"]:
                destination_attrs[k] = source_attrs[k]
        if "schema_mode" in source_attrs and source_attrs["schema_mode"] == "strong":
            destination_attrs["schema"] = source_attrs["schema"]

        return destination_attrs

    def _get_destination_file_attributes(self, source_attrs):
        destination_attrs = dict()
        if "user_attribute_keys" in source_attrs:
            for k in source_attrs["user_attribute_keys"]:
                destination_attrs[k] = source_attrs[k]

        return destination_attrs

    def _launch_operation(self, table):
        from yt.wrapper import YsonFormat, errors
        try:
            if self.yt_client.exists(table.src):
                input_output_format = YsonFormat()
                if table.sample:
                    spec = {"job_io": {"table_reader": {"sampling_seed": 1221, "sampling_rate": float(table.sample)}}}
                else:
                    spec = None

                operation = self.yt_client.run_map("cat", table.src, table.dst, spec=spec, sync=False,
                                                   input_format=input_output_format, output_format=input_output_format)
                logging.info("YT OPERATION: {id}".format(id=operation.id))

                table.operation_id = operation.id
                table.share_url = operation.url
                table.current_state = Table.IN_PROGRESS
            else:
                logging.warning("Table {src} not found. Skip it.".format(src=table.src))
                table.current_state = Table.FINISH_NO_DATA
        except errors.YtConcurrentOperationsLimitExceeded as e:
            logging.warning("Не удалось запустить операцию, т.к. превышен лимит на количество одновременно запущенных операций. Будет предпринята ещё попытка позже", exc_info=True)
            table.current_state = Table.NOT_LAUNCHED
            table.status = repr(e)
        except Exception as e:
            logging.warning("Ошибка при запуске YT-операции", exc_info=True)
            table.current_state = Table.INTERNAL_ERROR
            table.state = str(e)

    def _launch_query(self, table):
        try:
            if self.yt_client.exists(table.src):
                logging.info("Starting YQL operation for {src}".format(src=table.src))
                request = self.yql_client.query(table.query, syntax_version=1)
                request.run()
                logging.info("YQL OPERATION: {id} {src}".format(id=request.operation_id, src=table.src))

                table.operation_id = request.operation_id
                table.share_url = request.share_url
                table.current_state = Query.IN_PROGRESS
            else:
                logging.warning("Table {src} not found. Skip it.".format(src=table.src))
                table.current_state = Query.FINISH_NO_DATA
        except Exception as e:
            logging.warning("Ошибка при запуске YQL-запроса", exc_info=True)
            table.current_state = Query.INTERNAL_ERROR
            table.state = str(e)

    def _update_yql_status(self, table):
        from yql.client.operation import YqlOperationStatusRequest
        from yql.client.results import CantGetResultsException
        try:
            if table.current_state not in (Query.FINISH_NO_DATA, Query.FINISH_SUCCESS, Query.FINISH_FAIL):
                if table.operation_id:
                    logging.debug("Update YQL status for {id} {src}".format(id=table.operation_id, src=table.src))
                    self.yql_client.ping()
                    status = YqlOperationStatusRequest(table.operation_id)
                    status.run()
                    table.status = status.status
                    logging.debug("{id}:{status}".format(id=table.operation_id, status=table.status))
                    if status.in_progress:
                        table.current_state = Query.IN_PROGRESS
                    elif status.is_success:
                        table.current_state = Query.FINISH_SUCCESS
                    else:
                        issues = "\n".join([str(e) for e in status.errors])
                        logging.debug(issues)
                        # dirty hack FIXME
                        if any([e.message == 'It seems that you have too many running operations. Wait until some of them become completed and try again.' for e in status.errors]):
                            table.current_state = Query.NOT_LAUNCHED
                            table.status = issues
                        else:
                            table.current_state = Query.FINISH_FAIL
        except CantGetResultsException as e:
            logging.warning("Ошибка получения результата запроса. Operation id: '{id}' ({t}). Запрос будет перезапущен.".format(id=table.operation_id, t=type(table.operation_id)), exc_info=True)
            table.current_state = Query.NOT_LAUNCHED
            table.status = str(e)
        except Exception as e:
            logging.warning("Ошибка при обновлении состояния запроса", exc_info=True)
            table.current_state = Query.INTERNAL_ERROR
            table.status = str(e)
        return table

    def _update_operation_status(self, table):
        from yt.wrapper import Operation
        try:
            if table.current_state not in (Table.FINISH_NO_DATA, Table.FINISH_SUCCESS, Table.FINISH_FAIL):
                if table.operation_id:
                    operation = Operation(id=table.operation_id, client=self.yt_client)
                    table.operation_exists = operation.exists()
                    if table.operation_exists:
                        op_state = operation.get_state()
                        if op_state.is_running():
                            table.current_state = Table.IN_PROGRESS
                        elif op_state.is_unsuccessfully_finished():
                            table.current_state = Table.FINISH_FAIL
                        elif op_state.is_finished():
                            table.current_state = Table.FINISH_SUCCESS
                        table.status = op_state.name
                        table.progress = operation.get_progress()
                    logging.debug("{id}:{exists}:{status}".format(id=table.operation_id, exists=table.operation_exists, status=table.status))
        except Exception as e:
            logging.warning("Ошибка при обновлении состояния операции", exc_info=True)
            table.current_state = Table.INTERNAL_ERROR
            table.status = str(e)
        return table

    def get_dates(self, dt):
        result = []
        start = datetime.strptime(self.pipeline_state.start_date, DTF)
        finish = datetime.strptime(self.pipeline_state.finish_date, DTF)
        current = start
        while current < finish:
            result.append(current)
            current = current + dt
        return result

    def _download_table_from_yt(self, table):
        from yt.wrapper import yson, ypath_join, ypath_split

        dir_name, table_name = ypath_split(table)
        dir_name = dir_name[len(self.pipeline_state.destination_root) + 1:]  # +1 - remove extra slash
        fs.make_folder(self.destination(dir_name).as_posix())

        destination = self.destination(dir_name, table_name).as_posix()
        logging.info("Downloading yt table {src} to {dst}".format(src=table, dst=destination))
        with open(destination, "w") as fout:
            yson.dump(self.yt_client.read_table(table), fout, yson_type="list_fragment")

        metafile = destination + ".meta"
        logging.info("Writing metafile: {mf}".format(mf=metafile))
        with io.open(metafile, "wb") as meta_fout:
            attributes = self.yt_client.get(ypath_join(table, "@"))
            logging.debug("Source table attributes: {}".format(attributes))

            attributes = self._get_destination_table_attributes(attributes)

            logging.debug("Destination metafile attributes: {}".format(attributes))

            metadata = {
                "attributes": attributes,
                "type": "table",
                "format": "yson"
            }

            yson.dump(metadata, meta_fout)

    def _download_file_from_yt(self, file):
        from yt.wrapper import yson, ypath_join, ypath_split

        dir_name, file_name = ypath_split(file)
        dir_name = dir_name[len(self.pipeline_state.destination_root) + 1:]  # +1 - remove extra slash
        fs.make_folder(self.destination(dir_name).as_posix())

        destination = self.destination(dir_name, file_name).as_posix()
        logging.info("Downloading yt file {src} to {dst}".format(src=file, dst=destination))
        with open(destination, "w") as fout:
            fout.write(self.yt_client.read_file(file).read())

        metafile = destination + ".meta"
        logging.info("Writing metafile: {mf}".format(mf=metafile))
        with io.open(metafile, "wb") as meta_fout:
            attributes = self.yt_client.get(ypath_join(file, "@"))
            logging.debug("Source file attributes: {}".format(attributes))

            attributes = self._get_destination_file_attributes(attributes)

            logging.debug("Destination metafile attributes: {}".format(attributes))

            metadata = {
                "attributes": attributes,
                "type": "file"
            }

            yson.dump(metadata, meta_fout)

    def _create_map_node(self, dir):
        from yt.wrapper import yson

        destination = self.destination(dir).as_posix()
        logging.info("Creating map node {dst}".format(dst=destination))
        fs.make_folder(destination)

        metafile = destination + "/.meta"
        logging.info("Writing metafile: {mf}".format(mf=metafile))
        with io.open(metafile, "wb") as meta_fout:
            attributes = dict()

            logging.debug("Destination metafile attributes: {}".format(attributes))

            metadata = {
                "attributes": attributes,
                "type": "map_node"
            }

            yson.dump(metadata, meta_fout)

    @sdk2.report(title="YT-операции и YQL-запросы")
    def status_report(self):
        if self.pipeline_state:
            return utils.render("view.html.jinja2", {"pipeline_state": self.pipeline_state})
        else:
            return None
