import pytest

PERFORMER_1 = 'dbid0_uuid0'
PERFORMER_2 = 'dbid1_uuid1'


def insert_delivery(pgsql, *, depot_id, order_id, performer_id, status):
    pgsql['grocery_dispatch_tracking'].cursor().execute(
        'INSERT INTO dispatch_tracking.delivery'
        '   (depot_id, order_id, performer_id, status)'
        'VALUES (%s, %s, %s, %s)',
        (depot_id, order_id, performer_id, status),
    )


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
        insert_delivery(
            pgsql,
            depot_id=depot_id,
            order_id=order_id,
            performer_id=performer_id,
            status=delivery_status,
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


@pytest.mark.parametrize(
    ('order_status', 'performer_id', 'assembly_started', 'assembly_finished'),
    [
        ('new', None, None, None),
        ('new', None, '2021-08-12T07:22:40.721471+00:00', None),
        (
            'new',
            None,
            '2021-08-12T07:22:40.721471+00:00',
            '2021-08-12T07:27:40.721471+00:00',
        ),
        (
            'delivering',
            'dbid0_uuid0',
            '2021-08-12T07:22:40.721471+00:00',
            '2021-08-12T07:27:40.721471+00:00',
        ),
    ],
)
async def test_basic(
        taxi_grocery_dispatch_tracking,
        pgsql,
        order_status,
        performer_id,
        assembly_started,
        assembly_finished,
):
    insert_order(
        pgsql,
        order_id='test_order_id',
        depot_id='100',
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id=performer_id,
        delivery_status='delivering',
        assembly_started=assembly_started,
        assembly_finished=assembly_finished,
    )

    insert_performer(
        pgsql,
        depot_id='100',
        performer_id='dbid0_uuid777',
        status='idle',
        updated='2021-08-12T07:39:40.721471+00:00',
    )

    if performer_id is not None:
        insert_performer(
            pgsql,
            depot_id='100',
            performer_id=performer_id,
            status='deliver',
            updated='2021-08-12T07:39:40.721471+00:00',
        )

    response = await taxi_grocery_dispatch_tracking.post(
        '/internal/grocery-dispatch-tracking/v1/depot-state',
        json={'legacy_depot_id': '100'},
    )

    expected_json = {
        'orders': [
            {
                'order_id': 'test_order_id',
                'order_status': order_status,
                'delivery_type': 'courier',
            },
        ],
        'performers': [
            {'courier_dbid_uuid': 'dbid0_uuid777', 'performer_status': 'idle'},
        ],
    }

    if performer_id is not None:
        expected_json['orders'][0]['courier_dbid_uuid'] = performer_id
        expected_json['performers'].append(
            {'courier_dbid_uuid': performer_id, 'performer_status': 'deliver'},
        )

    if assembly_started is not None:
        expected_json['orders'][0]['assembly_started'] = assembly_started

    if assembly_finished is not None:
        expected_json['orders'][0]['assembly_finished'] = assembly_finished

    assert response.status_code == 200
    assert expected_json == response.json()


async def test_remove_duplicates_orders_when_many_deliveries(
        taxi_grocery_dispatch_tracking, pgsql,
):
    """Fix https://st.yandex-team.ru/LAVKALOGDEV-1120"""

    order_status = 'delivering'
    depot_id = '100'
    order_id = 'test_order_id'

    insert_order(
        pgsql,
        order_id=order_id,
        depot_id=depot_id,
        order_status=order_status,
        delivery_type='courier',
        max_eta=20,
        performer_id=PERFORMER_1,
        delivery_status='delivering',
    )

    insert_performer(
        pgsql,
        depot_id=depot_id,
        performer_id=PERFORMER_1,
        status='matched',
        updated='2021-08-12T07:39:40.721471+00:00',
    )
    insert_performer(
        pgsql,
        depot_id=depot_id,
        performer_id=PERFORMER_2,
        status='deliver',
        updated='2021-08-12T07:39:40.721471+00:00',
    )

    # Add new delivery
    insert_delivery(
        pgsql,
        depot_id=depot_id,
        order_id=order_id,
        performer_id=PERFORMER_2,
        status='delivering',
    )

    response = await taxi_grocery_dispatch_tracking.post(
        '/internal/grocery-dispatch-tracking/v1/depot-state',
        json={'legacy_depot_id': '100'},
    )

    expected_json = {
        'orders': [
            {
                'order_id': order_id,
                'courier_dbid_uuid': PERFORMER_2,
                'order_status': order_status,
                'delivery_type': 'courier',
            },
        ],
        'performers': [
            {'courier_dbid_uuid': PERFORMER_1, 'performer_status': 'matched'},
            {'courier_dbid_uuid': PERFORMER_2, 'performer_status': 'deliver'},
        ],
    }

    assert response.status_code == 200
    assert expected_json == response.json()
