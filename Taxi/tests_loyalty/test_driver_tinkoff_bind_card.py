import pytest

from . import utils as test_utils


HANDLER_URL = '/driver/v1/loyalty/v1/tinkoff/bind-card'
TAXIMETER_VERSION = 'Taximeter 8.80 (562)'
PROFILE_1 = {
    'dbid': 'driver_db_id1',
    'uuid': 'driver_uuid1',
    'session': 'driver_session1',
    'udid': 'driver_uniq_id1',
}


@pytest.mark.parametrize(
    'bank_id,expected_status_code,expected_error_code',
    [
        pytest.param(
            'Ya.Bank',
            400,
            'invalid_bank_id',
            marks=pytest.mark.pgsql(
                'loyalty', files=['loyalty_bank_driver_ids.sql'],
            ),
            id='wrong bank id',
        ),
        pytest.param('tinkoff', 404, '404', id='profile without udid'),
    ],
)
async def test_handler_fails(
        taxi_loyalty, stq, bank_id, expected_status_code, expected_error_code,
):
    response = await taxi_loyalty.post(
        HANDLER_URL,
        json={'bank_id': bank_id, 'contract_number': 'contract_number'},
        headers=test_utils.get_auth_headers(
            PROFILE_1['dbid'], PROFILE_1['uuid'], TAXIMETER_VERSION,
        ),
    )
    assert response.status_code == expected_status_code
    assert response.json()['code'] == expected_error_code
    assert stq.loyalty_bind_driver_card.times_called == 0


@pytest.mark.pgsql('loyalty', files=['loyalty_bank_driver_ids.sql'])
async def test_ok(taxi_loyalty, stq, unique_drivers):
    unique_drivers.set_unique_driver(
        PROFILE_1['dbid'], PROFILE_1['uuid'], PROFILE_1['udid'],
    )

    response = await taxi_loyalty.post(
        HANDLER_URL,
        json={'bank_id': 'tinkoff', 'contract_number': 'contract_number'},
        headers=test_utils.get_auth_headers(
            PROFILE_1['dbid'], PROFILE_1['uuid'], TAXIMETER_VERSION,
        ),
    )
    assert response.status_code == 200
    assert stq.loyalty_bind_driver_card.times_called == 1
