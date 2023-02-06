import mock
from sandbox.tasklet.sidecars.resource_manager.handlers import yt as yt_handler


class TestYtHandler:
    def test_download_resource(
        self, patch_handlers, api_session_class, agentr_session_class, sample_file, full_resource1_with_mds
    ):
        filename, _, filedata = sample_file
        resource_handler = yt_handler.YtHandler("TEST_TOKEN", mock.MagicMock())
        downloaded_filename = resource_handler.download_resource(full_resource1_with_mds["id"])
        assert downloaded_filename.endswith(filename)
        with open(downloaded_filename, "rb") as f:
            downloaded_filedata = f.read()
            assert downloaded_filedata == filedata, "{}\n{}".format(downloaded_filedata, filedata)
