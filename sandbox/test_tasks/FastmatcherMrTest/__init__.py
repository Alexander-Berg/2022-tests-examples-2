import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class FastmatcherMrTest(TestlibCommonTask):
    """ FastmatcherMr test for TestEnv."""
    test_name = 'fastmatcher-mr-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Fastmatcher.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from fastmatcher_test import TestFastmatcher
        self.test = TestFastmatcher
