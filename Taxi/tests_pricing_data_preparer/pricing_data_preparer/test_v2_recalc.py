# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called

from .plugins import test_utils
from .plugins import utils_request
from .round_values import round_values

from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.utils_response import econom_category
from .plugins.utils_response import econom_response
from .plugins.utils_response import business_category
from .plugins.utils_response import business_response
from .plugins.utils_response import econom_with_additional_prices
from .plugins.utils_response import decoupling_response
from .plugins.utils_response import category_list
from .plugins.utils_response import calc_price


@pytest.mark.parametrize(
    'request_file, meta, total',
    [
        ('simple_request.json', {}, 131.0),
        ('route_request.json', {}, 242.0),
        ('route_in_suburb_request.json', {}, 282.0),
        ('empty_route_request.json', {}, 129.0),
    ],
    ids=['simple', 'route', 'route_in_suburb', 'empty_route'],
)
async def test_v2_recalc(
        taxi_pricing_data_preparer, load_json, request_file, meta, total,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/recalc', json=load_json(request_file),
    )
    assert response.status_code == 200

    assert response.json() == {
        'price': {
            'driver': {'total': total, 'meta': meta},
            'user': {'total': total, 'meta': meta},
        },
    }


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'request_file',
    ['modifications_request.json', 'strikeout_request.json'],
    ids=['modifications', 'with_strikeout'],
)
async def test_v2_recalc_modifications(
        taxi_pricing_data_preparer, load_json, request_file,
):
    request_json = load_json(request_file)
    response = await taxi_pricing_data_preparer.post(
        'v2/recalc', json=request_json,
    )
    assert response.status_code == 200

    expected = {
        'price': {
            'driver': {'total': 307.0, 'meta': {'dummy': 42.0}},
            'user': {'total': 307.0, 'meta': {'dummy': 42.0}},
        },
    }
    for subject in ('driver', 'user'):
        if 'modifications_for_strikeout_price' in request_json[subject]:
            expected['price'][subject].update({'strikeout': 337.0})
    assert response.json() == expected


async def test_v2_recalc_route_parts(taxi_pricing_data_preparer, load_json):
    request = load_json('route_in_suburb_request.json')
    request['additional_payloads'] = {'need_route_parts': True}
    response = await taxi_pricing_data_preparer.post('v2/recalc', json=request)
    assert response.status_code == 200

    expected_resp = {
        'additional_payloads': {
            'route_parts': [
                {
                    'distance': {'meters': 7446.0, 'price': 84.474},
                    'time': {'seconds': 755.0, 'price': 68.25},
                    'area': {'zone': 'suburb'},
                },
            ],
        },
        'meta': {},
        'total': 282.0,
    }
    assert response.json() == {
        'price': {'driver': expected_resp, 'user': expected_resp},
    }


async def test_v2_recalc_propagate_corp_tariffs_429(
        taxi_pricing_data_preparer, mockserver, load_json,
):
    @mockserver.handler('/corp-tariffs/v1/tariff')
    async def _mock_corp_tariff(request):
        return mockserver.make_response(
            '429', status=429, content_type='text/plain',
        )

    request = load_json('decoupling_request.json')
    response = await taxi_pricing_data_preparer.post('v2/recalc', json=request)
    assert response.status_code == 429
