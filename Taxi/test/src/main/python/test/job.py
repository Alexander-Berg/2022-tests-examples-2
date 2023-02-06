import pyflink
import random
import sys
import typing as tp
from pyflink.common import WatermarkStrategy, Row
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import TableEnvironment, StreamTableEnvironment, EnvironmentSettings, DataTypes, TableDescriptor, Schema
from pyflink.table.expressions import lit, col
from pyflink.table.udf import udf
from pyflink.datastream.connectors import FileSink, OutputFileConfig, NumberSequenceSource
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import RuntimeContext, MapFunction
from datetime import datetime
print(sys.path)

print(pyflink.__file__)

from dmp_suite import datetime_utils as dtu
from dmp_suite import extract_utils as eu
from dmp_suite.data_transform import ExtractorType
from pyflink.datastream.state import ValueStateDescriptor

# from flow.runners.flink_runner.utils import convert_utils

ENV = "testing"
SOURCE_TOPIC = f"/logbroker-playground/kateleb/demo_raw_data"
TARGET_TOPIC = f"/logbroker-playground/kateleb/demo_ods_out_data"
CONSUMER = f"/logbroker-playground/kateleb/demo_ods_transformer"


TARGET_SCHEMA = (
    Schema.new_builder()
        .column("b", DataTypes.INT())
        .column("ex_c", DataTypes.INT())
        .column("bc", DataTypes.INT())
        .column("res", DataTypes.STRING())
        .column("NAME", DataTypes.STRING())
        .column("utc_created_dttm", DataTypes.STRING())
        .column("weirdo", DataTypes.STRING())
        .build()
)


def main():
    #====== TABLE ==============
    t_env = TableEnvironment.create(
        environment_settings=EnvironmentSettings.new_instance().in_streaming_mode().build()
    )

    config = t_env.get_config().get_configuration()
    config.set_string("execution.checkpointing.mode", "EXACTLY_ONCE")
    config.set_string("execution.checkpointing.interval", "2min")
    config.set_string("state.checkpoints.dir", "s3://taxi-agiotage/flink-checkpoint")

    source_schema = (
        Schema.new_builder()
            .column("name", DataTypes.STRING())
            .column("b", DataTypes.BIGINT())
            .column("c", DataTypes.BIGINT())
            .column("create_time", DataTypes.STRING())
            .build()
    )

    source_descriptor = (
        TableDescriptor
            .for_connector("logbroker")
            .schema(source_schema)
            .format("json")
            .option("installation", "logbroker")
            .option("topic", SOURCE_TOPIC)
            .option("consumer", CONSUMER)
            .option("credentials", "default-oauth")
            .build()
    )

    source_table = t_env.from_descriptor(source_descriptor)

    def my_func(s):
        return s.upper()

    func3 = udf(dtu.format_datetime_wo_delimiter, result_type=DataTypes.STRING())
    func = udf(my_func, result_type=DataTypes.STRING())

    def map_function(a: Row) -> Row:
        return Row(
            res='cxvbnb',
            weirdo='zxcfg',
            name=str(a.name) + '___',
            z='nowar',
            a='a',
            b=8,
            c=a.c,
            utc_created_dttm=dtu.format_datetime(a.create_time),
        )

    @udf(result_type=DataTypes.ROW([DataTypes.FIELD("id", DataTypes.BIGINT()),
                                    DataTypes.FIELD("data", DataTypes.STRING())]))
    def func2(data: Row) -> Row:
        return Row(1, data.name * 2)

    ffe3 = udf(map_function, result_type=DataTypes.ROW(
        [
            DataTypes.FIELD("a", DataTypes.STRING()),
            DataTypes.FIELD("b", DataTypes.INT()),
            DataTypes.FIELD("с", DataTypes.INT()),
            DataTypes.FIELD("name", DataTypes.STRING()),
            DataTypes.FIELD("res", DataTypes.STRING()),
            DataTypes.FIELD("utc_created_dttm", DataTypes.STRING()),
            DataTypes.FIELD("weirdo", DataTypes.STRING()),
            DataTypes.FIELD("z", DataTypes.STRING()),

        ]))

    result = (source_table
              .select(col("name"),col("create_time"), col("c"))
              .map(ffe3).alias('a, b, c, name, res, utc_created_dttm, weirdo, z'))
    #      # .select(
    #      col("b"),
    #      col("c").alias("ex_c"),
    #      col("create_time"),
    #      # concat(lit("Goodbye, "), col("name")).alias("hello")
    #      # func(lit("2021-05-10T13:55:40.140700")).alias("res")
    #      func2(lit("2021-05-10T13:55:40.140700")).alias("res"),
    #      func(col("name")).alias("NAME")
    # ).map(ffe2)

    target_descriptor = (
        TableDescriptor.for_connector("logbroker")
            .format("json")
            .option("installation", "logbroker")
            .option("topic", TARGET_TOPIC)
            .option("credentials", "default-oauth")
            .build()
    )

    result.execute_insert(target_descriptor)


if __name__ == '__main__':
    main()
