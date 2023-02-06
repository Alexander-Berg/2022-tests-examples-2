from contextlib import closing, contextmanager
import yatest.common
import logging

from robot.library.message_io.protos.message_format_pb2 import EMessageFormat
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.serialized_message.protos.basic_item_pb2 import TBasicItem
from robot.rthub.yql.generic_protos.serialized_message_pb2 import TSerializedMessage

logger = logging.getLogger('rthub_test_logger')


@contextmanager
def launch(config_file):
    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/test/serialized_message/conf/{}'.format(config_file))
    proto_path = yatest.common.build_path('robot/rthub/test/serialized_message/full_protos')
    queries_path = yatest.common.source_path('robot/rthub/test/serialized_message/queries')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, None, None)
    rthub_runner.update_config(None, proto_path, None, None, queries_path, None)
    rthub_runner.save_config()

    logger.info('Launching RTHub...')
    try:
        rthub_runner.run_rthub(binary=False, as_daemon=True)
        yield rthub_runner
    finally:
        rthub_runner.stop_daemon()


def test_raw_input():
    with launch('raw_input_config.pb.txt') as rthub_runner:
        lb_writer = rthub_runner.create_lb_writer('racc/itopic')
        lb_writer.send_next_message('0123456789')

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            data = reader.read_next_messages(1)

        assert len(data) == 1
        result_item = TSerializedMessage()
        result_item.ParseFromString(data[0])
        assert result_item.DataPtr > 0
        assert result_item.DataSize == 10
        assert result_item.Format == EMessageFormat.MF_BINARY
        assert not result_item.Decompress


def test_raw_output():
    with launch('raw_output_config.pb.txt') as rthub_runner:
        item = TBasicItem()
        item.Data = '0123456789'

        lb_writer = rthub_runner.create_lb_writer('racc/itopic')
        lb_writer.send_next_message(item.SerializeToString())

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            data = reader.read_next_messages(1)

        assert len(data) == 1
        assert data[0] == '01234567890123456789'
