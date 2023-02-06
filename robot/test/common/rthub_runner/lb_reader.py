import gzip
import logging
import concurrent.futures
import six

from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import PQStreamingAPI, ConsumerConfigurator, \
    ConsumerMessageType, WriterCodec

logger = logging.getLogger("lb_reader")


class LBReader(object):
    TIMEOUT = 10

    def __init__(self, port, topic):
        self.api = PQStreamingAPI("localhost", port)
        self.api.start().result(timeout=self.TIMEOUT)

        configurator = ConsumerConfigurator(topic, "test_client")
        self.consumer = self.api.create_consumer(configurator)
        result = self.consumer.start().result(timeout=self.TIMEOUT)
        assert result.HasField("init")

    def read_next_messages(self, count, timeout=None):
        remaining_count = count
        last_received_cookie = None
        last_committed_cookie = None
        data = []
        while remaining_count > 0 or last_received_cookie != last_committed_cookie:
            result = self.consumer.next_event().result(timeout=timeout or self.TIMEOUT)

            if result.type == ConsumerMessageType.MSG_DATA:
                for batch in result.message.data.message_batch:
                    for message in batch.message:
                        if remaining_count > 0:
                            data.append(self._decompress(message))
                            remaining_count -= 1
                            logger.info("Received message from offset {} with seq_no {}".format(message.offset,
                                                                                                message.meta.seq_no))
                            if remaining_count == 0:
                                self.consumer.reads_done()
                                break

                self.consumer.commit(result.message.data.cookie)
                last_received_cookie = result.message.data.cookie
            else:
                assert result.type == ConsumerMessageType.MSG_COMMIT
                last_committed_cookie = result.message.commit.cookie[-1]

        return data

    def ensure_no_messages(self, timeout=2):
        try:
            self.read_next_messages(1, timeout)
            raise Exception("Topic contains items unexpectedly")
        except concurrent.futures.TimeoutError:
            return

    def _decompress(self, message):
        if message.meta.codec == WriterCodec.GZIP:
            f = six.BytesIO()
            f.write(message.data)
            f.seek(0)

            df = gzip.GzipFile(fileobj=f, mode='rb')
            return df.read()

        assert message.meta.codec == WriterCodec.RAW
        return message.data

    def close(self):
        self.consumer.stop()
        self.api.stop()
