# pylint: disable=redefined-outer-name
import datetime

import bson
import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='manual_dispatch_override_rule',
    consumers=['manual-dispatch/handle-create'],
    clauses=[
        {
            'value': {'enabled': True},
            'predicate': {'init': {}, 'type': 'true'},
        },
    ],
    is_config=True,
    default_value={'tags': []},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='manual_dispatch_c2c_parameters',
    consumers=['manual-dispatch/handle-create-c2c'],
    clauses=[
        {
            'value': {
                'enabled': True,
                'params': {'tag': 'tag3', 'manual_switch_interval': 1800},
            },
            'predicate': {'init': {}, 'type': 'true'},
        },
    ],
    is_config=True,
    default_value={'enabled': True},
)
@pytest.mark.config(
    MANUAL_DISPATCH_TARIFF_MAPPINGS={
        'mappings': [
            {
                'lookup_tariffs': ['econom', 'express', 'courier'],
                'rule_tariff': 'econom',
            },
        ],
    },
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
@pytest.mark.parametrize(
    'order_type,user_tags,search_tariffs,rule_tariff,ref_id, claim_id',
    [
        (
            'b2b',
            [],
            ['courier'],
            'courier',
            'order/2ac83c64-60f4-4517-a13c-db513c7dd99e',
            'claim_id_1',
        ),
        (
            'b2b',
            [],
            ['courier', 'express', 'econom'],
            'econom',
            'claim_id_1',
            'claim_id_1',
        ),
        ('c2c', ['tag1', 'tag2'], ['courier'], 'courier', None, None),
    ],
)
async def test_enabled(
        stq_runner,
        mockserver,
        load_json,
        get_order,
        order_type,
        user_tags,
        search_tariffs,
        rule_tariff,
        get_order_audit,
        ref_id,
        claim_id,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def _segment_info(request):
        assert (
            request.query['segment_id']
            == 'a6229ae7-d4a0-4777-a48a-15a2a2e218fe'
        )
        return load_json('segment_info.json')

    @mockserver.json_handler('/cargo-dispatch/v1/admin/waybill/info')
    def waybill_info(request):
        assert 'order/' + request.query['cargo_order_id'] == ref_id
        return load_json('waybill_info.json')

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        assert request_body['update']['$set'] == {
            'order.request.lookup_ttl': 1800,
            'manual_dispatch': {'mirror_only': False},
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    created_ts = datetime.datetime.now(tz=datetime.timezone.utc).replace(
        microsecond=0,
    )
    corp_id = 'client_id_1' if order_type == 'b2b' else None
    await stq_runner.manual_dispatch_handle_create.call(
        task_id='order_id_1',
        kwargs={
            'client_id': corp_id,
            'created': created_ts,
            'tariffs': search_tariffs,
            'claim_id': ref_id,
            'due': None,
            'order_type': order_type,
            'zone_id': 'moscow',
            'user_tags': user_tags,
            'forced_performer_intent': 'cargo',
        },
        expect_fail=False,
    )
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0
    order = get_order('order_id_1', excluded=('updated_ts',))
    assert order is not None
    order['created_ts'] = (
        order['created_ts']
        .astimezone(datetime.timezone.utc)
        .replace(microsecond=0)
    )
    order['lock_expiration_ts'] = order['lock_expiration_ts'].replace(
        tzinfo=None,
    )
    assert order == {
        'order_id': 'order_id_1',
        'claim_id': claim_id,
        'corp_id': corp_id,
        'cost': None,
        'tariff': rule_tariff,
        'status': 'pending',
        'search_params': None,
        'performer_id': None,
        'created_ts': created_ts,
        'manual_switch_interval': datetime.timedelta(seconds=1800),
        'due_ts': None,
        'search_ts': None,
        'lookup_ttl': datetime.timedelta(seconds=1800),
        'new_list_hit_flow': False,
        'lookup_version': 0,
        'lock_expiration_ts': datetime.datetime(1, 1, 1, 0, 0),
        'owner_operator_id': None,
        'order_type': order_type,
        'address_shortname': None,
        'tag': None if not user_tags else 'tag3',
        'mirror_only_value': False,
        'country': 'rus',
        'zone_id': 'moscow',
    }

    audit = get_order_audit('order_id_1', ('status', 'reason'))
    assert len(audit) == 1
    assert audit[0] == {'status': 'pending', 'reason': 'create'}
    if ref_id != claim_id:
        assert waybill_info.times_called == 1
    else:
        assert waybill_info.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
@pytest.mark.parametrize('order_type', ['b2b', 'c2c'])
async def test_disabled_by_experiment(
        stq_runner,
        mockserver,
        get_order,
        get_order_audit,
        order_type,
        load_json,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    created_ts = datetime.datetime.utcnow()
    await stq_runner.manual_dispatch_handle_create.call(
        task_id='order_id_1',
        kwargs={
            'client_id': 'client_id_1' if order_type == 'b2b' else None,
            'created': created_ts,
            'tariffs': ['courier'],
            'claim_id': None,
            'due': None,
            'order_type': order_type,
            'zone_id': 'moscow',
            'user_tags': ['tag1', 'tag2'],
            'forced_performer_intent': None,
        },
        expect_fail=False,
    )
    assert _get_order_fields.times_called == 0
    assert _set_order_fields.times_called == 0
    assert start_lookup.times_called == 0
    order = get_order('order_id_1')
    assert order is None
    audit = get_order_audit('order_id_1')
    assert not audit


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='manual_dispatch_override_rule',
    consumers=['manual-dispatch/handle-create'],
    clauses=[
        {
            'value': {'enabled': True},
            'predicate': {'init': {}, 'type': 'true'},
        },
    ],
    is_config=True,
    default_value={'tags': []},
)
@pytest.mark.parametrize(
    ['client_id', 'tariff', 'is_rule_found'],
    [
        ('client_id_2', 'comfort', False),
        ('client_id_3', 'comfort', True),
        ('client_id_3', 'courier', False),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_disabled_by_rule(
        stq_runner,
        mockserver,
        load_json,
        get_order,
        get_order_audit,
        client_id,
        tariff,
        is_rule_found,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def _start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    created_ts = datetime.datetime.utcnow()
    await stq_runner.manual_dispatch_handle_create.call(
        task_id='order_id_1',
        kwargs={
            'client_id': client_id,
            'created': created_ts,
            'tariffs': [tariff],
            'claim_id': None,
            'due': None,
            'order_type': 'b2b',
            'zone_id': 'moscow',
            'user_tags': ['tag1', 'tag2'],
            'forced_performer_intent': 'cargo',
        },
        expect_fail=False,
    )

    order = get_order('order_id_1')
    audit = get_order_audit('order_id_1')

    if is_rule_found:
        assert order is not None
        assert audit
    else:
        assert order is None
        assert not audit


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='manual_dispatch_override_rule',
    consumers=['manual-dispatch/handle-create'],
    clauses=[
        {
            'value': {'enabled': True},
            'predicate': {'init': {}, 'type': 'true'},
        },
    ],
    is_config=True,
    default_value={'tags': []},
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_already_exists(
        stq_runner,
        mockserver,
        get_order,
        create_order,
        assert_orders_eq,
        load_json,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        assert (
            request_body['update']['$set']['order.request.lookup_ttl']
            == order['lookup_ttl'].seconds
        )
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    order = create_order()
    order['mirror_only_value'] = True
    await stq_runner.manual_dispatch_handle_create.call(
        task_id=order['order_id'],
        kwargs={
            'client_id': order['corp_id'],
            'created': order['created_ts'],
            'tariffs': [order['tariff']],
            'claim_id': order['corp_id'],
            'due': order['due_ts'],
            'order_type': 'b2b',
            'zone_id': 'moscow',
            'user_tags': ['tag1', 'tag2'],
            'forced_performer_intent': 'cargo',
        },
        expect_fail=False,
    )
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0
    new_order = get_order(order['order_id'], excluded=('updated_ts', 'cost'))
    assert_orders_eq(order, new_order)


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
@pytest.mark.now('2020-09-21T12:34:57.324+00:00')
async def test_409_in_version_update(
        taxi_manual_dispatch, headers, mockserver, load_json,
):
    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_get_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        assert set(request_body['fields']) > set(
            ['order.user_id', 'order.status'],
        )
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _mock_set_order_fields(request):
        return mockserver.make_response(
            status=409, json={'code': 'race_condition', 'message': '409'},
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _unique_drivers_retrieve_by_uniques(request):
        assert request.json == {'id_in_set': ['udid']}

        return {
            'profiles': [
                {
                    'unique_driver_id': 'udid',
                    'data': [
                        {
                            'park_id': 'dbid',
                            'driver_profile_id': 'uuid1',
                            'park_driver_profile_id': 'dbid_uuid1',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/proxy-retrieve',
    )
    def _proxy_retrieve(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': (
                        '7f74df331eb04ad78bc2ff25ff88a8f2_'
                        '172313ddc0174a0797b631f3539d8a85'
                    ),
                    'data': {
                        'phone_pd_ids': [],
                        'full_name': {
                            'first_name': 'Курьер',
                            'last_name': 'Курьерский',
                        },
                        'car_id': 'carid2',
                        'park_id': 'udid',
                        'uuid': 'uuid',
                    },
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'org_name': 'some park org name',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 1},
                    'provider_config': {'clid': 'clid', 'type': 'production'},
                },
            ],
        }

    response = await taxi_manual_dispatch.put(
        '/v1/driver-order-mapping',
        headers=headers,
        json={'order_id': 'order_id_1', 'driver_id': 'udid'},
    )
    assert response.status_code == 409
