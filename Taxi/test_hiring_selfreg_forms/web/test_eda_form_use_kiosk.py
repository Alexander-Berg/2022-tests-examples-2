import hashlib

import pytest

from test_hiring_selfreg_forms import conftest


IP_USE_KIOSK_TRUE = '127.0.0.1'
IP_USE_KIOSK_FALSE = '127.0.0.2'
IP_USE_KIOSK_EMPTY = '127.0.0.3'
IP_USE_KIOSK_NOT_IN_EXP = '100.0.0.1'


def hashed(string):
    return hashlib.md5(bytes(string, 'utf-8')).hexdigest()


@pytest.mark.client_experiments3(
    consumer='hiring_selfreg_forms/use_kiosk',
    experiment_name='hiring_sefreg_forms_kiosk',
    args=[
        {'name': 'ip', 'type': 'string', 'value': hashed(IP_USE_KIOSK_TRUE)},
    ],
    value={'use_kiosk': True},
)
@pytest.mark.client_experiments3(
    consumer='hiring_selfreg_forms/use_kiosk',
    experiment_name='hiring_sefreg_forms_kiosk',
    args=[
        {'name': 'ip', 'type': 'string', 'value': hashed(IP_USE_KIOSK_FALSE)},
    ],
    value={'use_kiosk': False},
)
@pytest.mark.client_experiments3(
    consumer='hiring_selfreg_forms/use_kiosk',
    experiment_name='hiring_sefreg_forms_kiosk',
    args=[
        {'name': 'ip', 'type': 'string', 'value': hashed(IP_USE_KIOSK_EMPTY)},
    ],
    value={},
)
@pytest.mark.parametrize(
    'ip_headers, use_kiosk',
    [
        (
            {
                conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_TRUE,
                conftest.X_REMOTE_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
                conftest.X_REAL_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
            },
            True,
        ),
        (
            {
                conftest.X_REMOTE_IP_KEY: IP_USE_KIOSK_TRUE,
                conftest.X_REAL_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
            },
            True,
        ),
        ({conftest.X_REAL_IP_KEY: IP_USE_KIOSK_TRUE}, True),
        ({conftest.X_USE_KIOSK_IP_KEY: IP_USE_KIOSK_TRUE}, True),
        (
            {
                conftest.X_USE_KIOSK_IP_KEY: IP_USE_KIOSK_TRUE,
                conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
                conftest.X_REMOTE_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
                conftest.X_REAL_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
            },
            True,
        ),
        (
            {
                conftest.X_USE_KIOSK_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP,
                conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_TRUE,
                conftest.X_REMOTE_IP_KEY: IP_USE_KIOSK_TRUE,
                conftest.X_REAL_IP_KEY: IP_USE_KIOSK_TRUE,
            },
            False,
        ),
        ({conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_FALSE}, False),
        ({conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_EMPTY}, False),
        ({conftest.X_FORM_USER_IP_KEY: IP_USE_KIOSK_NOT_IN_EXP}, False),
        ({}, False),
    ],
)
@conftest.main_configuration
async def test_eda_form_use_kiosk(make_request, ip_headers, use_kiosk):
    response_data = await make_request(
        conftest.ROUTE_EDA_FORM_USE_KIOSK,
        method='get',
        headers={**ip_headers},
        set_x_real_ip=False,
    )
    assert response_data['use_kiosk'] == use_kiosk
