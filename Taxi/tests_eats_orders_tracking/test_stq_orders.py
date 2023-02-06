# pylint: disable=too-many-lines

import datetime

import pytest

PERSONAL_PHONE_ID = '123456789'

PLACE_MASKING_PROVIDER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_orders_tracking_place_forwardings_provider',
    consumers=['eats-orders-tracking/place_forwardings_provider'],
    clauses=[
        {
            'title': 'VGW-api',
            'value': {'eater_place_forwarding_provider': 'vgw_api'},
            'predicate': {
                'init': {
                    'arg_name': 'eater_id',
                    'arg_type': 'string',
                    'value': '2',
                },
                'type': 'eq',
            },
        },
    ],
    default_value=dict({'eater_place_forwarding_provider': 'core'}),
)


def get_stq_orders_kwargs(
        order_nr,
        place_id,
        eater_id,
        status_history,
        event_time=16107965710948,
        updated_at='2020-10-28T18:26:43.51+00:00',
        raw_status='1',
        cancel_reason='duplicate',
        order_to_another_eater=None,
):
    date = '2020-10-20T12:00:00+00:00'

    kwargs = {
        'event_time': event_time,
        'order': {
            'order_nr': order_nr,
            'place_id': place_id,
            'eater_id': eater_id,
            'status': raw_status,
            'status_detail': {'id': 1, 'date': date},
            'promise': date,
            'location': {'latitude': 30.12, 'longitude': 30.34},
            'is_asap': False,
            'type': 'retail',
            'delivery_type': 'native',
            'shipping_type': 'delivery',
            'created_at': date,
            'updated_at': updated_at,
            'service': 'grocery',
            'client_app': 'native',
            'status_history': status_history,
            'changes_state': {'applicable_until': date},
            'region': {
                'name': 'Москва',
                'code': 'moscow',
                'timezone': 'Europe/Moscow',
                'country_code': 'RU',
            },
            'pre_order_date': date,
            'cancel_reason': cancel_reason,
            'payment_method': 'taxi',
            'is_second_batch_delivery': True,
            'short_order_nr': '000000-111-6543',
            'personal_phone_id': PERSONAL_PHONE_ID,
            'delivery_class': 'regular',
        },
    }

    if order_to_another_eater is not None:
        kwargs['order']['order_to_another_eater'] = order_to_another_eater

    return kwargs


def make_order_json_in_db(kwargs):
    order = kwargs['order'].copy()
    del order['order_nr']
    del order['eater_id']

    order['raw_type'] = kwargs['order']['type']
    order['raw_delivery_type'] = kwargs['order']['delivery_type']
    order['raw_shipping_type'] = kwargs['order']['shipping_type']
    order['raw_cancel_reason'] = kwargs['order']['cancel_reason']
    order['cancel_reason'] = kwargs['order']['cancel_reason']
    order['raw_payment_method'] = kwargs['order']['payment_method']
    order['payment_method'] = 'taxi'
    order['is_second_batch_delivery'] = True
    order['raw_delivery_class'] = kwargs['order']['delivery_class']

    raw_status = kwargs['order']['status']
    order['raw_status'] = raw_status
    if raw_status == '1':
        order['status'] = 'call_center_confirmed'
    elif raw_status == '4':
        order['status'] = 'delivered'
    elif raw_status == '5':
        order['status'] = 'cancelled'
    else:
        assert False

    return order


def make_place_json_in_db(load_json, kwargs):
    storage_response = load_json('storage_response.json')
    place_info = storage_response['places'][0]['place']
    location = place_info['location']['geo_point']

    return {
        'id': kwargs['order']['place_id'],
        'name': place_info['name'],
        'location': {'latitude': location[1], 'longitude': location[0]},
        'address': place_info['address']['short'],
        'place_slug': place_info['slug'],
        'brand_slug': place_info['brand']['slug'],
        'brand_id': place_info['brand']['id'],
        'address_comment': 'comment',
        'official_contact': {'personal_phone_id': '12345'},
        'main_tag': {'id': 1, 'name': 'Категория'},
    }


async def test_stq_orders_unknown_place(
        stq_runner, mock_storage_search_places_empty,
):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr='111111-222222',
            place_id='40',
            eater_id='1',
            status_history={},
        ),
        expect_fail=False,
    )


async def test_stq_orders_happy_path(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        get_place_info,
):
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
    )
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    order_in_db = get_order_info(kwargs_value['order']['order_nr'])
    assert order_in_db[0] == kwargs_value['order']['order_nr']
    assert order_in_db[1] == make_order_json_in_db(kwargs_value)

    place_in_db = get_place_info(kwargs_value['order']['place_id'])
    assert place_in_db[0] == kwargs_value['order']['place_id']
    assert place_in_db[1] == make_place_json_in_db(load_json, kwargs_value)


async def check_order(
        stq_runner, get_order_info, new_order_event, payload_order_in_base,
):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=new_order_event,
    )

    order_in_db = get_order_info(new_order_event['order']['order_nr'])
    assert order_in_db[0] == new_order_event['order']['order_nr']
    assert order_in_db[1] == payload_order_in_base


@pytest.mark.now('2020-10-28T18:26:43.51+00:00')
async def test_stq_orders_upsert_order(
        stq_runner, mock_storage_search_places, get_order_info,
):
    first_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710948,
        updated_at='2020-10-28T18:26:43.51+00:00',
    )
    await check_order(
        stq_runner,
        get_order_info,
        first_order,
        make_order_json_in_db(first_order),
    )

    second_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710949,
        updated_at='2020-10-28T19:26:43.51+00:00',
    )
    await check_order(
        stq_runner,
        get_order_info,
        second_order,
        make_order_json_in_db(second_order),
    )

    third_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710948,
        updated_at='2020-10-28T15:26:43.51+00:00',
    )
    await check_order(
        stq_runner,
        get_order_info,
        third_order,
        make_order_json_in_db(second_order),
    )


@pytest.mark.parametrize(
    'param_status, param_raw_status',
    [
        pytest.param('delivered', '4', id='status_delivered'),
        pytest.param('cancelled', '5', id='status_cancelled'),
    ],
)
@pytest.mark.now('2020-10-28T18:26:43.51+00:00')
async def test_stq_orders_final_status(
        stq_runner,
        mock_storage_search_places,
        get_order_info,
        param_status,
        param_raw_status,
):
    first_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710948,
        updated_at='2020-10-28T18:26:43.51+00:00',
        raw_status=param_raw_status,
    )
    await check_order(
        stq_runner,
        get_order_info,
        first_order,
        make_order_json_in_db(first_order),
    )

    second_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710949,
        updated_at='2020-10-28T19:26:43.51+00:00',
        raw_status='1',
    )
    # Order status must not be changed in final status.
    await check_order(
        stq_runner,
        get_order_info,
        second_order,
        make_order_json_in_db(first_order),
    )

    third_order = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={},
        event_time=16107965710950,
        updated_at='2020-10-28T19:26:43.51+00:00',
        raw_status=param_raw_status,
    )
    # Order can be updated in final status if the status is not changed.
    await check_order(
        stq_runner,
        get_order_info,
        third_order,
        make_order_json_in_db(third_order),
    )


def make_config_stq_retry(
        max_exec_tries, max_reschedule_counter, reschedule_seconds,
):
    return {
        'stq_orders': {
            'max_exec_tries': max_exec_tries,
            'max_reschedule_counter': max_reschedule_counter,
            'reschedule_seconds': reschedule_seconds,
        },
        'stq_couriers': {
            'max_exec_tries': 10,
            'max_reschedule_counter': 10,
            'reschedule_seconds': 10,
        },
        'stq_orders_eta': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_picker_orders': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_cargo_waybill_changes': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_taken_push': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
        'stq_order_to_another_eater_sms': {
            'max_exec_tries': 2,
            'max_reschedule_counter': 2,
            'reschedule_seconds': 10,
        },
    }


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=0,
    ),
)
async def test_stq_orders_retry_on_error(stq, stq_runner):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr='111111-222222',
            place_id='invalid_place_id',
            eater_id='1',
            status_history={},
        ),
        expect_fail=True,
    )

    assert stq.eats_orders_tracking_orders.has_calls is False


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=0,
    ),
)
async def test_stq_orders_stop_retries(stq, stq_runner):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr='111111-222222',
            place_id='invalid_place_id',
            eater_id='1',
            status_history={},
        ),
        exec_tries=10,
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_orders.has_calls is False


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
    ),
)
async def test_stq_orders_reschedule_on_error(stq, stq_runner):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr='111111-222222',
            place_id='invalid_place_id',
            eater_id='1',
            status_history={},
        ),
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_orders.has_calls is True


@pytest.mark.config(
    EATS_ORDERS_TRACKING_STQ_RETRY_3=make_config_stq_retry(
        max_exec_tries=10, max_reschedule_counter=10, reschedule_seconds=10,
    ),
)
async def test_stq_orders_stop_reschedules(stq, stq_runner):
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task',
        kwargs=get_stq_orders_kwargs(
            order_nr='111111-222222',
            place_id='invalid_place_id',
            eater_id='1',
            status_history={},
        ),
        reschedule_counter=10,
        expect_fail=False,
    )

    assert stq.eats_orders_tracking_orders.has_calls is False


async def get_masking_states_from_db(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr, state, proxy_phone_number, extension,
            expires_at AT TIME ZONE 'UTC'
            FROM eats_orders_tracking.eater_to_place_masking_states;""",
    )
    return cursor.fetchall()


async def test_stq_orders_not_marketplace(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order delivery type is not marketplace
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )

    kwargs_value['order']['delivery_type'] = 'native'

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert data == []


async def test_stq_orders_not_asap(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order is not asap and is not place confirmed
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = False
    kwargs_value['order']['status_history']['place_confirmed_at'] = None

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert data == []


async def test_stq_orders_not_masking_error(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order has masking state in db and it's state is not masking error
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True
    kwargs_value['order']['status_history'][
        'place_confirmed_at'
    ] = '2020-10-28T15:26:43.51+00:00'

    pgsql['eats_orders_tracking'].cursor().execute(
        f"""INSERT INTO eats_orders_tracking.eater_to_place_masking_states
            (order_nr, state, proxy_phone_number, extension)
            VALUES ('111111-222222', 'place_has_no_phone', NULL, NULL);""",
    )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'place_has_no_phone'
    assert data[0][2] is None
    assert data[0][3] is None


URL_STORAGE_SEARCH_PLACES = (
    '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/places/list'
)


async def test_stq_orders_no_personal_id(
        stq_runner, load_json, get_order_info, pgsql, mockserver,
):
    # Place has no personal_phone_id
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler(URL_STORAGE_SEARCH_PLACES)
    def _handler_storage_search_places(request):
        assert len(request.json['place_ids']) == 1
        assert 'place_slugs' not in request.json
        place_id = request.json['place_ids'][0]

        mock_response = load_json('storage_response.json')
        del mock_response['places'][0]['place']['contacts']
        mock_response['places'][0]['place_id'] = place_id

        return mockserver.make_response(json=mock_response, status=200)

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'place_has_no_phone'
    assert data[0][2] is None
    assert data[0][3] is None


async def test_stq_orders_has_extension(
        stq_runner, load_json, get_order_info, pgsql, mockserver,
):
    # Place has no personal_phone_id
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler(URL_STORAGE_SEARCH_PLACES)
    def _handler_storage_search_places(request):
        assert len(request.json['place_ids']) == 1
        assert 'place_slugs' not in request.json
        place_id = request.json['place_ids'][0]

        mock_response = load_json('storage_response.json')
        mock_response['places'][0]['place']['contacts'][1]['extension'] = '123'
        mock_response['places'][0]['place_id'] = place_id

        return mockserver.make_response(json=mock_response, status=200)

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'has_extension'
    assert data[0][2] is None
    assert data[0][3] is None


async def test_stq_orders_masking_disabled(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Config.is_masking_enabled is false
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'disabled_globally'
    assert data[0][2] is None
    assert data[0][3] is None


@PLACE_MASKING_PROVIDER
async def test_stq_orders_core_error(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # mask-for-order returned error
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler('/eats-core-masking/mask-for-order')
    def _handler_eats_core_masking_error(request):
        return mockserver.make_response(
            json={'error': 'validation_error'}, status=400,
        )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'masking_error'
    assert data[0][2] is None
    assert data[0][3] is None


@PLACE_MASKING_PROVIDER
async def test_stq_orders_core_disabled(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # mask-for-order returned blocked for region
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler('/eats-core-masking/mask-for-order')
    def _handler_eats_core_masking_no_masking(request):
        return mockserver.make_response(
            json={'no_masking_reason': 'disabled_for_region'}, status=200,
        )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'disabled_for_region'
    assert data[0][2] is None
    assert data[0][3] is None


@PLACE_MASKING_PROVIDER
async def test_stq_orders_core_success(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # mask-for-order returned success
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler('/eats-core-masking/mask-for-order')
    def _handler_eats_core_masking(request):
        return mockserver.make_response(
            json={
                'masked_phone_number': {
                    'phone_number': '12345',
                    'extension': '123',
                },
            },
            status=200,
        )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'success'
    assert data[0][2] == '12345'
    assert data[0][3] == '123'


def is_empty_masked_couriers(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT *
            FROM eats_orders_tracking.masked_courier_phone_numbers;""",
    )
    return cursor.fetchall() == []


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_courier_phone_masking.sql'],
)
async def test_stq_orders_del_mask(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order delivery type is not marketplace
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'native'

    # Masking will be deleted when order is in final state.
    # '5' - cancelled.
    kwargs_value['order']['status'] = '5'

    assert not is_empty_masked_couriers(pgsql)

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    assert is_empty_masked_couriers(pgsql)


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_courier_phone_masking.sql'],
)
async def test_stq_orders_dont_del_mask(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order delivery type is not marketplace
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'native'

    # Masking must not be deleted when order is not in final state.
    # '3' - ready for delivery.
    kwargs_value['order']['status'] = '3'

    assert not is_empty_masked_couriers(pgsql)

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    assert not is_empty_masked_couriers(pgsql)


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_courier_phone_masking.sql'],
)
async def test_stq_orders_del_mask_no_id(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # Order delivery type is not marketplace
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-333333',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'native'

    # Masking will be deleted when order is in final state.
    # '5' - cancelled.
    kwargs_value['order']['status'] = '5'

    assert not is_empty_masked_couriers(pgsql)

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    # Order '111111-333333' does not have claim-id in payload in db.
    assert not is_empty_masked_couriers(pgsql)


@pytest.mark.now('2021-01-01T10:00:00+03:00')
@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_eta(
        stq_runner, mock_storage_search_places, load_json, pgsql,
):
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['eta'] = '2021-01-01T10:00:00+03:00'
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    data = sql_get_all_orders_eta(pgsql)
    assert data == [('111111-222222', datetime.datetime(2021, 1, 1, 7, 0, 0))]


def sql_get_all_orders_eta(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        select order_nr, eta AT TIME ZONE 'UTC'
        from eats_orders_tracking.orders_eta
        """,
    )
    return list(cursor)


@pytest.mark.parametrize(
    'cancel_reason_stq,cancel_reason_db',
    [
        ('duplicate', 'duplicate'),
        ('client.self.did_not_pay', 'client_self_did_not_pay'),
        ('payment_failed', 'payment_failed'),
        ('cancel', 'other'),
    ],
)
async def test_stq_orders_cancel_reason(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        get_place_info,
        cancel_reason_stq,
        cancel_reason_db,
):
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        cancel_reason=cancel_reason_stq,
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    order_in_db = get_order_info(kwargs_value['order']['order_nr'])
    assert order_in_db[0] == kwargs_value['order']['order_nr']
    assert order_in_db[1]['cancel_reason'] == cancel_reason_db


@PLACE_MASKING_PROVIDER
async def test_stq_orders_vgw_masking_success(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # mask-for-order returned success
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='2',  # turn on vgw-api
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _handler_eats_vgw_masking(request):
        assert request.json['requester_phone_id'] == PERSONAL_PHONE_ID
        return mockserver.make_response(
            json={
                'phone': '12345',
                'ext': '123',
                'expires_at': (
                    '2020-10-28T18:26:43.51+00:00'  # random time here
                ),
            },
            status=200,
        )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == 'success'
    assert data[0][2] == '12345'
    assert data[0][3] == '123'
    assert data[0][4] == datetime.datetime(2020, 10, 28, 18, 26, 43, 510000)


@PLACE_MASKING_PROVIDER
@pytest.mark.parametrize(
    'vgw_response_body,vgw_response_code,expected_masking_state',
    [
        (
            {
                'code': 'BadRequester',
                'message': 'BadRequester',
                'error': {'code': 'BadRequester', 'message': 'BadRequester'},
            },
            '400',
            'masking_error',
        ),
        (
            {
                'code': 'RegionIsNotSupported',
                'message': 'RegionIsNotSupported',
                'error': {
                    'code': 'RegionIsNotSupported',
                    'message': 'RegionIsNotSupported',
                },
            },
            '400',
            'disabled_for_region',
        ),
        (
            {
                'code': 'ConsumerIsNotSupported',
                'message': 'ConsumerIsNotSupported',
                'error': {
                    'code': 'ConsumerIsNotSupported',
                    'message': 'ConsumerIsNotSupported',
                },
            },
            '400',
            'masking_error',
        ),
        (
            {
                'code': 500,
                'message': 'Server Error',
                'error': {'code': 'UnknownError', 'message': 'Server Error'},
            },
            '500',
            'masking_error',
        ),
        (
            {
                'code': 'PartnerInternalError',
                'message': 'PartnerInternalError',
                'error': {
                    'code': 'PartnerInternalError',
                    'message': 'PartnerInternalError',
                },
            },
            '502',
            'masking_error',
        ),
    ],
    ids=[
        'bad_request',
        'disabled_for_region',
        'disabled_for_consumer',
        'server_error',
        'provider_error',
    ],
)
async def test_stq_orders_vgw_masking_errors(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        vgw_response_body,
        vgw_response_code,
        expected_masking_state,
        pgsql,
        mockserver,
):
    # mask-for-order returned success
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='2',  # turn on vgw-api
        status_history={
            'call_center_confirmed_at': '2020-10-20T12:00:00+00:00',
        },
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _handler_eats_vgw_masking(request):
        return mockserver.make_response(
            json=vgw_response_body, status=vgw_response_code,
        )

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert len(data) == 1
    assert data[0][0] == '111111-222222'
    assert data[0][1] == expected_masking_state
    assert data[0][2] is None
    assert data[0][3] is None


@PLACE_MASKING_PROVIDER
async def test_stq_masking_skipped_before_payment(
        stq_runner,
        mock_storage_search_places,
        load_json,
        get_order_info,
        pgsql,
        mockserver,
):
    # mask-for-order returned success
    kwargs_value = get_stq_orders_kwargs(
        order_nr='111111-222222',
        place_id='40',
        eater_id='1',
        raw_status='8',
        status_history={},
    )
    kwargs_value['order']['delivery_type'] = 'marketplace'
    kwargs_value['order']['is_asap'] = True

    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )
    data = await get_masking_states_from_db(pgsql)

    assert not data


async def test_stq_orders_order_to_another_eater(
        stq_runner, stq, mock_storage_search_places,
):
    kwargs_value = get_stq_orders_kwargs(
        order_nr='000000-000001',
        place_id='40',
        eater_id='1',
        status_history={},
        raw_status='1',
        order_to_another_eater={'personal_phone_id': 'ppid'},
    )
    await stq_runner.eats_orders_tracking_orders.call(
        task_id='sample_task', kwargs=kwargs_value, expect_fail=False,
    )

    assert (
        stq.eats_orders_tracking_order_to_another_eater_sms.times_called == 1
    )
