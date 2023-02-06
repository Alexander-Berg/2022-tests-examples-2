import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.images.robot.tests.CommonTask import TestlibCommonTask


class ImagedbTest(TestlibCommonTask):
    """ ImageDB test for TestEnv."""
    test_name = 'imagedb-test'

    class Parameters(TestlibCommonTask.Parameters):
        ImgKiwiExport = sdk2.parameters.Resource('ImgKiwiExport', default_value=TestlibSbrIds.Imagedb.ImgKiwiExport, required=True)
        UrlDB = sdk2.parameters.Resource('UrlDB', required=False)

    def _prepare(self):
        self.yt_table_resources = [
            self.Parameters.ImgKiwiExport
        ]

        self.yt_table_bin_resources = []
        self.add_resource("URLDB_TEST", self.Parameters.UrlDB)

        from imagedb_test import TestImagedb
        self.test = TestImagedb
