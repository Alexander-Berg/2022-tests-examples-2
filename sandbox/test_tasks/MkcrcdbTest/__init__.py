import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class MkcrcdbTest(TestlibCommonTask):
    """ MkCrcDB test for TestEnv."""
    test_name = 'mkcrcdb-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Mkcrcdb.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from mkcrcdb_test import TestMkcrcdb
        self.test = TestMkcrcdb
