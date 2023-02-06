# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import pytest

from tests_pricing_fallback.plugins.mock_order_core import mock_order_core
from tests_pricing_fallback.plugins.mock_order_core import order_core
from tests_pricing_fallback.plugins.mock_order_core import OrderIdRequestType

AUTH = {
    'park_id': 'park_id_000',
    'session': 'session_000',
    'uuid': 'driverid000',
}

USER_AGENT = 'Taximeter-DEV 9.21 (2147483647)'

DEFAULT_HEADERS = {
    'X-Driver-Session': AUTH['session'],
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-EN',
}


@pytest.mark.parametrize(
    'testname, expected_code, expected_error',
    [
        ('order_not_found', 404, 'ORDER_NOT_FOUND'),
        ('pricing_data_not_found', 404, 'PRICING_DATA_NOT_FOUND'),
        ('pricing_data_is_not_fallback', 404, 'PRICING_DATA_IS_NOT_FALLBACK'),
        ('simple', 200, None),
    ],
    ids=[
        'order_not_found',
        'pricing_data_not_found',
        'pricing_data_is_not_fallback',
        'simple',
    ],
)
async def test_v1_get_modifications(
        taxi_pricing_fallback,
        load_json,
        driver_authorizer,
        testname,
        expected_code,
        expected_error,
        experiments3,
        mock_order_core,
        order_core,
):
    experiments3.add_config(
        consumers=['pricing-data-preparer/pricing_components'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='read_order_proc_from_order_core',
        default_value={
            '__default__': 'mongo',
            'fallback_get_modifications': 'order_core',
        },
    )

    request = load_json(testname + '/request.json')

    order_core.set_expected_key(
        request['order_id'], OrderIdRequestType.alias_id, require_latest=True,
    )

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_fallback.post(
        'v1/fallback/get_modifications',
        json=request,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == expected_code

    response = response.json()
    if expected_code == 200:
        expected_response = load_json(testname + '/response.json')
        assert response == expected_response
    else:
        assert 'code' in response and response['code'] == expected_error

    assert mock_order_core.times_called == 1
