from tests import mock_subprocess
from tests import utils


class TestSwitchd(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет рестарт `switchd.service` на Cumulus."""

    def test_datapath_traffic_conf_cuml3(self):
        """Проверяет, что при изменении `/etc/cumulus/datapath/traffic.conf` ничего не происходит.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.traffic_conf.CumulusTraffic`

        В этом тесте важно увидеть, что ни один сервис не релоадится/не рестартится.

        По идее, должен быть рестарт сервиса switchd.service, но он ломает
        форвардинг, и для него нужно в будущем реализовать явное подтверждение,
        см: https://st.yandex-team.ru/NOCDEV-2724

        Коммент из Аннушки: [NOCDEV-2724] Deemed too spooky as is
        """
        utils.run_commit_reload()

    def test_datapath_traffic_conf_cuml4(self):
        """Проверяет, что при изменении `/etc/cumulus/datapath/traffic.conf` ничего не происходит.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.traffic_conf.CumulusTraffic`

        В этом тесте важно увидеть, что ни один сервис не релоадится/не рестартится.

        По идее, должен быть рестарт сервиса switchd.service, но он ломает
        форвардинг, и для него нужно в будущем реализовать явное подтверждение,
        см: https://st.yandex-team.ru/NOCDEV-2724

        Коммент из Аннушки: [NOCDEV-2724] Deemed too spooky as is
        """
        utils.run_commit_reload()
