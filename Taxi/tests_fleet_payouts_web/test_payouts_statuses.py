import pytest

ENDPOINT = '/fleet/payouts-web/v1/payouts/statuses'

HEADERS = {
    'Accept-Language': 'ru,en;q=0.9,la;q=0.8',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
}

STATUSES = [
    {
        'fleet_status': 'created',
        'oebs_statuses': ['CREATED'],
        'selected': True,
        'tanker_key': 'status_created',
    },
    {
        'fleet_status': 'transmitted',
        'oebs_statuses': ['TRANSMITTED'],
        'selected': True,
        'tanker_key': 'status_transmitted',
    },
    {
        'fleet_status': 'paid',
        'oebs_statuses': ['CONFIRMED', 'RECONCILED'],
        'selected': True,
        'tanker_key': 'status_paid',
    },
    {
        'fleet_status': 'canceled',
        'oebs_statuses': ['VOID', 'DEFERRED', 'RETURNED'],
        'selected': False,
        'tanker_key': 'status_canceled',
    },
]


@pytest.mark.config(FLEET_PAYOUTS_WEB_PAYOUTS_STATUSES=STATUSES)
@pytest.mark.translations(
    opteum_page_report_payouts={
        'status_created': {'ru': 'Сформировано'},
        'status_transmitted': {'ru': 'Отправлено в банк'},
        'status_paid': {'ru': 'Выплачено'},
        'status_canceled': {'ru': 'Отмена'},
    },
)
async def test_success(taxi_fleet_payouts_web):
    response = await taxi_fleet_payouts_web.get(ENDPOINT, headers=HEADERS)

    assert response.status == 200, await response.json() == {
        'items': [
            {'id': 'created', 'name': 'Сформировано'},
            {'id': 'transmitted', 'name': 'Отправлено в банк'},
            {'id': 'paid', 'name': 'Выплачено'},
            {'id': 'canceled', 'name': 'Отмена'},
        ],
        'default': ['created', 'transmitted', 'paid'],
    }


@pytest.mark.config(FLEET_PAYOUTS_WEB_PAYOUTS_STATUSES=[])
async def test_empty_config(taxi_fleet_payouts_web):
    response = await taxi_fleet_payouts_web.get(ENDPOINT, headers=HEADERS)
    assert response.status == 500
