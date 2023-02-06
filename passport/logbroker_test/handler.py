import logging
import os

from passport.backend.logbroker_client.core.handlers.protobuf import BaseProtobufHandler


log = logging.getLogger('logbroker')


class LogbrokerTestHandler(BaseProtobufHandler):
    def process_message(self, header, message):
        log.debug(
            '--MESSAGE pid={} id={} test_data={} submessage_int={} submessage_str={}'
            .format(
                os.getpid(),
                message.id,
                message.test_data,
                message.sub_message.int,
                message.sub_message.str,
            ),
        )
