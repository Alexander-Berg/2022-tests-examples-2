# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import copy

import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from .plugins.mock_surge import surger, mock_surger
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs

from .plugins import utils_request

V2_PREPARE_REQUEST = {
    'categories': ['econom'],
    'order_type': 'APPLICATION',
    'classes_requirements': {},
    'tolls': 'DENY',
    'modifications_scope': 'taxi',
}

POINT_IN_EKB = [60.564025, 56.847124]
POINT_IN_EXPO = [60.762103, 56.767090]
POINT_IN_EKB_AIRPORT = [60.785488, 56.749149]
POINT_OUT_OF_EKB = [60.854187, 56.580299]


@pytest.mark.config(
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': False},
)
@pytest.mark.filldb(
    geoareas='match_transfers',
    tariffs='match_transfers',
    tariff_settings='match_transfers',
)
@pytest.mark.parametrize(
    'waypoints, zone, expected_transfer',
    [
        (
            [[30.3225928829, 59.8000738161], [30.273033, 59.799774]],
            'spb',
            ('suburb', 'spb_airport'),
        ),
        (
            [[30.4232290932, 60.0583669443], [30.273033, 59.799774]],
            'spb',
            ('suburb', 'spb_airport'),
        ),
        (
            [[30.31963332447087, 59.91410984815264], [30.273196, 59.800005]],
            'spb',
            ('spb', 'spb_airport'),
        ),
        (
            [[30.2711361366915, 59.79669026912626], [30.273033, 59.799774]],
            'spb_airport',
            (),
        ),
        (
            [
                [30.2711361366915, 59.79669026912626],
                [30.4232290932, 60.0583669443],
            ],
            'spb_airport',
            ('spb_airport', 'suburb'),
        ),
        (
            [
                [30.2711361366915, 59.79669026912626],
                [30.31963332447087, 59.91410984815264],
            ],
            'spb_airport',
            ('spb_airport', 'spb'),
        ),
        (
            [[37.414924, 55.981405], [37.900474, 55.414344]],
            'svo',
            ('svo', 'suburb'),
        ),
        #
        ([POINT_IN_EKB, POINT_IN_EKB], 'ekb', ()),
        ([POINT_IN_EKB, POINT_IN_EXPO], 'ekb', ('ekb', 'expo')),
        ([POINT_IN_EKB, POINT_IN_EKB_AIRPORT], 'ekb', ('ekb', 'ekb_airport')),
        ([POINT_IN_EKB, POINT_OUT_OF_EKB], 'ekb', ()),
        #
        ([POINT_IN_EXPO, POINT_IN_EKB], 'ekb', ('expo', 'ekb')),
        ([POINT_IN_EXPO, POINT_IN_EXPO], 'ekb', ('expo', 'ekb')),
        ([POINT_IN_EXPO, POINT_IN_EKB_AIRPORT], 'ekb', ('expo', 'ekb')),
        ([POINT_IN_EXPO, POINT_OUT_OF_EKB], 'ekb', ()),
        #
        ([POINT_IN_EKB_AIRPORT, POINT_IN_EKB], 'ekb', ('ekb_airport', 'ekb')),
        ([POINT_IN_EKB_AIRPORT, POINT_IN_EXPO], 'ekb', ('ekb_airport', 'ekb')),
        (
            [POINT_IN_EKB_AIRPORT, POINT_IN_EKB_AIRPORT],
            'ekb',
            ('ekb_airport', 'ekb'),
        ),
        (
            [POINT_IN_EKB_AIRPORT, POINT_OUT_OF_EKB],
            'ekb',
            ('ekb_airport', 'suburb'),
        ),
        #
        ([POINT_OUT_OF_EKB, POINT_IN_EKB], 'ekb', ()),
        ([POINT_OUT_OF_EKB, POINT_IN_EXPO], 'ekb', ()),
        (
            [POINT_OUT_OF_EKB, POINT_IN_EKB_AIRPORT],
            'ekb',
            ('suburb', 'ekb_airport'),
        ),
        ([POINT_OUT_OF_EKB, POINT_OUT_OF_EKB], 'ekb', ()),
    ],
)
async def test_v2_prepare_match_transfers(
        taxi_pricing_data_preparer,
        mock_surger,
        surger,
        waypoints,
        zone,
        expected_transfer,
):
    surger.set_user_id(None)

    request = copy.deepcopy(V2_PREPARE_REQUEST)
    request['waypoints'] = waypoints
    request['zone'] = zone
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    resp = response.json()

    assert 'categories' in resp and 'econom' in resp['categories']
    category_info = resp['categories']['econom']
    for subject in ['driver', 'user']:
        assert subject in category_info
        assert 'category_prices_id' in category_info[subject]
        actual_transfer = tuple(
            category_info[subject]['category_prices_id'].split('/')[2:],
        )
        assert actual_transfer == expected_transfer


@pytest.mark.config(FIXED_PRICE_MAX_ALLOWED_DISTANCE_ENABLED=True)
@pytest.mark.parametrize(
    'waypoints, zone, disable_fix_price, fixed_price_discard_reason',
    [
        (
            [[30.317992, 59.926419], [37.683, 55.774]],
            'spb',
            False,
            'LONG_TRIP',
        ),
        (
            [[30.3225928829, 59.8000738161], [30.273033, 59.799774]],
            'spb',
            True,
            'DISABLED_BY_CORP',
        ),
    ],
    ids=['long distance', 'corp_disable_fixed_price'],
)
async def test_v2_prepare_discard_transfer(
        taxi_pricing_data_preparer,
        mock_surger,
        surger,
        mock_yamaps_router,
        yamaps_router,
        load_json,
        experiments3,
        decoupling,
        mock_decoupling_corp_tariffs,
        testpoint,
        waypoints,
        zone,
        disable_fix_price,
        fixed_price_discard_reason,
):
    @testpoint('is_disabled_transfer')
    def _is_disabled_transfer(data):
        assert not data['is_transfer']

    surger.set_user_id(None)
    if fixed_price_discard_reason == 'LONG_TRIP':
        yamaps_router.set_long_route()
    else:
        yamaps_router.set_easy_msk_nojams()

    pre_request = utils_request.Request()
    pre_request.set_waypoints(waypoints)
    pre_request.set_user_id(None)
    if disable_fix_price:
        decoupling.disable_fix_price()
        experiments3.add_experiments_json(
            load_json('exp3_plugin_decoupling.json'),
        )
        pre_request.add_decoupling_method()

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    assert _is_disabled_transfer.times_called >= 2
    resp = response.json()

    if disable_fix_price:
        assert (
            mock_decoupling_corp_tariffs.handler_client_tariff.times_called
            == 1
        )

    assert 'categories' in resp and 'econom' in resp['categories']
    category_info = resp['categories']['econom']
    assert not category_info['fixed_price']
    assert (
        category_info['fixed_price_discard_reason']
        == fixed_price_discard_reason
    )
