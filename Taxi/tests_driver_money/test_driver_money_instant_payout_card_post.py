import pytest

PARAMS = [
    (None, None, None),
    (409, 'not_available', {'code': '409', 'message': 'Conflict'}),
    (409, 'duplicate_id', {'code': '409', 'message': 'Conflict'}),
    (
        429,
        'limit_exceeded',
        {
            'code': 'card_sessions_limit_exceeded',
            'localized_message': (
                'Превышен лимит открытых сессий. Попробуйте позднее'
            ),
        },
    ),
]


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize('error_status, error_code, error_json', PARAMS)
async def test_driver_money_instant_payout_card_post(
        taxi_driver_money, mockserver, error_status, error_code, error_json,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/internal/pro/v1/card-token-sessions',
    )
    def _mock_instant_payouts(_):
        if error_code is not None:
            return mockserver.make_response(
                status=error_status,
                json={'code': error_code, 'message': 'Error message'},
            )
        return {
            'id': '00000000-0000-0000-0000-000000000001',
            'created_at': '2019-06-02T12:00:00+0300',
            'expires_at': '2020-06-02T12:00:00+0300',
            'form_url': 'url_to_form',
        }

    response = await taxi_driver_money.post(
        'driver/v1/driver-money/v1/cards',
        json={'id': '00000000-0000-0000-0000-000000000001'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    if error_status is not None:
        assert response.status_code == error_status
        assert response.json() == error_json
    else:
        assert response.status_code == 200
        assert response.json() == {
            'id': '00000000-0000-0000-0000-000000000001',
            'form_url': 'url_to_form',
        }
