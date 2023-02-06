import datetime

import pytest

FIRST_DAY = datetime.datetime(2016, 3, 1, 0, 0, 0)
LAST_DAY = datetime.datetime(2016, 4, 1, 0, 0, 0)

EXPECTED_REPORTS = [
    (
        '<Journal client="client1_billing" contract="client1_contract" '
        'period_finish="01.04.16 00:00:00" period_start="01.03.16 00:00:00" '
        'service="Яндекс.Такси">'
        '<Order><ID text="order2"/>'
        '<Number text="order2"/>'
        '<Date text="19.03.2016"/>'
        '<Time text="15:35"/>'
        '<Originator text="Zoe"/>'
        '<Passenger text="Zoe"/>'
        '<AddressFrom text="Россия, Москва, улица Льва Толстого, 16"/>'
        '<AddressTo text="-"/><Slip text="order2"/>'
        '<Cost text="790.60"/>'
        '</Order>'
        '<Order><ID text="order1"/>'
        '<Number text="order1"/>'
        '<Date text="25.03.2016"/>'
        '<Time text="00:37"/>'
        '<Originator text="Zoe"/>'
        '<Passenger text="Zoe"/>'
        '<AddressFrom text="Россия, Москва, улица Тимура Фрунзе, 11к8"/>'
        '<AddressTo text="Россия, Москва, Большая Никитская улица, 13"/>'
        '<Slip text="order1"/>'
        '<Cost text="637.20"/>'
        '</Order>'
        '</Journal>'
    ),
    (
        '<Journal client="client2_billing" contract="client2_contract" '
        'period_finish="01.04.16 00:00:00" period_start="01.03.16 00:00:00" '
        'service="Яндекс.Такси">'
        '<Order><ID text="order3"/>'
        '<Number text="order3"/>'
        '<Date text="21.03.2016"/>'
        '<Time text="15:28"/>'
        '<Originator text="Moe"/>'
        '<Passenger text="Moe"/>'
        '<AddressFrom text="Россия, Москва, улица Льва Толстого, 16"/>'
        '<AddressTo text="Россия, Москва, Большая Никитская улица, 13"/>'
        '<Slip text="order3"/>'
        '<Cost text="790.60"/>'
        '</Order>'
        '</Journal>'
    ),
]


@pytest.mark.config(
    CORP_XML_CONTRACT_IDS=['client1_contract', 'client2_contract'],
)
async def test_xml_report(
        db, mongodb_init, simple_secdist, patch, monkeypatch,
):

    from taxi_corp import cron_run

    @patch('taxi_corp.stuff.xml_report._calculate_period')
    def _calculate_period(*args, **kwargs):
        return FIRST_DAY, LAST_DAY

    @patch('taxi_corp.stuff.xml_report.save_files')
    async def _save_file(*args, **kwargs):
        pass

    @patch('taxi_corp.stuff.xml_report.send_xml_reports')
    async def _send_xml(app, report, start):
        reports = [rep.decode() for rep, contract in report]
        assert reports == EXPECTED_REPORTS

    module = 'taxi_corp.stuff.xml_report'
    await cron_run.main([module, '-t', '0'])
