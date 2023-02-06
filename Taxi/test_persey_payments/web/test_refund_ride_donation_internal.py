import pytest


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.parametrize(
    'invoice_not_found, exp_resp_status, exp_resp',
    [
        (
            True,
            404,
            {
                'code': 'NO_DONATION',
                'message': 'No donation found for this order_id',
            },
        ),
        (False, 200, {}),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        mock_invoice_update,
        invoice_not_found,
        exp_resp_status,
        exp_resp,
):
    invoice_update_mock = mock_invoice_update(
        'expected_invoice_update_request.json', not_found=invoice_not_found,
    )

    response = await taxi_persey_payments_web.put(
        '/internal/v1/charity/ride_donation/refund',
        json={'order_id': 'order777'},
        headers={'X-Yandex-UID': 'market_uid', 'X-Brand': 'market'},
    )

    assert response.status == exp_resp_status
    assert await response.json() == exp_resp

    assert invoice_update_mock.times_called == 1
