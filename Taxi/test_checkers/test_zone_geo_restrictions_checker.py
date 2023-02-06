import decimal

import pytest

from taxi.util import context_timings
from taxi.util import performance

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

BASE_GEO_RESTRICTIONS = {
    'matched_geo': {
        'geo': {'center': [37.676062, 55.743145], 'radius': 1000},
        'is_deleted': False,
    },
    'not_matched_geo': {
        'geo': {'center': [30.676062, 60.743145], 'radius': 1000},
        'is_deleted': False,
    },
}
BASE_CLIENT = {
    '_id': 'client_id',
    'features': ['geo_restrictions', 'prohibiting_geo_restrictions'],
}
BASE_TAXI_ORDER_INFO = types.TaxiOrderInfo(
    classes=[],
    order_price=decimal.Decimal(),
    route=[
        types.GeoPoint(geopoint=[37.676062, 55.743145]),
        types.GeoPoint(geopoint=[37.676062, 55.743145]),
    ],
    cost_center=None,
    cost_centers=None,
    combo_order=None,
)

BASE_ZONE = types.TariffSetting(
    home_zone='',
    is_corp_paymentmethod=True,
    tariffs={},
    tanker_keys={},
    country='',
    tz='Europe/Moscow',
    driver_change_cost=None,
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {'data': checkers_utils.mock_prepared_data()},
            (True, ''),
            id='no zone',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'corpweb',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='skip for corpweb',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(client=BASE_CLIENT),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='no geo restrictions',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {'source': 'not_matched_geo'},
                            {'source': 'matched_geo'},
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='match one geo restriction (check only source)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'not_matched_geo': {
                            **BASE_GEO_RESTRICTIONS['not_matched_geo'],
                            **{'is_deleted': True},
                        },
                    },
                    limit={
                        'geo_restrictions': [{'source': 'not_matched_geo'}],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='skip deleted restriction (check only source)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [{'source': 'not_matched_geo'}],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата недоступна по этому адресу'),
            id='not found matched restrictions (check only source)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {'destination': 'not_matched_geo'},
                            {'destination': 'matched_geo'},
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                    ],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='match one geo restriction (check only destination)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {'destination': 'not_matched_geo'},
                            {'destination': 'matched_geo'},
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[types.GeoPoint(geopoint=[37.676062, 55.743145])],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата недоступна по этому адресу'),
            id='no destination in route (check only destination)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [
                            {'destination': 'not_matched_geo'},
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                    ],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата недоступна по этому адресу'),
            id='not found matched restrictions (check only destination)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {'source': 'not_matched_geo'},
                            {
                                'source': 'matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                    ],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='match one geo restriction (full check)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'not_matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                    ],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата недоступна по этому адресу'),
            id='not found matched restrictions (full check)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'not_matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                ),
                'order_info': BASE_TAXI_ORDER_INFO,
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='not zone, skip for taxi',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    zone_status=types.ZoneStatus.OK,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                    zone=BASE_ZONE,
                ),
                'order_info': BASE_TAXI_ORDER_INFO,
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='found matched restrictions (full check), taxi',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    zone_status=types.ZoneStatus.OK,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'not_matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                    zone=BASE_ZONE,
                ),
                'order_info': BASE_TAXI_ORDER_INFO,
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (False, 'error.order_is_restricted_in_the_geo'),
            id='not found matched restrictions (full check), taxi',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': []},
                    zone_status=types.ZoneStatus.OK,
                    geo_restrictions={
                        'not_matched_geo': BASE_GEO_RESTRICTIONS[
                            'not_matched_geo'
                        ],
                    },
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'not_matched_geo',
                                'destination': 'matched_geo',
                            },
                        ],
                    },
                    zone=BASE_ZONE,
                ),
                'order_info': BASE_TAXI_ORDER_INFO,
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='not feature, skip failed check',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    geo_restrictions={
                        'matched_geo': BASE_GEO_RESTRICTIONS['matched_geo'],
                    },
                    limit={
                        'geo_restrictions': [
                            {'source': 'not_matched_geo'},
                            {
                                'source': 'matched_geo',
                                'destination': 'matched_geo',
                                'prohibiting_restriction': True,
                            },
                        ],
                    },
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    currency='RUB',
                    country='rus',
                    route=[
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        types.GeoPoint(geopoint=[37.676062, 55.743145]),
                    ],
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата недоступна по этому адресу'),
            id='prohibiting_restriction, failed path',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client=BASE_CLIENT,
                    zone_status=types.ZoneStatus.OK,
                    geo_restrictions=BASE_GEO_RESTRICTIONS,
                    limit={
                        'geo_restrictions': [
                            {
                                'source': 'not_matched_geo',
                                'destination': 'matched_geo',
                                'prohibiting_restriction': True,
                            },
                        ],
                    },
                    zone=BASE_ZONE,
                ),
                'order_info': BASE_TAXI_ORDER_INFO,
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='prohibiting_restriction, success path',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_zone_geo_restrictions_checker(
        web_context, patch, input_data, expected_result,
):
    time_storage = performance.TimeStorage('geo_restrictions')
    context_timings.time_storage.set(time_storage)

    checker = checkers_utils.get_checker_instance(
        user_checkers.ZoneGeoRestrictionsChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
