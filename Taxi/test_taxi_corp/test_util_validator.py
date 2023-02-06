import pytest

from taxi_corp.api.common import exceptions
from taxi_corp.internal import consts
from taxi_corp.util import validator

_INF = consts.INF


@pytest.mark.parametrize(
    ['phone', 'expected_error'],
    [
        ('+79169222964', 'no_error'),
        ('+71269222964', 'no_error'),
        (
            '+78',
            'phone length with plus sign should be greater than {} symbols',
        ),
        ('+781234567890', 'phone number should be in format: {}'),
        ('+771234567890', 'no_error'),
        ('+80000000000', 'phone number should be in format: {}'),
        ('+22121212121', 'phone number should starts with: {}'),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
        {
            'min_length': 10,
            'max_length': 12,
            'prefixes': ['+77', '+80', '+712'],
            'matches': ['^77', '^10', '^712'],
        },
    ],
)
async def test_check_valid_phone(taxi_corp_auth_client, phone, expected_error):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    error = exceptions.Error(tanker_key='no_error')
    try:
        validator.check_valid_phone(
            phone, taxi_corp_auth_client.server.app.phones,
        )
    except exceptions.ValidatorError as exc:
        error = exc.error

    assert expected_error in [error.tanker_key, error.text]
