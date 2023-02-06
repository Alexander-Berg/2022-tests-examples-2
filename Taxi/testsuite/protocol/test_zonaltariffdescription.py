import json

import bson.objectid
import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


@pytest.fixture(name='mock_update_zonal_tariff')
def _mock_update_zonal_tariff(mockserver):
    class Context:
        response = None

    ctx = Context()

    @mockserver.json_handler(
        '/cargo_tariffs/internal/cargo-tariffs/v1/update-zonal-tariffs',
    )
    def _mock(request, *args, **kwargs):
        body = json.loads(request.get_data())
        if ctx.response is not None:
            response = ctx.response
        else:
            response = {}
            response['zonal_tariff_description'] = body[
                'zonal_tariff_description'
            ]
            response['is_updated'] = False
        return response

    ctx.mock = _mock

    return ctx


@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription(taxi_protocol, individual_tariffs_switch_on):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()
    assert len(data['max_tariffs']) > 0
    assert data['layout'] == 'tight'
    assert len(data['max_tariffs'][0]['intervals']) > 0
    assert data['paid_cancel_enabled'] is True
    classes = [tariff['class'] for tariff in data['max_tariffs']]
    assert set(classes) == set(
        ['business', 'comfortplus', 'econom', 'minivan', 'vip'],
    )


@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        '__default__': 'yataxi',
        'android': '/whitelabel/vezet',
    },
)
@pytest.mark.config(
    APPLICATION_BRAND_FILTERS={'/whitelabel/vezet': {'countries': ['rus']}},
)
def test_zonaltariffdescription_application_brand_filters(taxi_protocol):
    request = {'zone_name': 'almaty'}
    response = taxi_protocol.post(
        '3.0/zonaltariffdescription',
        request,
        headers={
            'User-Agent': (
                'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
            ),
        },
    )
    assert response.status_code == 404


def test_zonaltariffdescription_without_format_currency(taxi_protocol):
    request = {'zone_name': 'moscow', 'format_currency': False}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()
    assert len(data['max_tariffs']) > 0
    assert data['layout'] == 'tight'
    assert len(data['max_tariffs'][0]['intervals']) > 0
    assert data['paid_cancel_enabled'] is True


def test_zonaltariffdescription_with_currency_rules(taxi_protocol):
    request = {'zone_name': 'moscow', 'format_currency': True}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()
    assert len(data['max_tariffs']) > 0
    assert data['layout'] == 'tight'
    assert len(data['max_tariffs'][0]['intervals']) > 0
    assert data['paid_cancel_enabled'] is True
    assert 'currency_rules' in data


def test_zonatariffdescription_no_zone_name(taxi_protocol):
    request = {'format_currency': False}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 400
    data = response.json()
    assert data['error']['text'] == 'Bad Request'


def test_zonaltariffdescription_wrong_zone_name(taxi_protocol):
    request = {'zone_name': 'wrongzone', 'format_currency': False}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 404
    data = response.json()
    assert data['error']['text'] == 'zone not found in tariff settings'


@pytest.mark.user_experiments('disable_econom')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
                'use_legacy_experiments': True,
            },
        },
    },
)
def test_zonaltariffdescription_unforced_tariff_hidden_by_exp_legacy(
        taxi_protocol,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 0


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_econom',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
            },
        },
    },
)
def test_zonaltariffdescription_unforced_tariff_hidden_by_exp3(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 0


@pytest.mark.user_experiments('disable_econom')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'disable_econom',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'has_econom',
    (
        pytest.param(False, id='econom_disabled_by_exp'),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    FORCED_ZONALTARIFFDESCRIPTION_CATEGORIES_BY_VERSION={
                        'econom': {'android': {'version': [3, 19, 0]}},
                    },
                ),
            ],
            id='no_suitable_application_version_for_forced_econom',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    FORCED_ZONALTARIFFDESCRIPTION_CATEGORIES_BY_VERSION={
                        'econom': {'android': {'version': [3, 18, 0]}},
                    },
                ),
            ],
            id='econom_disabled_but_forced',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    FORCED_ZONALTARIFFDESCRIPTION_CATEGORIES_BY_VERSION={
                        'econom': {'android': {'version': [3, 18, 0]}},
                    },
                    TARIFF_CATEGORIES_VISIBILITY={
                        'moscow': {
                            'econom': {
                                'visible_by_default': True,
                                'visible_on_site': False,
                                'hide_experiment': 'disable_econom',
                                'use_legacy_experiments': True,
                            },
                        },
                    },
                ),
            ],
            id='econom_disabled_on_site',
        ),
    ),
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_forced_categories(
        taxi_protocol, has_econom, individual_tariffs_switch_on,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert bool(matches) == has_econom


@pytest.mark.user_experiments(
    'disable_business',
    'disable_comfortplus',
    'disable_econom',
    'disable_minivan',
    'disable_vip',
)
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'business': {
                'hide_experiment': 'disable_business',
                'use_legacy_experiments': True,
            },
            'comfortplus': {
                'hide_experiment': 'disable_comfortplus',
                'use_legacy_experiments': True,
            },
            'econom': {
                'hide_experiment': 'disable_econom',
                'use_legacy_experiments': True,
            },
            'minivan': {
                'hide_experiment': 'disable_minivan',
                'use_legacy_experiments': True,
            },
            'vip': {
                'hide_experiment': 'disable_vip',
                'use_legacy_experiments': True,
            },
        },
    },
)
def test_zonaltariffdescription_all_tariffs_hidden_by_exp_legacy(
        taxi_protocol,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 404


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_business',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_comfortplus',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_econom',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_minivan',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_vip',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'business': {'hide_experiment': 'disable_business'},
            'comfortplus': {'hide_experiment': 'disable_comfortplus'},
            'econom': {'hide_experiment': 'disable_econom'},
            'minivan': {'hide_experiment': 'disable_minivan'},
            'vip': {'hide_experiment': 'disable_vip'},
        },
    },
)
def test_zonaltariffdescription_all_tariffs_hidden_by_exp3(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 404


@pytest.mark.user_experiments('enable_econom')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'enable_econom',
                'use_legacy_experiments': True,
            },
        },
    },
)
def test_zonaltariffdescription_unforced_tariff_shown_by_exp_legacy(
        taxi_protocol,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 1


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='enable_econom',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'enable_econom',
            },
        },
    },
)
def test_zonaltariffdescription_unforced_tariff_shown_by_exp3(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    data = response.json()

    matches = [trf for trf in data['max_tariffs'] if trf['id'] == 'econom']
    assert len(matches) == 1


@pytest.mark.parametrize(
    'tariifs_enabled,supported,with_call_center',
    [
        (True, None, False),
        (False, ['category_type'], False),
        (True, ['category_type'], True),
    ],
)
@pytest.mark.filldb(tariffs='with_category')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_with_categories_type(
        taxi_protocol,
        config,
        tariifs_enabled,
        supported,
        with_call_center,
        individual_tariffs_switch_on,
):
    config.set_values(dict(INTEGRATION_TARIFFS_ENABLED=tariifs_enabled))

    request = {'zone_name': 'moscow', 'format_currency': True}
    if supported is not None:
        request['supported'] = supported

    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()

    assert len(data['max_tariffs']) > 0
    assert data['layout'] == 'tight'
    assert data['paid_cancel_enabled'] is True
    assert 'currency_rules' in data

    intervals = data['max_tariffs'][0]['intervals']
    if with_call_center:
        assert len(intervals) == 2
        for interval in intervals:
            if interval['category_type'] == 'call_center':
                assert len(interval['price_groups'][0]['prices']) == 13
            else:
                assert len(interval['price_groups'][0]['prices']) == 12
    else:
        assert len(intervals) == 1
        for interval in intervals:
            assert len(interval['price_groups'][0]['prices']) == 13


@pytest.mark.parametrize(
    'price',
    [
        (
            {
                'distance_price_intervals': [],
                'distance_price_intervals_meter_id': 0,
                'time_price_intervals': [],
                'time_price_intervals_meter_id': 1,
            },
            {
                'distance_price_intervals': [],
                'distance_price_intervals_meter_id': 1,
                'time_price_intervals': [],
                'time_price_intervals_meter_id': 0,
            },
        ),
    ],
)
def test_invalid_tariff_meters(taxi_protocol, db, price):
    almaty_tariff_id = bson.objectid.ObjectId('596cd824954073899ac1b428')

    cursor = db.tariffs.find({'_id': almaty_tariff_id})
    count = cursor.count()
    assert count == 1
    almaty_record = cursor[0]

    category = almaty_record['categories'][0]
    category['meters'] = ([{'prepaid': 0.4, 'trigger': 2}],)
    category['m'] = []
    category['special_taximeters'] = [{'price': price, 'zone_name': 'almaty'}]
    db.tariffs.update({'_id': almaty_tariff_id}, {'$set': almaty_record})

    request = {'zone_name': 'almaty'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 404


@pytest.mark.filldb(tariffs='with_zp')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_transfer_prepaid_info_name(
        taxi_protocol, individual_tariffs_switch_on,
):

    expected_transfer_names = [
        'transfer from city to vko(included 5.5 km and 3 min)',
        'transfer from city to zhukovskiy_transfer(included 0 min and 0 km)',
        'transfer from city to dme(included 30 km)',
        'transfer from city to svo(included 3 min)',
    ]

    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200

    vip = None
    for tariff in response.json()['max_tariffs']:
        if tariff['class'] == 'vip':
            vip = tariff
    assert vip is not None

    names = []
    for interval in vip['intervals']:
        for price_group in interval['price_groups']:
            if 'to_airport' in price_group['id']:
                for price in price_group['prices']:
                    names.append(price['name'])

    for exp_name in expected_transfer_names:
        assert exp_name in names


@pytest.mark.config(
    TARIFF_REQUIREMENTS_WITH_NOT_FIXED_PRICE={
        'animaltransport': {'meter_type': 'distance', 'units': 1000},
        'ski': {'meter_type': 'time', 'units': 60},
    },
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_not_fixed_price(
        taxi_protocol, individual_tariffs_switch_on,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()

    ski_price = None
    animaltransport_price = None
    bicycle_price = None
    for tariff in data['max_tariffs']:
        if tariff['class'] == 'business':
            price_group = tariff['intervals'][0]['price_groups'][0]
            for price_item in price_group['prices']:
                if price_item['id'] == 'ski':
                    ski_price = price_item['price']
                if price_item['id'] == 'animaltransport':
                    animaltransport_price = price_item['price']
                if price_item['id'] == 'bicycle':
                    bicycle_price = price_item['price']
            break

    assert ski_price == '150\xa0rub/min'
    assert animaltransport_price == '150\xa0rub/km'
    assert bicycle_price == '100\xa0rub'


@pytest.mark.filldb(tariffs='with_zp')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_transfer_many_transfer_objects_for_one_transfer_type(
        taxi_protocol, individual_tariffs_switch_on,
):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200

    vip = [x for x in response.json()['max_tariffs'] if x['class'] == 'vip']
    assert len(vip) == 1

    transfers_to_airport = []
    for interval in vip[0]['intervals']:
        for i, price_group in enumerate(interval['price_groups']):
            if 'to_airport' in price_group['id']:
                transfers_to_airport.append(price_group)

    assert len(transfers_to_airport) == 4

    expected_transfer_ids = [
        'to_airport_from_city_to_vko',
        'to_airport_from_city_to_zhukovskiy_transfer',
        'to_airport_from_city_to_dme',
        'to_airport_from_city_to_svo',
    ]

    expected_transfer_names = [
        'to_airport (transfer from city to vko)',
        'to_airport (transfer from city to zhukovskiy_transfer)',
        'to_airport (transfer from city to dme)',
        'to_airport (transfer from city to svo)',
    ]

    for i, transfer in enumerate(transfers_to_airport):
        assert transfer['id'] == expected_transfer_ids[i]
        assert transfer['name'] == expected_transfer_names[i]


@pytest.mark.config(
    ZONALTARIFFDESCRIPTION_TECHNICAL_REQUIREMENTS=['childchair_v2'],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_technical_reqs(
        taxi_protocol, db, individual_tariffs_switch_on,
):
    doc = db.tariffs.find_one({'home_zone': 'moscow', 'date_to': None})
    assert doc['_id'] is not None
    for cat in doc['categories']:
        if cat['category_type'] != 'application':
            continue
        cat['req_prices'].append({'p': 100500, 't': 'childchair_v2'})
    db.tariffs.update({'_id': doc['_id']}, doc)

    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()
    assert len(data['max_tariffs']) > 0

    prices = data['max_tariffs'][0]['intervals'][0]['price_groups'][0][
        'prices'
    ]
    assert len(prices) > 0
    assert 'childchair_moscow' in [p['id'] for p in prices]
    assert 'childchair_v2' not in [p['id'] for p in prices]


@pytest.mark.config(
    ZONALTARIFFDESCRIPTION_DISABLED_REQUIREMENTS_BY_APPLICATION=['android'],
)
def test_zonaltariffdescription_disabled_reqs_by_app(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200

    data = response.json()
    assert len(data['max_tariffs']) > 0

    prices = data['max_tariffs'][0]['intervals'][0]['price_groups'][0][
        'prices'
    ]
    assert len(prices) > 0
    assert 'childchair_moscow' not in [p['id'] for p in prices]


@pytest.mark.config(CARGO_TARIFFS_UPDATE_ZONAL_TARIFFS_ON_SERVER=True)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_updated_by_cargo_tariffs(
        taxi_protocol, mock_update_zonal_tariff, individual_tariffs_switch_on,
):
    data = {
        'is_updated': True,
        'zonal_tariff_description': {'layout': 'default'},
    }
    mock_update_zonal_tariff.response = data
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == data['zonal_tariff_description']


@pytest.mark.config(CARGO_TARIFFS_UPDATE_ZONAL_TARIFFS_ON_SERVER=True)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zonaltariffdescription_cargo_tariff_failed_without_update(
        taxi_protocol,
        mock_update_zonal_tariff,
        mockserver,
        individual_tariffs_switch_on,
):
    mock_update_zonal_tariff.response = mockserver.make_response(
        {}, status=500,
    )
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
    data = response.json()
    assert len(data['max_tariffs']) > 0
