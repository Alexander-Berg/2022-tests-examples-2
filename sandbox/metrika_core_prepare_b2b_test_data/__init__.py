# coding=utf-8
import datetime

from sandbox.projects.sandbox import remote_copy_resource

from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.core import utils as core_utils
from sandbox.projects.metrika.utils import base_metrika_task
from sandbox.projects.metrika.utils.pipeline import pipeline
from sandbox.sdk2 import parameters

chevent_log_source_table = "merge(chevent_log, '^CheckedEventLog_')"
chevent_log_where_template = "(eventtime >= toDateTime('{start}') and eventtime <= toDateTime('{end}')) and (((intHash32(uniqid) % {sampling}) = {sample}) or (uniqid = 0))"

TABLES = [
    {
        "name": "chevent_log",
        "source_table": chevent_log_source_table,
        "where_template": chevent_log_where_template,
        "database": "CheckedEventLogIncoming",
        "table_prefix": "CheckedEventLogIncoming_",
        "chunk_size": 10000
    },
    {
        "name": "undo_chevent_log",
        "source_table": "merge(undo_chevent_log, '^UndoCheckedEventLog_')",
        "where_template": "(eventtime >= toDateTime('{start}') and eventtime <= toDateTime('{end}'))",
        "database": "UndoCheckedEventLogIncoming",
        "table_prefix": "UndoCheckedEventLogIncoming_",
        "chunk_size": 1000
    },
    {
        "name": "action_checked_log",
        "source_table": "merge(action_checked_log, '^ActionCheckedLog_')",
        "where_template": """(eventtime >= toDateTime('{start}') and eventtime <= toDateTime('{end}'))
        and logid in (select logid from {chevent_log_source_table} where {chevent_log_where_template})
        """,
        "chevent_log_source_table": chevent_log_source_table,
        "chevent_log_where_template": chevent_log_where_template,
        "database": "action_checked_log",
        "table_prefix": "ActionCheckedLog_",
        "chunk_size": 10000,
    },
    {
        "name": "clicks_000",
        "source_table": "merge(clicks_000, '^ClickLog_[1-9]')",
        "where_template": "(EventTime >= toDateTime('{start}') and EventTime <= toDateTime('{end}')) and (((intHash32(UniqID) % {sampling}) = {sample}) or (UniqID = 0))",
        "database": "ClickLog_000",
        "table_prefix": "ClickLog_00000000000000000",
        "chunk_size": 4000
    },
    {
        "name": "clicks_001",
        "source_table": "merge(clicks_001, '^ClickLog_[1-9]')",
        "where_template": "(EventTime >= toDateTime('{start}') and EventTime <= toDateTime('{end}')) and (((intHash32(UniqID) % {sampling}) = {sample}) or (UniqID = 0))",
        "database": "ClickLog_001",
        "table_prefix": "ClickLog_00000000000000000",
        "chunk_size": 4000
    },
    {
        "name": "watch_log_001",
        "source_table": "merge(watch_log_001, '^WatchLog_')",
        "where_template": """(EventTime >= toDateTime('{start}') and EventTime <= toDateTime('{end}'))
                             and (intHash32(if(UniqID == 0, sipHash64(IPv6StringToNum(HumanReadableClientIP6) || UserAgent), UniqID) as UserID) % {sampling} = {sample})""",
        "database": "watch_log_001",
        "table_prefix": "WatchLog_{}000000000000".format(datetime.datetime.now().strftime("%Y%m%d")),
        "chunk_size": 100000
    }
]
SAMPLING = 100
SAMPLE = 42
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


@base_metrika_task.with_parents
class MetrikaCorePrepareB2BTestData(pipeline.PipelineBaseTask):
    """
    Подготовка тестовых данных для B2B Движка Метрики
    """
    name = "METRIKA_CORE_PREPARE_B2B_TEST_DATA"

    class Context(pipeline.PipelineBaseTask.Context):
        torrent_id = 0

    class Parameters(utils.CommonParameters):
        description = "Подготовка тестовых данных для B2B Движка Метрики"

        source = parameters.String("Источник тестовых данных", required=True, default="mtcalclog01et.metrika.yandex.net",
                                   description="FQDN машинки, откуда выгружаются данные")

        end_time = parameters.String("Дата и время конца интервала данных", required=True, default=datetime.datetime.now().strftime(DATETIME_FORMAT),
                                     description="Данные будут получены за предыдущие двое суток от указанной даты и времени")

        hostname = parameters.String("Машинка для данных", required=True, default="source.vla.yp-c.yandex.net",
                                     description="FQDN хоста, на который будут загружены тестовые данные")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def create_stages(self):
        return [
            (self.stage_select_test_data, "Получение тестовых данных"),
            (self.stage_split_test_data, "Разбивка на чанки"),
            (self.stage_share_test_data, "Раздача тестовых данных"),
            (self.stage_upload_test_data, "Загрузка тестовых данных")
        ]

    def stage_select_test_data(self):
        start_time = (datetime.datetime.strptime(self.Parameters.end_time, DATETIME_FORMAT) - datetime.timedelta(days=2)).strftime(DATETIME_FORMAT)

        self.set_info("Получение данных из <b>{}</b><br/>за интервал времени <b>{} - {}</b><br/>и сохранение на <b>{}</b>"
                      .format(self.Parameters.source, start_time, self.Parameters.end_time, self.Parameters.hostname), do_escape=False)

        for table in TABLES:
            query = "create table {} engine = StripeLog as select * from remote('{}', {}) where {}".format(
                table["name"],
                self.Parameters.source,
                table["source_table"],
                table["where_template"].format(
                    start=start_time,
                    end=self.Parameters.end_time,
                    sampling=SAMPLING,
                    sample=SAMPLE,
                    chevent_log_source_table=table.get("chevent_log_source_table", ""),
                    chevent_log_where_template=table.get("chevent_log_where_template", "").format(
                        start=start_time,
                        end=self.Parameters.end_time,
                        sampling=SAMPLING,
                        sample=SAMPLE
                    )
                )
            )
            core_utils.execute_remote_script(self, self.Parameters.hostname, """
                    clickhouse-client --query="drop table if exists {0}"
                    clickhouse-client --max_execution_time=0 --query="{1}"
                """.format(table["name"], query))

            self.set_info("Получено <b>{}</b> строк из <b>{}</b>".format(
                core_utils.get_remote_script_output(self, self.Parameters.hostname, "clickhouse-client --query='select count() from {}'".format(table["name"])), table["name"]), do_escape=False)

    def stage_split_test_data(self):
        core_utils.execute_remote_script(self, self.Parameters.hostname, "rm -rf /tmp/clickhouse /tmp/chunks; mkdir -p /tmp/clickhouse /tmp/chunks")

        for table in TABLES:
            core_utils.execute_remote_script(self, self.Parameters.hostname, """
                mkdir -p /tmp/chunks/{0}
                clickhouse-client --query="select * from {0} format TabSeparated" > /tmp/clickhouse/{0}.tsv
                split --lines={1} --numeric-suffixes --suffix-length=3 --additional-suffix={4} /tmp/clickhouse/{0}.tsv /tmp/chunks/{0}/{2}
                clickhouse-client --query="drop database if exists {3}"
                clickhouse-client --query="create database {3}"
                for file in $(ls /tmp/chunks/{0}); do
                    clickhouse-client --query="create table {3}.$file as {0}"
                    clickhouse-client --query="insert into {3}.$file format TabSeparated" < /tmp/chunks/{0}/$file
                done
            """.format(table["name"], table["chunk_size"], table["table_prefix"], table["database"], "001" if table["name"] == "watch_log_001" else ""))

        core_utils.execute_remote_script(self, self.Parameters.hostname, """
            table=$(clickhouse-client --query="select name from system.tables where database = 'watch_log_001' and name != 'all' order by name desc limit 1")
            clickhouse-client --query="rename table watch_log_001.${table} to watch_log_001.${table//001/002}"
        """)

    def stage_share_test_data(self):
        core_utils.execute_remote_script(self, self.Parameters.hostname, "rm -rf /tmp/mnt2; cp -r /mnt2 /tmp/mnt2; rm -rf /tmp/mnt2/clickhouse/data/* /tmp/mnt2/clickhouse/metadata/*")

        for table in TABLES:
            core_utils.execute_remote_script(self, self.Parameters.hostname, """
                cp -r /opt/clickhouse/data/{0} /tmp/mnt2/clickhouse/data/{0}
                cp -r /opt/clickhouse/metadata/{0} /tmp/mnt2/clickhouse/metadata/{0}
                cp /opt/clickhouse/metadata/{0}.sql /tmp/mnt2/clickhouse/metadata/{0}.sql
                sed -i "s/testing.date=.*/testing.date={1}/" /tmp/mnt2/metadata.properties
            """.format(table["database"], datetime.datetime.strptime(self.Parameters.end_time, DATETIME_FORMAT).strftime(DATE_FORMAT)))

        core_utils.execute_remote_script(self, self.Parameters.hostname, "tar -zcvf /tmp/mnt2.tar.gz -C /tmp/mnt2 .")

        self.Context.torrent_id = core_utils.get_remote_script_output(self, self.Parameters.hostname, "cd /tmp; sky share mnt2.tar.gz")

    def stage_upload_test_data(self):
        self.run_subtasks([(
            remote_copy_resource.RemoteCopyResource,
            {
                "resource_type": "METRIKA_CORE_B2B_TESTS_DATA",
                remote_copy_resource.RemoteCopyResource.ResName.name: "mnt2",
                remote_copy_resource.RemoteCopyResource.FileName.name: self.Context.torrent_id,
                remote_copy_resource.RemoteCopyResource.ResAttrs.name: "ttl=365,share=True,use=testing"
            }
        )])
