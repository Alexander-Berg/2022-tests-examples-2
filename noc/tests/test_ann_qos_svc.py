from tests import mock_subprocess
from tests import utils


class TestAnnQosSvc(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `ann-qos-svc.service`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/qos/remark.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.qos.WhiteboxQos`
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/qos/remark.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.qos.WhiteboxQos`
        """
        utils.run_commit_reload()
