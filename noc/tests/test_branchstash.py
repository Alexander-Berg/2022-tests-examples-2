from tests import mock_subprocess
from tests import utils


class TestBranchstash(mock_subprocess.MockedSubprocessTestCase):

    def test_has_modified_files(self):
        """Проверяет stash при наличии изменённых файлов."""
        utils.run_branchstash()

    def test_no_modified_files(self):
        """Проверяет ситуацию, когда нет изменённых файлов."""
        utils.run_branchstash()

    def test_exceed_branch_limit(self):
        """Проверяет stash при количестве shash-веток, превышающем ROLLBACK_BRANCH_LIMIT."""
        utils.run_branchstash()
