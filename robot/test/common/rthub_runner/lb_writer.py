import kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api as pqlib
from kikimr.public.sdk.python.persqueue.errors import SessionFailureResult

import logging

logger = logging.getLogger("lb_writer")


class LBWriter(object):
    def __init__(self, port, topic):
        self.api = pqlib.PQStreamingAPI("localhost", port)
        self.api.start().result(timeout=10)
        source_id = "lb_writer-{topic}".format(topic=topic)
        configurator = pqlib.ProducerConfigurator(topic, source_id)
        self.producer = self.api.create_producer(configurator)
        start_result = self.producer.start().result(timeout=10)
        self.max_seq_no = None

        if isinstance(start_result, SessionFailureResult):
            raise RuntimeError("Error occurred on start of producer: {}, port: {}".format(start_result, port))

        if not start_result.HasField("init"):
            raise RuntimeError("Unexpected producer start result from server: {}, port: {}".format(start_result, port))

        logger.info("Producer start result was: {}".format(start_result))
        self.max_seq_no = start_result.init.max_seq_no

        logger.info("Producer started, topic: {}, port: {}".format(topic, port))

    def send_next_message(self, message, codec=pqlib.WriterCodec.RAW):
        self.max_seq_no += 1
        response = self.producer.write(self.max_seq_no, data=message, codec=codec)
        write_result = response.result(timeout=10)
        if not write_result.HasField("ack"):
            raise RuntimeError("Message write failed with error {}".format(write_result))

    def send_next_messages(self, messages, codec=pqlib.WriterCodec.RAW):
        for message in messages:
            self.send_next_message(message, codec)

    def stop(self):
        self.producer.stop()
        self.api.stop()
