import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'subs_id, trust_response, trust_times_called, status_code, response_json',
    [
        ('some_external_id', {'status': 'success'}, 1, 200, None),
        (
            'some_external_id',
            {'status': 'error', 'status_code': 'invalid_payment_method'},
            1,
            400,
            {
                'code': 'TRUST_STATUS_ERROR',
                'message': 'invalid_payment_method',
            },
        ),
        (
            'nonexistent',
            None,
            0,
            404,
            {
                'code': 'SUBS_NOT_FOUND',
                'message': 'subs_id=nonexistent not found in db',
            },
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        mock_set_payment_method,
        subs_id,
        trust_response,
        trust_times_called,
        status_code,
        response_json,
):
    payment_method_mock = mock_set_payment_method(
        {'paymethod_id': 'card-x777'}, trust_response,
    )

    response = await taxi_persey_payments_web.put(
        '/payments/v1/charity/subs/payment_method',
        json={'subs_id': subs_id, 'payment_method_id': 'card-x777'},
        headers={'X-Yandex-UID': '41'},
    )
    assert response.status == status_code
    assert payment_method_mock.times_called == trust_times_called

    if response_json is not None:
        assert await response.json() == response_json
