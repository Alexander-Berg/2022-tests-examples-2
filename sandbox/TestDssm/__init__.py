import logging
from sandbox import sdk2
from sandbox.common.types import resource as ctr
from sandbox.projects.resource_types import OTHER_RESOURCE, SEARCH_DATABASE, DYNAMIC_MODELS_ARCHIVE_BASE


class TestDssm(sdk2.Task):
    """ An empty task, which does nothing except of logging 'Hello, World!'. """

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3600

        test_binary = sdk2.parameters.Resource(
            'Test binary',
            resource_type=OTHER_RESOURCE,
            state=(ctr.State.READY,),
            required=True
        )
        shard = sdk2.parameters.Resource(
            'Basesearch shard',
            resource_type=SEARCH_DATABASE,
            state=(ctr.State.READY,),
            required=True
        )
        models_archive = sdk2.parameters.Resource(
            'Models archive',
            resource_type=DYNAMIC_MODELS_ARCHIVE_BASE,
            state=(ctr.State.READY,),
            required=True
        )

    def on_execute(self):
        test_binary_path = sdk2.ResourceData(self.Parameters.test_binary).path
        shard_path = sdk2.ResourceData(self.Parameters.shard).path
        models_archive_path = sdk2.ResourceData(self.Parameters.models_archive).path

        logging.info(test_binary_path)
        logging.info(shard_path)
        logging.info(models_archive_path)

        import subprocess
        out, _ = subprocess.Popen([str(test_binary_path), str(shard_path), str(models_archive_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        logging.info(out)

        self.set_info(out)
