from contextlib import closing, contextmanager
from concurrent.futures import TimeoutError
import pytest
import yatest.common
import logging

from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.worker_pool.protos.basic_item_pb2 import TBasicItem

logger = logging.getLogger('rthub_test_logger')


@contextmanager
def launch():
    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/test/worker_pool/conf/main.pb.txt')
    proto_path = yatest.common.build_path('robot/rthub/test/worker_pool/full_protos')
    queries_path = yatest.common.source_path('robot/rthub/test/worker_pool/queries')
    udfs_path = yatest.common.build_path('robot/rthub/test/worker_pool/full_udfs')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, None, None)
    rthub_runner.update_config(udfs_path, proto_path, None, None, queries_path, None)
    rthub_runner.save_config()

    logger.info('Launching RTHub...')
    try:
        rthub_runner.run_rthub(binary=False, as_daemon=True)
        yield rthub_runner
    finally:
        rthub_runner.stop_daemon()


def test_slow():
    with launch() as rthub_runner:
        item = TBasicItem()
        item.Data = 'msg_slow1'

        lb_writer = rthub_runner.create_lb_writer('racc/itopic_slow')
        lb_writer.send_next_message(item.SerializeToString())

        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            with pytest.raises(TimeoutError):
                reader.read_next_messages(1, 3)

        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            data = reader.read_next_messages(1, 4)

        assert len(data) == 1
        result_item = TBasicItem()
        result_item.ParseFromString(data[0])
        assert result_item.Data.endswith(item.Data)


def test_fast():
    with launch() as rthub_runner:
        item = TBasicItem()
        item.Data = 'msg_fast1'

        lb_writer = rthub_runner.create_lb_writer('racc/itopic_fast')
        lb_writer.send_next_message(item.SerializeToString())

        with closing(rthub_runner.create_lb_reader('wacc/otopic_fast')) as reader:
            data = reader.read_next_messages(1, 3)

        assert len(data) == 1
        result_item = TBasicItem()
        result_item.ParseFromString(data[0])
        assert result_item.Data.endswith(item.Data)


def test_fast_first():
    with launch() as rthub_runner:
        slow_item = TBasicItem()
        slow_item.Data = 'msg_slow'

        lb_writer = rthub_runner.create_lb_writer('racc/itopic_slow')
        lb_writer.send_next_message(slow_item.SerializeToString())
        lb_writer.send_next_message(slow_item.SerializeToString())

        # not result yet
        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            with pytest.raises(TimeoutError):
                reader.read_next_messages(1, 1)

        fast_item = TBasicItem()
        fast_item.Data = 'msg_fast'

        lb_writer = rthub_runner.create_lb_writer('racc/itopic_fast')
        lb_writer.send_next_message(fast_item.SerializeToString())
        lb_writer.send_next_message(fast_item.SerializeToString())

        def _validate(d, expected):
            assert len(d) == 1
            result_item = TBasicItem()
            result_item.ParseFromString(d[0])
            assert result_item.Data.endswith(expected)

        with closing(rthub_runner.create_lb_reader('wacc/otopic_fast')) as reader:
            _validate(reader.read_next_messages(1, 2), fast_item.Data)

        # still no result
        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            with pytest.raises(TimeoutError):
                reader.read_next_messages(1, 1)

        with closing(rthub_runner.create_lb_reader('wacc/otopic_fast')) as reader:
            _validate(reader.read_next_messages(1, 2), fast_item.Data)

        # finally ready
        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            _validate(reader.read_next_messages(1, 4), slow_item.Data)

        with closing(rthub_runner.create_lb_reader('wacc/otopic_slow')) as reader:
            _validate(reader.read_next_messages(1, 6), slow_item.Data)
