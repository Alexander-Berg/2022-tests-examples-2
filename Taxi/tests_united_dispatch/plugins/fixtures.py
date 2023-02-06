"""
    Describe here service specific fixtures.
"""
# pylint: disable=redefined-outer-name
import copy
import datetime
import json

import pytest


@pytest.fixture(name='get_worker_state')
async def _get_worker_state(pgsql):
    def wrapper(worker_name):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            SELECT
                payload
            FROM united_dispatch.worker_state
            WHERE worker_name = %s
            """,
            (worker_name,),
        )
        state = cursor.fetchone()
        if state is None:
            return None
        return state['payload']

    return wrapper


@pytest.fixture(name='print_pg_table')
async def _print_pg_table(pgsql):
    def wrapper(table_name, db='united_dispatch', schema=None):
        if db == 'united_dispatch':
            if schema is None:
                schema = 'united_dispatch'
        else:
            assert False, f'Unexpected database \'{db}\''

        print(f'{schema}.{table_name} ROWS:')
        cursor = pgsql[db].dict_cursor()
        cursor.execute(f'select * from {schema}.{table_name}')
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            print(f'\t{dict(row)}')

    return wrapper


@pytest.fixture(name='autorun_stq')
async def _autorun_stq(stq, stq_runner):
    async def wrapper(stq_name, expect_fail=False):
        target_stq = getattr(stq, stq_name)
        for _ in range(target_stq.times_called):
            call = target_stq.next_call()
            if call is None:
                return
            if not call['kwargs']:
                return  # fix for empty kwargs on reschedule

            await getattr(stq_runner, stq_name).call(
                task_id='test', kwargs=call['kwargs'], expect_fail=expect_fail,
            )

    return wrapper


@pytest.fixture(name='autorun_propose')
async def _autorun_propose(autorun_stq):
    async def wrapper():
        await autorun_stq('united_dispatch_waybill_propose')
        await autorun_stq('united_dispatch_proposition_fail')

    return wrapper


@pytest.fixture(name='autorun_fail')
async def _autorun_fail(autorun_stq):
    async def wrapper():
        await autorun_stq('united_dispatch_proposition_fail')

    return wrapper


@pytest.fixture(name='autorun_waybill_reader')
async def _autorun_waybill_reader(autorun_stq):
    async def wrapper():
        await autorun_stq('united_dispatch_waybill_reader')

    return wrapper


@pytest.fixture(name='autorun_segment_reader')
async def _autorun_segment_reader(autorun_stq):
    async def wrapper():
        await autorun_stq('united_dispatch_segment_reader')

    return wrapper


@pytest.fixture(name='get_single_waybill')
async def _get_single_waybill(pgsql):
    def wrapper():
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute('select * from united_dispatch.waybills')

        waybills = [row for row in cursor]
        if not waybills:
            return None
        return dict(waybills[0])

    return wrapper


@pytest.fixture(name='get_waybill')
async def _get_waybill(pgsql):
    def wrapper(waybill_ref):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            'select * from united_dispatch.waybills where id = %s',
            (waybill_ref,),
        )
        waybill = cursor.fetchone()
        if not waybill:
            return None
        return dict(waybill)

    return wrapper


@pytest.fixture(name='get_waybill_by_segment')
async def _get_waybill_by_segment(pgsql):
    def wrapper(segment_id):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute('select * from united_dispatch.waybills')
        for row in cursor:
            for segment in row['waybill']['segments']:
                if segment['segment']['segment']['id'] == segment_id:
                    return dict(row)
        return None

    return wrapper


@pytest.fixture(name='get_segment')
async def _get_segment(pgsql):
    def wrapper(segment_id, waybill_building_version: int = 1):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            'select * from united_dispatch.segments where id = %s'
            ' AND waybill_building_version = %s',
            (segment_id, waybill_building_version),
        )

        row = cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        performer_requirements = copy.deepcopy(
            result['segment_info']['segment']['performer_requirements'],
        )
        if performer_requirements:
            result['taxi_classes'] = performer_requirements.pop('taxi_classes')
            result['special_requirements'] = performer_requirements.pop(
                'special_requirements',
            )
            result['taxi_requirements'] = performer_requirements
        return result

    return wrapper


@pytest.fixture(name='set_waybill_candidate')
async def _set_waybill_candidate(pgsql, build_waybill_candidate, mocked_time):
    def wrapper(*, waybill_ref, assigned_at=None, **kwargs):
        if assigned_at is None:
            now = mocked_time.now() if mocked_time else datetime.datetime.now()
            assigned_at = now

        candidate = build_waybill_candidate(**kwargs)
        candidate = {
            'assigned_at': assigned_at.replace(
                tzinfo=datetime.timezone.utc,
            ).isoformat(timespec='seconds'),
            'info': candidate,
        }

        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            UPDATE united_dispatch.waybills
            SET candidate = %s::JSONB
            WHERE id = %s
            """,
            (json.dumps(candidate), waybill_ref),
        )

    return wrapper


@pytest.fixture(name='make_rejected_candidates_delivery_ids')
async def _make_rejected_candidates_delivery_ids():
    def wrapper(*, segment):
        ids = set([])
        if segment.corp_client_id:
            for point in segment.points:
                if point.external_order_id:
                    delivery_id = '{}_{}'.format(
                        segment.corp_client_id, point.external_order_id,
                    )
                    ids.add(delivery_id)

        if not ids:
            ids.add(segment.id)
        return list(ids)

    return wrapper


@pytest.fixture(name='add_rejected_candidate')
async def _add_rejected_candidate(
        pgsql, make_rejected_candidates_delivery_ids,
):
    def wrapper(*, segment, candidate_id, rejections=1):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            INSERT INTO united_dispatch.rejected_candidates (
                delivery_id,
                candidate_id,
                rejections
            )
            SELECT
                delivery_id,
                %s,
                %s
            FROM unnest(%s) AS delivery_id
            """,
            (
                candidate_id,
                rejections,
                make_rejected_candidates_delivery_ids(segment=segment),
            ),
        )

    return wrapper


@pytest.fixture(name='set_waybill_lookup_flow')
async def _set_waybill_lookup_flow(pgsql):
    def wrapper(waybill_ref, lookup_flow):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            UPDATE united_dispatch.waybills
            SET lookup_flow = %s::united_dispatch.lookup_flow
            WHERE id = %s
            """,
            (lookup_flow, waybill_ref),
        )

    return wrapper


@pytest.fixture(name='increment_segment_revision')
async def _increment_segment_revision(pgsql):
    def wrapper(segment_id):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            UPDATE united_dispatch.segments
            SET updated_ts = now()
            WHERE id = %s
            RETURNING id
            """,
            (segment_id,),
        )
        assert cursor.fetchall()

    return wrapper


@pytest.fixture(name='increment_waybill_revision')
async def _increment_waybill_revision(pgsql):
    def wrapper(waybill_id):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            UPDATE united_dispatch.waybills
            SET updated_ts = now()
            WHERE id = %s
            RETURNING id, revision
            """,
            (waybill_id,),
        )

        for row in cursor.fetchall():
            return row['revision']
        assert False, 'empty result'

    return wrapper


@pytest.fixture(name='get_rejected_candidates')
async def _get_rejected_candidates(
        pgsql, make_rejected_candidates_delivery_ids,
):
    def wrapper(*, segment):
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            SELECT delivery_id, candidate_id
            FROM united_dispatch.rejected_candidates
            WHERE delivery_id = any(%s)
            """,
            (make_rejected_candidates_delivery_ids(segment=segment),),
        )
        rows = cursor.fetchall()
        rejected_candidates = []
        for row in rows:
            rejected_candidates.append(dict(row))
        return rejected_candidates

    return wrapper


@pytest.fixture(name='get_frozen_candidates')
async def _get_frozen_candidates(pgsql):
    def wrapper():
        cursor = pgsql['united_dispatch'].dict_cursor()
        cursor.execute(
            """
            SELECT candidate_id, waybill_id, expiration_ts
            FROM united_dispatch.frozen_candidates
            """,
        )
        rows = cursor.fetchall()
        frozen_candidates = []
        for row in rows:
            frozen_candidates.append(dict(row))
        return frozen_candidates

    return wrapper


@pytest.fixture(name='mark_waybill_rebuilt')
async def mark_waybill_rebuilt(pgsql):
    def _inner(waybill_ref: str):
        cursor = pgsql['united_dispatch'].cursor()
        cursor.execute(
            """
            UPDATE united_dispatch.waybills
                SET rebuilt_at = now()
            WHERE id = %s
            """,
            (waybill_ref,),
        )

    return _inner


@pytest.fixture(name='list_segment_executors')
async def _list_segment_executors(pgsql):
    def wrapper(segment_id):
        cursor = pgsql['united_dispatch'].dict_cursor()

        cursor.execute(
            'SELECT * FROM united_dispatch.segment_executors '
            'WHERE segment_id = %s '
            'ORDER BY execution_order',
            (segment_id,),
        )

        rows = cursor.fetchall()

        return [dict(r) for r in rows]

    return wrapper


@pytest.fixture(name='update_segment_executor_record')
async def _update_segment_executor_record(pgsql, mocked_time):
    def _inner(
            segment_id: str,
            execution_order: int,
            *,
            new_updated_ts: datetime.datetime = None,
            new_throttled_until_ts: datetime.datetime = None,
            new_gambles_count: int = None,
            new_status: str = None,
    ):
        if new_updated_ts is None:
            new_updated_ts = (
                mocked_time.now() if mocked_time else datetime.datetime.now()
            )

        cursor = pgsql['united_dispatch'].cursor()

        cursor.execute(
            """
            ALTER TABLE united_dispatch.segment_executors
            DISABLE TRIGGER united_dispatch__segment_executors__set_updated_ts;

            UPDATE united_dispatch.segment_executors
            SET
                updated_ts = %s::TIMESTAMP AT TIME ZONE 'UTC',
                gamble_count = COALESCE(%s, gamble_count),
                status = COALESCE(%s, status),
                throttled_until_ts = %s::TIMESTAMP AT TIME ZONE 'UTC'
            WHERE segment_id = %s AND execution_order = %s;

            ALTER TABLE united_dispatch.segment_executors
            ENABLE TRIGGER united_dispatch__segment_executors__set_updated_ts;
            """,
            (
                new_updated_ts.isoformat(),
                new_gambles_count,
                new_status,
                new_throttled_until_ts,
                segment_id,
                execution_order,
            ),
        )

    return _inner


# TODO: Remove after - move delivery planner to separate unit
@pytest.fixture(name='exp_delivery_configs')
async def _exp_delivery_configs(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_sla_groups_settings,
        exp_clients_to_sla_groups_mapping,
):
    async def wrapper(
            delivery_gamble_settings=True,
            delivery_generators_settings=True,
            sla_groups_settings=True,
            clients_to_sla_groups_mapping=True,
    ):
        if delivery_gamble_settings:
            await exp_delivery_gamble_settings()
        if delivery_generators_settings:
            await exp_delivery_generators_settings()
        if sla_groups_settings:
            await exp_sla_groups_settings()
        if clients_to_sla_groups_mapping:
            await exp_clients_to_sla_groups_mapping()

    return wrapper
