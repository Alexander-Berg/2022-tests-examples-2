from sandbox.projects.images.robot.tests.CommonIndexTask import CommonIndexTask


class ShardpreparerTest(CommonIndexTask):
    """ Shardpreparer test for TestEnv."""
    test_name = 'shardpreparer-test'

    def _prepare(self):
        super(ShardpreparerTest, self)._prepare()
        from shardpreparer_test import TestShardpreparer
        self.test = TestShardpreparer
