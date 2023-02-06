import pytest


@pytest.mark.config(
    MANUAL_DISPATCH_PROCESSING_RACES_FIXER_SETTINGS={
        'enabled': True,
        'sleep_time_ms': 0,
        'update_ttl': 0,
        'max_expected_races': 5,
    },
)
async def test_status_updated(
        taxi_manual_dispatch,
        create_order,
        stq_runner,
        get_order,
        pgsql,
        get_delayed_updates,
):
    await stq_runner.manual_dispatch_handle_finish.call(
        task_id='order_id_1',
        kwargs={
            'taxi_status': 'expired',
            'status': 'finished',
            'has_performer': False,
            'lookup_version': 1,
        },
    )
    await stq_runner.manual_dispatch_handle_driving.call(
        task_id='some_uuid',
        kwargs={
            'order_id': 'order_id_2',
            'performer_dbid': 'dbid1',
            'performer_uuid': 'performer_uuid_1',
            'lookup_version': 1,
        },
    )
    await stq_runner.manual_dispatch_handle_autoreorder.call(
        task_id='some_uuid',
        kwargs={
            'order_id': 'order_id_2',
            'performer_dbid': 'dbid1',
            'performer_uuid': 'performer_uuid_1',
            'lookup_version': 2,
        },
    )

    cursor = pgsql['manual-dispatch'].conn.cursor()
    cursor.execute(
        """INSERT INTO manual_dispatch.delayed_status_updates
                   (order_id, status, reason, lookup_version, created_ts)
                   VALUES ('order_id_4', 'cancelled', 'reason', 3,
                           NOW() + INTERVAL '2h')
                   """,
    )
    cursor.execute(
        """INSERT INTO manual_dispatch.delayed_status_updates
                   (order_id, status, reason, lookup_version, created_ts)
                   VALUES ('order_id_5', 'cancelled', 'reason', 3,
                           NOW() - INTERVAL '2h')
                   """,
    )

    # sanity check, tested in test_no_such_order
    assert len(get_delayed_updates()) == 5
    create_order(order_id='order_id_1', lookup_version=0)
    create_order(order_id='order_id_2', lookup_version=0)

    await taxi_manual_dispatch.run_task('manual-dispatch-status-updater')
    assert len(get_delayed_updates()) == 1
    assert get_delayed_updates()[0]['order_id'] == 'order_id_4'
    assert get_order(
        'order_id_1', projection=('status', 'lookup_version'),
    ) == {'status': 'search_failed', 'lookup_version': 1}
    assert get_order(
        'order_id_2', projection=('status', 'lookup_version'),
    ) == {'status': 'pending', 'lookup_version': 2}
