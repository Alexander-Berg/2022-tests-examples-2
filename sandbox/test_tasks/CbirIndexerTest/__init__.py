from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask
from sandbox import sdk2


class CbirIndexerTest(CommonIndexTask):
    """ Cbir Indexer test for TestEnv."""
    test_name = 'cbir-indexer-test'

    class Parameters(CommonIndexTask.Parameters):
        cbir = sdk2.parameters.Resource('Cbir table', required=False)

    def _prepare(self):
        super(CbirIndexerTest, self)._prepare()
        # We don't need all tables
        self.yt_table_resources = []

        self.add_resource("CBIR_TEST", self.Parameters.cbir)

        from cbir_indexer_test import TestCbirIndexer
        self.test = TestCbirIndexer
