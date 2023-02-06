# pylint: disable=too-many-lines
import copy
import json

import pytest


PROPOSITION_DUMP = {
    'external_ref': 'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
    'points': [
        {
            'point_id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
            'segment_id': 'seg_1',
            'visit_order': 1,
        },
        {
            'point_id': 'bfccd09a-f64e-455d-ae35-396ef9d5a2ce',
            'segment_id': 'seg_2',
            'visit_order': 2,
        },
        {
            'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
            'segment_id': 'seg_1',
            'visit_order': 3,
        },
        {
            'point_id': 'afccd09a-f82e-455d-ae35-396ef9d5a2ce',
            'segment_id': 'seg_2',
            'visit_order': 4,
        },
    ],
    'router_id': 'cargo_same_day_delivery_router',
    'segments': [
        {'segment_id': 'seg_1', 'waybill_building_version': 1},
        {'segment_id': 'seg_2', 'waybill_building_version': 1},
    ],
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

PROPOSITION_SEG_1_ONLY_DUMP = {
    'external_ref': 'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
    'points': [
        {
            'point_id': 'cfddc348-e716-464f-bd4e-fae98f11157d',
            'segment_id': 'seg_1',
            'visit_order': 1,
        },
        {
            'point_id': '4d7a74ff-9299-4091-9b9a-fc05b780091b',
            'segment_id': 'seg_1',
            'visit_order': 2,
        },
    ],
    'router_id': 'cargo_same_day_delivery_router',
    'segments': [{'segment_id': 'seg_1', 'waybill_building_version': 2}],
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
        SELECT segment_id, revision, status, proposition_ref
        FROM cargo_sdd.segments
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


@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_happy_path(mockserver, pgsql, stq_runner, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            proposition_ref
        )
        VALUES (
            'seg_1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        ),
        (
            'seg_2', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        )
        """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_sdd.propositions(
            waybill_ref, waybill_proposition
        )
        VALUES (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            \'{json.dumps(PROPOSITION_DUMP)}\'
        )
        """,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        req_json = request.json
        assert (
            req_json['external_ref']
            == 'cargo_same_day_delivery_router/task_id_1/park1_driver1_2'
        )

        del req_json['external_ref']

        expected_waybill = copy.deepcopy(PROPOSITION_DUMP)
        del expected_waybill['external_ref']

        assert req_json == expected_waybill
        return {}

    await stq_runner.cargo_sdd_repropose_same_waybill_on_autoreorder.call(
        task_id='cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        kwargs={
            'proposition_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_1',
            1,
            'waybill_proposed',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
        ),
        (
            'seg_2',
            1,
            'waybill_proposed',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
        ),
    ]

    dump_copy = copy.deepcopy(PROPOSITION_DUMP)
    del dump_copy['external_ref']

    propositions = await get_propositions(pgsql)
    assert propositions == [
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            {
                **dump_copy,
                'external_ref': (
                    'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
                ),
            },
            True,
        ),
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
            {
                **dump_copy,
                'external_ref': (
                    'cargo_same_day_delivery_router/task_id_1/park1_driver1_2'
                ),
            },
            False,
        ),
    ]


@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_already_reproposed(mockserver, pgsql, stq_runner, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            proposition_ref
        )
        VALUES (
            'seg_1', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        ),
        (
            'seg_2', 1, 'corp_id',
            'waybill_proposed', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        )
        """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_sdd.propositions(
            waybill_ref, waybill_proposition, already_reproposed
        )
        VALUES (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            \'{json.dumps(PROPOSITION_DUMP)}\',
            True
        )
        """,
    )

    await stq_runner.cargo_sdd_repropose_same_waybill_on_autoreorder.call(
        task_id='cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        kwargs={
            'proposition_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_1',
            1,
            'waybill_proposed',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
        (
            'seg_2',
            1,
            'waybill_proposed',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    propositions = await get_propositions(pgsql)
    assert propositions == [
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            PROPOSITION_DUMP,
            True,
        ),
    ]


@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_one_segment_resolved(mockserver, pgsql, stq_runner, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            proposition_ref
        )
        VALUES (
            'seg_1', 1, 'corp_id',
            'waybill_building_awaited', 2, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        ),
        (
            'seg_2', 1, 'corp_id',
            'inactive', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        )
        """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_sdd.propositions(
            waybill_ref, waybill_proposition
        )
        VALUES (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            \'{json.dumps(PROPOSITION_DUMP)}\'
        )
        """,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        assert request.json == PROPOSITION_SEG_1_ONLY_DUMP
        return {}

    await stq_runner.cargo_sdd_repropose_same_waybill_on_autoreorder.call(
        task_id='cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        kwargs={
            'proposition_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_1',
            1,
            'waybill_proposed',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
        ),
        (
            'seg_2',
            1,
            'inactive',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    propositions = await get_propositions(pgsql)
    assert propositions == [
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            PROPOSITION_DUMP,
            True,
        ),
        (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_2',
            PROPOSITION_SEG_1_ONLY_DUMP,
            False,
        ),
    ]


@pytest.mark.now('2021-10-30T15:00:00+00:00')
async def test_all_segment_resolved(mockserver, pgsql, stq_runner, stq):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            proposition_ref
        )
        VALUES (
            'seg_1', 1, 'corp_id',
            'inactive', 2, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        ),
        (
            'seg_2', 1, 'corp_id',
            'inactive', 1, 'moscow',
            '2021-10-30T12:35:00+00:00'::TIMESTAMPTZ,
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
        )
        """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_sdd.propositions(
            waybill_ref, waybill_proposition
        )
        VALUES (
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
            \'{json.dumps(PROPOSITION_DUMP)}\'
        )
        """,
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def _waybill_propose(request):
        return {}

    await stq_runner.cargo_sdd_repropose_same_waybill_on_autoreorder.call(
        task_id='cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        kwargs={
            'proposition_ref': (
                'cargo_same_day_delivery_router/task_id_1/park1_driver1_1'
            ),
        },
    )

    segments = await get_sdd_segments(pgsql)
    assert sorted(segments, key=lambda x: x[0]) == [
        (
            'seg_1',
            1,
            'inactive',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
        (
            'seg_2',
            1,
            'inactive',
            'cargo_same_day_delivery_router/task_id_1/park1_driver1_1',
        ),
    ]

    assert not _waybill_propose.times_called
