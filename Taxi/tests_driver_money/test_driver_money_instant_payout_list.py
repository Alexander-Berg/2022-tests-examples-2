import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
async def test_driver_money_instant_payout_list(
        taxi_driver_money, load_json, mockserver,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/list',
    )
    def _mock_instant_payouts_list(_):
        return {
            'payouts': [
                {
                    'id': '00000000-0001-0001-0001-000000000000',
                    'created_at': '2020-01-01T12:00:00+00:00',
                    'amount': '100.01',
                    'status': 'succeeded',
                },
                {
                    'id': '00000000-0001-0001-0002-000000000000',
                    'created_at': '2020-01-02T12:00:00+00:00',
                    'amount': '200.02',
                    'status': 'failed',
                },
                {
                    'id': '00000000-0001-0001-0003-000000000000',
                    'created_at': '2020-01-03T12:00:00+00:00',
                    'amount': '300.03',
                    'status': 'in_progress',
                },
            ],
        }

    response = await taxi_driver_money.post(
        'driver/v1/driver-money/v1/instant-payouts/list',
        json={'tz': 'Europe/Moscow'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
