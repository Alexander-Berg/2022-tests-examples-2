import logging
from sandbox import sdk2


class MyTestTask(sdk2.Task):
    def on_execute(self):
        logging.info("Hello, world!", self.i)
