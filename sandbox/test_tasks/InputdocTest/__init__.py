from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class InputdocTest(CommonIndexTask):
    """ InputDoc test for TestEnv."""
    test_name = 'inputdoc-test'

    def _prepare(self):
        super(InputdocTest, self)._prepare()
        from inputdoc_test import TestInputdoc
        self.test = TestInputdoc
