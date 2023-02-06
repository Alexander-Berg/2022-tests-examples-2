from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class PlannerTest(CommonIndexTask):
    """ Planner test for TestEnv."""
    test_name = 'planner-test'

    def _prepare(self):
        super(PlannerTest, self)._prepare()
        from planner_test import TestPlanner
        self.test = TestPlanner
