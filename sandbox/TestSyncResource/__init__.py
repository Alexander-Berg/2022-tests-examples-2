import logging
import os

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk.paths import copy_path, make_folder


class TestSyncResource(SandboxTask):
    type = 'TEST_SYNC_RESOURCE'

    class Rid(parameters.SandboxStringParameter):
        name = 'resource_id'
        description = 'Resource ID to download'
        default_value = ''
        multiline = True

    input_parameters = [Rid]

    def download_resource(self, resource_id, download_path):
        resource_local_path = channel.task.sync_resource(resource_id)
        copy_path(resource_local_path, download_path)

    def on_execute(self):
        logging.info(self.ctx)

        dir_name = "SYNC_RESOURCE_DIR"
        make_folder(dir_name)

        rid = int(self.ctx['resource_id'])
        logging.debug("Downloading resource....{}".format(rid))
        self.download_resource(rid, os.path.join(dir_name, 'test'))


__Task__ = TestSyncResource
