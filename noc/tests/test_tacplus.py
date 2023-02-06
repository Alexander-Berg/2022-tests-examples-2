from tests import mock_subprocess
from tests import utils


class TestTacplus(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт TACACS+ (tacplus)."""

    def test_tacplus_servers_cuml3(self):
        """Проверяет изменение `/etc/tacplus_servers`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.tacacs_plus.WhiteboxTacacs`

        В этом тесте важно убедиться, что в конце выполняются
        команды:

        - sudo killall -HUP audisp-tacplus
        - sudo service ssh reload
        """
        utils.run_commit_reload()

    def test_tacplus_servers_cuml4(self):
        """Проверяет изменение `/etc/tacplus_servers`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.tacacs_plus.WhiteboxTacacs`

        В этом тесте важно убедиться, что в конце выполняются
        команды:

        - sudo killall -HUP audisp-tacplus
        - sudo service ssh reload
        """
        utils.run_commit_reload()

    def test_tacplus_servers_switchdev(self):
        """Проверяет изменение `/etc/tacplus_servers`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.tacacs_plus.WhiteboxTacacs`

        В этом тесте важно убедиться, что в конце выполняются
        команды:

        - sudo killall -HUP audisp-tacplus
        - sudo service ssh reload
        """
        utils.run_commit_reload()
