import pytest

from tests_eda_antifraud.helpers import eda_antifraud


@pytest.mark.servicetest
async def test_validate_success(taxi_eda_antifraud):
    await eda_antifraud.validate(
        taxi_eda_antifraud, 'courier-id', 'signature', 200, {'is_valid': True},
    )


@pytest.mark.servicetest
async def test_validate_no_courier(taxi_eda_antifraud):
    await eda_antifraud.validate(
        taxi_eda_antifraud,
        None,
        'signature',
        400,
        {
            'code': 'empty_courier_id',
            'message': 'Header X-YaEda-CourierId is empty',
        },
    )


@pytest.mark.servicetest
async def test_validate_no_signature(taxi_eda_antifraud):
    await eda_antifraud.validate(
        taxi_eda_antifraud,
        'courier-id',
        '',
        400,
        {'code': 'empty_signature', 'message': 'Signature is empty'},
    )
