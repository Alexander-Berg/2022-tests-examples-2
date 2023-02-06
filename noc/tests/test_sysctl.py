from tests import mock_subprocess
from tests import utils


class TestSysctl(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет релоад `systemd-sysctl.service` при изменении `/etc/sysctl.d`."""

    def test_hash_cuml3(self):
        """Проверяет изменение файла `99-hash.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.sysctl.WhiteboxSysctl`
        """
        utils.run_commit_reload()

    def test_hash_cuml4(self):
        """Проверяет изменение файла `99-hash.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.sysctl.WhiteboxSysctl`
        """
        utils.run_commit_reload()

    def test_hash_switchdev(self):
        """Проверяет изменение файла `99-hash.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.sysctl.WhiteboxSysctl`
        """
        utils.run_commit_reload()
