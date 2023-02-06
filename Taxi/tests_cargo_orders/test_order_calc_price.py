import pytest

from testsuite.utils import matching


def assert_pricing_processing_data(
        pricing_request, is_taximeter, calc_stage=None, source_type=None,
):
    assert pricing_request['entity_id'] == 'order/taxi-order'
    if is_taximeter:
        assert (
            pricing_request['origin_uri']
            == 'cargo-orders/driver/v1/cargo-claims/v1/cargo/calc-price'
        )
    else:
        assert pricing_request['origin_uri'] == 'cargo-orders/v1/calc-price'
    if source_type == 'presetcar' or calc_stage == 'performer_assignment':
        assert pricing_request['calc_kind'] == 'offer'
    else:
        assert pricing_request['calc_kind'] == 'final'


async def test_happy_path(
        calc_price,
        calc_price_via_taximeter,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        my_waybill_info,
        resolve_waybill,
        mock_driver_tags_v1_match_profile,
):
    await calc_price()
    await calc_price()
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1

    resolve_waybill(my_waybill_info)
    calc_stage = 'order_finished'
    await calc_price_via_taximeter(stage=calc_stage, status='complete')
    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=True,
        calc_stage=calc_stage,
    )
    await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 2


async def test_hide_price(
        calc_price_via_taximeter,
        my_waybill_info,
        set_order_calculations_ids,
        resolve_waybill,
        exp_cargo_orders_show_price_on_order_card,
        mock_driver_tags_v1_match_profile,
):
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    resolve_waybill(my_waybill_info)
    resp = await calc_price_via_taximeter(
        stage='order_finished', status='complete',
    )
    assert 'price' not in resp.json()


def _next_call_request(mock):
    return mock.mock.next_call()['request'].json


async def test_non_decoupling_order_via_taximeter(
        calc_price,
        calc_price_via_taximeter,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        my_waybill_info,
        waybill_info_c2c,
        set_order_calculations_ids,
        resolve_waybill,
        mock_driver_tags_v1_match_profile,
):
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    waybill_info_c2c['execution']['points'][0]['resolution'][
        'is_visited'
    ] = True

    calc_mock = mock_cargo_pricing_calc
    calc_mock.substituted_driver_price = '135.1'
    calc_mock.substituted_driver_calc_id = 'calc_id_driver_preset'
    calc_stage = 'performer_assignment'
    preset_resp = await calc_price_via_taximeter(
        stage=calc_stage, status='new',
    )
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=True,
        calc_stage=calc_stage,
    )
    preset_driver_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert preset_driver_calc_req['price_for'] == 'performer'
    assert preset_driver_calc_req['previous_calc_id'] == 'calc_id_client_offer'
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1
    preset_client_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert preset_client_retrieve_req['calc_id'] == 'calc_id_client_offer'
    assert preset_resp.json()['price'] == '135.1'
    resolve_waybill(my_waybill_info)

    calc_mock.substituted_driver_price = '122.3'
    calc_mock.substituted_driver_calc_id = 'calc_id_driver_final'
    calc_mock.substituted_client_calc_id = 'calc_id_client_final'
    calc_stage = 'order_finished'
    finished_response = await calc_price_via_taximeter(
        stage=calc_stage, status='complete',
    )
    assert finished_response.json()['price'] == '122.3'
    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=True,
        calc_stage=calc_stage,
    )
    final_client_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert final_client_calc_req['price_for'] == 'client'
    assert final_client_calc_req['previous_calc_id'] == 'calc_id_driver_preset'
    final_driver_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert final_driver_calc_req['price_for'] == 'performer'
    assert final_driver_calc_req['previous_calc_id'] == 'calc_id_client_final'
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    mock_cargo_pricing_calc_retrieve.substituted_price = {
        'calc_id_client_final': '143.7',
        'calc_id_driver_final': '122.3',
    }
    confirm_response = await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc.mock.times_called == 0
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 2
    final_client_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert final_client_retrieve_req['calc_id'] == 'calc_id_client_final'
    final_driver_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert final_driver_retrieve_req['calc_id'] == 'calc_id_driver_final'
    assert confirm_response.json()['receipt']['total'] == 122.3
    assert confirm_response.json()['client_total_price'] == 143.7


async def test_non_decoupling_order_via_calc_price(
        calc_price,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_calc_retrieve,
        my_waybill_info,
        set_order_calculations_ids,
        resolve_waybill,
):
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    waybill_exec = my_waybill_info['execution']
    payment_info = waybill_exec['segments'][0]['client_info']['payment_info']
    payment_info['type'] = 'card'
    payment_info['method_id'] = 'card-123'
    waybill_exec['points'][0]['resolution']['is_visited'] = True

    calc_mock = mock_cargo_pricing_calc
    calc_mock.substituted_driver_price = '135.1'
    calc_mock.substituted_driver_calc_id = 'calc_id_driver_preset'
    mock_cargo_pricing_calc_retrieve.substituted_price = {
        'calc_id_client_offer': '154.19',
    }
    source_type = 'presetcar'
    preset_resp = await calc_price(source_type=source_type)
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=False,
        source_type=source_type,
    )
    preset_driver_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert preset_driver_calc_req['price_for'] == 'performer'
    assert preset_driver_calc_req['previous_calc_id'] == 'calc_id_client_offer'
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1
    preset_client_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert preset_client_retrieve_req['calc_id'] == 'calc_id_client_offer'
    assert preset_resp.json()['receipt']['total'] == 135.1
    assert preset_resp.json()['client_total_price'] == 154.19
    resolve_waybill(my_waybill_info)

    calc_mock.substituted_driver_price = '122.3'
    calc_mock.substituted_client_price = '143.7'
    calc_mock.substituted_driver_calc_id = 'calc_id_driver_final'
    calc_mock.substituted_client_calc_id = 'calc_id_client_final'
    source_type = 'requestconfirm'
    confirm_response = await calc_price(source_type=source_type)
    assert confirm_response.json()['receipt']['total'] == 122.3
    assert confirm_response.json()['client_total_price'] == 143.7
    assert (
        confirm_response.json()['recalc_taxi_pricing_response']
        == mock_cargo_pricing_calc.response['recalc_taxi_pricing_response']
    )
    assert (
        confirm_response.json()['price_extra_info']
        == mock_cargo_pricing_calc.response['price_extra_info']
    )
    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=False,
        source_type=source_type,
    )
    final_client_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert final_client_calc_req['price_for'] == 'client'
    assert final_client_calc_req['previous_calc_id'] == 'calc_id_driver_preset'
    final_driver_calc_req = _next_call_request(mock_cargo_pricing_calc)
    assert final_driver_calc_req['price_for'] == 'performer'
    assert final_driver_calc_req['previous_calc_id'] == 'calc_id_client_final'
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0

    mock_cargo_pricing_calc_retrieve.substituted_price = {
        'calc_id_client_final': '143.7',
        'calc_id_driver_final': '122.3',
    }
    finish_response = await calc_price(source_type='taxi_processing_finish')
    assert mock_cargo_pricing_calc.mock.times_called == 0
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 2
    final_client_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert final_client_retrieve_req['calc_id'] == 'calc_id_client_final'
    final_driver_retrieve_req = _next_call_request(
        mock_cargo_pricing_calc_retrieve,
    )
    assert final_driver_retrieve_req['calc_id'] == 'calc_id_driver_final'
    assert finish_response.json()['receipt']['total'] == 122.3
    assert finish_response.json()['client_total_price'] == 143.7
    assert (
        finish_response.json()['recalc_taxi_pricing_response']
        == mock_cargo_pricing_calc.response['recalc_taxi_pricing_response']
    )
    assert (
        finish_response.json()['price_extra_info']
        == mock_cargo_pricing_calc.response['price_extra_info']
    )


async def test_calc_with_taxi_autoreorder(
        calc_price, mock_cargo_pricing_calc, mock_cargo_pricing_calc_retrieve,
):
    source_type = 'presetcar'
    await calc_price(source_type=source_type)
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=False,
        source_type=source_type,
    )
    await calc_price(
        source_type=source_type, request_override={'driver_id': 'another'},
    )
    assert_pricing_processing_data(
        mock_cargo_pricing_calc.request,
        is_taximeter=False,
        source_type=source_type,
    )
    assert mock_cargo_pricing_calc.mock.times_called == 2
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 0


async def test_call_price_responses(
        taxi_cargo_orders,
        mock_cargo_pricing_calc,
        calc_price,
        my_waybill_info,
        fetch_order,
        default_order_id,
        resolve_waybill,
):
    my_waybill_info['waybill']['items'] = [
        {
            'item_id': 'item1',
            'title': 'title1',
            'weight': 10.5,
            'quantity': 4,
            'pickup_point': 'seg_1_point_1',
            'dropoff_point': 'seg_1_point_2',
            'return_point': 'seg_1_point_3',
        },
        {
            'item_id': 'item2',
            'title': 'title2',
            'quantity': 4,
            'pickup_point': 'seg_1_point_1',
            'dropoff_point': 'seg_1_point_2',
            'return_point': 'seg_1_point_3',
            'size': {'length': 10.3, 'width': 3.3, 'height': 1.6},
        },
    ]

    response = await calc_price()
    assert response.json() == {
        'is_cargo_pricing': True,
        'order_info': {
            'destination': {
                'point': [37.642979, 55.734977],
                'address': 'БЦ Аврора',
            },
            'source': {
                'point': [37.642979, 55.734977],
                'address': 'БЦ Аврора',
            },
        },
        'receipt': {
            'total': 933.0,
            'total_distance': 3541.0878,
            'waiting': {'cost': 0.0, 'sum': 0.0, 'time': 60.0},
            'waiting_in_transit': {'cost': 20.0, 'sum': 10.0, 'time': 30.0},
        },
        'taxi_pricing_response': mock_cargo_pricing_calc.response[
            'taxi_pricing_response'
        ],
    }

    cargo_items = [
        {
            'weight': 10.5,
            'quantity': 4,
            'pickup_point_id': 'seg_1_point_1',
            'dropoff_point_id': 'seg_1_point_2',
            'return_point_id': 'seg_1_point_3',
        },
        {
            'quantity': 4,
            'pickup_point_id': 'seg_1_point_1',
            'dropoff_point_id': 'seg_1_point_2',
            'return_point_id': 'seg_1_point_3',
            'size': {'length': 10.3, 'width': 3.3, 'height': 1.6},
        },
    ]

    assert mock_cargo_pricing_calc.request == {
        'clients': [
            {
                'corp_client_id': '5e36732e2bc54e088b1466e08e31c486',
                'user_id': 'taxi_user_id_1',
            },
        ],
        'external_ref': 'meta_order_id/taxi-order',
        'idempotency_token': 'presetcar-order-taxi-order-performer-driver_id1',
        'is_usage_confirmed': False,
        'payment_info': {
            'method_id': 'corp-5e36732e2bc54e088b1466e08e31c486',
            'type': 'corp',
        },
        'performer': {
            'assigned_at': '2020-01-01T00:00:00+00:00',
            'driver_id': 'driver_id1',
            'park_db_id': 'park_db_id1',
        },
        'price_for': 'performer',
        'homezone': 'moscow',
        'taxi_requirements': {},
        'tariff_class': 'mock-tariff',
        'transport': 'electric_bicycle',
        'waypoints': [
            {
                'position': [37.642979, 55.734977],
                'type': 'pickup',
                'id': 'seg_1_point_1',
                'claim_id': 'claim_uuid_1',
            },
            {
                'position': [37.583, 55.9873],
                'type': 'dropoff',
                'id': 'seg_1_point_2',
                'claim_id': 'claim_uuid_1',
            },
            {
                'position': [37.583, 55.8873],
                'type': 'return',
                'id': 'seg_1_point_3',
                'claim_id': 'claim_uuid_1',
            },
        ],
        'cargo_items': cargo_items,
        'entity_id': 'order/taxi-order',
        'origin_uri': 'cargo-orders/v1/calc-price',
        'calc_kind': 'offer',
        'special_requirements': [],
        'make_processing_create_event': True,
    }

    resolve_waybill(my_waybill_info)
    await calc_price(source_type='requestconfirm')
    assert (
        mock_cargo_pricing_calc.request['previous_calc_id']
        == 'cargo-pricing/v1/f6e1661746e34f8c8234832e1d718d85'
    )
    assert mock_cargo_pricing_calc.request['waypoints'] == [
        {
            'first_time_arrived_at': '2020-08-18T14:01:49.939497+00:00',
            'position': [37.642979, 55.734977],
            'resolution_info': {
                'resolution': 'delivered',
                'resolved_at': '2020-08-18T14:06:49.939497+00:00',
            },
            'type': 'pickup',
            'id': 'seg_1_point_1',
            'claim_id': 'claim_uuid_1',
        },
        {
            'first_time_arrived_at': '2020-08-18T14:01:49.939497+00:00',
            'position': [37.583, 55.9873],
            'resolution_info': {
                'resolution': 'delivered',
                'resolved_at': '2020-08-18T14:06:49.939497+00:00',
            },
            'type': 'dropoff',
            'id': 'seg_1_point_2',
            'claim_id': 'claim_uuid_1',
        },
        {
            'position': [37.583, 55.8873],
            'resolution_info': {
                'resolution': 'skipped',
                'resolved_at': '2020-08-18T14:01:49.939497+00:00',
            },
            'type': 'return',
            'id': 'seg_1_point_3',
            'claim_id': 'claim_uuid_1',
        },
    ]
    assert mock_cargo_pricing_calc.request['resolution_info'] == {
        'resolution': 'completed',
        'resolved_at': matching.any_string,
    }
    assert mock_cargo_pricing_calc.request['cargo_items'] == cargo_items
    assert not mock_cargo_pricing_calc.request['make_processing_create_event']

    order = fetch_order(default_order_id)
    assert not order.final_calc_fallback_was_used


async def test_v1_taxi_calc_request_special_requirements(
        mock_cargo_pricing_calc, calc_price, my_waybill_info,
):
    my_waybill_info['waybill']['special_requirements']['virtual_tariffs'] = [
        {'class': 'courier', 'special_requirements': [{'id': 'courier_req1'}]},
        {
            'class': 'mock-tariff',
            'special_requirements': [{'id': 'spec_req1'}, {'id': 'spec_req2'}],
        },
    ]

    response = await calc_price()
    assert response.status_code == 200

    assert sorted(mock_cargo_pricing_calc.request['special_requirements']) == [
        'spec_req1',
        'spec_req2',
    ]


@pytest.fixture(name='calc_price_via_taximeter_expected_response')
def _calc_price_via_taximeter_expected_response(load_json):
    return load_json('calc_price_via_taximeter_response.json')


async def test_taximeter_call_price_on_order_finished(
        calc_price_via_taximeter,
        calc_price_via_taximeter_expected_response,
        mock_driver_tags_v1_match_profile,
):
    response = await calc_price_via_taximeter(
        stage='order_finished', status='complete',
    )
    expected_response = calc_price_via_taximeter_expected_response
    expected_response['payment']['method'] = 'corp'
    assert response.json() == expected_response


async def test_taximeter_call_price_on_performer_assignment_no_visited_points(
        calc_price_via_taximeter,
        my_waybill_info,
        calc_price_via_taximeter_expected_response,
        mock_driver_tags_v1_match_profile,
):
    first_segment = my_waybill_info['execution']['segments'][0]
    first_segment['client_info']['payment_info']['type'] = 'googlepay'

    response = await calc_price_via_taximeter(
        stage='performer_assignment', status='new',
    )

    assert response.json() == {
        'currency_code': '',
        'payment': {'method': 'card'},
        'services': [],
    }


async def test_calc_price_no_performer(
        calc_price_via_taximeter,
        calc_price,
        default_order_id,
        fetch_order,
        my_waybill_info,
):

    response = await calc_price(request_override={'driver_id': 'MY_DRIVER'})
    assert response.status_code == 200
    order = fetch_order(default_order_id)
    assert order.last_calculated_for_driver_with_id == 'MY_DRIVER'


async def test_taximeter_call_price_on_performer_assignment(
        calc_price_via_taximeter,
        my_waybill_info,
        calc_price_via_taximeter_expected_response,
        mock_driver_tags_v1_match_profile,
):
    first_segment = my_waybill_info['execution']['segments'][0]
    first_segment['client_info']['payment_info']['type'] = 'corp'
    point = my_waybill_info['execution']['points'][1]
    point['resolution']['is_visited'] = True

    response = await calc_price_via_taximeter(
        stage='performer_assignment', status='new',
    )

    expected_response = calc_price_via_taximeter_expected_response
    expected_response['payment']['method'] = 'corp'
    assert response.json() == expected_response


async def test_resolution_fallback(
        mock_cargo_pricing_calc,
        my_waybill_info,
        calc_price,
        set_point_visited,
):
    set_point_visited(my_waybill_info, 0)
    response = await calc_price(source_type='taxi_processing_finish')
    assert response.status_code == 200
    assert mock_cargo_pricing_calc.request['waypoints'][0] == {
        'first_time_arrived_at': matching.any_string,
        'position': [37.642979, 55.734977],
        'resolution_info': {
            'resolution': 'skipped',
            'resolved_at': matching.any_string,
        },
        'type': 'pickup',
        'id': 'seg_1_point_1',
        'claim_id': 'claim_uuid_1',
    }
    assert mock_cargo_pricing_calc.request['resolution_info'] == {
        'resolution': 'failed_by_performer',
        'resolved_at': matching.any_string,
    }


def _set_source_points_was_ready(v1_waybill_info_response):
    for point in v1_waybill_info_response['execution']['points']:
        if point['type'] == 'source':
            point['was_ready_at'] = '2020-08-18T14:00:00+00:00'


async def test_same_source_was_ready_at(
        taxi_cargo_orders,
        mock_cargo_pricing_calc,
        waybill_info_with_same_source_point,
        calc_price,
):
    _set_source_points_was_ready(waybill_info_with_same_source_point)
    response = await calc_price()
    assert response.status_code == 200
    assert (
        mock_cargo_pricing_calc.request['waypoints'][0].get('was_ready_at')
        == '2020-08-18T14:00:00+00:00'
    )


def _set_final_pricing_calc_id(v1_waybill_info_response):
    v1_waybill_info_response['execution']['segments'][0]['pricing'] = {
        'final_pricing_calc_id': 'some-calc-id',
    }


async def test_waybill_with_final_calc_id(
        taxi_cargo_orders,
        mock_cargo_pricing_calc,
        waybill_info_c2c,
        calc_price,
        mock_cargo_pricing_calc_retrieve,
):
    _set_final_pricing_calc_id(waybill_info_c2c)
    waybill_info_c2c['dispatch']['resolution'] = 'cancelled'
    waybill_info_c2c['dispatch']['resolved_at'] = '2020-06-17T22:39:50+0300'
    await calc_price()
    assert mock_cargo_pricing_calc.mock.times_called == 0
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1


async def test_waybill_with_final_calc_id_not_cancelled_by_client(
        taxi_cargo_orders,
        mock_cargo_pricing_calc,
        waybill_info_c2c,
        calc_price,
        mock_cargo_pricing_calc_retrieve,
        set_order_calculations_ids,
):
    _set_final_pricing_calc_id(waybill_info_c2c)
    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')
    await calc_price()
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_calc_retrieve.mock.times_called == 1


@pytest.mark.config(CARGO_ORDERS_SKIP_CALCULATION_FOR_ORDERS=['taxi-order'])
async def test_skip_calc_for_order(calc_price):
    response = await calc_price()
    assert response.json()['is_cargo_pricing'] is False


async def test_retrive_calc(
        taxi_cargo_orders,
        mock_cargo_pricing_calc_retrieve,
        set_order_calculations_ids,
        default_order_id,
        mockserver,
        waybill_state,
):
    cargo_c2c_order_id = 'cargo_c2c_order_id_1'
    offer_expectations = {'seconds_to_arrive': 100, 'meters_to_arrive': 101}

    @mockserver.json_handler('/cargo-c2c/v1/intiator-client-order')
    def _mosck_c2c(request):
        assert request.json == {'cargo_c2c_order_id': cargo_c2c_order_id}
        return {
            'user_id': 'some_user_id',
            'user_agent': 'some_user_agent',
            'offer_expectations': offer_expectations,
        }

    waybill_state.set_cargo_c2c_order_id(cargo_c2c_order_id)

    set_order_calculations_ids(client_offer_calc_id='calc_id_client_offer')

    response = await taxi_cargo_orders.post(
        '/v1/retrieve-pricing-data',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'order_info': {
            'destination': {
                'point': [37.642979, 55.734977],
                'address': 'БЦ Аврора',
            },
            'source': {
                'point': [37.642979, 55.734977],
                'address': 'БЦ Аврора',
            },
        },
        'receipt': {
            'total': 827.0,
            'total_distance': 13155.5,
            'waiting': {'cost': 0.0, 'sum': 0.0, 'time': 0.0},
            'waiting_in_transit': {'cost': 0.0, 'sum': 0.0, 'time': 0.0},
        },
        'taxi_pricing_response': mock_cargo_pricing_calc_retrieve.response[
            'taxi_pricing_response'
        ],
        'offer_expectations': offer_expectations,
    }


@pytest.fixture(name='conf_exp3_additional_prices')
def _conf_exp3_additional_prices(experiments3, taxi_cargo_orders):
    async def configurate(enabled):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_additional_price_calcs',
            consumers=['cargo-orders/additional_price_calcs'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_orders.invalidate_caches()

    return configurate


@pytest.fixture(name='my_batch_waybill_info_with_segments')
def _my_batch_waybill_info_with_segments(waybill_state, mock_waybill_info):
    return waybill_state.load_waybill(
        'cargo-dispatch/v1_waybill_info_batch_tpl_filled_segments.json',
    )


async def test_calc_with_additional_prices_calc_requests(
        calc_price,
        mock_cargo_pricing_calc,
        my_batch_waybill_info_with_segments,
        resolve_waybill,
        conf_exp3_additional_prices,
):
    resolve_waybill(my_batch_waybill_info_with_segments)
    await conf_exp3_additional_prices(enabled=True)
    await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc.mock.times_called == 3
    calc_requests = [
        _next_call_request(mock_cargo_pricing_calc),
        _next_call_request(mock_cargo_pricing_calc),
        _next_call_request(mock_cargo_pricing_calc),
    ]
    additional_calcs_s1 = [
        x
        for x in calc_requests
        if x['external_ref'] == 'estimate_claim/claim_uuid_1'
    ]
    assert additional_calcs_s1 == [
        {
            'idempotency_token': (
                'resolved-order-taxi-order-performer-1-seg-seg_1'
            ),
            'clients': [
                {
                    'corp_client_id': '5e36732e2bc54e088b1466e08e31c486',
                    'user_id': 'taxi_user_id_1',
                },
            ],
            'external_ref': 'estimate_claim/claim_uuid_1',
            'is_usage_confirmed': False,
            'payment_info': {
                'method_id': 'corp-5e36732e2bc54e088b1466e08e31c486',
                'type': 'corp',
            },
            'performer': {
                'driver_id': 'driver_id1',
                'park_db_id': 'park_db_id1',
            },
            'price_for': 'performer',
            'resolution_info': {
                'resolution': 'completed',
                'resolved_at': '2020-06-01T09:00:00+00:00',
            },
            'homezone': 'moscow',
            'taxi_requirements': {'door_to_door': True},
            'tariff_class': 'mock-tariff',
            'transport': 'electric_bicycle',
            'waypoints': [
                {
                    'position': [37.642979, 55.734977],
                    'type': 'pickup',
                    'id': 'seg_1_point_1',
                    'claim_id': 'claim_uuid_1',
                    'first_time_arrived_at': (
                        '2020-08-18T14:01:49.939497+00:00'
                    ),
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': matching.any_string,
                    },
                },
                {
                    'position': [37.583, 55.8873],
                    'type': 'dropoff',
                    'id': 'seg_1_point_2',
                    'claim_id': 'claim_uuid_1',
                    'first_time_arrived_at': (
                        '2020-08-18T14:01:49.939497+00:00'
                    ),
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': matching.any_string,
                    },
                },
                {
                    'position': [37.583, 55.8873],
                    'type': 'return',
                    'id': 'seg_1_point_3',
                    'claim_id': 'claim_uuid_1',
                    'resolution_info': {
                        'resolution': 'skipped',
                        'resolved_at': matching.any_string,
                    },
                },
            ],
            'cargo_items': [
                {
                    'dropoff_point_id': 'seg_1_point_2',
                    'pickup_point_id': 'seg_1_point_1',
                    'quantity': 1,
                    'return_point_id': 'seg_1_point_3',
                    'size': {'height': 0.1, 'length': 0.1, 'width': 0.1},
                    'weight': 1.0,
                },
            ],
            'entity_id': 'order/taxi-order',
            'origin_uri': 'cargo-orders/v1/calc-price',
            'calc_kind': 'analytical',
        },
    ]
    additional_calcs_s2 = [
        x
        for x in calc_requests
        if x['external_ref'] == 'estimate_claim/claim_uuid_2'
    ]
    assert additional_calcs_s2 == [
        {
            'cargo_items': [],
            'clients': [
                {
                    'corp_client_id': '5e36732e2bc54e088b1466e08e31c486',
                    'user_id': 'taxi_user_id_1',
                },
            ],
            'external_ref': 'estimate_claim/claim_uuid_2',
            'homezone': 'moscow',
            'idempotency_token': (
                'resolved-order-taxi-order-performer-1-seg-seg_2'
            ),
            'is_usage_confirmed': False,
            'payment_info': {
                'method_id': 'corp-5e36732e2bc54e088b1466e08e31c486',
                'type': 'corp',
            },
            'performer': {
                'driver_id': 'driver_id1',
                'park_db_id': 'park_db_id1',
            },
            'price_for': 'performer',
            'resolution_info': {
                'resolution': 'completed',
                'resolved_at': '2020-06-01T09:00:00+00:00',
            },
            'tariff_class': 'mock-tariff',
            'taxi_requirements': {},
            'transport': 'electric_bicycle',
            'waypoints': [
                {
                    'first_time_arrived_at': (
                        '2020-08-18T14:01:49.939497+00:00'
                    ),
                    'id': 'seg_2_point_1',
                    'claim_id': 'claim_uuid_2',
                    'position': [37.583, 55.9873],
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': matching.any_string,
                    },
                    'type': 'pickup',
                },
                {
                    'first_time_arrived_at': (
                        '2020-08-18T14:01:49.939497+00:00'
                    ),
                    'id': 'seg_2_point_2',
                    'claim_id': 'claim_uuid_2',
                    'position': [37.583, 55.8873],
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': matching.any_string,
                    },
                    'type': 'dropoff',
                },
                {
                    'id': 'seg_2_point_3',
                    'claim_id': 'claim_uuid_2',
                    'position': [37.583, 55.8873],
                    'resolution_info': {
                        'resolution': 'skipped',
                        'resolved_at': matching.any_string,
                    },
                    'type': 'return',
                },
            ],
            'entity_id': 'order/taxi-order',
            'origin_uri': 'cargo-orders/v1/calc-price',
            'calc_kind': 'analytical',
        },
    ]


async def test_calc_with_additional_prices_disabled(
        calc_price,
        mock_cargo_pricing_calc,
        my_batch_waybill_info_with_segments,
        conf_exp3_additional_prices,
):
    await conf_exp3_additional_prices(enabled=False)
    await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc.mock.times_called == 1


async def test_calc_with_additional_prices_kwargs(
        calc_price,
        mock_cargo_pricing_calc,
        my_batch_waybill_info_with_segments,
        conf_exp3_additional_prices,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_additional_price_calcs',
    )
    await conf_exp3_additional_prices(enabled=True)
    await calc_price(source_type='requestconfirm')

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['consumer'] == 'cargo-orders/additional_price_calcs'
    assert kwargs['homezone'] == 'moscow'
    assert kwargs['batched_claims_count'] == 2
    assert kwargs['price_for'] == 'performer'
    assert kwargs['calc_stage'] == 'order_finished'
    assert kwargs['tariff_class'] == 'mock-tariff'
    assert kwargs['request_timestamp']


async def test_calc_request_waypoints_on_batched_order(
        calc_price,
        mock_cargo_pricing_calc,
        my_batch_waybill_info_with_segments,
        resolve_waybill,
):
    resolve_waybill(my_batch_waybill_info_with_segments)
    await calc_price(source_type='requestconfirm')
    assert mock_cargo_pricing_calc.mock.times_called == 1
    waypoints = mock_cargo_pricing_calc.request['waypoints']
    for point in waypoints:
        point.pop('first_time_arrived_at', None)
        point.pop('resolution_info')
    assert mock_cargo_pricing_calc.request['waypoints'] == [
        {
            'position': [37.642979, 55.734977],
            'type': 'pickup',
            'id': 'seg_1_point_1',
            'claim_id': 'claim_uuid_1',
        },
        {
            'id': 'seg_2_point_1',
            'claim_id': 'claim_uuid_2',
            'position': [37.583, 55.9873],
            'type': 'pickup',
        },
        {
            'id': 'seg_2_point_2',
            'claim_id': 'claim_uuid_2',
            'position': [37.583, 55.8873],
            'type': 'dropoff',
        },
        {
            'position': [37.583, 55.8873],
            'type': 'dropoff',
            'id': 'seg_1_point_2',
            'claim_id': 'claim_uuid_1',
        },
        {
            'position': [37.583, 55.8873],
            'type': 'return',
            'id': 'seg_1_point_3',
            'claim_id': 'claim_uuid_1',
        },
        {
            'id': 'seg_2_point_3',
            'claim_id': 'claim_uuid_2',
            'position': [37.583, 55.8873],
            'type': 'return',
        },
    ]
