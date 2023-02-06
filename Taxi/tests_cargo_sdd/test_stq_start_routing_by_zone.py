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


async def get_sdd_segments(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT segment_id, revision, status, routing_task_id
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
                ],
                'couriers': [
                    {'park_id': 'park1', 'driver_id': 'driver1'},
                    {'park_id': 'park2', 'driver_id': 'driver2'},
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
    CARGO_SDD_CORP_TO_ROUTING_COMPANY_MAPPING={
        '70a499f9eec844e9a758f4bc33e667c0': [123],
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
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json == {
            'vehicles': [
                {
                    'id': 'park1_driver1',
                    'routing_mode': 'driving',
                    'capacity': {'units': 12},
                    'visit_depot_at_start': False,
                    'return_to_depot': False,
                    'start_at': 'park1_driver1_garage',
                },
                {
                    'id': 'park2_driver2',
                    'routing_mode': 'driving',
                    'capacity': {'units': 12},
                    'visit_depot_at_start': False,
                    'return_to_depot': False,
                    'start_at': 'park2_driver2_garage',
                },
            ],
            'options': {
                'absolute_time': True,
                'avoid_tolls': True,
                'merge_multiorders': True,
                'quality': 'normal',
                'time_zone': 0.0,
                'date': '2021-10-30',
            },
            'depots': [
                {
                    'id': 'fake',
                    'point': {'lat': 0.0, 'lon': 0.0},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'hard_window': False,
                },
            ],
            'locations': [
                {
                    'id': 'park1_driver1_garage',
                    'point': {'lat': 7, 'lon': 8},
                    'type': 'garage',
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                },
                {
                    'id': 'park2_driver2_garage',
                    'point': {'lat': 7, 'lon': 8},
                    'type': 'garage',
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                },
                {
                    'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                    'shared_with_company_ids': [123],
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                    'shared_with_company_ids': [123],
                },
                {
                    'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                    'shared_with_company_ids': [123],
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                    'shared_with_company_ids': [123],
                },
            ],
        }
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={'zone_id': 'moscow', 'threshold': '2021-10-30T12:00:00+00:00'},
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 2)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


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
                ],
                'couriers': [
                    {'park_id': 'park1', 'driver_id': 'driver1'},
                    {'park_id': 'park2', 'driver_id': 'driver2'},
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_multipoints(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['points'] = [
            {
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
                'contact': {
                    'name': 'Б2',
                    'personal_phone_id': 'e1371405ac984a82a5f9818e04a1eb70',
                },
                'location_id': 'b471e75a88a040abb6d84a523142d2fa',
                'point_id': 'cfcdd62a-f64e-455d-ae35-696ef9d5a8ce',
                'type': 'dropoff',
                'visit_order': 3,
            },
            {
                'contact': {
                    'name': 'Тимофеева  ',
                    'personal_phone_id': 'f2c0d0cd46e74c1a8e7242dcba6fdfc8',
                },
                'location_id': 'f1c6e566c76a4bbfbb8082cc8dd9a0d0',
                'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
                'type': 'return',
                'visit_order': 4,
            },
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
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json['options'] == {
            'absolute_time': True,
            'avoid_tolls': True,
            'date': '2021-10-30',
            'merge_multiorders': True,
            'quality': 'normal',
            'time_zone': 0.0,
            'location_groups': [
                {
                    'dependent': True,
                    'location_ids': [
                        'cfddc348-e716-464f-bd4e-fae98f11157d',
                        'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                        'cfcdd62a-f64e-455d-ae35-696ef9d5a8ce',
                    ],
                    'solid': False,
                    'title': 'seg_id',
                },
                {
                    'dependent': True,
                    'location_ids': [
                        'cfddc348-e716-464f-bd4e-fae98f11157d',
                        'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                        'cfcdd62a-f64e-455d-ae35-696ef9d5a8ce',
                    ],
                    'solid': False,
                    'title': 'seg_id',
                },
            ],
        }

        assert request.json['locations'] == [
            {
                'id': 'park1_driver1_garage',
                'point': {'lat': 7, 'lon': 8},
                'type': 'garage',
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
            },
            {
                'id': 'park2_driver2_garage',
                'point': {'lat': 7, 'lon': 8},
                'type': 'garage',
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
            },
            {
                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'point': {'lat': 55.774532, 'lon': 37.632745},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                'type': 'pickup',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 1,
            },
            {
                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                'type': 'delivery',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 2,
            },
            # Б2
            {
                'id': 'cfcdd62a-f64e-455d-ae35-696ef9d5a8ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                'type': 'delivery',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 3,
            },
            {
                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'point': {'lat': 55.774532, 'lon': 37.632745},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                'type': 'pickup',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 1,
            },
            {
                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                'type': 'delivery',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 2,
            },
            # Б2
            {
                'id': 'cfcdd62a-f64e-455d-ae35-696ef9d5a8ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                'type': 'delivery',
                'hard_window': False,
                'shipment_size': {'units': 1},
                'sequence_order': 3,
            },
        ]
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={'zone_id': 'moscow', 'threshold': '2021-10-30T12:00:00+00:00'},
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 2)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


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
                ],
                'couriers': [
                    {
                        'park_id': 'park1',
                        'driver_id': 'driver1',
                        'max_duration_s': 10,
                        'minimal_stops': 2,
                        'maximal_stops': 3,
                        'time_window': (
                            '1970-01-01T10:17:00+00:00/'
                            '1970-01-01T12:47:00+00:00'
                        ),
                        'hard_window': True,
                        'units': 10,
                        'cost': {
                            'fixed': 1,
                            'hour': 2,
                            'km': 3,
                            'location': 4,
                            'run': 5,
                        },
                    },
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
                'matrix_router': 'global',
                'proximity_factor': 0.6,
                'minimize_lateness_risk': True,
                'location_hard_window': True,
                'location_penalty': {
                    'late': {'fixed': 100000, 'minute': 0},
                    'drop': 1000000000,
                },
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_configurable_routing_params(mockserver, pgsql, stq_runner, stq):
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
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json == {
            'vehicles': [
                {
                    'id': 'park1_driver1',
                    'routing_mode': 'driving',
                    'capacity': {'units': 10},
                    'visit_depot_at_start': False,
                    'return_to_depot': False,
                    'start_at': 'park1_driver1_garage',
                    'shifts': [
                        {
                            'id': 'courier_park1_driver1',
                            'max_duration_s': 10.0,
                            'minimal_stops': 2,
                            'maximal_stops': 3,
                            'time_window': (
                                '2021-10-30T10:17:00+00:00/'
                                '2021-10-30T12:47:00+00:00'
                            ),
                            'hard_window': True,
                        },
                    ],
                    'cost': {
                        'fixed': 1.0,
                        'hour': 2.0,
                        'km': 3.0,
                        'location': 4.0,
                        'run': 5.0,
                    },
                },
            ],
            'options': {
                'absolute_time': True,
                'avoid_tolls': True,
                'date': '2021-10-30',
                'merge_multiorders': True,
                'quality': 'normal',
                'time_zone': 0.0,
                'matrix_router': 'global',
                'minimize_lateness_risk': True,
                'proximity_factor': 0.6,
            },
            'depots': [
                {
                    'id': 'fake',
                    'point': {'lat': 0.0, 'lon': 0.0},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'hard_window': False,
                },
            ],
            'locations': [
                {
                    'id': 'park1_driver1_garage',
                    'point': {'lat': 7, 'lon': 8},
                    'type': 'garage',
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                },
                {
                    'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': True,
                    'shipment_size': {'units': 1},
                    'penalty': {
                        'drop': 1000000000,
                        'late': {'fixed': 100000, 'minute': 0},
                    },
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': True,
                    'shipment_size': {'units': 1},
                    'penalty': {
                        'drop': 1000000000,
                        'late': {'fixed': 100000, 'minute': 0},
                    },
                },
                {
                    'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': True,
                    'shipment_size': {'units': 1},
                    'penalty': {
                        'drop': 1000000000,
                        'late': {'fixed': 100000, 'minute': 0},
                    },
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': True,
                    'shipment_size': {'units': 1},
                    'penalty': {
                        'drop': 1000000000,
                        'late': {'fixed': 100000, 'minute': 0},
                    },
                },
            ],
        }
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={'zone_id': 'moscow', 'threshold': '2021-10-30T12:00:00+00:00'},
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 1)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


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
                ],
                'couriers': [
                    {'park_id': 'park1', 'driver_id': 'driver1'},
                    {'park_id': 'park2', 'driver_id': 'driver2'},
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
                'matrix_router': 'global',
                'proximity_factor': 0.6,
                'minimize_lateness_risk': True,
                'location_service_duration_s': 30,
                'location_hard_window': True,
                'check_couriers_statuses': True,
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_check_couriers_statuses(mockserver, pgsql, stq_runner, stq):
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
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json['vehicles'] == [
            {
                'id': 'park2_driver2',
                'routing_mode': 'driving',
                'capacity': {'units': 12},
                'visit_depot_at_start': False,
                'return_to_depot': False,
                'start_at': 'park2_driver2_garage',
            },
        ]
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {
            'statuses': [
                {'status': 'busy', 'park_id': 'park1', 'driver_id': 'driver1'},
                {
                    'status': 'online',
                    'park_id': 'park2',
                    'driver_id': 'driver2',
                },
            ],
        }

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={'zone_id': 'moscow', 'threshold': '2021-10-30T12:00:00+00:00'},
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 1)]


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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
            {
                'corp_client_ids': ['111', '333'],
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
                ],
                'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_different_corp_intervals(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
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
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:36:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json == {
            'vehicles': [
                {
                    'id': 'park2_driver2',
                    'routing_mode': 'driving',
                    'capacity': {'units': 12},
                    'visit_depot_at_start': False,
                    'return_to_depot': False,
                    'start_at': 'park2_driver2_garage',
                },
            ],
            'options': {
                'absolute_time': True,
                'avoid_tolls': True,
                'merge_multiorders': True,
                'quality': 'normal',
                'time_zone': 0.0,
                'date': '2021-10-30',
            },
            'depots': [
                {
                    'id': 'fake',
                    'point': {'lat': 0.0, 'lon': 0.0},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'hard_window': False,
                },
            ],
            'locations': [
                {
                    'id': 'park2_driver2_garage',
                    'point': {'lat': 7, 'lon': 8},
                    'type': 'garage',
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                },
                {
                    'id': 'seg1',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
                {
                    'id': 'seg3',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
            ],
        }
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': 'moscow',
            'threshold': '2021-10-30T12:00:00+00:00',
            'corp_client_ids': ['111', '333'],
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'waybill_building_awaited', None),
        ('seg3', 1, 'routing_launched', '12345'),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 1)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['corp_client_ids'] == ['111', '333']
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'
    assert 'ignore_corp_ids' not in stq_call['kwargs']


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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
            {
                'corp_client_ids': ['111', '333'],
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
                ],
                'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_ignore_corp_intervals(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
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
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:36:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert request.json == {
            'vehicles': [
                {
                    'id': 'park1_driver1',
                    'routing_mode': 'driving',
                    'capacity': {'units': 12},
                    'visit_depot_at_start': False,
                    'return_to_depot': False,
                    'start_at': 'park1_driver1_garage',
                },
            ],
            'options': {
                'absolute_time': True,
                'avoid_tolls': True,
                'merge_multiorders': True,
                'quality': 'normal',
                'time_zone': 0.0,
                'date': '2021-10-30',
            },
            'depots': [
                {
                    'id': 'fake',
                    'point': {'lat': 0.0, 'lon': 0.0},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'hard_window': False,
                },
            ],
            'locations': [
                {
                    'id': 'park1_driver1_garage',
                    'point': {'lat': 7, 'lon': 8},
                    'type': 'garage',
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                },
                {
                    'id': 'seg2',
                    'point': {'lat': 55.774532, 'lon': 37.632745},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T13:00:00Z',
                    'type': 'pickup',
                    'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
                {
                    'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                    'point': {'lat': 55.76815715, 'lon': 37.63223287},
                    'time_window': '2021-10-30T12:00:00Z/2021-10-30T16:00:00Z',
                    'type': 'delivery',
                    'hard_window': False,
                    'shipment_size': {'units': 1},
                },
            ],
        }
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': 'moscow',
            'threshold': '2021-10-30T12:00:00+00:00',
            'ignore_corp_ids': ['111', '333'],
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'waybill_building_awaited', None),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 1, 1)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert 'corp_client_ids' not in stq_call['kwargs']
    assert stq_call['kwargs']['ignore_corp_ids'] == ['111', '333']
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
            {
                'corp_client_ids': ['111', '222', '333'],
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
                ],
                'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        ],
    },
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_delivery_interval(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['points'][0]['point_id'] = request.query[
            'segment_id'
        ]
        return segment

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, '111',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T11:45:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:45:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg2', 1, '222',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T11:55:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:55:00+00:00'::TIMESTAMPTZ
        ),
        (
            'seg3', 1, '333',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:36:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T12:45:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T14:45:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': 'moscow',
            'threshold': '2021-10-30T12:00:00+00:00',
            'corp_client_ids': ['111', '222', '333'],
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 1)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == 'moscow'
    assert stq_call['kwargs']['corp_client_ids'] == ['111', '222', '333']
    assert 'ignore_corp_ids' not in stq_call['kwargs']
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


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
                ],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 3, 'lat': 7},
                'copy_fake_courier': {
                    'count': 2,
                    'courier_pattern': {
                        'units': 10,
                        'park_id': 'fake_park',
                        'driver_id': 'fake_driver',
                    },
                },
            },
        ],
    },
)
@pytest.mark.now('2022-04-12T12:00:00+00:00')
async def test_copy_courier(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, '111',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T11:45:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:45:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.json['vehicles'] == [
            {
                'id': 'park1_driver1',
                'capacity': {'units': 12},
                'routing_mode': 'driving',
                'return_to_depot': False,
                'visit_depot_at_start': False,
                'start_at': 'park1_driver1_garage',
            },
            {
                'id': 'fake_park1_fake_driver1',
                'capacity': {'units': 10},
                'routing_mode': 'driving',
                'return_to_depot': False,
                'visit_depot_at_start': False,
                'start_at': 'fake_park1_fake_driver1_garage',
            },
            {
                'id': 'fake_park2_fake_driver2',
                'capacity': {'units': 10},
                'routing_mode': 'driving',
                'return_to_depot': False,
                'visit_depot_at_start': False,
                'start_at': 'fake_park2_fake_driver2_garage',
            },
        ]
        assert request.json['locations'] == [
            {
                'id': 'park1_driver1_garage',
                'point': {'lat': 7.0, 'lon': 8.0},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'garage',
            },
            {
                'id': 'fake_park1_fake_driver1_garage',
                'point': {'lat': 7.0, 'lon': 3.0},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'garage',
            },
            {
                'id': 'fake_park2_fake_driver2_garage',
                'point': {'lat': 7.0, 'lon': 3.0},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'garage',
            },
            {
                'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'hard_window': False,
                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'point': {'lat': 55.774532, 'lon': 37.632745},
                'shipment_size': {'units': 1},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'pickup',
            },
            {
                'hard_window': False,
                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'shipment_size': {'units': 1},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T16:00:00Z',
                'type': 'delivery',
            },
        ]
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': 'moscow',
            'threshold': '2021-10-30T12:00:00+00:00',
            'corp_client_ids': ['111'],
        },
    )


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
                ],
                'couriers': [
                    {'park_id': 'park1', 'driver_id': 'driver1'},
                    {
                        'park_id': '633f10b0ce75477fbdde029895c63486',
                        'driver_id': '5f584b52d1bfbfbdab63b980d828855d',
                    },
                ],
                'taxi_classes': [],
                'fake_depot': {'lon': 3, 'lat': 7},
            },
        ],
    },
    CARGO_SDD_IGNORE_FAKE_LOCATIONS=True,
)
@pytest.mark.now('2022-04-12T12:00:00+00:00')
async def test_ignore_fake(mockserver, pgsql, stq_runner, stq):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, '111',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T11:45:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T13:45:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        assert request.json['vehicles'] == [
            {
                'id': 'park1_driver1',
                'capacity': {'units': 12},
                'routing_mode': 'driving',
                'return_to_depot': False,
            },
            {
                'id': (
                    '633f10b0ce75477fbdde029895c63486'
                    '_5f584b52d1bfbfbdab63b980d828855d'
                ),
                'capacity': {'units': 12},
                'routing_mode': 'driving',
                'return_to_depot': False,
                'visit_depot_at_start': False,
                'start_at': (
                    '633f10b0ce75477fbdde029895c63486'
                    '_5f584b52d1bfbfbdab63b980d828855d_garage'
                ),
            },
        ]
        assert request.json['locations'] == [
            {
                'id': (
                    '633f10b0ce75477fbdde029895c63486'
                    '_5f584b52d1bfbfbdab63b980d828855d_garage'
                ),
                'point': {'lat': 7.0, 'lon': 8.0},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'garage',
            },
            {
                'delivery_to': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'hard_window': False,
                'id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
                'point': {'lat': 55.774532, 'lon': 37.632745},
                'shipment_size': {'units': 1},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T13:00:00Z',
                'type': 'pickup',
            },
            {
                'hard_window': False,
                'id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
                'point': {'lat': 55.76815715, 'lon': 37.63223287},
                'shipment_size': {'units': 1},
                'time_window': '2022-04-12T12:00:00Z/2022-04-12T16:00:00Z',
                'type': 'delivery',
            },
        ]
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': 'moscow',
            'threshold': '2021-10-30T12:00:00+00:00',
            'corp_client_ids': ['111'],
        },
    )


@pytest.mark.config(CARGO_SDD_USE_NEW_ZONE_CONFIG=True)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_use_new_config(
        mockserver, pgsql, stq_runner, stq, experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/stq-start-routing'],
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
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 2,
                            'courier_pattern': {
                                'park_id': 'park',
                                'driver_id': 'driver',
                            },
                        },
                        'taxi_classes': [],
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
            'seg1', 1, 'corp_id1',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        ),
        (
            'seg2', 1, 'corp_id2',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:35:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        ),
        (
            'seg3', 1, 'corp_id3',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        );
        """,
    )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    exp_kwargs = {
        'corp_client_id': 'corp_id3',
        'start_point': {'lat': 55.774532, 'lon': 37.632745},
        'zone_name': 'moscow',
    }
    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': '',
            'threshold': '2021-10-30T12:00:00+00:00',
            'clause_alias': 'moscow_alias',
            'corp_client_ids': [],
            'exp3_kwargs': exp_kwargs,
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg1', 1, 'routing_launched', '12345'),
        ('seg2', 1, 'routing_launched', '12345'),
        ('seg3', 1, 'waybill_building_awaited', None),
    ]

    routing_tasks = await get_routing_tasks(pgsql)
    assert routing_tasks == [('12345', 'stq_task_id1', 'pending', 2, 2)]

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['id'] == '12345'
    assert stq_call['kwargs']['routing_task_id'] == '12345'
    assert stq_call['kwargs']['zone_id'] == ''
    assert stq_call['kwargs']['exp3_kwargs'] == exp_kwargs
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'


@pytest.mark.config(
    CARGO_SDD_USE_NEW_ZONE_CONFIG=True, CARGO_SDD_IGNORE_FAKE_LOCATIONS=True,
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_service_time(mockserver, pgsql, stq_runner, stq, experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/stq-start-routing'],
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
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 2,
                            'courier_pattern': {
                                'park_id': 'park',
                                'driver_id': 'driver',
                            },
                        },
                        'taxi_classes': [],
                        'fake_depot': {'lon': 0, 'lat': 0},
                        'pickup_location_service_duration_s': 600,
                        'dropoff_location_service_duration_s': 500,
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
            'seg1', 1, '70a499f9eec844e9a758f4bc33e667c0',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        );
        """,
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        for location in request.json['locations']:
            if location['type'] == 'pickup':
                assert location['service_duration_s'] == 600
            else:
                assert location['service_duration_s'] == 500

        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    exp_kwargs = {
        'corp_client_id': 'corp_id1',
        'start_point': {'lat': 55.774532, 'lon': 37.632745},
        'zone_name': 'moscow',
    }
    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': '',
            'threshold': '2021-10-30T12:00:00+00:00',
            'clause_alias': 'moscow_alias',
            'corp_client_ids': [],
            'exp3_kwargs': exp_kwargs,
        },
    )


@pytest.mark.config(
    CARGO_SDD_USE_NEW_ZONE_CONFIG=True, CARGO_SDD_IGNORE_FAKE_LOCATIONS=True,
)
@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_sort_till(mockserver, pgsql, stq_runner, stq, experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/stq-start-routing'],
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
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 2,
                            'courier_pattern': {
                                'park_id': 'park',
                                'driver_id': 'driver',
                            },
                        },
                        'taxi_classes': [],
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

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            exp3_settings_alias
        )
        VALUES (
            'seg1', 1, '70a499f9eec844e9a758f4bc33e667c0',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'moscow_alias'
        );
        """,
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'direction': 0,
                    'lat': 7,
                    'lon': 8,
                    'speed': 0,
                    'timestamp': 100,
                },
                'type': 'raw',
            },
            status=200,
        )

    @mockserver.json_handler('/b2bgeo/v1/add/mvrp')
    def _mock_b2bgeo(request):
        for location in request.json['locations']:
            if location['type'] == 'pickup':
                assert (
                    location['time_window']
                    == '2021-10-30T12:20:00Z/2021-10-30T13:00:00Z'
                )
            else:
                assert (
                    location['time_window']
                    == '2021-10-30T12:20:00Z/2021-10-30T16:00:00Z'
                )

        return mockserver.make_response(
            json={
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': 123},
            },
            status=202,
        )

    exp_kwargs = {
        'corp_client_id': 'corp_id1',
        'start_point': {'lat': 55.774532, 'lon': 37.632745},
        'zone_name': 'moscow',
    }
    await stq_runner.cargo_sdd_start_routing_by_zone.call(
        task_id='stq_task_id1',
        kwargs={
            'zone_id': '',
            'threshold': '2021-10-30T12:00:00+00:00',
            'clause_alias': 'moscow_alias',
            'corp_client_ids': [],
            'exp3_kwargs': exp_kwargs,
        },
    )

    assert stq.cargo_sdd_check_routing_result.times_called == 1
    stq_call = stq.cargo_sdd_check_routing_result.next_call()
    assert stq_call['kwargs']['threshold'] == '2021-10-30T12:00:00+00:00'
