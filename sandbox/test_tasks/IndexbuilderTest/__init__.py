from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class IndexbuilderTest(CommonIndexTask):
    """ Indexbuilder test for TestEnv."""
    test_name = 'indexbuilder-test'

    def _prepare(self):
        super(IndexbuilderTest, self)._prepare()
        from indexbuilder_test import TestIndexbuilder
        self.test = TestIndexbuilder
