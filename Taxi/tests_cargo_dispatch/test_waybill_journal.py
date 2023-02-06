import jwt
import pytest

from testsuite.utils import matching


FALLBACK_ROUTER = 'fallback_router'
JWT_SECRET = 'not-a-secret'

BASE_WAYBILLS_EVENTS = [
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'external_ref': 'waybill_fb_1',
        'current': {},
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'external_ref': 'waybill_fb_2',
        'current': {},
    },
    {
        'created_ts': matching.AnyString(),
        'revision': 1,
        'external_ref': 'waybill_fb_3',
        'current': {},
    },
]


async def test_first_request_without_cursor(
        happy_path_state_fallback_waybills_proposed, read_waybill_journal,
):
    response = await read_waybill_journal(FALLBACK_ROUTER)
    assert 'cursor' in response


@pytest.mark.config(
    CARGO_DISPATCH_WAYBILLS_JOURNAL={
        'max_items': 1,
        'min_polling_delay_ms': 1000,
        'max_polling_delay_ms': 5000,
        'wait_lost_event_s': 60,
    },
)
async def test_events_limit(
        happy_path_state_fallback_waybills_proposed,
        read_waybill_journal,
        run_waybills_journal_mover,
):
    # Move events from buffer to journal
    await run_waybills_journal_mover()

    response = await read_waybill_journal(FALLBACK_ROUTER)
    assert len(response['events']) == 1


async def test_no_events_for_router(
        happy_path_state_fallback_waybills_proposed,
        read_waybill_journal,
        run_waybills_journal_mover,
):
    # Move events from buffer to journal
    await run_waybills_journal_mover()

    response = await read_waybill_journal(router_id='unknown_router')
    assert not response['events']


async def test_order_id_when_order_created(
        happy_path_state_orders_created,
        read_waybill_journal,
        cargo_orders_db,
        run_waybills_journal_mover,
):
    # Move events from buffer to journal
    await run_waybills_journal_mover()

    response = await read_waybill_journal(FALLBACK_ROUTER)
    last_event = response['events'][-1]
    assert 'taxi_order_id' in last_event['current']

    taxi_order_id = last_event['current']['taxi_order_id']
    waybill_ref = cargo_orders_db.waybill_ref_from_taxi_order_id(taxi_order_id)
    assert waybill_ref == 'waybill_fb_3'


# New journal tests


async def insert_old_journal_event(
        pgsql, pkey: int, external_ref: str, router_id: str = FALLBACK_ROUTER,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_dispatch.waybills_journal
            (id, external_ref, router_id, waybill_revision)
        VALUES (\'{pkey}\', \'{external_ref}\',
                \'{router_id}\', \'{pkey + 10}\')
        """,
    )


async def insert_new_journal_event(
        pgsql, pkey: int, external_ref: str, router_id: str = FALLBACK_ROUTER,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_dispatch.waybills_journal_v2
            (id, external_ref, router_id, waybill_revision)
        VALUES (\'{pkey}\', \'{external_ref}\',
                \'{router_id}\', \'{pkey + 10}\')
        """,
    )


def build_fake_cursor():
    return jwt.encode(
        {'last_known_id': 1, 'holes': [], 'version': 1},
        JWT_SECRET,
        algorithm='HS512',
    ).decode('utf-8')


async def test_new_journal_holes(
        happy_path_state_fallback_waybills_proposed,
        pgsql,
        request_waybill_journal,
):
    await insert_new_journal_event(
        pgsql, 100, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )
    await insert_new_journal_event(
        pgsql, 1000000, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )

    # Request with cursor forces new journal usage
    response = await request_waybill_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(),
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 110,
            'external_ref': 'waybill_fb_3',
            'current': {},
        },
        {
            'created_ts': matching.AnyString(),
            'revision': 1000010,
            'external_ref': 'waybill_fb_3',
            'current': {},
        },
    ]

    decoded = jwt.decode(resp_body['cursor'], JWT_SECRET, algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 1000000,
        'version': 1,
    }


async def test_cursor_version(taxi_cargo_dispatch, request_waybill_journal):
    response = await request_waybill_journal(
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
        taxi_cargo_dispatch,
        taxi_config,
        happy_path_state_fallback_waybills_proposed,
        run_waybills_journal_mover,
        request_waybill_journal,
        pgsql,
):
    await insert_new_journal_event(
        pgsql, 10, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )

    # 1. First request
    response = await request_waybill_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(),
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 20,
            'external_ref': 'waybill_fb_3',
            'current': {},
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
        pgsql, 100, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )

    # 3. Second request
    response = await request_waybill_journal(
        FALLBACK_ROUTER, cursor=resp_body['cursor'],
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 110,
            'external_ref': 'waybill_fb_3',
            'current': {},
        },
    ]
    decoded = jwt.decode(resp_body['cursor'], JWT_SECRET, algorithms=['HS512'])
    assert decoded == {
        'holes': [],
        'journal_version': 2,
        'last_known_id': 100,
        'version': 1,
    }


async def test_duplicates(
        happy_path_state_fallback_waybills_proposed,
        pgsql,
        request_waybill_journal,
):
    await insert_new_journal_event(
        pgsql, 100, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )
    await insert_new_journal_event(
        pgsql, 200, 'waybill_fb_3', router_id=FALLBACK_ROUTER,
    )

    # Request without duplicates
    response = await request_waybill_journal(
        FALLBACK_ROUTER, cursor=build_fake_cursor(), without_duplicates=True,
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['events'] == [
        {
            'created_ts': matching.AnyString(),
            'revision': 210,
            'external_ref': 'waybill_fb_3',
            'current': {},
        },
    ]
