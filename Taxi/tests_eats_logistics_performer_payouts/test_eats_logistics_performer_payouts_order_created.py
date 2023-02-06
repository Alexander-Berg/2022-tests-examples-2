# pylint: disable=import-error

import pytest


PG_SCHEMA = 'eats_logistics_performer_payouts'
PG_FILES = ['eats_logistics_performer_payouts/insert_all_factors.sql']


def make_kwargs(claim_uuid, order_nr, place_id):
    json = {
        'order_nr': order_nr,
        'claim_id': claim_uuid,
        'corp_client_alias': 'eats',
        'attempt': 1,
    }
    if place_id is not None:
        json['place_id'] = place_id
    return json


CATALOG_PLACES_JSON = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {'id': 2, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {'id': 2, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.526396503606774, 55.75898074159372]},
        'region': {'id': 3, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
]


# The minimal data to satisfy claims/full parser.
ORDERSHISTORY_ORDER_BASE = {
    'order_id': '000000-000000',
    'place_id': 1873,
    'status': 'in_progress',
    'source': 'eda',
    'delivery_location': {'lat': 55.737293, 'lon': 37.640197},
    'total_amount': '742.00',
    'is_asap': True,
    'created_at': '2022-05-31T10:39:23+00:00',
    'flow_type': 'native',
}

HANDLER_ORDERS_LIST = '/eats-ordershistory/internal/v1/get-orders/list'


def mk_json_orders_list(order_nr, place_id):
    order_json = ORDERSHISTORY_ORDER_BASE
    order_json['order_id'] = order_nr
    order_json['place_id'] = place_id
    json = {'orders': [order_json]}
    return json


HANDLER_SURGE_LEVEL = '/eats-surge-resolver/api/v1/surge-level'


def mk_json_surge_level(place_id, load_level, busy=None, free=None):
    place_json = {
        'placeId': place_id,
        'nativeInfo': {
            'surgeLevel': 0,
            'loadLevel': load_level,
            'deliveryFee': 228.0,
        },
        'taxiInfo': {'surgeLevel': 8, 'show_radius': 3000.0},
        'calculatorName': 'calc_surge_eats_dummy_dummy',
    }
    if busy is not None:
        place_json['nativeInfo']['busy'] = busy
    if free is not None:
        place_json['nativeInfo']['free'] = free
    json = {'jsonrpc': '2.0', 'id': 1, 'result': [place_json]}
    return json


TESTPT_CDM_FACTOR = 'test_courier_demand_multiplier_factor'


EXPERIMENT_DEFAULT_JSON = {
    'pipeline_name': 'courier_demand_pclinear',
    'coeff_basic': 1.1,
    'coeff_low_density': 1.4,
    'coeff_ll_min': 50,
    'coeff_ll_max': 75,
    'coeff_surge_slope': 14.0,
}

EXPERIMENT_REGION3_JSON = {
    'pipeline_name': 'courier_demand_pclinear',  # Shall be opt. Why is not?
    'coeff_basic': 1.1,
    'coeff_low_density': 1.4,
    'coeff_ll_min': 20,
    'coeff_ll_max': 40,
    'coeff_surge_slope': 20.0,
}

CLAUSE_REGION3_JSON = {
    'title': '1',
    'value': EXPERIMENT_REGION3_JSON,
    'extend_method': 'extend',
    'predicate': {
        'init': {'set': [3], 'arg_name': 'region_id', 'set_elem_type': 'int'},
        'type': 'in_set',
    },
}


def tp_courier_demand_multiplier_ft(data, load_level, expected_cdm):
    assert data['id']['type'] == 'order'
    coeff_factor = data['factors'][0]
    assert coeff_factor['name'] == 'courier_demand_multiplier'
    assert coeff_factor['value'] == '{0:.4g}'.format(expected_cdm)
    ll_factor = data['factors'][1]
    assert ll_factor['name'] == 'coeff_load_level'
    assert ll_factor['value'] == load_level


CLAIM_UUID = 'aafd000000000000cdee000000000000'
ORDER_NR = '990000-120000'
DFT_PLACE_ID = 1


@pytest.mark.experiments3(
    name='eats_pauouts_courier_demand_pipeline_arguments',
    consumers=['eats-logistics-performer-payouts/courier-demand-calculator'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value=EXPERIMENT_DEFAULT_JSON,
    clauses=[CLAUSE_REGION3_JSON],
)
@pytest.mark.pgsql(PG_SCHEMA, files=PG_FILES)
@pytest.mark.eats_catalog_storage_cache(CATALOG_PLACES_JSON)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
@pytest.mark.parametrize(
    'place_id,load_level,expected_cdm,call_cnt_map',
    [
        pytest.param(None, 73, 1.1, {HANDLER_ORDERS_LIST: 1}, id='old spec'),
        pytest.param(1, 73, 1.1, {HANDLER_ORDERS_LIST: 0}, id='happy path'),
        pytest.param(
            3, 73, 3.0, {HANDLER_ORDERS_LIST: 0}, id='experimental region',
        ),
    ],
)
async def test_handle_order_created(
        call_cnt_map,
        expected_cdm,
        load_level,
        mockserver,
        place_id,
        stq_runner,
        testpoint,
):
    claim_uuid = CLAIM_UUID
    order_nr = ORDER_NR
    mk_place_id = place_id if place_id is not None else DFT_PLACE_ID

    @mockserver.json_handler(HANDLER_ORDERS_LIST)
    def orders_list_handler(request):
        return mk_json_orders_list(order_nr, mk_place_id)

    @mockserver.json_handler(HANDLER_SURGE_LEVEL)
    def surge_level_handler(request):
        return mk_json_surge_level(mk_place_id, load_level)

    @testpoint(TESTPT_CDM_FACTOR)
    def cdm_factor_tp(data):
        tp_courier_demand_multiplier_ft(data, load_level, expected_cdm)

    await stq_runner.eats_logistics_performer_payouts_order_created.call(
        task_id='test_task',
        kwargs=make_kwargs(claim_uuid, order_nr, place_id),
    )
    assert (
        orders_list_handler.times_called == call_cnt_map[HANDLER_ORDERS_LIST]
    )
    assert surge_level_handler.times_called == 1
    assert cdm_factor_tp.times_called == 1
