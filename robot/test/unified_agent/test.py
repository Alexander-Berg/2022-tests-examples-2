from contextlib import closing, contextmanager
import yatest.common
import logging
import os
from subprocess import Popen

from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.unified_agent.protos.traced_item_pb2 import TInputItem, TOutputItem
from robot.rthub.yql.generic_protos.trace_message_pb2 import TTraceMessage

logger = logging.getLogger('rthub_test_logger')


@contextmanager
def launch(config_file):

    ua_config_template = yatest.common.source_path('robot/rthub/test/unified_agent/unified_agent.yml')
    ua_config_path = "unified_agent.yml"

    with open(ua_config_template, 'r') as f:
        s = f.read()
    with open(ua_config_path, 'w') as f:
        f.write(s.replace("LOGBROKER_PORT", os.getenv("LOGBROKER_PORT")))

    unified_agent = yatest.common.build_path('logbroker/unified_agent/bin/unified_agent')
    ua = Popen([unified_agent, "--config", ua_config_path])

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/test/unified_agent/conf/{}'.format(config_file))
    proto_path = yatest.common.build_path('robot/rthub/test/unified_agent/full_protos')
    queries_path = yatest.common.source_path('robot/rthub/test/unified_agent/queries')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, None, None)
    rthub_runner.update_config(None, proto_path, None, None, queries_path, None)
    rthub_runner.save_config()

    logger.info('Launching RTHub...')
    try:
        rthub_runner.run_rthub(binary=False, as_daemon=True)
        yield rthub_runner
    finally:
        rthub_runner.stop_daemon()

    ua.terminate()


def test_message_trace():
    with launch('trace_config.pb.txt') as rthub_runner:

        item1 = TInputItem()
        item1.Text = 'text1'
        item1.Data = 'data1'
        item1.Mark = True

        item2 = TInputItem()
        item2.Text = 'text2'
        item2.Data = 'data2'
        item2.Mark = True
        f = item2.Keys.add()
        f.Key = "key1"
        f.Value = "value1"
        f = item2.Keys.add()
        f.Key = "key2"
        f.Value = "value2"
        f = item2.Keys.add()
        f.Key = "key3"
        f.Value = "value3"

        lb_writer = rthub_runner.create_lb_writer('racc/itopic')
        lb_writer.send_next_message(item1.SerializeToString())
        lb_writer.send_next_message(item2.SerializeToString())

        with closing(rthub_runner.create_lb_reader('wacc/otopic')) as reader:
            data = reader.read_next_messages(3)

        assert len(data) == 3

        result1 = TOutputItem()
        result1.ParseFromString(data[0])
        result2 = TOutputItem()
        result2.ParseFromString(data[1])
        result3 = TOutputItem()
        result3.ParseFromString(data[2])

        assert result1.Text == "text2"
        assert result1.Data == "data2"
        assert result1.Mark
        assert result1.Key == "key1"
        assert result1.Value == "value1"

        assert result2.Text == "text2"
        assert result2.Data == "data2"
        assert not result2.Mark
        assert result2.Key == "key2"
        assert result2.Value == "value2"

        assert result3.Text == "text2"
        assert result3.Data == "data2"
        assert result3.Mark
        assert result3.Key == "key3"
        assert result3.Value == "value3"

        with closing(rthub_runner.create_lb_reader('tacc/ttopic')) as reader:
            data = reader.read_next_messages(4)

        assert len(data) == 4

        trace1 = TTraceMessage()
        trace1.ParseFromString(data[0])
        trace2 = TTraceMessage()
        trace2.ParseFromString(data[1])
        trace3 = TTraceMessage()
        trace3.ParseFromString(data[2])
        trace4 = TTraceMessage()
        trace4.ParseFromString(data[3])

        assert trace1.YqlName == 'Transform'
        assert trace1.Direction == TTraceMessage.Input
        assert trace1.UserFormat == 'NRTHubTest.TInputItem'
        assert len(trace1.Fields) == 1
        assert trace1.Fields[0].FieldName == 'NRTHubTest.TInputItem.Text'
        assert trace1.Fields[0].Value == 'text1'

        assert trace2.YqlName == 'Transform'
        assert trace2.Direction == TTraceMessage.Input
        assert trace2.UserFormat == 'NRTHubTest.TInputItem'
        assert len(trace2.Fields) == 1
        assert trace2.Fields[0].FieldName == 'NRTHubTest.TInputItem.Text'
        assert trace2.Fields[0].Value == 'text2'

        assert trace3.YqlName == 'Transform'
        assert trace3.Direction == TTraceMessage.Output
        assert trace3.UserFormat == 'NRTHubTest.TOutputItem'
        assert len(trace3.Fields) == 3
        assert trace3.Fields[0].FieldName == 'NRTHubTest.TOutputItem.Text'
        assert trace3.Fields[0].Value == 'text2'
        assert trace3.Fields[1].FieldName == 'NRTHubTest.TOutputItem.Key'
        assert trace3.Fields[1].Value == 'key1'
        assert trace3.Fields[2].FieldName == 'NRTHubTest.TOutputItem.Value'
        assert trace3.Fields[2].Value == 'value1'

        assert trace4.YqlName == 'Transform'
        assert trace4.Direction == TTraceMessage.Output
        assert trace4.UserFormat == 'NRTHubTest.TOutputItem'
        assert len(trace4.Fields) == 3
        assert trace4.Fields[0].FieldName == 'NRTHubTest.TOutputItem.Text'
        assert trace4.Fields[0].Value == 'text2'
        assert trace4.Fields[1].FieldName == 'NRTHubTest.TOutputItem.Key'
        assert trace4.Fields[1].Value == 'key3'
        assert trace4.Fields[2].FieldName == 'NRTHubTest.TOutputItem.Value'
        assert trace4.Fields[2].Value == 'value3'
