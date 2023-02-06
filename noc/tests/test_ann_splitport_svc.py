from tests import mock_subprocess
from tests import utils


class TestAnnSplitportSvc(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `ann-splitport-svc.service`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/ann/splitport.sh`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.portsplit.WhiteboxSplit`
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/ann/splitport.sh`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.portsplit.WhiteboxSplit`
        """
        utils.run_commit_reload()
