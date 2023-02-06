from tests import mock_subprocess
from tests import utils


class TestSxEcmpHash(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `sx-ecmp-hash.service` на Cumulus/Mellanox."""

    def test_cuml3(self):
        """Проверяет изменение файла `/etc/sx_ecmp_hash.conf`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.load_balancing.CumulusLoadBalance`

        На Cumulus версии 3 установлен deb-пакет `sx-ecmp-hash`, который имеет
        конфиг в файле `/etc/sx_ecmp_hash.conf`

        Для этого конфига dpkg правильно определяет принадлежность пакету:

        ```
        tacacs15@vla2-8s75:~$ dpkg -S /etc/sx_ecmp_hash.conf
        sx-ecmp-hash: /etc/sx_ecmp_hash.conf
        ```
        """
        utils.run_commit_reload()

    def test_cuml4(self):
        """Проверяет изменение файла `/etc/sx_ecmp_hash/sx_ecmp_hash.json`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.load_balancing.CumulusLoadBalance`

        На Cumulus версии 4 установлен deb-пакет `sx-ecmp-hash`, который имеет
        конфиг в файле `/etc/sx_ecmp_hash/sx_ecmp_hash.json`

        Для этого конфига dpkg правильно определяет принадлежность пакету:

        ```
        tacacs15@vla1-9s3:mgmt:~$ dpkg -S /etc/sx_ecmp_hash/sx_ecmp_hash.json
        sx-ecmp-hash: /etc/sx_ecmp_hash/sx_ecmp_hash.json
        ```
        """
        utils.run_commit_reload()
