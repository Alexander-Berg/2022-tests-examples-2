from tests import mock_subprocess
from tests import utils


class TestCommitreload(mock_subprocess.MockedSubprocessTestCase):

    # def test_usual(self):
    #     """Проверяет commitreload."""
    #     utils.run_commit_reload()

    def test_not_master_branch(self):
        """Проверяет ситуацию, когда текущая ветка не master."""
        with self.assertRaises(Exception) as err:
            utils.run_commit_reload()
        exc = err.exception
        self.assertEqual(str(exc), "not master branch")

    def test_nothing_to_commit(self):
        """Проверяет ситуацию, когда изменений нет."""
        utils.run_commit_reload()
