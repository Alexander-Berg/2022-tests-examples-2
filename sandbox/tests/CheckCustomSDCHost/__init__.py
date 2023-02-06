import logging
import socket

from sandbox import sdk2
import sandbox.common.types.client as ctc


class TestCustomSDCTagDispatch(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.CUSTOM_SDC

    def on_execute(self):
        hostname = socket.gethostbyaddr(socket.gethostname())[0]
        if hostname.endswith('.sdc.yandex.net'):
            self.set_info('OK')
        else:
            logging.info('hostname %r', hostname)
            self.set_info('Fail')
