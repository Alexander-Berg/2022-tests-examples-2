from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask
from sandbox import sdk2


class MetadocTest(CommonIndexTask):
    """ Metadoc test for TestEnv."""
    test_name = 'metadoc-test'

    class Requirements(sdk2.Task.Requirements):
        disk_space = 120 * 1024
        ram = 52 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(CommonIndexTask.Parameters):
        inputdoc = sdk2.parameters.Resource('Inputdoc table', required=False)
        remapindex = sdk2.parameters.Resource('Remap index table', required=False)

    def _prepare(self):
        super(MetadocTest, self)._prepare()
        # We don't need all tables
        self.yt_table_resources = []

        self.add_resource("INPUTDOC_TEST", self.Parameters.inputdoc)
        self.add_resource("REMAPINDEX_TEST", self.Parameters.remapindex)

        from metadoc_test import TestMetadoc
        self.test = TestMetadoc
