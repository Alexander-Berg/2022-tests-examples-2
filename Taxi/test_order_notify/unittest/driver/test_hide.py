import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.driver import driver_vars


@pytest.mark.parametrize(
    'zone, driver_name, exp_driver_phone, exp_park_phone, exp_car_number,'
    'exp_driver_name',
    [
        pytest.param(None, 'd', 'f', 's', '1234321', 'd', id='zone_None'),
        pytest.param('moscow', 'd', 'f', 's', '1234321', 'd', id='no_zone'),
        pytest.param('skolkovo', 'd', '', '', '**343**', 'k', id='hide'),
    ],
)
@pytest.mark.config(
    HIDE_DRIVER_INFO={
        '__default__': {
            'car_number': False,
            'driver_phone': False,
            'fio': False,
            'park_phone': False,
        },
        'skolkovo': {
            'car_number': True,
            'driver_phone': True,
            'fio': True,
            'park_phone': True,
        },
    },
)
def test_hide_driver_vars(
        stq3_context: stq_context.Context,
        zone,
        driver_name,
        exp_driver_phone,
        exp_park_phone,
        exp_car_number,
        exp_driver_name,
):
    expected_vars = {
        'driver_phone': exp_driver_phone,
        'park_phone': exp_park_phone,
        'car_number': exp_car_number,
        'driver_name': exp_driver_name,
    }
    d_vars = driver_vars.hide_driver_vars(
        context=stq3_context,
        driver_vars={
            'driver_phone': 'f',
            'park_phone': 's',
            'car_number': '1234321',
            'driver_name': driver_name,
        },
        zone=zone,
        driver_first_name='k',
    )
    assert d_vars == expected_vars
