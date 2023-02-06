from tests import mock_subprocess
from tests import utils


class TestGrub(mock_subprocess.MockedSubprocessTestCase):

    def test_update_cuml3(self):
        utils.run_commit_reload()

    def test_update_cuml4(self):
        utils.run_commit_reload()

    def test_update_switchdev(self):
        utils.run_commit_reload()
