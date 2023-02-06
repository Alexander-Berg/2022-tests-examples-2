# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import pytest

from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called

from .plugins import utils_request
from .plugins import utils_response

from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_ride_discounts import ride_discounts
from .plugins.mock_ride_discounts import mock_ride_discounts
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_combo_contractors import combo_contractors
from .plugins.mock_combo_contractors import mock_combo_contractors
from .plugins.mock_alt_offer_discount import alt_offer_discount
from .plugins.mock_alt_offer_discount import mock_alt_offer_discount
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs


def _add_category_data(
        data,
        category,
        has_fixed,
        dict_fixed,
        dict_taximeter,
        dict_antisurge_fixed,
        dict_antisurge_taximeter,
):
    if has_fixed:
        dict_fixed[category] = data['modifications']['for_fixed']

        dict_antisurge_fixed[category] = data['additional_prices'][
            'antisurge'
        ]['modifications']['for_fixed']

    dict_taximeter[category] = data['modifications']['for_taximeter']

    dict_antisurge_taximeter[category] = data['additional_prices'][
        'antisurge'
    ]['modifications']['for_taximeter']


def _add_price(
        data,
        category,
        driver_price,
        driver_antisurge_price,
        user_price,
        user_antisurge_price,
):
    driver_price[category] = utils_response.calc_price(data['driver']['price'])
    driver_antisurge_price[category] = utils_response.calc_price(
        data['driver']['additional_prices']['antisurge']['price'],
    )
    user_price[category] = {}
    user_price[category]['price'] = utils_response.calc_price(
        data['user']['price'],
    )
    user_price[category]['strikeout'] = data['user']['price']['strikeout']
    user_antisurge_price[category] = {}
    user_antisurge_price[category]['price'] = utils_response.calc_price(
        data['user']['additional_prices']['antisurge']['price'],
    )
    user_antisurge_price[category]['strikeout'] = data['user'][
        'additional_prices'
    ]['antisurge']['price']['strikeout']


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.experiments3(filename='exp3_combo_order_config.json')
@pytest.mark.experiments3(filename='exp3_perfect_chain_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.filldb(tariff_settings='all_fixed')
@pytest.mark.parametrize('scope', ['taxi', 'cargo'])
@pytest.mark.parametrize('alt_offer_discount_case', ['exist', 'empty'])
async def test_v2_prepare_collect_rules(
        taxi_pricing_data_preparer,
        taxi_config,
        pgsql,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        combo_contractors,
        mock_combo_contractors,
        alt_offer_discount,
        mock_alt_offer_discount,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        scope,
        alt_offer_discount_case,
):
    if scope == 'cargo':
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                f'UPDATE price_modifications.workabilities '
                f'SET scope = \'{scope}\';',
            )
        await taxi_pricing_data_preparer.invalidate_caches()

    categories = [
        'econom',
        'comfortplus',
        'maybach',
        'business',
        'minivan',
        'demostand',
        'cargo',
        'vip',
        'ubernight',
    ]
    pre_request = utils_request.Request().set_categories(categories)
    pre_request.set_additional_prices(
        antisurge=True,
        strikeout=True,
        combo_order=True,
        combo_inner=True,
        combo_outer=True,
        combo=True,
        alt_offer_discount=True,
        full_auction=True,
    )
    pre_request.set_modifications_scope(scope)

    surger.set_explicit_antisurge()

    if alt_offer_discount_case == 'exist':
        alt_offer_discount.set_param('kekw', 2.0)
    elif alt_offer_discount_case == 'empty':
        alt_offer_discount.clear_offers()

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    driver_fixed = {}
    driver_taximeter = {}
    driver_antisurge_fixed = {}
    driver_antisurge_taximeter = {}
    user_fixed = {}
    user_taximeter = {}
    user_antisurge_fixed = {}
    user_antisurge_taximeter = {}
    driver_price = {}
    driver_antisurge_price = {}
    user_price = {}
    user_antisurge_price = {}

    for category in categories:
        _add_category_data(
            data['categories'][category]['driver'],
            category,
            data['categories'][category]['fixed_price'],
            driver_fixed,
            driver_taximeter,
            driver_antisurge_fixed,
            driver_antisurge_taximeter,
        )

        _add_category_data(
            data['categories'][category]['user'],
            category,
            data['categories'][category]['fixed_price'],
            user_fixed,
            user_taximeter,
            user_antisurge_fixed,
            user_antisurge_taximeter,
        )

        _add_price(
            data['categories'][category],
            category,
            driver_price,
            driver_antisurge_price,
            user_price,
            user_antisurge_price,
        )

    driver_fixed_exp = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 15, 16]
    driver_taximeter_exp = [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 16]
    driver_antisurge_fixed_exp = [9, 11, 12, 14]
    driver_antisurge_taximeter_exp = [9, 10, 12, 14]
    user_fixed_exp = [1, 2, 3, 5, 6, 7, 8, 9, 11, 13, 15, 16]
    user_taximeter_exp = [1, 2, 3, 5, 6, 7, 8, 9, 10, 13, 15, 16]
    user_antisurge_fixed_exp = [9, 11, 13, 14]
    user_antisurge_taximeter_exp = [9, 10, 13, 14]

    for each in driver_fixed.values():
        assert each == driver_fixed_exp
    for each in driver_taximeter.values():
        assert each == driver_taximeter_exp
    for each in driver_antisurge_fixed.values():
        assert each == driver_antisurge_fixed_exp
    for each in driver_antisurge_taximeter.values():
        assert each == driver_antisurge_taximeter_exp

    for each in user_fixed.values():
        assert each == user_fixed_exp
    for each in user_taximeter.values():
        assert each == user_taximeter_exp
    for each in user_antisurge_fixed.values():
        assert each == user_antisurge_fixed_exp
    for each in user_antisurge_taximeter.values():
        assert each == user_antisurge_taximeter_exp

    driver_price_exp = {
        'econom': 131.0,
        'comfortplus': 256.0,
        'maybach': 1799,
        'business': 200.0,
        'minivan': 499,
        'demostand': 131.0,
        'cargo': 949,
        'ubernight': 307,
        'vip': 488.0,
    }
    driver_antisurge_price_exp = {
        'econom': 131.0,
        'comfortplus': 256.0,
        'maybach': 1799,
        'business': 200.0,
        'minivan': 499,
        'demostand': 131.0,
        'cargo': 949,
        'ubernight': 99,
        'vip': 456,
    }
    user_price_exp = {
        'econom': {'price': 131, 'strikeout': 131},
        'comfortplus': {'price': 256.0, 'strikeout': 256.0},
        'maybach': {'price': 1799, 'strikeout': 1799},
        'business': {'price': 200, 'strikeout': 200},
        'minivan': {'price': 499, 'strikeout': 499},
        'demostand': {'price': 131, 'strikeout': 131},
        'cargo': {'price': 949, 'strikeout': 949},
        'ubernight': {'price': 307, 'strikeout': 99},
        'vip': {'price': 496, 'strikeout': 432},
    }
    user_antisurge_price_exp = {
        'econom': {'price': 131, 'strikeout': 131},
        'comfortplus': {'price': 256, 'strikeout': 256},
        'maybach': {'price': 1799, 'strikeout': 1799},
        'business': {'price': 200, 'strikeout': 200},
        'minivan': {'price': 499, 'strikeout': 499},
        'demostand': {'price': 131, 'strikeout': 131},
        'cargo': {'price': 949, 'strikeout': 949},
        'ubernight': {'price': 99, 'strikeout': 99},
        'vip': {'price': 464, 'strikeout': 432},
    }

    assert driver_price == driver_price_exp
    assert driver_antisurge_price == driver_antisurge_price_exp
    assert user_price == user_price_exp
    assert user_antisurge_price == user_antisurge_price_exp

    assert data['categories']['ubernight']['user']['additional_prices'][
        'combo_order'
    ]['price'] == {'total': 308.0, 'strikeout': 99.0}
    assert data['categories']['ubernight']['user']['additional_prices'][
        'combo_inner'
    ]['price'] == {'total': 317.0, 'strikeout': 109.0}
    assert data['categories']['ubernight']['user']['additional_prices'][
        'combo_outer'
    ]['price'] == {'total': 297.0, 'strikeout': 89.0}
    check_called(mock_combo_contractors)

    if alt_offer_discount_case == 'exist':
        discounts = data['categories']['ubernight']['user'][
            'additional_prices'
        ]['alt_offer_discount']
        assert len(discounts) == 1
        assert discounts[0]['price_data']['price'] == {
            'total': 614.0,
            'strikeout': 198.0,
        }

        assert (
            not 'alt_offer_discount'
            in data['categories']['econom']['user']['additional_prices']
        )
    elif alt_offer_discount_case == 'empty':
        assert (
            not 'alt_offer_discount'
            in data['categories']['ubernight']['user']['additional_prices']
        )

    assert data['categories']['ubernight']['user']['additional_prices'][
        'full_auction'
    ]['price'] == {'total': 199.0, 'strikeout': 199.0}
    assert data['categories']['ubernight']['driver']['additional_prices'][
        'full_auction'
    ]['price'] == {'total': 199.0}


@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.experiments3(filename='exp3_combo_order_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.filldb(tariff_settings='all_fixed')
@pytest.mark.parametrize('scope', ['taxi', 'cargo'])
async def test_v2_prepare_strikeout_price_modifications_test(
        taxi_pricing_data_preparer,
        taxi_config,
        pgsql,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        combo_contractors,
        mock_combo_contractors,
        scope,
):
    if scope == 'cargo':
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                f'UPDATE price_modifications.workabilities '
                f'SET scope = \'{scope}\';',
            )
        await taxi_pricing_data_preparer.invalidate_caches()

    pre_request = utils_request.Request().set_categories(['econom'])
    pre_request.set_additional_prices(
        antisurge=False,
        strikeout=True,
        combo_order=False,
        combo_inner=False,
        combo_outer=False,
    )
    pre_request.set_need_strikeout_price_flag(True)
    pre_request.set_modifications_scope(scope)

    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    def _get_strikeout_modifications_list(_for):
        user = data['categories']['econom']['user']
        assert 'additional_payloads' in user
        assert (
            'modifications_for_strikeout_price' in user['additional_payloads']
        )
        return user['additional_payloads'][
            'modifications_for_strikeout_price'
        ][_for]

    _expected_modifications_for_fixed = [9, 11, 13]
    _expected_modifications_for_taximeter = [9, 10, 13]

    modifications_for_fixed = _get_strikeout_modifications_list('for_fixed')
    assert modifications_for_fixed == _expected_modifications_for_fixed
    modifications_for_taximeter = _get_strikeout_modifications_list(
        'for_taximeter',
    )
    assert modifications_for_taximeter == _expected_modifications_for_taximeter
    check_not_called(mock_combo_contractors)
