from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class CbirTest(CommonIndexTask):
    """ Cbir test for TestEnv."""
    test_name = 'cbir-test'

    def _prepare(self):
        super(CbirTest, self)._prepare()
        from cbir_test import TestCbir
        self.test = TestCbir
