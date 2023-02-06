import pytest


async def test_top_delivery_order_history(
        taxi_logistic_platform_gateway,
        mockserver,
        top_delivery_order_events_retrieve,
        load,
        load_json,
):
    top_delivery_order_events_retrieve.set_data(
        load('top_delivery_response.xml'),
    )

    response = await taxi_logistic_platform_gateway.post(
        '/internal/operator/top-delivery/order/history',
        params={'external_order_id': '6002176'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'skipped_events_count',
    [pytest.param(0, id='no skips'), pytest.param(999, id='full skip')],
)
async def test_top_delivery_order_history_stq(
        stq_runner,
        load_json,
        mockserver,
        push_order_event,
        pgsql,
        skipped_events_count,
):
    all_events = load_json('converted_events.json')

    @mockserver.json_handler(
        '/logistic-platform-gateway/internal/operator/top-delivery/order/history',  # noqa E501
    )
    def order_history(request):
        return {'order_events': all_events}

    cursor = pgsql['logistic_platform'].cursor()
    cursor.execute(
        """
        INSERT INTO
        operator_events_history (
            operator_id,
            external_order_id,
            external_place_id,
            history_user_id,
            history_action,
            history_timestamp,
            event_status,
            event_instant,
            class_name
        )
        SELECT
            'top-delivery', '6002176',
            '', '', '', 0, '', 0, ''
        FROM generate_series(1, %s::INTEGER) AS g (id)
        """,
        (skipped_events_count,),
    )

    cursor = pgsql['logistic_platform_gateway'].cursor()
    cursor.execute(
        """
        INSERT INTO logistic_platform_gateway.tracked_orders
            (operator_id, cluster_id, external_order_id)
        VALUES
            ('top-delivery', 'main_cluster', '6002176');
        """,
    )

    await stq_runner.logistic_platform_gateway_update_order_history_top_delivery_main_cluster.call(  # noqa E501
        task_id='6002176',
    )

    assert order_history.times_called == 1
    assert push_order_event.get_events() == all_events[skipped_events_count:]


async def test_top_delivery_preserved_event(
        stq_runner, load_json, mockserver, push_order_event, pgsql,
):
    all_events = load_json('preserved_event.json')

    @mockserver.json_handler(
        '/logistic-platform-gateway/internal/operator/top-delivery/order/history',  # noqa E501
    )
    def order_history(request):
        return {'order_events': all_events}

    cursor = pgsql['logistic_platform'].cursor()
    cursor.execute(
        """
        INSERT INTO
        operator_events_history (
            operator_id,
            external_order_id,
            external_place_id,
            history_user_id,
            history_action,
            history_timestamp,
            event_status,
            event_instant,
            class_name
        )
        SELECT
            'top-delivery', '123456',
            '', '', '', 0, '', 0, ''
        FROM generate_series(1, %s::INTEGER) AS g (id)
        """,
        (999,),
    )

    cursor = pgsql['logistic_platform_gateway'].cursor()
    cursor.execute(
        """
        INSERT INTO logistic_platform_gateway.tracked_orders
            (operator_id, cluster_id, external_order_id)
        VALUES
            ('top-delivery', 'main_cluster', '123456');
        """,
    )

    await stq_runner.logistic_platform_gateway_update_order_history_top_delivery_main_cluster.call(  # noqa E501
        task_id='123456',
    )

    assert order_history.times_called == 1
    assert push_order_event.get_events() == all_events


async def test_top_delivery_tracker_disabled(taxi_logistic_platform_gateway):
    await taxi_logistic_platform_gateway.run_distlock_task(
        'top-delivery-main-tracker',
    )


@pytest.mark.config(
    LOGISTIC_PLATFORM_GATEWAY_TRACKER_SETTINGS={
        'top-delivery-main_cluster': {
            'enabled': True,
            'period': 1,
            'batch_size': 1,
        },  # noqa E501
    },
)
@pytest.mark.parametrize(
    'tracked_order_ids, platform_order_ids, expected_stq_ids',
    [
        pytest.param(
            [], ['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'], id='add all',
        ),
        pytest.param(
            ['foo', 'qux'],
            ['foo', 'bar', 'baz'],
            ['bar', 'baz'],
            id='add only new',
        ),
        pytest.param(
            ['foo', 'bar', 'baz'],
            ['foo', 'bar', 'baz'],
            [],
            id='no updates',  # noqa E501
        ),
    ],
)
async def test_top_delivery_tracker(
        taxi_logistic_platform_gateway,
        pgsql,
        stq,
        get_active_order_ids,
        tracked_order_ids,
        platform_order_ids,
        expected_stq_ids,
):
    get_active_order_ids.set_data('top-delivery', platform_order_ids)

    cursor = pgsql['logistic_platform_gateway'].cursor()
    cursor.execute(
        f"""
        INSERT INTO
            logistic_platform_gateway.tracked_orders
            (operator_id, cluster_id, external_order_id)
        SELECT
            'top-delivery',
            'main_cluster',
            UNNEST(%s::TEXT[])
        """,
        (tracked_order_ids,),
    )

    await taxi_logistic_platform_gateway.run_distlock_task(
        'top-delivery-main-tracker',
    )

    assert expected_stq_ids == [
        stq.logistic_platform_gateway_update_order_history_top_delivery_main_cluster.next_call()[  # noqa E501
            'id'
        ]
        for _ in range(
            stq.logistic_platform_gateway_update_order_history_top_delivery_main_cluster.times_called,  # noqa E501
        )
    ]
