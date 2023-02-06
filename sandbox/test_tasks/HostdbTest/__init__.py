import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class HostdbTest(TestlibCommonTask):
    """ HostDB test for TestEnv."""
    test_name = 'hostdb-test'

    class Parameters(TestlibCommonTask.Parameters):
        export = sdk2.parameters.Resource('Export Tables', default_value=TestlibSbrIds.Hostdb.Export, required=True)

        state = sdk2.parameters.Resource('State Tables', default_value=TestlibSbrIds.Hostdb.State, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.export,
            self.Parameters.state
        ]

        from hostdb_test import TestHostdb
        self.test = TestHostdb
