from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class ImagesIndexTest(CommonIndexTask):
    """ End to end index test for TestEnv."""
    test_name = 'index-test'

    def _prepare(self):
        super(ImagesIndexTest, self)._prepare()

        from index_test import TestIndex
        self.test = TestIndex
