from tests import mock_subprocess
from tests import utils


class TestAnnHostnameSvc(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `ann-hostname-svc.service`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/ann/hostname`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.hostname.WBHostname`
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/ann/hostname`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.hostname.WBHostname`
        """
        utils.run_commit_reload()
