import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize('card_not_found', [True, False])
async def test_driver_money_instant_payout_card_byid_del(
        taxi_driver_money, mockserver, card_not_found,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/internal/pro/v1/cards/by-id',
    )
    def _mock_instant_payouts(_):
        if card_not_found:
            return mockserver.make_response(
                status=404,
                json={'code': 'does_not_exist', 'message': 'Does not exist'},
            )
        return mockserver.make_response(status=204)

    response = await taxi_driver_money.delete(
        'driver/v1/driver-money/v1/cards/by-id',
        params={'card_id': '00000000-0000-0000-0000-000000000001'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    if card_not_found:
        assert response.status_code == 404
        assert response.json() == {
            'code': 'card_not_found',
            'localized_message': 'Карта не найдена',
        }
    else:
        assert response.status_code == 204
