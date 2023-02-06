import pytest

URL = '/api/v1/reports/payouts/statuses'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}

STATUSES = [
    {
        'fleet_status': 'created',
        'oebs_statuses': ['CREATED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_created',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'transmitted',
        'oebs_statuses': ['TRANSMITTED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_transmitted',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'paid',
        'oebs_statuses': ['CONFIRMED', 'RECONCILED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_paid',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'canceled',
        'oebs_statuses': ['VOID', 'DEFERRED', 'RETURNED'],
        'selected': False,
        'tanker_key': {
            'key': 'status_canceled',
            'keyset': 'opteum_page_report_payouts',
        },
    },
]


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES)
@pytest.mark.translations(
    opteum_page_report_payouts={
        'status_created': {'ru': 'Сформировано'},
        'status_transmitted': {'ru': 'Отправлено в банк'},
        'status_paid': {'ru': 'Выплачено'},
        'status_canceled': {'ru': 'Отмена'},
    },
)
async def test_success(web_app_client):
    response = await web_app_client.post(URL, headers=HEADERS)

    assert response.status == 200, await response.json() == {
        'statuses': [
            {'id': 'created', 'name': 'Сформировано'},
            {'id': 'transmitted', 'name': 'Отправлено в банк'},
            {'id': 'paid', 'name': 'Выплачено'},
            {'id': 'canceled', 'name': 'Отмена'},
        ],
        'default': ['created', 'transmitted', 'paid'],
    }


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_STATUSES=[])
async def test_empty_config(web_app_client):
    response = await web_app_client.post(URL, headers=HEADERS)
    assert response.status == 500
