import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class RimTest(TestlibCommonTask):
    """ Rim test for TestEnv."""
    test_name = 'rim-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Rim.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from rim_test import TestRim
        self.test = TestRim
