from tests import mock_subprocess
from tests import utils


class TestRollback(mock_subprocess.MockedSubprocessTestCase):

    def test_usual(self):
        """Проверяет rollback."""
        utils.run_rollback(commit="0000001000000000000000000000000000000000")

    def test_not_master_branch(self):
        """Проверяет ситуацию, когда текущая ветка не master."""
        with self.assertRaises(Exception) as err:
            utils.run_rollback(commit="0000001000000000000000000000000000000000")
        exc = err.exception
        self.assertEqual(str(exc), "not master branch")

    def test_exceed_branch_limit(self):
        """Проверяет rollback при количестве rollback-веток, превышающем ROLLBACK_BRANCH_LIMIT."""
        utils.run_rollback(commit="0000001000000000000000000000000000000000")
