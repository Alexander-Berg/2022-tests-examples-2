import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class Userfactors2Test(TestlibCommonTask):
    """ UserFactors2 test for TestEnv."""
    test_name = 'userfactors2-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Userfactors2.InputTables, required=True)

        factors_config = sdk2.parameters.Resource('Factors config', default_value=TestlibSbrIds.Userfactors2.FactorsConfig, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        self.other_resources = [
            self.Parameters.factors_config
        ]

        from userfactors2_test import TestUserfactors2
        self.test = TestUserfactors2
