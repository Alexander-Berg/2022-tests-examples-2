from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class RemapindexTest(CommonIndexTask):
    """ Remapindex test for TestEnv."""
    test_name = 'remapindex-test'

    def _prepare(self):
        super(RemapindexTest, self)._prepare()
        from remapindex_test import TestRemapindex
        self.test = TestRemapindex
