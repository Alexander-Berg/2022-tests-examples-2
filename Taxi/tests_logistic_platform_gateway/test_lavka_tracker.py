import pytest


@pytest.mark.config(
    LOGISTIC_PLATFORM_SETTINGS={
        'event.deferred.enabled': 'true',
        'operator.lavka.delivered.defer_duration': '20m',
    },
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
async def test_lavka_order_history(
        taxi_logistic_platform_gateway, lavka_order_events_retrieve, load_json,
):
    lavka_order_events_retrieve.set_data(load_json('lavka_response.json'))

    response = await taxi_logistic_platform_gateway.post(
        '/internal/operator/lavka/order/history',
        params={'external_order_id': 'ce13727d-ef0b-4279-a11f-dfc14e7320cc'},
    )

    assert response.status_code == 200
    assert response.json()['order_events'] == load_json(
        'converted_events.json',
    )


@pytest.mark.parametrize(
    'skipped_events_count',
    [pytest.param(0, id='no skips'), pytest.param(3, id='3 skips')],
)
async def test_lavka_order_history_stq(
        stq_runner,
        load_json,
        mockserver,
        push_order_event,
        pgsql,
        skipped_events_count,
):
    all_events = load_json('converted_events.json')

    @mockserver.json_handler(
        '/logistic-platform-gateway/internal/operator/lavka/order/history',
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
            'lavka',
            'ce13727d-ef0b-4279-a11f-dfc14e7320cc',
            '32888751_KOROBKA1',
            '', '', 0, '', 0, ''
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
            ('lavka', 'main_cluster', 'ce13727d-ef0b-4279-a11f-dfc14e7320cc');
        """,
    )

    await stq_runner.logistic_platform_gateway_update_order_history_lavka_main_cluster.call(  # noqa E501
        task_id='ce13727d-ef0b-4279-a11f-dfc14e7320cc',
    )

    assert order_history.times_called == 1
    assert push_order_event.get_events() == all_events[skipped_events_count:]


async def test_lavka_tracker_disabled(taxi_logistic_platform_gateway):
    await taxi_logistic_platform_gateway.run_distlock_task(
        'lavka-main-tracker',
    )


@pytest.mark.config(
    LOGISTIC_PLATFORM_GATEWAY_TRACKER_SETTINGS={
        'lavka-main_cluster': {'enabled': True, 'period': 1, 'batch_size': 1},
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
            ['foo', 'bar', 'baz'], ['foo', 'bar', 'baz'], [], id='no updates',
        ),
    ],
)
async def test_lavka_tracker(
        taxi_logistic_platform_gateway,
        pgsql,
        stq,
        get_active_order_ids,
        tracked_order_ids,
        platform_order_ids,
        expected_stq_ids,
):
    get_active_order_ids.set_data('lavka', platform_order_ids)

    cursor = pgsql['logistic_platform_gateway'].cursor()
    cursor.execute(
        f"""
        INSERT INTO
            logistic_platform_gateway.tracked_orders
            (operator_id, cluster_id, external_order_id)
        SELECT
            'lavka',
            'main_cluster',
            UNNEST(%s::TEXT[])
        """,
        (tracked_order_ids,),
    )

    await taxi_logistic_platform_gateway.run_distlock_task(
        'lavka-main-tracker',
    )

    assert expected_stq_ids == [
        stq.logistic_platform_gateway_update_order_history_lavka_main_cluster.next_call()[  # noqa E501
            'id'
        ]
        for _ in range(
            stq.logistic_platform_gateway_update_order_history_lavka_main_cluster.times_called,  # noqa E501
        )
    ]
