# coding: utf-8
import copy
import datetime
import json

import pytest

from taxi import config
from taxi.core import async
from taxi.internal import dbh
from taxi.internal import tariffs_manager
from taxi.internal.dbh import tariffs


SADOVOE_POINT = [5, 0]
MOSCOW_CITY_POINT = [6, 0]
POINT_WITHOUT_POOL = [1, 1]


@pytest.mark.parametrize(
    (
        'home_zone,category_name,source_zones,source_airport,with_destination,'
        'predicted_price,expected_tariff_description'
    ),
    [
        # point inside moscow, without destination
        (
            'moscow', 'econom', {'moscow', 'cao'}, None, False, 142,
            tariffs_manager.TariffDescription(
                source_zone='moscow',
                minimal_price=99,
                time=tariffs_manager.TarifficationUnit(included=5, price=9),
                distance=tariffs_manager.TarifficationUnit(included=2, price=9),
                is_transfer=False,
                home_zone='moscow',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=15,
            )
        ),

        # point inside moscow, with destination
        (
            'moscow', 'econom', {'moscow', 'cao'}, 'dme', True, 142,
            tariffs_manager.TariffDescription(
                source_zone='moscow',
                minimal_price=99,
                time=tariffs_manager.TarifficationUnit(included=5, price=9),
                distance=tariffs_manager.TarifficationUnit(included=2, price=9),
                is_transfer=False,
                home_zone='moscow',
                with_destination=True,
                predicted_price=142,
                paid_dispatch_price=15,
            )
        ),

        # point inside suburb, without destination
        (
            'moscow', 'econom', {'suburb'}, None, False, 142,
            tariffs_manager.TariffDescription(
                source_zone='suburb',
                minimal_price=99,
                # yeah, we should use moscow taximeters
                time=tariffs_manager.TarifficationUnit(included=5, price=9),
                distance=tariffs_manager.TarifficationUnit(included=2, price=9),
                is_transfer=False,
                home_zone='moscow',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=15,
            )
        ),

        # point inside suburb, with destination
        (
            'moscow', 'econom', {'suburb'}, None, True, 142,
            tariffs_manager.TariffDescription(
                source_zone='suburb',
                minimal_price=99,
                # yeah, we should use moscow taximeters
                time=tariffs_manager.TarifficationUnit(included=5, price=9),
                distance=tariffs_manager.TarifficationUnit(included=2, price=9),
                is_transfer=False,
                home_zone='moscow',
                with_destination=True,
                predicted_price=142,
                paid_dispatch_price=15,
            )
        ),

        # point inside airport with defined transfers_config
        (
            'moscow', 'econom', {'svo', 'suburb'}, 'svo', False, 142,
            tariffs_manager.TariffDescription(
                source_zone='svo',
                minimal_price=1100,
                # get taximeter from zonal_prices
                time=tariffs_manager.TarifficationUnit(included=90, price=9),
                distance=None,
                is_transfer=True,
                home_zone='moscow',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=0,
            )
        ),

        # point inside airport with undefined transfers_config
        (
            'moscow', 'econom', {'vko', 'suburb'}, 'vko', False, 142,
            tariffs_manager.TariffDescription(
                source_zone='vko',
                minimal_price=700,
                time=tariffs_manager.TarifficationUnit(included=90, price=9),
                distance=None,
                is_transfer=True,
                home_zone='moscow',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=0,
            )
        ),

        # point inside some non-airport transfer zone with undefined transfers_config
        (
            'moscow', 'econom', {'vko', 'suburb'}, None, False, 142,
            tariffs_manager.TariffDescription(
                source_zone='suburb',
                minimal_price=99,
                time=tariffs_manager.TarifficationUnit(included=5, price=9),
                distance=tariffs_manager.TarifficationUnit(included=2, price=9),
                is_transfer=False,
                home_zone='moscow',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=15,
            )
        ),

        # point inside airport with "not fixed" transfer
        (
            'spb', 'econom', {'spb_airport', 'suburb'}, 'spb_airport', False, 142,
            tariffs_manager.TariffDescription(
                source_zone='spb_airport',
                minimal_price=149,
                time=tariffs_manager.TarifficationUnit(included=0, price=5),
                distance=tariffs_manager.TarifficationUnit(included=0, price=15),
                is_transfer=True,
                home_zone='spb',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=0,
            )
        ),

        # point inside spb
        (
            'spb', 'econom', {'spb'}, None, False, 142,
            tariffs_manager.TariffDescription(
                source_zone='spb',
                minimal_price=49,
                time=tariffs_manager.TarifficationUnit(included=0, price=5),
                distance=tariffs_manager.TarifficationUnit(included=0, price=15),
                is_transfer=False,
                home_zone='spb',
                with_destination=False,
                predicted_price=142,
                paid_dispatch_price=0,
            )
        ),
    ]
)
@pytest.mark.filldb(
    tariffs='for_tariff_description_test',
    tariff_settings='for_tariff_description_test',
)
@pytest.inline_callbacks
def test_build_tariff_description(home_zone, category_name, source_zones,
                                  source_airport, with_destination, predicted_price,
                                  expected_tariff_description):

    tariff = yield dbh.tariffs.Doc.find_active(
        home_zone, datetime.datetime(2100, 1, 1, 17, 0)
    )
    tariff_category = next(category for category in tariff.categories
                           if category.category_name == category_name)
    tariff_settings = yield dbh.tariff_settings.Doc.find_by_home_zone(home_zone)
    category_settings = tariff_settings.for_category(category_name)

    result = tariffs_manager.build_tariff_description(
        tariff_category, category_settings, home_zone, source_zones,
        source_airport, with_destination, predicted_price,
    )
    assert expected_tariff_description == result


@pytest.inline_callbacks
def test_get_all_home_areas():
    result = ['moscow', 'mytishchi']
    all_home_areas = yield tariffs_manager.get_all_home_areas()

    # Not using set(A) == set(B), because amount and return type also matters.
    assert (all_home_areas == [result[0], result[1]] or
            all_home_areas == [result[1], result[0]])


@pytest.inline_callbacks
def test_all_categories():
    all_categories = yield tariffs_manager.all_categories()
    assert 3 == len(all_categories)
    assert set(['econom', 'comfort', 'comfortplus']) == set(all_categories)


@pytest.mark.filldb(_fill=False)
def test_category_info(load):
    tariff = tariffs.Doc(json.loads(load('tariff_with_meters_original.json')))
    category = tariff.categories[0]
    info = tariffs_manager.CategoryInfo(category)
    assert 19 == info.included_distance_units('moscow')
    assert 10 == info.included_time_units('moscow')
    assert 23 == info.included_distance_units('suburb')
    assert 10 == info.included_time_units('suburb')

    assert 16 == info.time_price_after_included(['moscow'])
    assert 10 == info.distance_price_after_included(['moscow'])
    assert 16 == info.time_price_after_included(['suburb'])
    assert 20 == info.distance_price_after_included(['suburb'])


# checking that BulkTariffs is in sync with tariffs.Doc.find_active
@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.mark.parametrize('zone,timestamp', [
    ('ekb', datetime.datetime(2016, 4, 1, 0, 0, 0)),
    ('ekb', datetime.datetime(2016, 4, 1, 0, 3, 0)),
    ('moscow', datetime.datetime(2016, 4, 1, 0, 3, 0)),
    ('moscow', datetime.datetime(2016, 4, 1, 0, 5, 0)),
    ('moscow', datetime.datetime(2016, 4, 1, 0, 3, 0)),
    ('moscow', datetime.datetime(2099, 4, 1, 0, 5, 0)),
])
@pytest.inline_callbacks
def test_bulk_tariffs(zone, timestamp):
    bulk_tariffs = yield tariffs_manager.BulkTariffs.create()
    tariff = bulk_tariffs._get_active_tariff_in_zone(zone, timestamp)
    expected_tariff = yield tariffs.Doc.find_active(zone, timestamp)
    assert tariff._id == expected_tariff._id


@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.mark.parametrize('zone,timestamp,expected_exception', [
    ('unknown_zone', datetime.datetime(2016, 4, 1),
     tariffs_manager.NoTariffsInZone),
    ('moscow', datetime.datetime(2000, 4, 1),
     tariffs_manager.NoActiveTariffsInZone),
])
@pytest.inline_callbacks
def test_bulk_tariffs_failure(zone, timestamp, expected_exception):
    bulk_tariffs = yield tariffs_manager.BulkTariffs.create()
    with pytest.raises(expected_exception):
        bulk_tariffs._get_active_tariff_in_zone(zone, timestamp)


@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.inline_callbacks
def test_bulk_tariffs_mytishchi():
    # checking that mytishchi crutches are turned off
    bulk_tariffs = yield tariffs_manager.BulkTariffs.create()
    with pytest.raises(tariffs_manager.NoActiveTariffsInZone):
        bulk_tariffs._get_active_tariff_in_zone(
            'mytishchi', datetime.datetime(2016, 12, 31)
        )


@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.mark.parametrize('zone,timestamp,expected_cost', [
    ('moscow', datetime.datetime(2016, 4, 1, 8, 0), 100),
    ('moscow', datetime.datetime(2016, 4, 1, 12, 0), 200),
])
@pytest.inline_callbacks
def test_bulk_tariffs_get_minimal_cost(zone, timestamp, expected_cost):
    bulk_tariffs = yield tariffs_manager.BulkTariffs.create()
    city_doc = {'tz': 'Europe/Moscow', 'country': 'rus'}
    order = dbh.orders.Doc()
    order.performer.tariff.cls = 'econom'
    order.request.due = timestamp
    order.nearest_zone = zone
    actual_cost = yield bulk_tariffs.get_minimal_cost(order, city_doc)
    assert actual_cost == expected_cost


@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.mark.parametrize('zone,timestamp,expected_cost', [
    ('moscow', datetime.datetime(2016, 4, 1, 8, 0), 100),
])
@pytest.inline_callbacks
def test_bulk_tariffs_loads_new_tariffs_when_get_minimal_cost_for_new_order(zone, timestamp, expected_cost):
    # Create BulkTariff manually with one tariff.
    tariff = dbh.tariffs.Doc()
    tariff.home_zone = 'TEST_ZONE'
    bulk_tariffs = tariffs_manager.BulkTariffs([tariff])

    # Try to get minimal cost for tariff that exists in DB but not present in the memory.
    # Successfully finds cost for order with set category id.
    city_doc = {'tz': 'Europe/Moscow'}
    order = dbh.orders.Doc()
    order.request.due = timestamp
    order.nearest_zone = zone

    with pytest.raises(tariffs_manager.NoMinimalCostError):
        order.performer.tariff.category_id = 5
        yield bulk_tariffs.get_minimal_cost(order, city_doc)

    order.performer.tariff.category_id = 50001
    actual_cost = yield bulk_tariffs.get_minimal_cost(order, city_doc)
    assert actual_cost == expected_cost


@pytest.mark.filldb(
    _specified=True,
    tariffs='for_bulk_tariffs_test',
)
@pytest.mark.parametrize('zone,timestamp,expected_cost', [
    ('moscow', datetime.datetime(2016, 4, 1, 8, 0), 100),
])
@pytest.inline_callbacks
def test_bulk_tariffs_doesnt_load_new_tariffs_when_get_minimal_cost_for_old_order(zone, timestamp, expected_cost):
    # Create BulkTariff manually with one tariff.
    tariff = dbh.tariffs.Doc()
    tariff.home_zone = 'TEST_ZONE'
    bulk_tariffs = tariffs_manager.BulkTariffs([tariff])

    # Try to get minimal cost for tariff that exists in DB but not present in the memory.
    # Raises for old orders (without category id).
    with pytest.raises(tariffs_manager.NoMinimalCostError):
        city_doc = {'tz': 'Europe/Moscow'}
        order = dbh.orders.Doc()
        order.performer.tariff.cls = 'econom'
        order.request.due = timestamp
        order.nearest_zone = zone
        yield bulk_tariffs.get_minimal_cost(order, city_doc)


@pytest.mark.parametrize('test_case,round_factor', [
    ('with_meters', 1),
    ('with_step', 3),
    ('with_jamsless_transfers', 1)
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_to_tariffs_31(test_case, round_factor, patch, load):
    @patch('taxi.internal.city_kit.currency_manager.get_round_factor')
    @pytest.inline_callbacks
    def _get_round_factor(currency):
        assert currency == 'RUB'
        yield async.return_value(round_factor)

    tariff_file_name = 'tariff_{}_original.json'.format(test_case)
    tariff31_file_name = 'tariff_{}_converted.json'.format(test_case)

    tariff = tariffs.Doc(json.loads(load(tariff_file_name)))
    expected_tariffs31 = json.loads(load(tariff31_file_name))

    for category, expected in zip(tariff.categories, expected_tariffs31):
        generated_tariff_31 = yield tariffs_manager.to_tariffs_31(category)
        print 'ACTUAL\n\n{}\n'.format(json.dumps(generated_tariff_31))
        print 'EXPECTED\n\n{}\n'.format(json.dumps(expected))
        print (
            'In case of problems, better to compare using '
            'http://benjamine.github.io/jsondiffpatch/demo/index.html'
        )
        assert generated_tariff_31 == expected


def _make_category(
        category_id, minimal, waiting_price, distance_intervals,
        time_intervals, paid_dispatch_intervals, special_distance_intervals,
        special_time_intervals, special_zone_name, zonal_distance_intervals,
        zonal_time_intervals, zonal_minimal, zonal_once, zonal_waiting_price,
        luggage_price, waiting_in_transit):
    tariff = dbh.tariffs.Doc()
    tariff.categories = []
    category = tariff.categories.new()
    category.tariff_id = category_id
    category.minimal = minimal
    category.waiting_price = waiting_price
    category.summable_requirements = []
    luggage_requirement = category.summable_requirements.new()
    luggage_requirement.type = 'luggage'
    luggage_requirement.max_price = luggage_price
    waiting_in_transit_requirement = category.summable_requirements.new()
    waiting_in_transit_requirement.type = 'waiting_in_transit'
    waiting_in_transit_requirement.max_price = waiting_in_transit

    _add_all_intervals(
        category=category,
        distance_intervals=distance_intervals,
        time_intervals=time_intervals,
        paid_dispatch_intervals=paid_dispatch_intervals,
        special_distance_intervals=special_distance_intervals,
        special_time_intervals=special_time_intervals,
        st_zone_name=special_zone_name,
        zonal_distance_intervals=zonal_distance_intervals,
        zonal_time_intervals=zonal_time_intervals,
        zonal_minimal=zonal_minimal,
        zonal_once=zonal_once,
        zonal_waiting_price=zonal_waiting_price,
    )
    return category


def _add_all_intervals(
        category, distance_intervals, time_intervals, paid_dispatch_intervals,
        special_distance_intervals, special_time_intervals, st_zone_name,
        zonal_distance_intervals, zonal_time_intervals,
        zonal_minimal, zonal_once, zonal_waiting_price):
    category.distance_price_intervals = []
    _add_intervals(
        distance_intervals,
        category.distance_price_intervals,
    )

    category.time_price_intervals = []
    _add_intervals(
        time_intervals,
        category.time_price_intervals,
    )

    category.paid_dispatch_distance_price_intervals = []
    _add_intervals(
        paid_dispatch_intervals,
        category.paid_dispatch_distance_price_intervals,
    )
    category.special_taximeters = []
    special = category.special_taximeters.new()

    special.zone_name = st_zone_name

    special.price.distance_price_intervals = []
    _add_intervals(
        special_distance_intervals,
        special.price.distance_price_intervals,
    )

    special.price.time_price_intervals = []
    _add_intervals(
        special_time_intervals,
        special.price.time_price_intervals,
    )

    category.zonal_prices = []
    zonal = category.zonal_prices.new()
    zonal.price.waiting_price = zonal_waiting_price
    zonal.price.minimal = zonal_minimal
    zonal.price.once = zonal_once

    zonal.price.distance_price_intervals = []
    _add_intervals(
        zonal_distance_intervals,
        zonal.price.distance_price_intervals,
    )

    zonal.price.time_price_intervals = []
    _add_intervals(
        zonal_time_intervals,
        zonal.price.time_price_intervals,
    )


def _add_intervals(intervals, dbh_intervals):
    for begin, end, price in intervals:
        new = dbh_intervals.new()
        new.begin = begin
        if end is not None:
            new.end = end
        new.price = price


_MINIMAL_SURGE_MULTIPLIER = 2.1
_TIME_SURGE_MULTIPLIER = 2.5
_DISTANCE_SURGE_MULTIPLIER = 2.3
_SURGE_PRICE = 2.6
_SURGE_SURCHARGE = 100.0
_PRICE_MULTIPLIER = 0.99


def _waiting_price(surge, price_multiplier=None, base_price=None):
    return (base_price or 5) * surge * (price_multiplier or 1.0)


def _zonal_waiting_price(surge, price_multiplier=1.0):
    return 6 * surge * price_multiplier


def _waiting_in_transit_price(surge, price_multiplier=1.0):
    return 100 * surge * price_multiplier


_SURGED_ORDINARY_CATEGORY = _make_category(
    category_id='some_ordinary_category_id',
    minimal=199 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE,
    waiting_price=_waiting_price(_TIME_SURGE_MULTIPLIER),
    # (begin, end, price)
    distance_intervals=[
        (0, 2000, 9 * _DISTANCE_SURGE_MULTIPLIER),
        (2000, None, 11 * _DISTANCE_SURGE_MULTIPLIER)
    ],
    # (begin, end, price)
    time_intervals=[
        (0, 20, 15 * _TIME_SURGE_MULTIPLIER),
        (20, None, 30 * _TIME_SURGE_MULTIPLIER)
    ],
    paid_dispatch_intervals=[(0, None, 20 * _DISTANCE_SURGE_MULTIPLIER)],
    special_distance_intervals=[
        (0, None, 19 * _DISTANCE_SURGE_MULTIPLIER)
    ],
    special_time_intervals=[
        (20, None, 30 * _TIME_SURGE_MULTIPLIER)
    ],
    special_zone_name='spb',
    zonal_distance_intervals=[
        (0, None, 29 * _DISTANCE_SURGE_MULTIPLIER)
    ],
    zonal_time_intervals=[
        (20, None, 39 * _TIME_SURGE_MULTIPLIER)
    ],
    zonal_minimal=1500 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE,
    zonal_once=1600 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE,
    zonal_waiting_price=_zonal_waiting_price(_TIME_SURGE_MULTIPLIER),
    # surge is not applied to the req_prices
    luggage_price=50,
    waiting_in_transit=100 * _TIME_SURGE_MULTIPLIER,
)

_SURGED_CATEGORY_WITH_MULTIPLIER = _make_category(
    category_id='some_ordinary_category_id',
    minimal=(199 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE) * _PRICE_MULTIPLIER,
    waiting_price=_waiting_price(_TIME_SURGE_MULTIPLIER, _PRICE_MULTIPLIER),
    # (begin, end, price)
    distance_intervals=[
        (0, 2000, 9 * _DISTANCE_SURGE_MULTIPLIER * _PRICE_MULTIPLIER),
        (2000, None, 11 * _DISTANCE_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    # (begin, end, price)
    time_intervals=[
        (0, 20, 15 * _TIME_SURGE_MULTIPLIER * _PRICE_MULTIPLIER),
        (20, None, 30 * _TIME_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    paid_dispatch_intervals=[
        (0, None, 20 * _DISTANCE_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    special_distance_intervals=[
        (0, None, 19 * _DISTANCE_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    special_time_intervals=[
        (20, None, 30 * _TIME_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    special_zone_name='spb',
    zonal_distance_intervals=[
        (0, None, 29 * _DISTANCE_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    zonal_time_intervals=[
        (20, None, 39 * _TIME_SURGE_MULTIPLIER * _PRICE_MULTIPLIER)
    ],
    zonal_minimal=(1500 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE) * _PRICE_MULTIPLIER,
    zonal_once=(1600 * _MINIMAL_SURGE_MULTIPLIER + _SURGE_SURCHARGE) * _PRICE_MULTIPLIER,
    zonal_waiting_price=_zonal_waiting_price(_TIME_SURGE_MULTIPLIER, _PRICE_MULTIPLIER),
    # surge is not applied to the req_prices
    luggage_price=50 * _PRICE_MULTIPLIER,
    waiting_in_transit=100 * _TIME_SURGE_MULTIPLIER * _PRICE_MULTIPLIER,
)


def _with_params(category, new_id=None, new_waiting_price=None,
                 new_zonal_waiting_price=None, new_waiting_in_transit=None):
    category = copy.deepcopy(category)
    if new_id is not None:
        category.tariff_id = new_id
    if new_waiting_price is not None:
        category.waiting_price = new_waiting_price
    if new_zonal_waiting_price is not None:
        category.zonal_prices[0].price.waiting_price = new_zonal_waiting_price
    if new_waiting_in_transit is not None:
        for req in category.summable_requirements:
            if req.type == 'waiting_in_transit':
                req.max_price = new_waiting_in_transit
    return category


_SURGE_CATEGORY_ID = (
    'surge--'
    'some_ordinary_category_id--'
    'distance_2.3-'
    'time_2.5-'
    'minimal_2.1-'
    'surcharge_100.0'
)

_ORDINARY_CATEGORY = object()


@pytest.mark.parametrize('apply_clean_surge_to_waiting_price', [True, False])
@pytest.mark.parametrize('category_id,surge_info,expected_category', [
    (
        'some_ordinary_category_id',
        tariffs_manager.CategoryModifiers(
            minimal=_MINIMAL_SURGE_MULTIPLIER,
            time=_TIME_SURGE_MULTIPLIER,
            distance=_DISTANCE_SURGE_MULTIPLIER,
            hidden=False,
            sp=_SURGE_PRICE,
            included=[],
            surcharge=_SURGE_SURCHARGE,
            multiplier=1,
            tariff_requirement=None,
        ),
        _SURGED_ORDINARY_CATEGORY
    ),
    (
        'some_ordinary_category_id',
        tariffs_manager.CategoryModifiers(
            minimal=_MINIMAL_SURGE_MULTIPLIER,
            time=_TIME_SURGE_MULTIPLIER,
            distance=_DISTANCE_SURGE_MULTIPLIER,
            hidden=False,
            sp=_SURGE_PRICE,
            included=[],
            surcharge=_SURGE_SURCHARGE,
            multiplier=_PRICE_MULTIPLIER,
            tariff_requirement=None,
        ),
        _SURGED_CATEGORY_WITH_MULTIPLIER
    ),
    (
        'some_ordinary_category_id',
        tariffs_manager.CategoryModifiers(
            minimal=_MINIMAL_SURGE_MULTIPLIER,
            time=_TIME_SURGE_MULTIPLIER,
            distance=_DISTANCE_SURGE_MULTIPLIER,
            hidden=False,
            sp=None,
            included=[],
            surcharge=_SURGE_SURCHARGE,
            multiplier=1,
            tariff_requirement=None,
        ),
        _SURGED_ORDINARY_CATEGORY
    ),
    (
        'some_ordinary_category_id',
        tariffs_manager.CategoryModifiers(
            minimal=_MINIMAL_SURGE_MULTIPLIER,
            time=_TIME_SURGE_MULTIPLIER,
            distance=_DISTANCE_SURGE_MULTIPLIER,
            hidden=False,
            sp=None,
            included=[],
            surcharge=_SURGE_SURCHARGE,
            multiplier=_PRICE_MULTIPLIER,
            tariff_requirement=None,
        ),
        _SURGED_CATEGORY_WITH_MULTIPLIER
    ),
])
@pytest.mark.filldb(
    tariffs='for_make_category_with_surge_price_test'
)
@pytest.inline_callbacks
def test_make_category_with_surge_price(category_id, surge_info,
                                        expected_category,
                                        apply_clean_surge_to_waiting_price):
    yield config.CLEAN_SURGE_TO_WAITING_PRICE_APPLIANCE.save(
        {
            '__default__': False,
            'spb': apply_clean_surge_to_waiting_price
        }
    )

    if apply_clean_surge_to_waiting_price and surge_info.sp:
        expected_category = _with_params(
            expected_category,
            new_waiting_price=_waiting_price(
                surge_info.sp, surge_info.multiplier
            ),
            new_zonal_waiting_price=_zonal_waiting_price(
                surge_info.sp, surge_info.multiplier
            ),
            new_waiting_in_transit=_waiting_in_transit_price(
                surge_info.sp, surge_info.multiplier
            )
        )

    category = yield dbh.tariffs.find_category_by_id(category_id)
    actual_category = yield tariffs_manager.make_category_with_surge_price(
        category=category,
        surge_info=surge_info,
        home_zone='spb'
    )
    # TODO(aershov182): remove dict
    assert dict(actual_category) == dict(expected_category)


@pytest.mark.parametrize('send_sp,expected_id', [
    (
        True,
        'surge--id12345--'
        'minimal_0.93-distance_3.1416-time_3.1416-hidden_0-sp_1.2-'
        'included_1_13_9-surcharge_100.0-multiplier_0.95'
    ),
    (
        False,
        'surge--id12345--'
        'minimal_0.93-distance_3.1416-time_3.1416-hidden_0-'
        'included_1_13_9-surcharge_100.0-multiplier_0.95'
    ),
])
@pytest.inline_callbacks
def test_make_modified_tariff_id(send_sp, expected_id):
    category_id = 'id12345'
    surge_mult = 3.1416
    included = [1, 13, 9]
    surge_surcharge = 100.0
    minimal_price = 90.0
    price_multiplier = 0.95
    minimal_multiplier = 0.93
    surge_price = 1.2
    tariff_requirement = None

    yield config.SEND_CLEAN_SURGE_TO_SETCAR.save(send_sp)

    tariff_id = yield tariffs_manager.get_modified_tariff_id(
        category_id, surge_mult, True, False, surge_price, included,
        minimal_price, surge_surcharge, price_multiplier, minimal_multiplier,
        tariff_requirement
    )
    assert tariff_id == expected_id


@pytest.mark.filldb(
    tariffs='for_make_category_with_surge_price_test'
)
@pytest.mark.parametrize(
    'apply_clean_surge_to_waiting_price,modifiers_category_ids,'
    'expected_categories,with_waiting_price,with_zonal_waiting_price', [
        (
            False,
            [
                _SURGE_CATEGORY_ID,
                'some_ordinary_category_id',
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,
                    new_id=_SURGE_CATEGORY_ID,
                ),
                _ORDINARY_CATEGORY,
            ],
            True,
            True,
        ),
        (
            False,
            [
                _SURGE_CATEGORY_ID + '-sp_2.8',
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,  # ignore sp
                    new_id=_SURGE_CATEGORY_ID + '-sp_2.8',
                ),
            ],
            True,
            True,
        ),
        (
            True,
            [
                _SURGE_CATEGORY_ID
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,  # fallback to surge.time if no sp
                    new_id=_SURGE_CATEGORY_ID,
                ),
            ],
            True,
            True,
        ),
        (
            True,
            [
                _SURGE_CATEGORY_ID + '-sp_2.8',
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,
                    new_id=_SURGE_CATEGORY_ID + '-sp_2.8',
                    new_waiting_price=_waiting_price(2.8),
                    new_zonal_waiting_price=_zonal_waiting_price(2.8),
                    new_waiting_in_transit=_waiting_in_transit_price(2.8),
                ),
            ],
            True,
            True,
        ),
        (
            True,
            [
                _SURGE_CATEGORY_ID + '-sp_2.8',
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,
                    new_id=_SURGE_CATEGORY_ID + '-sp_2.8',
                    new_waiting_price=_waiting_price(2.8, base_price=30),
                    new_zonal_waiting_price=_zonal_waiting_price(2.8),
                    new_waiting_in_transit=_waiting_in_transit_price(2.8),
                ),
            ],
            False,
            True,
        ),
        (
            True,
            [
                _SURGE_CATEGORY_ID + '-sp_2.8',
            ],
            [
                _with_params(
                    _SURGED_ORDINARY_CATEGORY,
                    new_id=_SURGE_CATEGORY_ID + '-sp_2.8',
                    new_waiting_price=_waiting_price(2.8, base_price=30),
                    new_zonal_waiting_price=_waiting_price(2.8, base_price=39),
                    new_waiting_in_transit=_waiting_in_transit_price(2.8),
                ),
            ],
            False,
            False,
        ),
    ]
)
@pytest.inline_callbacks
def test_find_categories_for_taximeter_api(apply_clean_surge_to_waiting_price,
                                           modifiers_category_ids,
                                           expected_categories,
                                           with_waiting_price,
                                           with_zonal_waiting_price):
    yield config.CLEAN_SURGE_TO_WAITING_PRICE_APPLIANCE.save(
        {
            '__default__': False,
            'spb': apply_clean_surge_to_waiting_price
        }
    )

    if not with_waiting_price:
        yield dbh.tariffs.Doc.update(
            {'categories': {'$exists': True}},
            {'$unset': {'categories.$.waiting_price': ''}},
            multi=True
        )

    if not with_zonal_waiting_price:
        yield dbh.tariffs.Doc.update(
            {'categories': {'$exists': True}},
            {'$unset': {'categories.$.zp.0.p.waiting_price': ''}},
            multi=True
        )

    data = yield tariffs_manager.find_categories_for_taximeter_api(
        modifiers_category_ids
    )
    expected_categories = [
        (
            (
                yield dbh.tariffs.find_category_by_id(
                    'some_ordinary_category_id'
                )
            )
            if category is _ORDINARY_CATEGORY
            else category
        )
        for category in expected_categories
    ]
    actual_categories = [datum.category for datum in data]
    assert sorted(actual_categories) == sorted(expected_categories)


@pytest.mark.filldb(
    tariffs='for_get_pair_of_overlapping_categories_test'
)
@pytest.mark.parametrize('tariff_id', [
    'some_overlapping_tariff_id',
    # 21:00 - 07:59 intersects 01:00 - 02:00
    'some_overlapping_splitted_tariff_id',
    # weekend overlap
    'some_overlapping_everyday_tariff_id',
])
@pytest.inline_callbacks
def test_get_pair_of_overlapping_categories(tariff_id):
    tariff = yield dbh.tariffs.Doc.find_one_by_id(tariff_id)
    actual_result = tariffs_manager.get_pair_of_overlapping_categories(tariff)
    assert bool(actual_result)


@pytest.mark.filldb(
    tariffs='for_get_pair_of_overlapping_categories_test'
)
@pytest.mark.parametrize('tariff_id', [
    'some_no_overlapping_tariff_id',
    # express & econom overlaps but they're different categories, so it's okay
    'some_no_overlapping_same_category_tariff_id',
    'some_no_overlapping_splitted_tariff_id',
    # express & express overlaps but have different dt
    'some_no_overlapping_work_weekend_tariff_id',
    # we ignore dayoff
    'some_no_overlapping_dayoff_dt_tariff_id',
    # no overlapping cause different category_type
    'some_no_overlapping_category_type_tariff_id'
])
@pytest.inline_callbacks
def test_get_pair_of_overlapping_categories_error(tariff_id):
    tariff = yield dbh.tariffs.Doc.find_one_by_id(tariff_id)
    with pytest.raises(tariffs_manager.NoOverlappingCategoriesError):
        tariffs_manager.get_pair_of_overlapping_categories(tariff)


@pytest.mark.filldb(
    tariff_settings='subzones'
)
@pytest.mark.parametrize('hz,point,expected', [
    ('moscow', SADOVOE_POINT, ['comfort', 'pool']),
    ('moscow', MOSCOW_CITY_POINT, ['comfort', 'pool']),
    ('moscow', POINT_WITHOUT_POOL, ['comfort'])
])
@pytest.inline_callbacks
def test_get_categories_available_in_point(hz, point, expected, patch):

    @patch('taxi.external.taxi_protocol.resolve_zones')
    @async.inline_callbacks
    def resolve_zones(point, allowed_zones):
        points_and_zones = [
            (SADOVOE_POINT, {'sadovoe_koltso'}),
            (MOSCOW_CITY_POINT, {'moscow_city'}),
        ]
        for zone_point, zones in points_and_zones:
            if zone_point == point:
                break
        else:
            zones = set()
        yield
        async.return_value(list(zones.intersection(allowed_zones)))

    doc = yield dbh.tariff_settings.Doc.find_by_home_zone(hz)
    categories = yield tariffs_manager.get_categories_available_in_point(
        doc.categories, point
    )
    assert sorted(
        [category.category_name for category in categories]
    ) == sorted(expected)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('brand,expected', [
    ('yataxi', set([
        'business', 'business2', 'comfortplus', 'econom', 'express',
        'minivan', 'pool', 'vip'
    ])),
    ('yauber', set(['uberx', 'uberselect', 'uberblack', 'uberkids'])),
    ('yango', set([
        'business', 'business2', 'comfortplus', 'econom', 'express',
        'minivan', 'pool', 'vip'
    ]))
])
@pytest.inline_callbacks
def test_get_categories_for_brand(brand, expected):
    categories = yield tariffs_manager.get_categories_for_brand(brand)
    assert categories == expected


DEFAULT_VISIBILITY_CONFIG = {
    'moscow': {
        'business': {
            'visible_by_default': False,
        },
        'comfortplus': {
            'visible_by_default': False,
            'show_experiment': 'show_comfortplus',
        },
        'vip': {
            'visible_by_default': True,
            'hide_experiment': 'hide_vip',
        },
        'express': {
            'visible_by_default': True,
            'hide_experiment': 'hide_express',
            'show_experiment': 'show_express',
        }
    },
    '__default__': {
        'pool': {
            'visible_by_default': False,
        }
    }
}
