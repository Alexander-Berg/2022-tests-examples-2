import logging

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp
import sandbox.common.types.client as ctc


class SdcTestDockerRunAlpine(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.CUSTOM_SDC

    def on_execute(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("docker_run")) as pl:
            exitcode = sp.Popen(
                "docker run --rm alpine sh -c 'id; uname -a'",
                shell=True, stdout=pl.stdout, stderr=sp.STDOUT,
            ).wait()

        self.set_info('Exitcode {}'.format(exitcode))
        if exitcode != 0:
            raise Exception('Error running command {}'.format(exitcode))
