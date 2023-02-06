import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize('is_conflict', [True, False])
@pytest.mark.parametrize('amount', ['100.00', '100,00'])
async def test_driver_money_instant_payout_create(
        taxi_driver_money, mockserver, is_conflict, amount,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/withdrawal',
    )
    def _mock_instant_payouts_withdrawal(_):
        if is_conflict:
            return mockserver.make_response(
                status=409,
                json={'code': 'invalid_argument', 'message': 'Conflict'},
            )
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/fleet-offers/internal/v1/fleet-offers/v1/not-signed/count',
    )
    def _mock_fleet_offers_count(_):
        return {'count': 0}

    response = await taxi_driver_money.post(
        'driver/v1/driver-money/v1/instant-payouts',
        json={'amount': amount},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    if is_conflict:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'conflict',
            'localized_message': 'Правило перевода средств изменилось',
        }
    else:
        assert response.status_code == 204


FLEET_OFFERS_PARAMS = [
    (0, 204, None),
    (1, 400, {'code': 'forbidden', 'localized_message': 'Доступ запрещен'}),
]


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'not_signed_offers_count, ' 'expected_code, expected_response',
    FLEET_OFFERS_PARAMS,
)
async def test_driver_money_instant_payout_check_offers(
        taxi_driver_money,
        mockserver,
        not_signed_offers_count,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/withdrawal',
    )
    def mock_instant_payouts_withdrawal(_):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/fleet-offers/internal/v1/fleet-offers/v1/not-signed/count',
    )
    def mock_fleet_offers_count(_):
        return {'count': not_signed_offers_count}

    response = await taxi_driver_money.post(
        'driver/v1/driver-money/v1/instant-payouts',
        json={'amount': '100.00'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    assert mock_fleet_offers_count.times_called == 1

    if not_signed_offers_count > 0:
        assert mock_instant_payouts_withdrawal.times_called == 0
    else:
        assert mock_instant_payouts_withdrawal.times_called == 1

    assert response.status_code == expected_code
    if expected_response is not None:
        assert response.json() == expected_response
