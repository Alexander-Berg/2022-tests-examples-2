from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask
from sandbox import sdk2


class SelectionrankTest(CommonIndexTask):
    """ SelectionRank test for TestEnv."""
    test_name = 'selectionrank-test'

    class Parameters(CommonIndexTask.Parameters):
        metadoc = sdk2.parameters.Resource('Metadoc table', required=False)

    def _prepare(self):
        super(SelectionrankTest, self)._prepare()
        # We don't need all tables
        self.yt_table_resources = []

        self.add_resource("METADOC_TEST", self.Parameters.metadoc)

        from selectionrank_test import TestSelectionrank
        self.test = TestSelectionrank
