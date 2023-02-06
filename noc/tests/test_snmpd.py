from tests import mock_subprocess
from tests import utils


class TestSnmpd(mock_subprocess.MockedSubprocessTestCase):

    def test_reload_cuml3(self):
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        utils.run_commit_reload()

    def test_reload_switchdev(self):
        utils.run_commit_reload()
