from tests import mock_subprocess
from tests import utils


class TestAnnCoppSvc(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `ann-copp-svc.service`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/ann/copp.sh`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.copp.WhiteboxCopp`
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/ann/copp.sh`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.copp.WhiteboxCopp`
        """
        utils.run_commit_reload()
