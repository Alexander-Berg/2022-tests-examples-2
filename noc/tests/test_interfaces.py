from tests import mock_subprocess
from tests import utils


class TestInterfaces(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет вызов ifreload при изменении network-interfaces.

    Отслеживаются изменения в:
        - `/etc/network/interfaces`
        - `/etc/network/interfaces.d`
    """

    def test_interfaces_file_cuml3(self):
        """Проверяет изменение файла `/etc/network/interfaces`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.interfaces.WhiteboxInterfaces`
        """
        utils.run_commit_reload()

    def test_interfaces_file_cuml4(self):
        """Проверяет изменение файла `/etc/network/interfaces`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.interfaces.WhiteboxInterfaces`
        """
        utils.run_commit_reload()

    def test_interfaces_file_switchdev(self):
        """Проверяет изменение файла `/etc/network/interfaces`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.interfaces.WhiteboxInterfaces`
        """
        utils.run_commit_reload()
