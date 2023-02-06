import pytest

from testsuite.utils import matching


async def test_new_segments_not_ready_to_build_waybills(
        happy_path_state_first_import, get_segment_info,
):
    seginfo = await get_segment_info('seg1')
    assert not seginfo['dispatch']['waybill_building_awaited']
    assert seginfo['dispatch'] == {
        'resolved': False,
        'revision': 1,
        'routers': [],
        'status': 'new',
        'waybill_building_awaited': False,
        'waybill_building_version': 1,
        'waybill_chosen': False,
    }


async def test_logistic_contract(
        happy_path_state_routers_chosen, get_segment_info,
):
    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['is_new_logistic_contract']


async def test_segments_with_chosen_routers_ready_to_build_waybills(
        happy_path_state_routers_chosen, get_segment_info,
):
    seginfo = await get_segment_info('seg1')
    assert seginfo['dispatch']['waybill_building_awaited']


@pytest.mark.parametrize(
    'current_resolution', ['finished', 'performer_not_found'],
)
async def test_resolve_segment(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        get_segment_info,
        run_claims_segment_replication,
        mockserver,
        current_resolution,
):
    seginfo = await get_segment_info('seg1')
    assert not seginfo['dispatch']['resolved']

    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def _handler(request):
        journal = happy_path_claims_segment_db.read_claims_journal()
        entry = journal['entries'][-1].copy()
        entry['current']['resolution'] = current_resolution
        entry['revision'] = 2
        entry['segment_id'] = 'seg1'
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json={'cursor': '100', 'entries': [entry]},
        )

    await run_claims_segment_replication()

    seginfo = await get_segment_info('seg1')
    assert seginfo['dispatch']['resolved']


async def test_requirements(happy_path_state_first_import, get_segment_info):
    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['performer_requirements'] == {
        'dispatch_requirements': {
            'soft_requirements': [
                {
                    'logistic_group': 'lavka',
                    'type': 'performer_group',
                    'performers_restriction_type': 'group_only',
                },
            ],
        },
        'door_to_door': True,
        'special_requirements': {
            'virtual_tariffs': [
                {
                    'class': 'express',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        },
        'taxi_classes': ['express'],
        'cargo_type_int': 1,
        'cargo_points': [2, 2],
        'cargo_points_field': 'fake_middle_point_express',
    }


async def test_time_intervals(happy_path_state_first_import, get_segment_info):
    seginfo = await get_segment_info('seg1')
    time_intervals = [
        x['time_intervals'] for x in seginfo['segment']['points']
    ]
    assert time_intervals == [
        [],
        [
            {
                'type': 'strict_match',
                'from': '2020-01-01T00:00:00+00:00',
                'to': '2020-01-02T00:00:00+00:00',
            },
        ],
        [],
        [
            {
                'type': 'strict_match',
                'from': '2020-01-03T00:00:00+00:00',
                'to': '2020-01-06T00:00:00+00:00',
            },
            {
                'type': 'perfect_match',
                'from': '2020-01-04T00:00:00+00:00',
                'to': '2020-01-05T00:00:00+00:00',
            },
        ],
        [],
        [],
        [],
    ]


@pytest.mark.parametrize('allow_batch', [False, True])
async def test_allow_batch(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
        allow_batch,
):
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['allow_batch'] = allow_batch

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['allow_batch'] == allow_batch


async def test_due(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
):
    due = '2020-08-14T18:35:00+00:00'
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['due'] = due

    seginfo = await get_segment_info('seg1')
    points = sorted(
        seginfo['segment']['points'], key=lambda point: point['visit_order'],
    )
    assert points[0]['due'] == due


async def test_modified_classes_passed_as_is(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
        segment_id='seg1',
):
    modified_classes = ['eda', 'lavka', 'whatever']
    happy_path_claims_segment_db.set_segment_modified_classes(
        segment_id, modified_classes,
    )
    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['modified_classes'] == modified_classes


async def test_no_modified_classes_by_default(
        happy_path_state_first_import, get_segment_info,
):
    seginfo = await get_segment_info('seg1')
    assert 'modified_classes' not in seginfo['dispatch']
    assert 'tariffs_substitution' not in seginfo['dispatch']


async def test_tariffs_substitution_passed_as_is(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
        segment_id='seg1',
):
    tariffs_substitution = ['courier', 'express']
    happy_path_claims_segment_db.set_seg_tariffs_substitution(
        segment_id, tariffs_substitution,
    )
    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['tariffs_substitution'] == tariffs_substitution


@pytest.mark.parametrize('custom_context', [{'region_id': 123}, None])
async def test_custom_context(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
        custom_context: dict,
):
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['custom_context'] = custom_context

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment'].get('custom_context', None) == custom_context
    assert seginfo['segment']['zone_id'] == 'moscow'
    assert (
        seginfo['segment']['corp_client_id']
        == 'corp_client_id_56789012345678912'
    )


async def test_delayed_tariffs(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        get_segment_info,
        segment_id='seg3',
):
    delayed_tariffs = {
        'lookup_started_at': '2030-08-14T18:37:00.123+00:00',
        'tariffs': [{'taxi_class': 'express', 'delay_since_lookup': 200}],
        'ignorable_special_requirements': [
            {
                'delay_by_due': -300,
                'requirements': ['thermobag_confirmed'],
                'taxi_class': 'courier',
            },
        ],
    }

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_delayed_tariffs(delayed_tariffs)

    seginfo = await get_segment_info(segment_id)
    assert seginfo['segment']['delayed_tariffs'] == delayed_tariffs


async def test_client_info(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        get_segment_info,
        segment_id='seg3',
):
    client_info = {
        'user_id': 'user_1',
        'payment_info': {'type': 'type_1', 'method_id': 'method_1'},
        'user_locale': 'fr',
    }

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_client_info(client_info)

    seginfo = await get_segment_info(segment_id)
    assert seginfo['segment']['client_info'] == client_info


async def test_best_router_id(
        happy_path_state_routers_chosen, get_segment_info,
):
    seginfo = await get_segment_info('seg1')
    assert seginfo['dispatch']['best_router_id'] == 'smart_router'


async def test_routers(happy_path_state_routers_chosen, get_segment_info):
    seginfo = await get_segment_info('seg1')
    assert seginfo['dispatch']['routers'] == [
        {
            'id': 'smart_router',
            'is_deleted': False,
            'source': 'cargo-dispatch-choose-routers:segment_routers:0',
            'priority': 10,
            'autoreorder_flow': 'newway',
        },
        {
            'id': 'fallback_router',
            'is_deleted': False,
            'source': 'cargo-dispatch-choose-routers:segment_routers:0',
            'priority': 100,
            'autoreorder_flow': 'newway',
        },
    ]


async def test_execution(happy_path_state_orders_created, get_segment_info):
    seginfo = await get_segment_info('seg1')
    assert 'search_limits_overrides' in seginfo['execution']
    seginfo['execution'].pop('search_limits_overrides')
    assert seginfo['execution'] == {
        'taxi_order_id': matching.AnyString(),
        'cargo_order_id': matching.AnyString(),
    }


async def test_comments_passed(
        happy_path_state_first_import, get_segment_info, segment_id='seg3',
):
    seginfo = await get_segment_info(segment_id)
    comments = [loc.get('comment') for loc in seginfo['segment']['points']]
    assert comments == [
        'comment_for_seg3_A1',
        'comment_for_seg3_B1',
        'comment_for_seg3_A1',
    ]


async def test_external_order_id_passed(
        happy_path_state_first_import, get_segment_info, segment_id='seg3',
):
    seginfo = await get_segment_info(segment_id)
    external_order_ids = [
        loc.get('external_order_id') for loc in seginfo['segment']['points']
    ]
    assert external_order_ids == [
        '1234-5678-seg3_A1',
        None,
        '1234-5678-seg3_A1',
    ]


@pytest.mark.parametrize(
    'dispatch_min_revision, claims_min_revision', [(None, None), (1, '1')],
)
async def test_send_min_claims_revision(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_info_handler,
        dispatch_min_revision,
        claims_min_revision,
):
    seginfo = await get_segment_info(
        'seg1', min_revision=dispatch_min_revision,
    )
    assert seginfo['diagnostics']['claims_segment_revision'] == 1

    assert happy_path_claims_segment_info_handler.times_called == 1
    assert (
        happy_path_claims_segment_info_handler.next_call()[
            'request'
        ].query.get('min_revision', None)
        == claims_min_revision
    )


async def test_use_slave_and_fallback_to_master(
        happy_path_state_first_import,
        request_segment_info,
        happy_path_claims_segment_info_handler,
        testpoint,
):
    @testpoint('min-revision-provided-use-slave')
    def use_slave(data):
        return

    @testpoint('min-revision-provided-fallback-to-master')
    def use_master(data):
        return

    @testpoint('min-revision-provided-outdated-master-version')
    def outdated_master(data):
        return

    response = await request_segment_info('seg1', min_revision=10)

    await use_slave.wait_call()
    await use_master.wait_call()
    await outdated_master.wait_call()

    assert response.status_code == 200


async def test_do_not_use_master_if_found_in_slave(
        happy_path_state_first_import,
        request_segment_info,
        happy_path_claims_segment_info_handler,
        testpoint,
):
    @testpoint('min-revision-provided-use-slave')
    def use_slave(data):
        return

    @testpoint('min-revision-provided-no-fallback-to-master')
    def do_not_use_master(data):
        return

    response = await request_segment_info('seg1', min_revision=1)

    await use_slave.wait_call()
    await do_not_use_master.wait_call()

    assert response.status_code == 200


def taxi_calc_retrieve_response(pricing_case, paid_supply_price):
    response = {
        'calculations': [
            {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'prices': {'total_price': '259.999'},
                    'details': {
                        'algorithm': {'pricing_case': pricing_case},
                        'currency': {'code': 'RUB'},
                        'services': [],
                        'waypoints': [],
                    },
                    'cancel_options': {
                        'free_cancel': {'free_cancel_timeout': 300},
                    },
                    'diagnostics': {},
                },
            },
        ],
    }

    if paid_supply_price:
        response['calculations'][0]['result']['prices'][
            'paid_supply_price'
        ] = paid_supply_price
    return response


@pytest.mark.config(
    DISPATCH_SETTINGS_OVERRIDE_SETTINGS={
        'experiment_names': ['cargo_dispatch_settings_override'],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_dispatch_settings_override',
    consumers=['cargo/dispatch-settings'],
    clauses=[],
    default_value={
        'dispatch_settings_override_values': {
            'DIST': 666,
            'MAX_ROBOT_DISTANCE': 1666,
            'PEDESTRIAN_MAX_SEARCH_RADIUS': 1234,
            'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 16123,
        },
    },
)
async def test_paid_supply(
        taxi_cargo_dispatch,
        happy_path_state_routers_chosen,
        get_segment_info,
        happy_path_claims_segment_db,
        mockserver,
        dispatch_settings_mocks,
):
    dispatch_settings_mocks.set_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'QUERY_LIMIT_FREE_PREFERRED': 27,
                            'QUERY_LIMIT_LIMIT': 37,
                            'QUERY_LIMIT_MAX_LINE_DIST': 15000,
                            'MAX_ROBOT_DISTANCE': 15000,
                            'MAX_ROBOT_TIME': 900,
                        },
                    },
                ],
            },
        ],
    )
    await taxi_cargo_dispatch.invalidate_caches()
    segment_id = 'seg1'
    happy_path_claims_segment_db.set_yandex_uid(segment_id, '123')
    happy_path_claims_segment_db.set_calc_id(
        segment_id, 'cargo-pricing/v1/01234567890123456789012345678912',
    )

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _pricing_retrieve(request):
        return taxi_calc_retrieve_response('paid_cancel_in_driving', '59.01')

    seginfo = await get_segment_info(segment_id)
    assert seginfo['execution']['search_limits_overrides'] == [
        {
            'tariff': 'express',
            'limits': {
                'free_preferred': 27,
                'limit': 37,
                'max_line_distance': 1999,
                'max_route_distance': 1999,
                'max_route_time': 1080,
                'pedestrian_max_search_radius': 1234,
                'pedestrian_max_route_distance': 16123,
                'pedestrian_max_route_time': 10800,
                'transport_types': [
                    {
                        'settings': {
                            'max_route_distance': 15000,
                            'max_route_time': 10800,
                            'max_search_radius': 2000,
                        },
                        'type': '__default__',
                    },
                ],
            },
        },
    ]


@pytest.mark.parametrize(
    'cancel_type, paid_supply_price, result',
    [
        (
            'free_cancel',
            None,
            {
                'tariff': 'express',
                'limits': {
                    'free_preferred': 10,
                    'limit': 20,
                    'max_line_distance': 4900,
                    'max_route_distance': 4900,
                    'max_route_time': 720,
                    'pedestrian_max_search_radius': 2000,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
            },
        ),
        (
            'paid_cancel_in_driving',
            '59.01',
            {
                'limits': {
                    'free_preferred': 10,
                    'limit': 20,
                    'max_line_distance': 5880,
                    'max_route_distance': 5880,
                    'max_route_time': 864,
                    'pedestrian_max_route_distance': 15000,
                    'pedestrian_max_route_time': 10800,
                    'pedestrian_max_search_radius': 2000,
                    'transport_types': [
                        {
                            'settings': {
                                'max_route_distance': 15000,
                                'max_route_time': 10800,
                                'max_search_radius': 2000,
                            },
                            'type': '__default__',
                        },
                    ],
                },
                'tariff': 'express',
            },
        ),
    ],
)
async def test_paid_supply_without_exp(
        taxi_cargo_dispatch,
        happy_path_state_routers_chosen,
        get_segment_info,
        happy_path_claims_segment_db,
        mockserver,
        dispatch_settings_mocks,
        cancel_type,
        paid_supply_price,
        result,
):
    await taxi_cargo_dispatch.invalidate_caches()
    segment_id = 'seg1'
    happy_path_claims_segment_db.set_yandex_uid(segment_id, '123')
    happy_path_claims_segment_db.set_calc_id(
        segment_id, 'cargo-pricing/v1/01234567890123456789012345678912',
    )

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _pricing_retrieve(request):
        return taxi_calc_retrieve_response(cancel_type, paid_supply_price)

    seginfo = await get_segment_info(segment_id)
    assert seginfo['execution']['search_limits_overrides'] == [result]


@pytest.mark.skip(reason='search_limits_overrides exists always')
async def test_paid_supply_error(
        happy_path_state_routers_chosen,
        get_segment_info,
        happy_path_claims_segment_db,
        mockserver,
):
    segment_id = 'seg1'
    happy_path_claims_segment_db.set_yandex_uid(segment_id, '123')
    happy_path_claims_segment_db.set_calc_id(
        segment_id, 'cargo-pricing/v1/01234567890123456789012345678912',
    )

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _pricing_retrieve(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': '500'},
        )

    seginfo = await get_segment_info(segment_id)
    assert 'search_limits_overrides' not in seginfo['execution']


async def test_estimations(happy_path_state_first_import, get_segment_info):
    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['estimations'] == [
        {
            'classes_substitution': ['courier', 'express'],
            'offer_id': 'taxi_offer_id_1',
            'offer_price': '999.0010',
            'offer_price_mult': '1198.8012',
            'tariff_class': 'express',
        },
    ]


async def test_same_day_data(
        happy_path_state_first_import,
        get_segment_info,
        happy_path_claims_segment_db,
):
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['same_day_data'] = {
        'delivery_interval': {
            'from': '2020-01-01T00:00:00+00:00',
            'to': '2020-01-01T00:01:00+00:00',
        },
    }

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['same_day_data'] == {
        'delivery_interval': {
            'from': '2020-01-01T00:00:00+00:00',
            'to': '2020-01-01T00:01:00+00:00',
        },
    }
