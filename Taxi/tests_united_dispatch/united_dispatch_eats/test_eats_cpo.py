CPO_VALUE = 10
CPO_VALUE_BATCH = 20
CPO_CURRENCY = 'RUB'


def check_driver_scoring_request(req):
    for request in req['requests']:
        for candidate in request['candidates']:
            assert candidate['cpo_info'] == {
                'use_fallback': False,
                'cpo_value': (
                    CPO_VALUE
                    if len(
                        request['search']['order']['request'][
                            'batch_properties'
                        ]['segments'],
                    )
                    == 1
                    else CPO_VALUE_BATCH
                ),
                'currency': CPO_CURRENCY,
            }


def sort_candidates(candidates):
    candidates.sort(
        key=lambda candidate: (
            candidate['courier_id'],
            candidate['to_rest_distance_m'],
        ),
    )


def make_mock_cpo_response(request):
    info = []
    for arg in request['args']:
        way_info = {
            'key': arg['key'],
            'currency': CPO_CURRENCY,
            'orders': [],
            'candidates': [],
        }

        orders = []
        for order in arg['orders']:
            orders.append(
                {
                    'order_nr': order['order_nr'],
                    'courier_demand_coefficient': 1,
                },
            )
        way_info['orders'] = orders

        candidates = []
        for candidate in arg['candidates']:
            candidates.append(
                {
                    'courier_id': candidate['courier_id'],
                    'cpo_value': (
                        CPO_VALUE if len(orders) == 1 else CPO_VALUE_BATCH
                    ),
                },
            )
        way_info['candidates'] = candidates

        info.append(way_info)

    return {'info': info}


class CpoBulkEstimateMockServer:
    def __init__(self, way_args):
        self.way_args = {}
        self.way_args_calls = {}
        for arg in way_args:
            key = arg['key']
            self.way_args[key] = arg
            self.way_args_calls[key] = 0

    def call(self, request):
        for arg in request['args']:
            key = arg['key']
            assert key in self.way_args
            sort_candidates(arg['candidates'])
            sort_candidates(self.way_args[key]['candidates'])
            assert self.way_args[key] == arg
            assert self.way_args_calls[key] == 0
            self.way_args_calls[key] += 1

        return make_mock_cpo_response(request)

    def check_calls(self):
        for count in self.way_args_calls.values():
            assert count == 1


async def test_eats_cpo_segment_routes(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        exp_eats_dispatch_settings,
        mockserver,
        scoring,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_cpo_requests_filter',
        consumers=['united-dispatch/cpo-requests-filter-kwargs'],
        clauses=[],
        default_value={'allowed': True},
    )
    await exp_eats_dispatch_settings(request_cpo_for_driver_scoring=True)

    cpo_bulk_estimate_server = CpoBulkEstimateMockServer(
        [
            {
                'key': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/pedestrian',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                        'to_client_distance_m': 8895,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian1',
                        'to_rest_distance_m': 1111,
                    },
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 0,
                    },
                ],
            },
            {
                'key': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/car',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                        'to_client_distance_m': 8895,
                    },
                ],
                'candidates': [
                    {'courier_id': 'dbid1_car1', 'to_rest_distance_m': 1572},
                    {'courier_id': 'dbid1_car2', 'to_rest_distance_m': 1111},
                ],
            },
            {
                'key': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/pedestrian',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                        'to_client_distance_m': 8895,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian1',
                        'to_rest_distance_m': 6763,
                    },
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 6671,
                    },
                ],
            },
            {
                'key': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/car',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                        'to_client_distance_m': 8895,
                    },
                ],
                'candidates': [
                    {'courier_id': 'dbid1_car1', 'to_rest_distance_m': 7862},
                    {'courier_id': 'dbid1_car2', 'to_rest_distance_m': 7783},
                ],
            },
        ],
    )

    @mockserver.json_handler(
        '/eats-logistics-performer-payouts/v1/cpo/bulk-estimate',
    )
    def _mock_cpo_bulk_estimate(request):
        return cpo_bulk_estimate_server.call(request.json)

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        segment_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[0.01, 0],
        dropoff_coordinates=[0.01, 0.08],
    )
    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        segment_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[0.07, 0],
        dropoff_coordinates=[0.07, 0.08],
    )
    await state_waybill_proposed()

    cpo_bulk_estimate_server.check_calls()
    check_driver_scoring_request(scoring.requests[-1].json)


async def test_eats_cpo_batch_routes(
        mockserver,
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        make_eats_custom_context,
        load_json,
        candidates,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        scoring,
        experiments3,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'] = candidates_json['candidates'][:2]

    candidates(candidates_json)

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_cpo_requests_filter',
        consumers=['united-dispatch/cpo-requests-filter-kwargs'],
        clauses=[],
        default_value={'allowed': True},
    )
    await exp_eats_dispatch_settings(request_cpo_for_driver_scoring=True)

    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=True,
        use_driver_scoring_score_for_segments=True,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(_):
        return mockserver.make_response(status=499)

    await exp_eats_scoring_coefficients(
        pickup_cost=0,
        dropoff_cost=0,
        long_arrival_cost=0,
        long_arrival_distance_km=0,
        arrival_kilometer_payment=1000,
        delivery_kilometer_payment=1000,
        additional_cost=0,
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        segment_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[0.01, 0],
        dropoff_coordinates=[0.01, 0.08],
    )
    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        segment_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[0.07, 0],
        dropoff_coordinates=[0.07, 0.08],
    )
    await state_taxi_order_performer_found()
    await state_taxi_order_performer_found()

    cpo_bulk_estimate_server = CpoBulkEstimateMockServer(
        [
            {
                'key': (
                    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/3/'
                    + 'cccccccc-cccc-cccc-cccc-cccccccccccc/2'
                ),
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                        'is_first_in_batch': True,
                        'to_client_distance_m': 1572,
                    },
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
                        'is_first_in_batch': False,
                        'to_rest_distance_m': 0,
                        'to_client_distance_m': 7862,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 6671,
                    },
                ],
            },
            {
                'key': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/pedestrian',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                        'to_client_distance_m': 8895,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 6671,
                    },
                ],
            },
            {
                'key': (
                    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb/2/'
                    + 'cccccccc-cccc-cccc-cccc-cccccccccccc/3'
                ),
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
                        'is_first_in_batch': True,
                        'to_client_distance_m': 8895,
                    },
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
                        'is_first_in_batch': False,
                        'to_rest_distance_m': 0,
                        'to_client_distance_m': 1572,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 6671,
                    },
                ],
            },
            {
                'key': 'cccccccc-cccc-cccc-cccc-cccccccccccc/pedestrian',
                'orders': [
                    {
                        'order_nr': '1234-5678',
                        'claim_uuid': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
                        'to_client_distance_m': 7862,
                    },
                ],
                'candidates': [
                    {
                        'courier_id': 'dbid1_pedestrian1',
                        'to_rest_distance_m': 6763,
                    },
                    {
                        'courier_id': 'dbid1_pedestrian2',
                        'to_rest_distance_m': 6671,
                    },
                ],
            },
        ],
    )

    @mockserver.json_handler(
        '/eats-logistics-performer-payouts/v1/cpo/bulk-estimate',
    )
    def _mock_cpo_bulk_estimate(request):
        return cpo_bulk_estimate_server.call(request.json)

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        segment_id='cccccccc-cccc-cccc-cccc-cccccccccccc',
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[0.07, 0],
        dropoff_coordinates=[0.06, 0.07],
    )
    await state_waybill_proposed()

    cpo_bulk_estimate_server.check_calls()
    check_driver_scoring_request(scoring.requests[-2].json)
    check_driver_scoring_request(scoring.requests[-1].json)
