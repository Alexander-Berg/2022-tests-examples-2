import copy
import datetime

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
        SELECT segment_id, revision, status, start_point
        FROM cargo_sdd.segments
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_sdd_segments_with_intervals(pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT segment_id, revision, status,
         delivery_interval_from, delivery_interval_to,
         start_point
        FROM cargo_sdd.segments
        ORDER BY id
        """,
    )
    return cursor.fetchall()


@pytest.fixture(name='run_segments_journal_reader')
def _run_segments_journal_reader(run_task_once):
    async def _wrapper():
        return await run_task_once('segments-journal-reader')

    return _wrapper


@pytest.mark.now('2020-01-27T15:40:08+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_happy_path(run_segments_journal_reader, mockserver, pgsql):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler_journal(request):
        assert request.json == {
            'router_id': 'cargo_same_day_delivery_router',
            'without_duplicates': True,
        }
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_1',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 2,
                    'segment_id': 'seg_2',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 2
    assert result['oldest-segment-lag-ms'] == 8000

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_1', 6, 'waybill_building_awaited', '(37.632745,55.774532)'),
        ('seg_2', 6, 'waybill_building_awaited', '(37.632745,55.774532)'),
    ]


@pytest.mark.now('2020-01-27T15:41:01+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_inactive(run_segments_journal_reader, mockserver, pgsql):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['dispatch']['waybill_building_awaited'] = False
        segment['segment']['resolution'] = 'cancelled_by_user'
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler(request):
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_1',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 1
    assert result['oldest-segment-lag-ms'] == 61000

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_1', 6, 'inactive', '(37.632745,55.774532)'),
    ]


@pytest.mark.now('2020-01-27T15:40:02+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_update_segment(run_segments_journal_reader, mockserver, pgsql):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info_1(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler_journal_1(request):
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_1',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    await run_segments_journal_reader()
    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_1', 6, 'waybill_building_awaited', '(37.632745,55.774532)'),
    ]

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info_2(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['dispatch']['waybill_building_awaited'] = False
        segment['dispatch']['revision'] = 7
        segment['segment']['resolution'] = 'cancelled_by_user'
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler_journal_2(request):
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 2,
                    'segment_id': 'seg_1',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 1
    assert result['oldest-segment-lag-ms'] == 2000

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_1', 7, 'inactive', '(37.632745,55.774532)'),
    ]


@pytest.mark.now('2020-01-27T15:40:01+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_unknown_status(run_segments_journal_reader, mockserver, pgsql):
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

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['dispatch']['waybill_building_awaited'] = False
        segment['segment']['resolution'] = None
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler(request):
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_id',
                    'waybill_building_version': 3,
                    'waybill_building_awaited': False,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 1
    assert result['oldest-segment-lag-ms'] == 1000

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_id', 6, 'inactive', None),
    ]


@pytest.mark.now('2020-01-27T15:40:01+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_sdd_waybill_selected(
        run_segments_journal_reader, mockserver, pgsql,
):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg_id', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['dispatch']['waybill_building_awaited'] = False
        segment['dispatch']['chosen_waybill'][
            'router_id'
        ] = 'cargo_same_day_delivery_router'
        segment['segment']['resolution'] = None
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler(request):
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_id',
                    'waybill_building_version': 3,
                    'waybill_building_awaited': False,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 0
    assert result['oldest-segment-lag-ms'] == 1000

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        ('seg_id', 1, 'waybill_proposed', None),
    ]


@pytest.mark.now('2020-01-27T15:40:08+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
)
async def test_delivery_interval(
        run_segments_journal_reader, mockserver, pgsql,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        segment = copy.deepcopy(BASE_SEGMENT)
        segment['segment']['same_day_data'] = {
            'delivery_interval': {
                'from': '2020-01-27T15:50:00+00:00',
                'to': '2020-01-27T17:50:00+00:00',
            },
        }
        return segment

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler_journal(request):
        assert request.json == {
            'router_id': 'cargo_same_day_delivery_router',
            'without_duplicates': True,
        }
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 1,
                    'segment_id': 'seg_1',
                    'waybill_building_version': 1,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 1
    assert result['oldest-segment-lag-ms'] == 8000

    segments = await get_sdd_segments_with_intervals(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_1',
            6,
            'waybill_building_awaited',
            datetime.datetime(
                2020, 1, 27, 15, 50, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2020, 1, 27, 17, 50, tzinfo=datetime.timezone.utc,
            ),
            '(37.632745,55.774532)',
        ),
    ]


@pytest.mark.now('2020-01-27T15:40:03+0000')
@pytest.mark.config(
    CARGO_SDD_SEGMENTS_JOURNAL_READER={
        'enabled': True,
        'launches_pause_ms': 0,
    },
    CARGO_SDD_REPROPOSE_REORDERED_WAYBILL=True,
)
async def test_set_stq_to_retry_waybill(
        run_segments_journal_reader, mockserver, pgsql, stq, mocked_time,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def _handler_info(request):
        return BASE_SEGMENT

    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    async def _handler_journal(request):
        assert request.json == {
            'router_id': 'cargo_same_day_delivery_router',
            'without_duplicates': True,
        }
        response = {
            'events': [
                {
                    'created_ts': '2020-01-27T15:40:00+00:00',
                    'revision': 2,
                    'segment_id': 'seg_id',
                    'waybill_building_version': 2,
                    'waybill_building_awaited': True,
                },
            ],
            'cursor': '123',
        }
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'}, json=response,
        )

    # Set old proposition_ref
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts
        )
        VALUES (
            'seg_id', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )
    cursor.execute(
        """
        UPDATE cargo_sdd.segments
        SET proposition_ref = 'cargo_same_day_delivery_router/'
                              'task_id_1/park1_driver1_1'
        """,
    )

    result = await run_segments_journal_reader()
    assert result['segments-processed-count'] == 0
    assert result['oldest-segment-lag-ms'] == 3000

    assert (
        stq.cargo_sdd_repropose_same_waybill_on_autoreorder.times_called == 1
    )
    stq_call = stq.cargo_sdd_repropose_same_waybill_on_autoreorder.next_call()
    assert (
        stq_call['id']
        == 'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
    )
    assert stq_call['eta'] == mocked_time.now() + datetime.timedelta(
        seconds=10,
    )
    assert (
        stq_call['kwargs']['proposition_ref']
        == 'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
    )
