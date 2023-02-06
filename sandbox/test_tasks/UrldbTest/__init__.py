import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class UrldbTest(TestlibCommonTask):
    """ Urldb test for TestEnv."""
    test_name = 'urldb-test'

    class Parameters(TestlibCommonTask.Parameters):
        RTHubLinks = sdk2.parameters.Resource('RTHubLinks', default_value=TestlibSbrIds.Urldb.RTHubLinks, required=True)
        HostDB = sdk2.parameters.Resource('HostDB table', required=False)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.RTHubLinks,
        ]

        self.yt_table_bin_resources = []
        self.add_resource("HOSTDB_TEST", self.Parameters.HostDB)

        from urldb_test import TestUrldb
        self.test = TestUrldb
