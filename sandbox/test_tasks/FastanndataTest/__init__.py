import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class FastanndataTest(TestlibCommonTask):
    """ FastAnnData test for TestEnv."""
    test_name = 'fastanndata-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Fastanndata.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from fastanndata_test import TestFastanndata
        self.test = TestFastanndata
