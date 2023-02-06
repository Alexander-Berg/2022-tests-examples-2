import pytest


@pytest.mark.config(
    FLEET_RENT_CHARGING_AMOUNT_LIMITS={
        'lower_limit': '5.00',
        'upper_limit': '100000.00',
    },
)
async def test_ok(web_app_client, driver_auth_headers, patch):
    response = await web_app_client.get(
        '/fleet/rent/v1/park/rents/amount-limits',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id5',
            'X-Real-IP': '127.0.0.1',
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {
        'lower_limit': '5.00',
        'upper_limit': '100000.00',
    }
