from tests import mock_subprocess
from tests import utils


class TestHostname(mock_subprocess.MockedSubprocessTestCase):

    def test_commit(self):
        """Проверяет установку hostname в ядре при коммите /etc/hostname."""
        utils.run_commit_reload()

    def test_rollback(self):
        """Проверяет установку hostname в ядре при откате /etc/hostname.

        Файл /etc/hostname откатывается на предыдущее значение, и на это же значение
        устанавливается hostname в ядре
        """
        utils.run_rollback(commit="0000001000000000000000000000000000000000")
