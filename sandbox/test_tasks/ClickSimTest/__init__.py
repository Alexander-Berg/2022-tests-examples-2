import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class ClickSimTest(TestlibCommonTask):
    """ ClickSim test for TestEnv."""
    test_name = 'click-sim-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.ClickSim.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from click_sim_test import TestClickSim
        self.test = TestClickSim
