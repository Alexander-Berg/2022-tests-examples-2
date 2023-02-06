# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
from typing import Optional

import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called_once

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


DISCOUNTS_TEST_PARAMS = pytest.mark.parametrize(
    'has_cashback, has_money',
    (
        pytest.param(False, True, id='with_money_without_cashback'),
        pytest.param(True, True, id='with_money_and_with_cashback'),
        pytest.param(True, False, id='with_cashback_and_without_money'),
    ),
)


@DISCOUNTS_TEST_PARAMS
@pytest.mark.config(PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_v2_prepare_discounts(
        taxi_pricing_data_preparer,
        experiments3,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        ride_discounts,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        has_cashback,
        has_money,
):
    request = utils_request.Request()
    request.set_categories(['econom', 'business'])
    if has_money:
        ride_discounts.add_table_discount('econom')
    if has_cashback:
        ride_discounts.add_flat_discount('econom', is_cashback=True)
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request.get(),
    )
    assert response.status_code == 200
    check_called_once(mock_ride_discounts)
    response_json = response.json()
    response_categories = response_json['categories']
    response_category = response_categories['econom']
    backend_variables = response_category['user']['data']
    discount = backend_variables.get('discount')
    if has_money:
        assert discount
        assert 'calc_data_coeff' not in discount
        assert 'calc_data_hyperbolas' not in discount
        assert 'calc_data_table_data' in discount
    else:
        assert discount is None
    cashback_discount = backend_variables.get('cashback_discount')

    if has_cashback:
        assert cashback_discount
        assert 'calc_data_coeff' in cashback_discount
        assert 'calc_data_hyperbolas' not in cashback_discount
        assert 'calc_data_table_data' not in cashback_discount
    else:
        assert cashback_discount is None

    response_category = response_categories['business']
    backend_variables = response_category['user']['data']
    discount = backend_variables.get('discount')
    assert discount is None
