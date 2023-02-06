from tests import mock_subprocess
from tests import utils


class TestNsswitch(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет изменение `/etc/nsswitch.conf`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/nsswitch.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.nsswitch_conf.WhiteboxNsswitch`

        В этом тесте важно убедиться, что в конце выполняется
        команда "service ssh reload"
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/nsswitch.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.nsswitch_conf.WhiteboxNsswitch`

        В этом тесте важно убедиться, что в конце выполняется
        команда "service ssh reload"
        """
        utils.run_commit_reload()

    def test_reload_switchdev(self):
        """Проверяет изменение `/etc/nsswitch.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.nsswitch_conf.WhiteboxNsswitch`

        В этом тесте важно убедиться, что в конце выполняется
        команда "service ssh reload"
        """
        utils.run_commit_reload()
