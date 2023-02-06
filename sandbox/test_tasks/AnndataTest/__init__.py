import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class AnndataTest(TestlibCommonTask):
    """ AnnData test for TestEnv."""
    test_name = 'anndata-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Anndata.InputTables, required=True)

        factors_config = sdk2.parameters.Resource('Factors config', default_value=TestlibSbrIds.Anndata.FactorsConfig, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        self.other_resources = [
            self.Parameters.factors_config
        ]

        from anndata_test import TestAnndata
        self.test = TestAnndata
