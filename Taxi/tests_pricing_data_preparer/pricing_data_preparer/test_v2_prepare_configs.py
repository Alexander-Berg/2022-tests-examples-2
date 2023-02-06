# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called_once

from .plugins import test_utils
from .plugins import utils_request

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


CONFIGS_CASES = test_utils.BooleanFlagCases(
    [
        'router_off',
        'surger_off',
        'coupons_off',
        'discounts_off',
        'tags_off',
        'yt_log_off',
    ],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    PRICING_DATA_PREPARER_YT_LOGGER_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=CONFIGS_CASES.get_names(),
    argvalues=CONFIGS_CASES.get_args(),
    ids=CONFIGS_CASES.get_ids(),
)
async def test_v2_prepare_configs(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        router_off,
        surger_off,
        coupons_off,
        discounts_off,
        tags_off,
        yt_log_off,
        taxi_config,
        testpoint,
):
    if router_off:
        taxi_config.set(
            PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': False},
        )
    if surger_off:
        taxi_config.set(
            PRICING_DATA_PREPARER_SURGER_ENABLED={
                '__default__': {'__default__': False},
            },
        )
    if coupons_off:
        taxi_config.set(PRICING_DATA_PREPARER_COUPONS_ENABLED=False)
    if discounts_off:
        taxi_config.set(PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=False)
    if tags_off:
        taxi_config.set(PRICING_PASSENGER_TAGS_ENABLED=False)
    if yt_log_off:
        taxi_config.set(PRICING_DATA_PREPARER_YT_LOGGER_ENABLED=False)

    @testpoint('yt_logger_v1_prepare_message')
    def yt_logger_v1_prepare_message(data):
        assert data == {}

    request = utils_request.Request().add_coupon().get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    if router_off:
        check_not_called(mock_yamaps_router)
    else:
        check_called_once(mock_yamaps_router)

    if surger_off:
        check_not_called(mock_surger)
    else:
        check_called_once(mock_surger)

    if coupons_off:
        check_not_called(mock_coupons)
    else:
        check_called_once(mock_coupons)

    if tags_off:
        check_not_called(mock_tags)
    else:
        check_called_once(mock_tags)

    if discounts_off:
        check_not_called(mock_ride_discounts)
    else:
        check_called_once(mock_ride_discounts)

    if yt_log_off:
        assert yt_logger_v1_prepare_message.times_called == 0
    else:
        pass


@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_yamaps_router',
)
@pytest.mark.config(
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_COUPONCHECK_QOS={
        'series_settings': {'maasx5': 'maas_qos_settings_id'},
        'qos_settings_map': {
            'maas_qos_settings_id': {
                'qos_info': {'timeout-ms': 200, 'attempts': 2},
            },
        },
    },
)
@pytest.mark.parametrize(
    'coupon_code, expected_retries', [('maasx500001', 2), ('some_coupon', 1)],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_couponcheck_custom_qos(
        taxi_pricing_data_preparer, mockserver, coupon_code, expected_retries,
):
    pre_request = utils_request.Request()
    pre_request.add_coupon(coupon_code)

    request = pre_request.get()

    @mockserver.json_handler('/coupons/v1/couponcheck')
    def _couponcheck_handler(request):
        return mockserver.make_response(json={}, status=500)

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )

    assert response.status_code == 200
    assert _couponcheck_handler.times_called == expected_retries
