import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class LinkdbTest(TestlibCommonTask):
    """ LinkDB test for TestEnv."""
    test_name = 'linkdb-test'

    class Parameters(TestlibCommonTask.Parameters):
        rthub_links_tables = sdk2.parameters.Resource('RTHubLinks Tables', default_value=TestlibSbrIds.LinkDB.RTHubLinks, required=True)
        urldb_tables = sdk2.parameters.Resource('Urldb Tables', required=False)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.rthub_links_tables
        ]

        self.yt_table_bin_resources = []
        self.add_resource("URLDB_TEST", self.Parameters.urldb_tables)

        from linkdb_test import TestLinkdb
        self.test = TestLinkdb
