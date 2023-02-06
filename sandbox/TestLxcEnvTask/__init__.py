from sandbox import sdk2
import sandbox.common.types.misc as ctm
import logging


class TestLxcEnvTask(sdk2.Task):
    """ An empty task, which does nothing except of logging 'Hello, World!'. """
    kill_timeout = 60 * 60

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        my_name = sdk2.parameters.String("Your name", default="Anonymous", required=True)
        branch = sdk2.parameters.String("Branch ref", default="master", required=True)
        _container = sdk2.parameters.Container(
            "Environment container", default_value=275193263,
            required=True
        )

    def on_execute(self):
        logging.info("Hello, World from task!")
