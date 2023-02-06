# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called_once
from pricing_extended.mocking_base import check_called

from .plugins import utils_request

from .plugins.mock_cashback_rates import cashback_rates_fixture
from .plugins.mock_cashback_rates import mock_cashback_rates
from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_ride_discounts import ride_discounts
from .plugins.mock_ride_discounts import mock_ride_discounts
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    ROUTE_RETRIES=1,
    SURGE_CALCULATOR_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 100},
    },
)
@pytest.mark.parametrize(
    'decoupling_tariffs', [True, False], ids=['dec', 'no_dec'],
)
@pytest.mark.parametrize('match_tags', [True, False], ids=['tags', 'no_tags'])
@pytest.mark.parametrize(
    'get_surge', [True, False], ids=['surger', 'no_surger'],
)
@pytest.mark.parametrize(
    'yamaps_route', [True, False], ids=['yamaps_router', 'no_router'],
)
@pytest.mark.parametrize(
    'user_api_users, user_api_phones, couponcheck, get_discount, get_cashback_rates',
    [
        (True, True, True, True, True),
        (True, True, True, False, True),
        (True, True, False, True, True),
        (True, True, False, False, True),
        (True, False, True, False, True),
        (True, False, False, False, True),
        (False, True, False, False, True),
        (False, False, False, False, True),
        (False, False, False, False, False),
        (True, True, False, False, False),
    ],
    ids=[
        'users-phones-coupon-dscnt',
        'users-phones-coupon-no_dscnt',
        'users-phones-no_coupon-dscnt',
        'users-phones-no_coupon-no_dscnt',
        'users-no_phones-coupon-no_dscnt',
        'users-no_phones-no_coupon-no_dscnt',
        'no_users-phones-no_coupon-no_dscnt',
        'no_users-no_phones-no_coupon-no_dscnt',
        'no_users-no_phones-no_coupon-no_dscnt-no-rates',
        'users-phones-no_coupon-no_dscnt-no-rates',
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_v2_prepare_fallback(
        taxi_pricing_data_preparer,
        user_api_users,
        user_api_phones,
        yamaps_route,
        get_surge,
        get_discount,
        match_tags,
        couponcheck,
        decoupling_tariffs,
        yamaps_router,
        mock_yamaps_router,
        user_api,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        ride_discounts,
        mock_ride_discounts,
        tags,
        mock_tags,
        coupons,
        mock_coupons,
        decoupling,
        mock_decoupling_corp_tariffs,
        get_cashback_rates,
        cashback_rates_fixture,
        mock_cashback_rates,
):
    if not user_api_users:
        user_api.crack_users()
    if not user_api_phones:
        user_api.crack_phone()
        surger.set_phone_id(None)
    if not yamaps_route:
        yamaps_router.must_crack(always=True)
    if not get_surge:
        surger.must_crack()
    if not get_discount:
        ride_discounts.must_crack()
    if not match_tags:
        tags.must_crack()
    if not couponcheck:
        coupons.must_crack()
    if not decoupling_tariffs:
        decoupling.tariffs_crack()
    if not get_cashback_rates:
        cashback_rates_fixture.must_crack()

    request = (
        utils_request.Request().add_coupon().add_decoupling_method().get()
    )

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    data = response.json()
    assert 'categories' in data
    assert 'econom' in data['categories'] and len(data['categories']) == 1
    econom = data['categories']['econom']
    assert 'user' in econom and 'driver' in econom
    assert econom['user']['additional_prices'] == {}
    assert econom['driver']['additional_prices'] == {}

    check_called_once(mock_user_api_get_users)
    check_called_once(mock_user_api_get_phones)
    check_called_once(mock_surger)
    check_called_once(mock_tags)
    if user_api_users and user_api_phones:
        check_called_once(mock_ride_discounts)
        check_called_once(mock_cashback_rates)
    if user_api_users:
        check_called_once(mock_coupons)
    check_called(mock_yamaps_router)
    check_called_once(mock_decoupling_corp_tariffs.handler_client_tariff)

    assert 'data' in econom['user']
    backend_variables = econom['user']['data']

    assert 'surge_params' in backend_variables
    assert backend_variables['surge_params']['value'] == 1
    assert 'surcharge' not in backend_variables['surge_params']
    assert 'surcharge_alpha' not in backend_variables['surge_params']
    assert 'surcharge_beta' not in backend_variables['surge_params']

    if user_api_users:
        if couponcheck:
            assert 'coupon' in backend_variables
            assert 'value' in backend_variables['coupon']
            assert backend_variables['coupon']['value'] == 0
        else:
            assert not 'coupon' in backend_variables
    assert 'user_data' in backend_variables
    assert 'has_yaplus' in backend_variables['user_data']
    assert not backend_variables['user_data']['has_yaplus']
    assert 'has_cashback_plus' in backend_variables['user_data']
    assert not backend_variables['user_data']['has_cashback_plus']
