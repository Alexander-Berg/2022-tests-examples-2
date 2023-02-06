import datetime

import pytest

from tests_delayed import mock_utils


@pytest.mark.pgsql('delayed_orders', files=['delayed_orders.sql'])
@pytest.mark.parametrize(
    'request_body,response_status,archive_orders',
    [
        ({'order_id': 'example_order_id'}, 200, ['example_order_id']),
        ({'some_broken_request': 22}, 400, []),
        ({'order_id': 'archive_failed_order_id'}, 404, []),
        (
            {'order_id': 'already_existing_order_id'},
            409,
            ['already_existing_order_id'],
        ),
    ],
)
@pytest.mark.now('2019-02-04T00:00:00Z')
async def test_add_order(
        taxi_delayed,
        archive,
        pgsql,
        request_body,
        response_status,
        archive_orders,
        now,
):
    archive.set_order_procs(
        [
            {'_id': order_id, 'order': {'_id': order_id}}
            for order_id in archive_orders
        ],
    )

    await taxi_delayed.tests_control()

    headers = {'X-YaRequestId': 'request_link'}
    response = await taxi_delayed.post('v1/add', request_body, headers=headers)

    assert response.status_code == response_status, response.content

    expected_db = [
        mock_utils.create_order_entry(
            order_id='already_existing_order_id',
            due=now,
            link_id='link_5',
            is_processing=False,
            last_processing=now - datetime.timedelta(days=1),
            is_processing_change_time=now - datetime.timedelta(days=2),
        ),
    ]

    if response.status_code == 200:
        expected_db.append(
            mock_utils.create_order_entry(
                order_id=request_body['order_id'],
                due=archive.STATIC_ORDER_PROC['order']['request']['due'],
                link_id=headers['X-YaRequestId'],
                is_processing=False,
                last_processing=now,
                is_processing_change_time=now,
                zone=archive.STATIC_ORDER_PROC['order']['nz'],
                tariff=sorted(
                    archive.STATIC_ORDER_PROC['order']['request']['class'],
                )[0],
            ),
        )

    delayed_orders = mock_utils.validate_items_count_in_db(
        delayed_orders=len(expected_db), dispatched_orders=0, pgsql=pgsql,
    )[0]

    assert sorted(delayed_orders) == sorted(expected_db)
