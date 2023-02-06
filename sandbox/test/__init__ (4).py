import logging
from sandbox import sdk2


class RtecTestTask(sdk2.Task):

    def on_execute(self):
        logging.info("Hello, world!")
