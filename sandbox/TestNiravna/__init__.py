import logging
from sandbox import sdk2


class WmsSupportTestNirvana(sdk2.Task):

    def on_execute(self):
        logging.info("Hello, world!")
