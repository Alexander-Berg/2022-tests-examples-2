import sandbox.common.types.resource as ctr
import sandbox.common.types.task as ctt
import sandbox.sdk2 as sdk2

from sandbox.projects.resource_types import IMAGES_MR_INDEX_CONFIG
import sandbox.projects as proj
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class CommonIndexTask(TestlibCommonTask):
    """ Common Index test for TestEnv."""
    test_name = 'common-index-test'

    class Parameters(TestlibCommonTask.Parameters):
        crcdb = sdk2.parameters.Resource(
            'Crcdb input table', default_value=TestlibSbrIds.CommonIndexResources.CrcDB, required=True
        )

        mrconfig = sdk2.parameters.Resource('MRConfig', required=False)
        nnsim = sdk2.parameters.Resource(
            'nnsim-options.ini', default_value=TestlibSbrIds.CommonIndexResources.Nnsim, required=True
        )

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.crcdb
        ]

        self.other_resources = [
            self.Parameters.nnsim
        ]

        self.add_config(IMAGES_MR_INDEX_CONFIG, proj.GetImagesMrIndexConfig.__Task__.type, self.Parameters.mrconfig)

    def add_config(self, type_resource, task_type, resource):
        if not hasattr(self, "other_resources"):
            self.other_resources = []

        if not resource:
            task = sdk2.Task.find(
                sdk2.Task[task_type],
                status=ctt.Status.RELEASED,
                children=True,
                release_status=ctt.ReleaseStatus.STABLE
            ).first()

            resource = sdk2.Resource.find(
                task=task,
                type=type_resource,
                status=ctr.State.READY
            ).first()

        if resource:
            self.other_resources.append(resource)
