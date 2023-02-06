import jwt
import pytest

from testsuite.utils import matching


async def test_request_without_cursor_empty(
        taxi_cargo_claims, run_journal_events_mover,
):
    """
    Request without cursor. No segments
    """

    # Move events from buffer to journal
    await run_journal_events_mover()

    response = await taxi_cargo_claims.post('v1/segments/journal', json={})
    assert response.status_code == 200

    assert response.headers['X-Polling-Delay-Ms'] == '5000'
    assert 'cursor' in response.json()


async def test_request_without_cursor(
        taxi_cargo_claims, create_segment, run_journal_events_mover,
):
    """
    Request without cursor.
    """

    # Create 1 segment
    await create_segment()

    # Move events from buffer to journal
    await run_journal_events_mover()

    response = await taxi_cargo_claims.post('v1/segments/journal', json={})
    assert response.status_code == 200

    assert response.headers['X-Polling-Delay-Ms'] == '1000'
    assert 'cursor' in response.json()

    entries = response.json()['entries']
    assert len(entries) == 1
    assert 'claim_id' in entries[0]['current']
    assert entries[0]['revision'] == 1
    assert entries[0]['current']['points_user_version'] == 1


@pytest.mark.config(
    CARGO_CLAIMS_SEGMENTS_JOURNAL_SETTINGS={
        'wait_lost_event_s': 60,
        'journal_chunk_size': 1,
        'min_polling_delay_ms': 1000,
        'max_polling_delay_ms': 5000,
    },
)
async def test_new_cursor(
        taxi_cargo_claims, create_segment, run_journal_events_mover,
):
    """
    Test that request with new cursor returns new values
    """
    await create_segment()

    # Move events from buffer to journal
    await run_journal_events_mover()

    response = await taxi_cargo_claims.post('v1/segments/journal', json={})
    assert response.status_code == 200

    response_body = response.json()
    segment_1 = response_body['entries'][0]['segment_id']
    assert segment_1

    # TODO: create second segment and uncomment this
    # response = await taxi_cargo_claims.post('v1/segments/journal',
    # json={'cursor': response_body['cursor']})
    # assert response.status_code == 200
    # segment_2 = response.json()['entries'][0]['segment_id']
    #
    # assert segment_1 != segment_2


async def test_finished_segment(
        taxi_cargo_claims,
        create_segment,
        prepare_state,
        run_journal_events_mover,
):
    await prepare_state(visit_order=3)

    # Move events from buffer to journal
    await run_journal_events_mover()

    response = await taxi_cargo_claims.post('v1/segments/journal', json={})
    assert response.status_code == 200

    response_body = response.json()
    segment_1 = response_body['entries'][-1]
    assert segment_1['current']['resolution'] == 'finished'


async def insert_old_journal_event(
        pgsql, pkey: int, segment_id: str, claim_id: str,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claim_segments_journal
            (id, segment_id, segment_revision, claim_uuid,
                segment_status, points_user_version)
        VALUES (\'{pkey}\', \'{segment_id}\', \'{pkey + 10}\',
                \'{claim_id}\', 'new', 1)
        """,
    )


async def insert_new_journal_event(
        pgsql, pkey: int, segment_id: str, claim_id: str,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claim_segments_journal_v2
            (id, segment_id, segment_revision, claim_uuid,
                segment_status, points_user_version)
        VALUES (\'{pkey}\', \'{segment_id}\', \'{pkey + 10}\',
                \'{claim_id}\', 'new', 1)
        """,
    )


async def insert_new_journal_buffer_event(
        pgsql, pkey: int, segment_id: str, claim_id: str, revision_addition=0,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claim_segments_journal_v2_buffer
            (id, segment_id, segment_revision, claim_uuid,
                segment_status, points_user_version, is_processed)
        VALUES (\'{pkey}\', \'{segment_id}\', \'{pkey + revision_addition}\',
                \'{claim_id}\', 'new', 1, False)
        """,
    )


async def flush_new_journal_buffer(pgsql):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        DELETE FROM cargo_claims.claim_segments_journal_v2_buffer
        WHERE is_processed = True
        """,
    )


async def test_new_journal_holes(
        taxi_cargo_claims,
        create_segment,
        prepare_state,
        pgsql,
        get_segment_id,
):
    claim_info = await create_segment()
    segment_id = await get_segment_id()

    await insert_new_journal_event(pgsql, 100, segment_id, claim_info.claim_id)
    await insert_new_journal_event(
        pgsql, 1000000, segment_id, claim_info.claim_id,
    )

    # Request with cursor forces new journal usage
    response = await taxi_cargo_claims.post(
        'v1/segments/journal', json={'cursor': build_fake_cursor()},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['entries'] == [
        {
            'created_ts': matching.AnyString(),
            'current': {
                'claim_id': claim_info.claim_id,
                'points_user_version': 1,
            },
            'revision': 110,
            'segment_id': segment_id,
        },
        {
            'created_ts': matching.AnyString(),
            'current': {
                'claim_id': claim_info.claim_id,
                'points_user_version': 1,
            },
            'revision': 1000010,
            'segment_id': segment_id,
        },
    ]

    decoded = jwt.decode(resp_body['cursor'], 'secret', algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 1000000,
        'version': 1,
    }


def build_fake_cursor():
    return jwt.encode(
        {'last_known_id': 1, 'holes': [], 'version': 1},
        'secret',
        algorithm='HS512',
    ).decode('utf-8')


async def test_cursor_version(taxi_cargo_claims, taxi_config):
    response = await taxi_cargo_claims.post(
        'v1/segments/journal', json={'cursor': build_fake_cursor()},
    )
    assert response.status_code == 200

    decoded = jwt.decode(
        response.json()['cursor'], 'secret', algorithms=['HS512'],
    )
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 1,
        'version': 1,
    }


async def test_new_journal_usage(
        taxi_cargo_claims,
        create_segment,
        prepare_state,
        pgsql,
        get_segment_id,
):
    claim_info = await create_segment()
    segment_id = await get_segment_id()

    await insert_new_journal_event(pgsql, 10, segment_id, claim_info.claim_id)

    # 1. First request
    response = await taxi_cargo_claims.post(
        'v1/segments/journal', json={'cursor': build_fake_cursor()},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['entries'] == [
        {
            'created_ts': matching.AnyString(),
            'current': {
                'claim_id': claim_info.claim_id,
                'points_user_version': 1,
            },
            'revision': 20,
            'segment_id': segment_id,
        },
    ]
    decoded = jwt.decode(resp_body['cursor'], 'secret', algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 10,
        'version': 1,
    }

    # 2. Add new event
    await insert_new_journal_event(pgsql, 100, segment_id, claim_info.claim_id)

    # 3. Second request
    response = await taxi_cargo_claims.post(
        'v1/segments/journal', json={'cursor': resp_body['cursor']},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['entries'] == [
        {
            'created_ts': matching.AnyString(),
            'current': {
                'claim_id': claim_info.claim_id,
                'points_user_version': 1,
            },
            'revision': 110,
            'segment_id': segment_id,
        },
    ]
    decoded = jwt.decode(resp_body['cursor'], 'secret', algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 100,
        'version': 1,
    }


async def test_equal_segments_(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        pgsql,
        prepare_state,
        run_journal_events_mover,
):
    claim_info = await create_segment()
    segment_id = await get_segment_id()
    await run_journal_events_mover()
    await flush_new_journal_buffer(pgsql)

    await insert_new_journal_buffer_event(
        pgsql, 2, segment_id, claim_info.claim_id, -1,
    )
    await run_journal_events_mover()

    response = await taxi_cargo_claims.post('v1/segments/journal', json={})
    assert response.status_code == 200
