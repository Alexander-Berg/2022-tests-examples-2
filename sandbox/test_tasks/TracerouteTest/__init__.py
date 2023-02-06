import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class TracerouteTest(TestlibCommonTask):
    """ TraceRoute test for TestEnv."""
    test_name = 'traceroute-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Traceroute.InputTables, required=True)

        urlDbTables = sdk2.parameters.Resource('Input UrlDb Tables', required=False)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        self.yt_table_bin_resources = []
        self.add_resource("URLDB_TEST", self.Parameters.urlDbTables)

        from traceroute_test import TestTraceroute
        self.test = TestTraceroute
