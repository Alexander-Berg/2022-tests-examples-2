# pylint: disable=too-many-lines
import copy

import pytest


BASE_SEGMENT = {
    'diagnostics': {
        'claim_id': '72896ecfddee4da991d88873142dbcab',
        'claims_segment_created_ts': '2021-09-23T15:37:02.826677+00:00',
        'claims_segment_revision': 1,
        'created_ts': '2021-09-23T15:37:07.095141+00:00',
        'current_revision_ts': '2021-09-23T15:38:20.819954+00:00',
    },
    'dispatch': {
        'best_router_id': 'logistic-dispatch',
        'chosen_waybill': {
            'external_ref': (
                'logistic-dispatch/7d246299-8b70-484c-ba11-127319ac98b6'
            ),
            'router_id': 'logistic-dispatch',
        },
        'resolved': False,
        'revision': 6,
        'status': 'wait_for_resolution',
        'waybill_building_awaited': True,
        'waybill_building_deadline': '2021-09-23T15:38:47.185337+00:00',
        'waybill_building_version': 1,
        'waybill_chosen': True,
    },
    'execution': {
        'cargo_order_id': '65608976-bd27-48ee-94ed-b20acf212dfc',
        'taxi_order_id': '6486f411742b2b149b2b55fd4849ba70',
    },
    'segment': {
        'allow_alive_batch_v1': True,
        'allow_alive_batch_v2': False,
        'allow_batch': True,
        'claim_comment': 'cargo-return-on-point-B,speed-1800,wait-3',
        'claim_features': [],
        'client_info': {
            'payment_info': {
                'method_id': 'corp-70a499f9eec844e9a758f4bc33e667c0',
                'type': 'corp',
            },
            'user_locale': 'ru',
        },
        'corp_client_id': '70a499f9eec844e9a758f4bc33e667c0',
        'custom_context': {},
        'id': 'seg_id',
        'items': [
            {
                'dropoff_point': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'item_id': 'bf0d5230ab544d29b5dc0a785aaa169c',
                'pickup_point': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'quantity': 1,
                'return_point': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                'size': {'height': 0.0, 'length': 0.0, 'width': 0.0},
                'title': 'Миска Joy ',
                'weight': 0.0,
            },
        ],
        'locations': [
            {
                'coordinates': [37.632745, 55.774532],
                'id': 'c0d07aa9fefc4df3bf9fde2fcceb8e83',
            },
            {
                'coordinates': [37.63223287, 55.76815715],
                'id': 'b471e75a88a040abb6d84a523142d2fa',
            },
            {
                'coordinates': [37.632745, 55.774532],
                'id': 'f1c6e566c76a4bbfbb8082cc8dd9a0d0',
            },
        ],
        'performer_requirements': {
            'door_to_door': True,
            'special_requirements': {'virtual_tariffs': []},
            'taxi_classes': ['courier'],
        },
        'points': [
            {
                'comment': 'Это доп.инструкции\\n\\n',
                'contact': {
                    'name': 'Тимофеева  ',
                    'personal_phone_id': 'f2c0d0cd46e74c1a8e7242dcba6fdfc8',
                },
                'location_id': 'c0d07aa9fefc4df3bf9fde2fcceb8e83',
                'point_id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'type': 'pickup',
                'visit_order': 1,
            },
            {
                'comment': '\\n\\n',
                'contact': {
                    'name': 'последнееимя первоеимя среднееимя',
                    'personal_phone_id': 'e1371405ac984a82a5f9818e04a1eb70',
                },
                'location_id': 'b471e75a88a040abb6d84a523142d2fa',
                'point_id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'type': 'dropoff',
                'visit_order': 2,
            },
            {
                'comment': 'Это доп.инструкции\n',
                'contact': {
                    'name': 'Тимофеева  ',
                    'personal_phone_id': 'f2c0d0cd46e74c1a8e7242dcba6fdfc8',
                },
                'location_id': 'f1c6e566c76a4bbfbb8082cc8dd9a0d0',
                'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                'type': 'return',
                'visit_order': 3,
            },
        ],
        'zone_id': 'moscow',
    },
}


BASE_ROUTING_RESPONSE = {
    'id': 'task_id_1',
    'result': {
        'dropped_locations': [],
        'routes': [
            {
                'route': [
                    # 1 фейковый склад
                    {
                        'arrival_time_s': 29820,
                        'node': {
                            'type': 'depot',
                            'value': {'id': 'fake point'},
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                    # 1 гараж
                    {
                        'arrival_time_s': 29820,
                        'node': {
                            'type': 'location',
                            'value': {'id': 'park2_driver2_garage'},
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                    {
                        'arrival_time_s': 32383,
                        'node': {
                            'type': 'location',
                            'value': {
                                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                            },
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                    {
                        'arrival_time_s': 32383,
                        'node': {
                            'type': 'location',
                            'value': {
                                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                            },
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                ],
                'vehicle_id': 'park1_driver1',
            },
        ],
        'solver_status': 'SOLVED',
    },
    'status': {
        'calculated': 1594918486.55505,
        'completed': 1594918486.6293,
        'matrix_downloaded': 1594918485.5085,
        'queued': 1594918485.2221,
        'started': 1594918485.26308,
    },
}


BASE_SETTINGS = {
    'moscow': [
        {
            'delivery_guarantees': [
                {
                    'orders_created_till': '1970-01-01T12:00:00+00:00',
                    'start_routing_at': '1970-01-01T12:00:00+00:00',
                    'pickup_till': '1970-01-01T13:00:00+00:00',
                    'deliver_till': '1970-01-01T16:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T13:00:00+00:00',
                },
                {
                    'orders_created_till': '1970-01-01T14:00:00+00:00',
                    'start_routing_at': '1970-01-01T14:00:00+00:00',
                    'pickup_till': '1970-01-01T15:00:00+00:00',
                    'deliver_till': '1970-01-01T18:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T15:00:00+00:00',
                },
            ],
            'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
            'taxi_classes': ['cargo'],
            'fake_depot': {'lon': 0, 'lat': 0},
        },
        {
            'corp_client_ids': ['111', '333'],
            'delivery_guarantees': [
                {
                    'orders_created_till': '1970-01-01T12:00:00+00:00',
                    'start_routing_at': '1970-01-01T12:10:00+00:00',
                    'pickup_till': '1970-01-01T13:10:00+00:00',
                    'deliver_till': '1970-01-01T16:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T13:00:00+00:00',
                },
                {
                    'orders_created_till': '1970-01-01T14:00:00+00:00',
                    'start_routing_at': '1970-01-01T14:00:00+00:00',
                    'pickup_till': '1970-01-01T15:00:00+00:00',
                    'deliver_till': '1970-01-01T18:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T15:00:00+00:00',
                },
            ],
            'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
            'taxi_classes': ['cargo'],
            'fake_depot': {'lon': 0, 'lat': 0},
        },
    ],
}

PROPOSITION_DUMP = {
    'external_ref': 'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
    'points': [
        {
            'point_id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
            'segment_id': 'seg_id',
            'visit_order': 1,
        },
        {
            'point_id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
            'segment_id': 'seg_id',
            'visit_order': 2,
        },
        {
            'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
            'segment_id': 'seg_id',
            'visit_order': 3,
        },
    ],
    'router_id': 'cargo_same_day_delivery_router',
    'segments': [{'segment_id': 'seg_id', 'waybill_building_version': 1}],
    'special_requirements': {'virtual_tariffs': []},
    'taxi_order_requirements': {
        'door_to_door': True,
        'taxi_classes': ['cargo'],
    },
    'taxi_lookup_extra': {
        'intent': 'cargo-sdd',
        'performer_id': 'park1_driver1',
    },
}


async def get_sdd_segments(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT
            segment_id, revision, status,
            dropped_location_reason, proposition_ref
        FROM cargo_sdd.segments
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_routing_tasks(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT
            task_id, idempotency_token, status,
            segments_count, couriers_count
        FROM cargo_sdd.routing_tasks
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_propositions(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT
            waybill_ref, waybill_proposition, already_reproposed
        FROM cargo_sdd.propositions
        ORDER BY id
        """,
    )
    return cursor.fetchall()


@pytest.mark.config(
    CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS={
        'moscow': [
            {
                'delivery_guarantees': [
                    {
                        'orders_created_till': '1970-01-01T12:00:00+00:00',
                        'start_routing_at': '1970-01-01T12:00:00+00:00',
                        'pickup_till': '1970-01-01T13:00:00+00:00',
                        'deliver_till': '1970-01-01T16:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T13:00:00+00:00'
                        ),
                    },
                    {
                        'orders_created_till': '1970-01-01T14:00:00+00:00',
                        'start_routing_at': '1970-01-01T14:00:00+00:00',
                        'pickup_till': '1970-01-01T15:00:00+00:00',
                        'deliver_till': '1970-01-01T18:00:00+00:00',
                        'waybill_building_deadline': (
                            '1970-01-01T15:00:00+00:00'
                        ),
                    },
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': ['cargo'],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_happy_path(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg_id', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        assert task_id == 'task_id_1'
        return BASE_ROUTING_RESPONSE

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        assert request.json == {
            'external_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
            'router_id': 'cargo_same_day_delivery_router',
            'segments': [
                {'segment_id': 'seg_id', 'waybill_building_version': 1},
            ],
            'points': [
                {
                    'point_id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                    'segment_id': 'seg_id',
                    'visit_order': 1,
                },
                {
                    'point_id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'segment_id': 'seg_id',
                    'visit_order': 2,
                },
                {
                    'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                    'segment_id': 'seg_id',
                    'visit_order': 3,
                },
            ],
            'special_requirements': {'virtual_tariffs': []},
            'taxi_order_requirements': {
                'door_to_door': True,
                'taxi_classes': ['cargo'],
            },
            'taxi_lookup_extra': {
                'performer_id': 'park1_driver1',
                'intent': 'cargo-sdd',
            },
        }
        return {}

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={'zone_id': 'moscow', 'routing_task_id': 'task_id_1'},
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_id',
            2,
            'waybill_proposed',
            None,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [
        ('task_id_1', 'task_id_1_idempotency', 'SOLVED', 2, 2),
    ]

    propositions = await get_propositions(pgsql)
    assert propositions == [
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            PROPOSITION_DUMP,
            False,
        ),
    ]

    assert not stq.cargo_sdd_check_routing_result.times_called


@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_unfeasible(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        assert task_id == 'task_id_1'
        response = copy.deepcopy(BASE_ROUTING_RESPONSE)
        response['result']['solver_status'] = 'UNFEASIBLE'
        return response

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={'zone_id': 'moscow', 'routing_task_id': 'task_id_1'},
    )

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [
        ('task_id_1', 'task_id_1_idempotency', 'UNFEASIBLE', 2, 2),
    ]
    assert not stq.cargo_sdd_check_routing_result.times_called


# test_result_not_ready
# test_resolt_failed
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_not_ready_yet(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        assert task_id == 'task_id_1'
        return mockserver.make_response(
            status=201,
            json={'status': {'queued': 0, 201: 0}, 'id': 'task_id_1'},
        )

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={'zone_id': 'moscow', 'routing_task_id': 'task_id_1'},
    )

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [
        ('task_id_1', 'task_id_1_idempotency', 'pending', 2, 2),
    ]
    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == 'task_id_1'


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=BASE_SETTINGS)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_different_corp_intervals(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['id'] = request.query['segment_id']
        segment['segment']['points'][0]['point_id'] = request.query[
            'segment_id'
        ]
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        assert task_id == 'task_id_1'
        response = copy.deepcopy(BASE_ROUTING_RESPONSE)
        # Фейки, чтобы маршрут построился
        # (т.к. переопределил тут id в BASE_SEGMENT)
        response['result']['routes'][0]['route'][2]['node']['value'][
            'id'
        ] = 'seg1'
        return response

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        assert request.json == {
            'external_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
            'router_id': 'cargo_same_day_delivery_router',
            'segments': [
                {'segment_id': 'seg1', 'waybill_building_version': 1},
                {'segment_id': 'seg3', 'waybill_building_version': 1},
            ],
            'points': [
                {'point_id': 'seg1', 'segment_id': 'seg1', 'visit_order': 1},
                {
                    'point_id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'segment_id': 'seg3',
                    'visit_order': 2,
                },
                {
                    'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                    'segment_id': 'seg3',
                    'visit_order': 3,
                },
                {
                    'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                    'segment_id': 'seg1',
                    'visit_order': 4,
                },
            ],
            'special_requirements': {'virtual_tariffs': []},
            'taxi_order_requirements': {
                'door_to_door': True,
                'taxi_classes': ['cargo'],
            },
            'taxi_lookup_extra': {
                'performer_id': 'park1_driver1',
                'intent': 'cargo-sdd',
            },
        }
        return {}

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'corp_client_ids': ['111', '333'],
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg1',
            2,
            'waybill_proposed',
            None,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
        ('seg2', 1, 'routing_launched', None, None),
        (
            'seg3',
            2,
            'waybill_proposed',
            None,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [
        ('task_id_1', 'task_id_1_idempotency', 'SOLVED', 2, 2),
    ]

    assert not stq.cargo_sdd_check_routing_result.times_called


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=BASE_SETTINGS)
async def test_fetch_segments_by_corp(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def mock_segment_info(request):
        assert request.query['segment_id'] in ['seg1', 'seg3']
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['points'][0]['point_id'] = request.query[
            'segment_id'
        ]
        return segment

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        return BASE_ROUTING_RESPONSE

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        return {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg4', 1, '444',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'corp_client_ids': ['111', '333'],
        },
    )

    assert mock_segment_info.times_called == 2


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=BASE_SETTINGS)
async def test_fetch_segments_without_corp(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def mock_segment_info(request):
        assert request.query['segment_id'] == 'seg2'
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['points'][0]['point_id'] = request.query[
            'segment_id'
        ]
        return segment

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        return BASE_ROUTING_RESPONSE

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        return {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg4', 1, '444',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'ignore_corp_ids': ['111', '333', '444'],
        },
    )

    assert mock_segment_info.times_called == 1


DROPPED_ROUTING_RESPONSE = {
    'id': 'task_id_1',
    'result': {
        'dropped_locations': [
            {
                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'drop_reason': 'reason',
                'point': {'lat': 55.774532, 'lon': 37.632745},
            },
        ],
        'routes': [
            {
                'route': [
                    # 1 фейковый склад
                    {
                        'arrival_time_s': 29820,
                        'node': {
                            'type': 'depot',
                            'value': {'id': 'fake point'},
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                    # 1 гараж
                    {
                        'arrival_time_s': 29820,
                        'node': {
                            'type': 'location',
                            'value': {'id': 'park2_driver2_garage'},
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                    {
                        'arrival_time_s': 32383,
                        'node': {
                            'type': 'location',
                            'value': {
                                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                            },
                        },
                        'transit_distance_m': 22375,
                        'transit_duration_s': 2263,
                    },
                ],
                'vehicle_id': 'park1_driver1',
            },
        ],
        'solver_status': 'PARTIAL_SOLVED',
    },
    'status': {
        'calculated': 1594918486.55505,
        'completed': 1594918486.6293,
        'matrix_downloaded': 1594918485.5085,
        'queued': 1594918485.2221,
        'started': 1594918485.26308,
    },
}


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=BASE_SETTINGS)
@pytest.mark.parametrize('enable_fallback', [True, False])
@pytest.mark.parametrize('resolved_locations', [True, False])
async def test_fallback_dropped_locations(
        mockserver,
        pgsql,
        stq_runner,
        stq,
        taxi_config,
        enable_fallback,
        resolved_locations,
):
    taxi_config.set(
        CARGO_SDD_ENABLE_DROPPED_SEGMENT_PROCESSING=enable_fallback,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def mock_segment_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['id'] = request.query['segment_id']
        segment['segment']['points'][1]['point_id'] = '123'
        return segment

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        response = copy.deepcopy(DROPPED_ROUTING_RESPONSE)
        if resolved_locations:
            response['result']['dropped_locations'].append(
                {
                    'id': 'pickup_resolved_point_id',
                    'drop_reason': 'Dependent group isn\'t in same vehicles',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                },
            )
            response['result']['dropped_locations'].append(
                {
                    'id': 'dropped_resolved_point_id',
                    'drop_reason': 'Dependent group isn\'t in same vehicles',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                },
            )
        return response

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        return {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            1, 2, 'moscow'
        )
        """,
    )

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'corp_client_ids': ['111'],
        },
    )

    segments = await get_sdd_segments(pgsql)

    if enable_fallback:
        assert sorted(segments, key=lambda x: x[0]) == [
            ('seg1', 2, 'fallback', 'reason', None),
        ]
        assert stq.cargo_sdd_fallback_dropped_locations.times_called == 1
        stq_call = stq.cargo_sdd_fallback_dropped_locations.next_call()
        assert stq_call['kwargs']['segment_ids'] == ['seg1']
    else:
        assert sorted(segments, key=lambda x: x[0]) == [
            ('seg1', 2, 'dropped', 'reason', None),
        ]
        assert stq.cargo_sdd_fallback_dropped_locations.times_called == 0

    assert mock_segment_info.times_called == 1


@pytest.mark.config(CARGO_SDD_USE_NEW_ZONE_CONFIG=True)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_use_new_config(
        mockserver, pgsql, stq_runner, stq, experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/stq-check-routing'],
        clauses=[
            {
                'title': 'clause',
                'alias': 'moscow_alias',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'zone_name',
                                    'arg_type': 'string',
                                    'value': 'moscow',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'settings': {
                        'delivery_guarantees': [
                            {
                                'orders_created_till': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T13:00:00+00:00',
                                'deliver_till': '1970-01-01T16:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T13:00:00+00:00'
                                ),
                            },
                            {
                                'orders_created_till': (
                                    '1970-01-01T14:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T14:00:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T15:00:00+00:00',
                                'deliver_till': '1970-01-01T18:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T15:00:00+00:00'
                                ),
                            },
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 1,
                            'courier_pattern': {
                                'park_id': 'park1',
                                'driver_id': 'driver1',
                            },
                        },
                        'taxi_classes': ['cargo'],
                        'fake_depot': {'lon': 0, 'lat': 0},
                    },
                },
            },
        ],
        default_value={
            'settings': {
                'delivery_guarantees': [],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        },
    )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            exp3_settings_alias
        )
        VALUES (
            'seg_id', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        );
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        assert task_id == 'task_id_1'
        return BASE_ROUTING_RESPONSE

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        return {}

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'clause_alias': 'moscow_alias',
            'corp_client_ids': [],
            'exp3_kwargs': {
                'corp_client_id': 'corp_id3',
                'start_point': {'lat': 55.774532, 'lon': 37.632745},
                'zone_name': 'moscow',
            },
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_id',
            2,
            'waybill_proposed',
            None,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [
        ('task_id_1', 'task_id_1_idempotency', 'SOLVED', 2, 2),
    ]

    propositions = await get_propositions(pgsql)
    assert propositions == [
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            PROPOSITION_DUMP,
            False,
        ),
    ]

    assert not stq.cargo_sdd_check_routing_result.times_called


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=BASE_SETTINGS)
async def test_segments_from_another_request(
        mockserver, pgsql, stq_runner, stq,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def mock_segment_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        for point in segment['segment']['points']:
            point['point_id'] = 'other_' + point['point_id']
        return segment

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        return BASE_ROUTING_RESPONSE

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def mock_waybill_propose(request):
        return {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg1', 1, '111',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'corp_client_ids': ['111', '222'],
        },
    )

    assert mock_segment_info.times_called == 2
    assert mock_waybill_propose.times_called == 0


@pytest.mark.config(CARGO_SDD_USE_NEW_ZONE_CONFIG=True)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_due(mockserver, pgsql, stq_runner, stq, experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/stq-check-routing'],
        clauses=[
            {
                'title': 'clause',
                'alias': 'moscow_alias',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'zone_name',
                                    'arg_type': 'string',
                                    'value': 'moscow',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'settings': {
                        'delivery_guarantees': [
                            {
                                'orders_created_till': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T12:00:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T13:00:00+00:00',
                                'deliver_till': '1970-01-01T16:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T13:00:00+00:00'
                                ),
                            },
                            {
                                'orders_created_till': (
                                    '1970-01-01T14:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T14:00:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T15:00:00+00:00',
                                'deliver_till': '1970-01-01T18:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T15:00:00+00:00'
                                ),
                            },
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 1,
                            'courier_pattern': {
                                'park_id': 'park1',
                                'driver_id': 'driver1',
                            },
                        },
                        'taxi_classes': ['cargo'],
                        'fake_depot': {'lon': 0, 'lat': 0},
                        'deffered_dispatch_time_s': 1200,
                    },
                },
            },
        ],
        default_value={
            'settings': {
                'delivery_guarantees': [],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        },
    )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    @mockserver.json_handler(
        r'/b2bgeo/v1/result/mvrp/(?P<task_id>.+)$', regex=True,
    )
    def _mock_b2bgeo(request, task_id):
        return BASE_ROUTING_RESPONSE

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            exp3_settings_alias
        )
        VALUES (
            'seg_id', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        );
        """,
    )
    cursor.execute(
        """
        INSERT INTO cargo_sdd.routing_tasks(
            task_id, idempotency_token, status,
            segments_count, couriers_count, zone_id
        )
        VALUES (
            'task_id_1', 'task_id_1_idempotency', 'pending',
            2, 2, 'moscow'
        )
        """,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        assert (
            request.json['taxi_lookup_extra']['due']
            == '2021-10-30T15:30:00+00:00'
        )
        return {}

    await stq_runner.cargo_sdd_check_routing_result.call(
        task_id='task_id_1',
        kwargs={
            'zone_id': 'moscow',
            'routing_task_id': 'task_id_1',
            'clause_alias': 'moscow_alias',
            'corp_client_ids': [],
            'exp3_kwargs': {
                'corp_client_id': 'corp_id3',
                'start_point': {'lat': 55.774532, 'lon': 37.632745},
                'zone_name': 'moscow',
            },
            'threshold': '2021-10-30T15:10:00+00:00',
        },
    )

    assert _waybill_propose.times_called == 1
