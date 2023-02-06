import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class RtcvdupTest(TestlibCommonTask):
    """ RtCvdup test for TestEnv."""
    test_name = 'rtcvdup-test'

    class Parameters(TestlibCommonTask.Parameters):
        tables = sdk2.parameters.Resource('Input Tables', default_value=TestlibSbrIds.Rtcvdup.InputTables, required=True)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.tables
        ]

        from rtcvdup_test import TestRtcvdup
        self.test = TestRtcvdup
