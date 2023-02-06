from contextlib import closing, contextmanager
import yatest.common
import logging
import zlib

from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.web_api.protos.basic_item_pb2 import TBasicItem

import robot.rthub.yql.generic_protos.web_output_pb2 as web_output_pb2

logger = logging.getLogger('rthub_test_logger')


@contextmanager
def launch(web_server_input_format):
    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/test/web_api/conf/main.pb.txt')
    proto_path = yatest.common.build_path('robot/rthub/test/web_api/full_protos')
    queries_path = yatest.common.source_path('robot/rthub/test/web_api/queries')

    rthub_runner = None
    try:
        rthub_runner = RTHubRunner(rthub_bin, orig_config, None, None)

        rthub_runner.update_config(None, proto_path, None, None, queries_path, None)
        rthub_runner.save_config()

        logger.info('Launching RTHub...')

        rthub_runner.run_rthub(binary=False, web_server_input_format=web_server_input_format, as_daemon=True)
        yield rthub_runner
    finally:
        rthub_runner.stop_daemon()


def _check_agg_metrics(rthub_runner, expected_bytes, expected_count):
    sensors = rthub_runner.get_json_sensors('rthub_agg')
    c = sensors.find_sensor({'sensor': 'Count',
                             'host': 'const',
                             'type': 'agg_channel_outputs',
                             'field': 'Data',
                             'output': 'Output',
                             'sub_type': 'per_field'})
    assert c == expected_count

    b = sensors.find_sensor({'sensor': 'Bytes',
                             'host': 'const',
                             'type': 'agg_channel_outputs',
                             'field': 'Data',
                             'output': 'Output',
                             'sub_type': 'per_field'})

    assert b == expected_bytes


def _check_invalid_format_message_count_sensor(rthub_runner, expected_count):
    sensors = rthub_runner.get_json_sensors('rthub')
    c = sensors.find_sensor({'sensor': 'InvalidFormatMessagesCount'})
    assert c == expected_count


def test_single():
    with launch('binary') as rthub_runner:
        item = TBasicItem()
        item.Data = '0123456789'

        web_client = rthub_runner.get_web_client('racc/itopic', 'Output')

        _check_agg_metrics(rthub_runner, None, None)
        # invalid payload: unable to unzip
        result = web_client.send_message('ABC')
        assert len(result.Message) == 0
        _check_invalid_format_message_count_sensor(rthub_runner, 1)

        # invalid payload: unable to parse protobuf
        result = web_client.send_message(zlib.compress('ABC'))
        assert len(result.Message) == 0
        _check_invalid_format_message_count_sensor(rthub_runner, 2)

        # crash in yql
        poison_item = TBasicItem()
        poison_item.Data = 'poison'
        result = web_client.send_message(zlib.compress(poison_item.SerializeToString()))
        assert len(result.Message) == 0
        # no increment here =\
        _check_invalid_format_message_count_sensor(rthub_runner, 2)

        # should work
        result = web_client.send_message(zlib.compress(item.SerializeToString()))
        assert len(result.Message) == 1
        msg = result.Message[0]
        assert msg.Name == 'Output'
        assert msg.Proto == 'NRTHubTest.TBasicItem'
        assert msg.ResponseStatus == web_output_pb2.TWebMessage.Ok
        assert len(msg.ErrorDescription) == 0
        assert len(msg.Content) == 12

        result_item = TBasicItem()
        result_item.ParseFromString(msg.Content)
        assert result_item.Data == '0123456789'

        _check_agg_metrics(rthub_runner, 10, 1)

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            data = reader.read_next_messages(1)

        assert len(data) == 1
        result_item = TBasicItem()
        result_item.ParseFromString(data[0])
        assert result_item.Data == '0123456789'


def test_batch():
    with launch('binary_batch') as rthub_runner:
        item = TBasicItem()
        item.Data = '0123456789'

        web_client = rthub_runner.get_web_client('racc/itopic', 'Output')

        _check_agg_metrics(rthub_runner, None, None)
        # invalid payload: unable to unzip
        result = web_client.send_batch(['ABC'])
        assert len(result.Outputs) == 1
        # yes, we do not have error in reply =\
        assert len(result.Outputs[0].Message) == 0
        _check_invalid_format_message_count_sensor(rthub_runner, 1)

        # invalid payload: unable to parse protobuf
        result = web_client.send_batch([zlib.compress('ABC')])
        assert len(result.Outputs) == 1
        # yes, we do not have error in reply =\
        assert len(result.Outputs[0].Message) == 0
        _check_invalid_format_message_count_sensor(rthub_runner, 2)

        result = web_client.send_batch([zlib.compress(item.SerializeToString())])
        assert len(result.Outputs) == 1
        assert len(result.Outputs[0].Message) == 1
        msg = result.Outputs[0].Message[0]
        assert msg.Name == 'Output'
        assert msg.Proto == 'NRTHubTest.TBasicItem'
        assert msg.ResponseStatus == web_output_pb2.TWebMessage.Ok
        assert len(msg.ErrorDescription) == 0
        assert len(msg.Content) == 12

        result_item = TBasicItem()
        result_item.ParseFromString(msg.Content)
        assert result_item.Data == '0123456789'

        _check_agg_metrics(rthub_runner, 10, 1)

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            data = reader.read_next_messages(1)

        assert len(data) == 1
        result_item = TBasicItem()
        result_item.ParseFromString(data[0])
        assert result_item.Data == '0123456789'

        # send 5 items
        datas = ['1', '2', '3', '4', '5']
        items = []
        for d in datas:
            item = TBasicItem()
            item.Data = d
            items.append(zlib.compress(item.SerializeToString()))

        result = web_client.send_batch(items)
        assert len(result.Outputs) == 5
        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            lb_data = reader.read_next_messages(len(result.Outputs))

        lb_items = []
        for d in lb_data:
            result_item = TBasicItem()
            result_item.ParseFromString(d)
            lb_items.append(result_item.Data)

        # there is no guarantee on items order in topic
        lb_items.sort()

        for i in xrange(len(result.Outputs)):
            msg = result.Outputs[i].Message[0]
            assert msg.Name == 'Output'
            assert msg.Proto == 'NRTHubTest.TBasicItem'
            assert msg.ResponseStatus == web_output_pb2.TWebMessage.Ok
            assert len(msg.ErrorDescription) == 0
            result_item = TBasicItem()
            result_item.ParseFromString(msg.Content)
            assert result_item.Data == datas[i]
            assert result_item.Data == lb_items[i]

        # send 5 items again, but turn off http output
        result = web_client.send_batch(items, omit_content=True)
        assert len(result.Outputs) == 5
        for output in result.Outputs:
            assert len(output.Message[0].Content) == 0

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            lb_data = reader.read_next_messages(len(result.Outputs))
        assert len(lb_data) == len(result.Outputs)

        # send 5 items again, but turn off writing to LB
        result = web_client.send_batch(items, write_to_pq=False)
        assert len(result.Outputs) == 5
        for output in result.Outputs:
            assert len(output.Message[0].Content) > 0

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            reader.ensure_no_messages()
