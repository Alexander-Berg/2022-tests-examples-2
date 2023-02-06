import sys
print(sys.path)
import json
from pyflink.common import WatermarkStrategy, Row
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import FsStateBackend
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.time_characteristic import TimeCharacteristic
from pyflink.datastream.functions import RuntimeContext, MapFunction
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common.typeinfo import Types

from ya_flink.datastream.connectors.logbroker.config import LogbrokerConsumerConfig, LogbrokerProducerConfig
from ya_flink.datastream.connectors.logbroker.consumers import get_logbroker_consumer
from ya_flink.datastream.connectors.logbroker.producers import get_logbroker_producer


ENV = "testing"
SOURCE_TOPIC = f"/logbroker-playground/kateleb/demo_raw_data"
TARGET_TOPIC = f"/logbroker-playground/kateleb/demo_ods_out_data"
CONSUMER = f"/logbroker-playground/kateleb/demo_ods_transformer"

# class MyMapFunction(MapFunction):
#
#     def open(self, runtime_context: RuntimeContext):
#         state_desc = ValueStateDescriptor('cnt', Types.PICKLED_BYTE_ARRAY())
#         self.cnt_state = runtime_context.get_state(state_desc)
#
#     def map(self, value):
#         cnt = self.cnt_state.value()
#         if cnt is None or cnt < 2:
#             self.cnt_state.update(1 if cnt is None else cnt + 1)
#             return value[0], value[1] + 1
#         else:
#             return value[0], value[1]

def simple_map(line):
    import json
    res = json.loads(line)
    res['new_val']=res['c'] + res['b']
    return res


def sss(line):
    res = json.loads(line)
    return json.dumps({'name' : res['name'], 'c' : res['c'], 'create_time' : res['create_time'], 'new_field': 1234})


def mappers_from_extractors():
    pass


def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    env.enable_checkpointing(60000)  # interval in millis
    env.set_state_backend(FsStateBackend("s3://taxi-agiotage/flink-checkpoint"))

    lb_config = LogbrokerConsumerConfig.builder(SOURCE_TOPIC, CONSUMER) \
        .set_read_only_local(True) \
        .set_default_oauth_credentials() \
        .enable_retries() \
        .build()

    lb_consumer = get_logbroker_consumer(lb_config, deserialization_schema=SimpleStringSchema())
    ds = env.add_source(lb_consumer, "test_in")
    # output_type=Types.ROW_NAMED(['c', 'create_time', 'name'], [Types.INT(), Types.STRING(), Types.STRING()])
    output_type=Types.STRING()
    ds = ds.map(sss, output_type=output_type)

    lb_producer_config = LogbrokerProducerConfig.builder(TARGET_TOPIC) \
        .set_default_oauth_credentials() \
        .build()
    lb_producer = get_logbroker_producer(lb_producer_config, SimpleStringSchema())
    ds.add_sink(lb_producer)

    env.execute()


if __name__ == '__main__':
    main()
