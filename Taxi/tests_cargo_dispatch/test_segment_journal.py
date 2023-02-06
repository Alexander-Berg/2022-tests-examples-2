import jwt
import pytest

from testsuite.utils import matching


FALLBACK_ROUTER = 'fallback_router'
JWT_SECRET = 'not-a-secret'

BASE_SEGMENTS_EVENTS = [
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'segment_id': 'seg1',
        'waybill_building_version': 1,
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'segment_id': 'seg2',
        'waybill_building_version': 1,
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'segment_id': 'seg3',
        'waybill_building_version': 1,
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 2,
        'segment_id': 'seg1',
        'waybill_building_version': 1,
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 2,
        'segment_id': 'seg2',
        'waybill_building_version': 1,
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 2,
        'segment_id': 'seg3',
        'waybill_building_version': 1,
    },
]


def get_job_settings(enabled: bool = True, limit: int = 1000):
    return {'enabled': enabled, 'limit': limit}


async def test_first_request_without_cursor(
        happy_path_state_routers_chosen, read_segment_journal,
):
    response = await read_segment_journal(FALLBACK_ROUTER, cursor=None)
    assert 'cursor' in response


@pytest.mark.config(CARGO_DISPATCH_SEGMENTS_JOURNAL={'max_items': 2})
async def test_events_limit(
        happy_path_state_routers_chosen,
        read_segment_journal,
        run_segments_journal_mover,
):
    await run_segments_journal_mover()

    response = await read_segment_journal(FALLBACK_ROUTER, cursor=None)
    assert len(response['events']) == 2


@pytest.mark.config(CARGO_DISPATCH_SEGMENTS_JOURNAL={'max_items': 1000})
async def test_segment_after_reorder(
        happy_path_segment_after_reorder,
        read_segment_journal,
        run_segments_journal_mover,
):
    await run_segments_journal_mover()

    response = await read_segment_journal(FALLBACK_ROUTER, cursor=None)
    assert response['events'][-1] == {
        'waybill_building_version': 2,
        'segment_id': 'seg3',
        'revision': 7,
        'created_ts': matching.any_string,
    }


# New journal tests


async def insert_old_journal_event(pgsql, pkey: int, segment_id: str):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_dispatch.segments_journal
            (id, segment_id, segment_revision, waybill_building_version)
        VALUES (\'{pkey}\', \'{segment_id}\', \'{pkey + 10}\', 1)
        """,
    )


async def insert_new_journal_event(
        pgsql, pkey: int, segment_id: str, router_id: str,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_dispatch.segments_journal_v2
            (id, segment_id, segment_revision,
                waybill_building_version, router_id)
        VALUES (\'{pkey}\', \'{segment_id}\', \'{pkey + 10}\', 1,
                \'{router_id}\')
        """,
    )


def build_fake_cursor():
    return jwt.encode(
        {'last_known_id': 1, 'holes': [], 'version': 1},
        JWT_SECRET,
        algorithm='HS512',
    ).decode('utf-8')


async def test_new_journal_holes(
        happy_path_state_routers_chosen, pgsql, request_segment_journal,
):
    await insert_new_journal_event(
        pgsql, 100, 'seg1', router_id=FALLBACK_ROUTER,
    )
    await insert_new_journal_event(
        pgsql, 1000000, 'seg3', router_id=FALLBACK_ROUTER,
    )

    # Request with cursor forces new journal usage
    response = await request_segment_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(),
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 110,
            'segment_id': 'seg1',
            'waybill_building_version': 1,
        },
        {
            'created_ts': matching.AnyString(),
            'revision': 1000010,
            'segment_id': 'seg3',
            'waybill_building_version': 1,
        },
    ]

    decoded = jwt.decode(resp_body['cursor'], JWT_SECRET, algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 1000000,
        'version': 1,
    }


async def test_cursor_versions(request_segment_journal):
    response = await request_segment_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(),
    )
    assert response.status_code == 200

    decoded = jwt.decode(
        response.json()['cursor'], JWT_SECRET, algorithms=['HS512'],
    )
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 1,
        'version': 1,
    }


async def test_new_journal_usage(
        happy_path_state_routers_chosen, request_segment_journal, pgsql,
):
    await insert_new_journal_event(
        pgsql, 10, 'seg3', router_id=FALLBACK_ROUTER,
    )

    # 1. First request
    response = await request_segment_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(),
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 20,
            'segment_id': 'seg3',
            'waybill_building_version': 1,
        },
    ]
    decoded = jwt.decode(resp_body['cursor'], JWT_SECRET, algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 10,
        'version': 1,
    }

    # 2. Add new event
    await insert_new_journal_event(
        pgsql, 100, 'seg3', router_id=FALLBACK_ROUTER,
    )

    # 3. Second request
    response = await request_segment_journal(
        FALLBACK_ROUTER, cursor=resp_body['cursor'],
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 110,
            'segment_id': 'seg3',
            'waybill_building_version': 1,
        },
    ]
    decoded = jwt.decode(resp_body['cursor'], JWT_SECRET, algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 100,
        'version': 1,
    }
