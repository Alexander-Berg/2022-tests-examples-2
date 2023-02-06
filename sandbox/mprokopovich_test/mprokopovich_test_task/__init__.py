import logging
from sandbox import sdk2

class MprokopovichTestResource(sdk2.Resource):
    releasable = True
    releasers = ["robot-lets-message"]
    ttl = 30
    executable = True

class MprokopovichTestTask(sdk2.Task):
    def on_execute(self):
        logging.info("Hello, world!")
