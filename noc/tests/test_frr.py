from tests import mock_subprocess
from tests import utils


class TestFrr(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `ann-copp-svc.service`."""

    def test_reload_cuml3(self):
        """Проверяет изменение `/etc/frr/frr.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.frr.WhiteboxFrr`

        Хаки релоада frr находятся в пакете frr-overrides в репозитории
        https://noc-gitlab.yandex-team.ru/nocdev/linuxswitch/
        """
        utils.run_commit_reload()

    def test_reload_cuml4(self):
        """Проверяет изменение `/etc/frr/frr.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.frr.WhiteboxFrr`

        Хаки релоада frr находятся в пакете frr-overrides в репозитории
        https://noc-gitlab.yandex-team.ru/nocdev/linuxswitch/
        """
        utils.run_commit_reload()

    def test_reload_switchdev(self):
        """Проверяет изменение `/etc/frr/frr.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.frr.WhiteboxFrr`

        Хаки релоада frr находятся в пакете frr-overrides в репозитории
        https://noc-gitlab.yandex-team.ru/nocdev/linuxswitch/
        """
        utils.run_commit_reload()
