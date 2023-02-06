import pytest

ENDPOINT = 'service/loyalty/v1/status/by-bank-driver-id'


def build_params(bank_id, bank_driver_id):
    return {'bank_id': bank_id, 'bank_driver_id': bank_driver_id}


def build_response(status):
    return {'loyalty': {'status': status}}


OK_PARAMS = [('tinkoff', '101', 'silver'), ('tinkoff', '103', 'none')]


@pytest.mark.parametrize('bank_id, bank_driver_id, expected_status', OK_PARAMS)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_bank_driver_ids.sql'],
)
async def test_service_driver_status(
        taxi_loyalty, bank_id, bank_driver_id, expected_status,
):
    response = await taxi_loyalty.get(
        ENDPOINT, params=build_params(bank_id, bank_driver_id),
    )

    assert response.status_code == 200, response.text
    assert response.json() == build_response(expected_status)


BAD_PARAMS = [
    (
        'bad_bank',
        'bad_id',
        400,
        {'code': 'invalid_bank_id', 'message': 'Invalid bank id'},
    ),
    (
        'tinkoff',
        'bad_id',
        404,
        {'code': 'driver_id_not_found', 'message': 'Driver id not found'},
    ),
]


@pytest.mark.parametrize(
    'bank_id, bank_driver_id, expected_code, expected_response', BAD_PARAMS,
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_bank_driver_ids.sql'],
)
async def test_service_driver_status_fail(
        taxi_loyalty,
        bank_id,
        bank_driver_id,
        expected_code,
        expected_response,
):
    response = await taxi_loyalty.get(
        ENDPOINT, params=build_params(bank_id, bank_driver_id),
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
