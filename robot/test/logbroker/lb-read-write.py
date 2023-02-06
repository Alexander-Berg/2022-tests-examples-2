import logging
import subprocess

import yatest.common

from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import PQStreamingAPI, ConsumerMessageType
from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import ProducerConfigurator, ConsumerConfigurator

from robot.rthub.protos.config_pb2 import TConfig
import google.protobuf.text_format as pbtext
from robot.rthub.test.echoitem.echo_item_pb2 import TEchoItem

import os
import shutil

logger = logging.getLogger()

TIMEOUT = 10


def test_lb():
    port = int(os.getenv('LOGBROKER_PORT'))

    dc_name = "dc1"  # lb's recipe default dc

    racc = "racc"
    wacc = "wacc"
    itopic = "itopic"
    otopic = "otopic"

    itopic_name = racc + "/" + itopic
    otopic_name = wacc + "/" + otopic

    api = PQStreamingAPI("localhost", port)
    api.start().result(timeout=TIMEOUT)

    p = yatest.common.work_path("test-protos")
    os.mkdir(p)
    os.makedirs(p + "/google/protobuf")
    shutil.copy2(yatest.common.source_path("contrib/libs/protobuf/src/google/protobuf/descriptor.proto"), p + "/google/protobuf/descriptor.proto")
    os.makedirs(p + "/echoitem")
    shutil.copy2(yatest.common.source_path("robot/rthub/test/echoitem/echo_item.proto"), p + "/echoitem/echo_item.proto")

    p = yatest.common.work_path("test-queries")
    os.mkdir(p)
    shutil.copy2(yatest.common.source_path("robot/rthub/test/echoitem/Echo.sql"), p + "/")

    p = yatest.common.work_path("test-udfs")
    os.mkdir(p)

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    config = TConfig()
    with open(yatest.common.source_path("robot/rthub/test/logbroker/local-lb.pb.txt"), 'r') as f:
        pbtext.Parse(f.read(), config)

    config.Channel[0].Input[0].Source.Server = "localhost"
    config.Channel[0].Input[0].Source.DataPort = port
    config.Channel[0].Input[0].Source.ControlPort = port

    config.Channel[0].Output[0].Queue[0].Server = "localhost"
    config.Channel[0].Output[0].Queue[0].DataPort = port
    config.Channel[0].Output[0].Queue[0].ControlPort = port

    with open("local-lb.pb.txt", 'w') as f:
        f.write(pbtext.MessageToString(config))

    rthub_cmd = [
        rthub_bin,
        "--config", "local-lb.pb.txt",
        "-r",
    ]

    rthub = subprocess.Popen(
        rthub_cmd
    )

    text = "ABCD"

    witem = TEchoItem()
    witem.Data = text

    # write msg

    pconfigurator = ProducerConfigurator(itopic_name, "test_src")
    writer = api.create_producer(pconfigurator)
    result = writer.start().result(timeout=TIMEOUT)
    assert result.HasField("init")

    write_res = writer.write(1, witem.SerializeToString()).result(timeout=TIMEOUT)
    assert write_res.HasField("ack")

    # read msg

    cconfigurator = ConsumerConfigurator(otopic_name, "test_client")
    reader = api.create_consumer(cconfigurator)
    result = reader.start().result(timeout=TIMEOUT)
    assert result.HasField("init")

    event = reader.next_event().result(timeout=TIMEOUT)
    assert event.type == ConsumerMessageType.MSG_DATA
    batch = event.message.data.message_batch[0]
    full_otopic = "rt3.{}--{}--{}".format(dc_name, wacc, otopic)
    assert batch.topic == full_otopic

    ritem = TEchoItem()
    ritem.ParseFromString(batch.message[0].data)
    assert ritem.Data == "<" + text + ">"

    rthub.terminate()
