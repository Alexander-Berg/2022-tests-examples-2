import datetime

import pytest

LEGACY_DEPOT_ID_1 = '123'
LEGACY_DEPOT_ID_2 = '456'


def insert_order(
        pgsql,
        *,
        order_id,
        depot_id,
        order_status,
        delivery_type,
        max_eta,
        performer_id=None,
        delivery_status=None,
        assembly_started=None,
        assembly_finished=None,
):
    pgsql['grocery_dispatch_tracking'].cursor().execute(
        'INSERT INTO dispatch_tracking.orders'
        '   (order_id, depot_id, status, delivery_type, max_eta)'
        'VALUES (%s, %s, %s, %s, %s)',
        (order_id, depot_id, order_status, delivery_type, max_eta),
    )

    if performer_id is not None:
        pgsql['grocery_dispatch_tracking'].cursor().execute(
            'INSERT INTO dispatch_tracking.delivery'
            '   (depot_id, order_id, performer_id, status)'
            'VALUES (%s, %s, %s, %s)',
            (depot_id, order_id, performer_id, delivery_status),
        )

    if assembly_started is not None and assembly_finished is not None:
        pgsql['grocery_dispatch_tracking'].cursor().execute(
            'INSERT INTO'
            '   dispatch_tracking.order_assemble_ready_events'
            '   (depot_id, order_id, ts, assembled_ts)'
            'VALUES (%s, %s, %s, %s)',
            (depot_id, order_id, assembly_started, assembly_finished),
        )
    elif assembly_started is not None:
        pgsql['grocery_dispatch_tracking'].cursor().execute(
            'INSERT INTO '
            '   dispatch_tracking.order_assemble_ready_events'
            '   (depot_id, order_id, ts)'
            'VALUES (%s, %s, %s)',
            (depot_id, order_id, assembly_started),
        )


def insert_performer(pgsql, *, depot_id, performer_id, status, updated):
    pgsql['grocery_dispatch_tracking'].cursor().execute(
        'INSERT INTO dispatch_tracking.performers'
        '   (depot_id, performer_id, status, updated)'
        'VALUES (%s, %s, %s, %s)',
        (depot_id, performer_id, status, updated),
    )


def get_depot_states(pgsql):
    cursor = pgsql['grocery_dispatch_tracking'].cursor()
    cursor.execute(
        """
            SELECT *
            FROM dispatch_tracking.depot_state
        """,
    )
    return cursor.fetchall()


NOW = datetime.datetime(
    2017,
    3,
    13,
    8,
    30,
    tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)),
)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('enable_component', [True, False])
@pytest.mark.parametrize('chunk_size', [1, 10])
async def test_basic(
        taxi_grocery_dispatch_tracking,
        pgsql,
        enable_component,
        chunk_size,
        taxi_config,
        grocery_depots,
):
    order_status = 'delivering'
    assembly_started = '2021-08-12T07:22:40.721471+00:00'
    assembly_finished = '2021-08-12T07:27:40.721471+00:00'

    taxi_config.set_values(
        {
            'GROCERY_DISPATCH_TRACKING_DEPOT_STATE_STORAGE_FLAG': (
                enable_component
            ),
            'GROCERY_DISPATCH_TRACKING_DEPOT_STATE_STORAGE_UPDATE_CHUNK_SIZE': (  # noqa: E501
                chunk_size
            ),
        },
    )

    insert_order(
        pgsql,
        order_id='test_order_id_1',
        depot_id=LEGACY_DEPOT_ID_1,
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id='dbid0_uuid0',
        delivery_status='delivering',
        assembly_started=assembly_started,
        assembly_finished=assembly_finished,
    )
    insert_order(
        pgsql,
        order_id='test_order_id_2',
        depot_id=LEGACY_DEPOT_ID_2,
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id='dbid0_uuid777',
        delivery_status='delivering',
        assembly_started=assembly_started,
        assembly_finished=assembly_finished,
    )

    insert_performer(
        pgsql,
        depot_id=LEGACY_DEPOT_ID_1,
        performer_id='dbid0_uuid0',
        status='idle',
        updated='2021-08-12T07:39:40.721471+00:00',
    )
    insert_performer(
        pgsql,
        depot_id=LEGACY_DEPOT_ID_2,
        performer_id='dbid0_uuid777',
        status='idle',
        updated='2021-08-12T07:39:40.721471+00:00',
    )

    grocery_depots.add_depot(
        depot_test_id=LEGACY_DEPOT_ID_1,
        depot_id=LEGACY_DEPOT_ID_1,
        legacy_depot_id=LEGACY_DEPOT_ID_1,
        auto_add_zone=False,
    )
    grocery_depots.add_depot(
        depot_test_id=LEGACY_DEPOT_ID_2,
        depot_id=LEGACY_DEPOT_ID_2,
        legacy_depot_id=LEGACY_DEPOT_ID_2,
        auto_add_zone=False,
    )

    await taxi_grocery_dispatch_tracking.invalidate_caches()

    await taxi_grocery_dispatch_tracking.run_periodic_task(
        'depot-state-storage-periodic',
    )

    depot_states = get_depot_states(pgsql)

    if enable_component:
        assert depot_states == [
            (
                LEGACY_DEPOT_ID_1,
                [
                    {
                        'order_id': 'test_order_id_1',
                        'order_status': order_status,
                        'delivery_type': 'courier',
                        'assembly_started': assembly_started,
                        'assembly_finished': assembly_finished,
                        'courier_dbid_uuid': 'dbid0_uuid0',
                    },
                ],
                [
                    {
                        'courier_dbid_uuid': 'dbid0_uuid0',
                        'performer_status': 'idle',
                    },
                ],
                NOW,
            ),
            (
                LEGACY_DEPOT_ID_2,
                [
                    {
                        'order_id': 'test_order_id_2',
                        'order_status': order_status,
                        'delivery_type': 'courier',
                        'assembly_started': assembly_started,
                        'assembly_finished': assembly_finished,
                        'courier_dbid_uuid': 'dbid0_uuid777',
                    },
                ],
                [
                    {
                        'courier_dbid_uuid': 'dbid0_uuid777',
                        'performer_status': 'idle',
                    },
                ],
                NOW,
            ),
        ]
    else:
        assert depot_states == []


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(GROCERY_DISPATCH_TRACKING_DEPOT_STATE_STORAGE_FLAG=True)
async def test_update(
        taxi_grocery_dispatch_tracking,
        pgsql,
        mocked_time,
        grocery_depots,
        insert_depot_state,
):
    order_status = 'delivering'
    assembly_started = '2021-08-12T07:22:40.721471+00:00'
    assembly_finished = '2021-08-12T07:27:40.721471+00:00'

    insert_order(
        pgsql,
        order_id='test_order_id_1',
        depot_id=LEGACY_DEPOT_ID_1,
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id='dbid0_uuid0',
        delivery_status='delivering',
        assembly_started=assembly_started,
        assembly_finished=assembly_finished,
    )
    insert_performer(
        pgsql,
        depot_id=LEGACY_DEPOT_ID_1,
        performer_id='dbid0_uuid0',
        status='idle',
        updated='2021-08-12T07:39:40.721471+00:00',
    )

    order_1 = {
        'order_id': 'test_order_id_1',
        'order_status': order_status,
        'delivery_type': 'courier',
        'assembly_started': assembly_started,
        'assembly_finished': assembly_finished,
        'courier_dbid_uuid': 'dbid0_uuid0',
    }
    performer_1 = {
        'courier_dbid_uuid': 'dbid0_uuid0',
        'performer_status': 'idle',
    }

    insert_depot_state(
        depot_id=LEGACY_DEPOT_ID_1,
        orders=order_1,
        performers=performer_1,
        updated=NOW,
    )

    grocery_depots.add_depot(
        depot_test_id=LEGACY_DEPOT_ID_1,
        depot_id=LEGACY_DEPOT_ID_1,
        legacy_depot_id=LEGACY_DEPOT_ID_1,
        auto_add_zone=False,
    )

    await taxi_grocery_dispatch_tracking.invalidate_caches()

    mocked_time.set(NOW + datetime.timedelta(minutes=5))

    insert_order(
        pgsql,
        order_id='test_order_id_2',
        depot_id=LEGACY_DEPOT_ID_1,
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id='dbid0_uuid777',
        delivery_status='delivering',
        assembly_started=assembly_started,
        assembly_finished=assembly_finished,
    )

    insert_performer(
        pgsql,
        depot_id=LEGACY_DEPOT_ID_1,
        performer_id='dbid0_uuid777',
        status='idle',
        updated='2021-08-12T07:39:40.721471+00:00',
    )

    await taxi_grocery_dispatch_tracking.invalidate_caches()

    await taxi_grocery_dispatch_tracking.run_periodic_task(
        'depot-state-storage-periodic',
    )

    depot_states = get_depot_states(pgsql)

    assert len(depot_states) == 2

    assert depot_states == [
        (
            LEGACY_DEPOT_ID_1,
            {
                'order_id': 'test_order_id_1',
                'order_status': order_status,
                'delivery_type': 'courier',
                'assembly_started': assembly_started,
                'assembly_finished': assembly_finished,
                'courier_dbid_uuid': 'dbid0_uuid0',
            },
            {'courier_dbid_uuid': 'dbid0_uuid0', 'performer_status': 'idle'},
            NOW,
        ),
        (
            LEGACY_DEPOT_ID_1,
            [
                {
                    'order_id': 'test_order_id_1',
                    'order_status': order_status,
                    'delivery_type': 'courier',
                    'assembly_started': assembly_started,
                    'assembly_finished': assembly_finished,
                    'courier_dbid_uuid': 'dbid0_uuid0',
                },
                {
                    'order_id': 'test_order_id_2',
                    'order_status': order_status,
                    'delivery_type': 'courier',
                    'assembly_started': assembly_started,
                    'assembly_finished': assembly_finished,
                    'courier_dbid_uuid': 'dbid0_uuid777',
                },
            ],
            [
                {
                    'courier_dbid_uuid': 'dbid0_uuid0',
                    'performer_status': 'idle',
                },
                {
                    'courier_dbid_uuid': 'dbid0_uuid777',
                    'performer_status': 'idle',
                },
            ],
            NOW + datetime.timedelta(minutes=5),
        ),
    ]
