import copy

import pytest


def get_all_notified_orders(db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT order_id, check_in_reminders_sent '
        'FROM dispatch_check_in.check_in_orders '
        'WHERE check_in_reminders_sent != 0;',
    )
    return sorted([r for r in cursor])


@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
@pytest.mark.config(
    DISPATCH_CHECK_IN_CHECK_IN_REMINDER={
        'enabled': True,
        'interval_seconds': 600,
    },
)
@pytest.mark.parametrize(
    ['exp3_enabled', 'user2_title', 'user3_title'],
    [
        pytest.param(
            True,
            'Не забудьте сделать чек-ин (дефолт клоз)',
            'Не забудьте сделать чек-ин (user_phone_id3 клоз)',
        ),
        pytest.param(
            False, 'Не забудьте сделать чек-ин', 'Не забудьте сделать чек-ин',
        ),
    ],
)
async def test_check_in_reminders(
        taxi_dispatch_check_in,
        pgsql,
        experiments3,
        load_json,
        mockserver,
        mocked_time,
        exp3_enabled,
        user2_title,
        user3_title,
):
    db = pgsql['dispatch_check_in']
    expected_json_user2 = {
        'client_id': 'some_user2',
        'intent': 'check_in_reminder',
        'notification': {
            'text': 'Нужно нажать кнопку "Я на месте"',
            'title': user2_title,
        },
        'service': 'go',
    }
    expected_json_user3 = copy.deepcopy(expected_json_user2)
    expected_json_user3['client_id'] = 'some_user3'
    expected_json_user3['notification']['title'] = user3_title

    @mockserver.handler('/client-notify/v2/push')
    async def mock_client_notify(request):
        if request.json['client_id'] == 'some_user2':
            assert request.json == expected_json_user2
        else:
            if request.json['client_id'] == 'some_user3':
                assert request.json == expected_json_user3
            else:
                assert False
        return mockserver.make_response(
            status=200,
            content_type='application/json',
            json={'notification_id': 'abc'},
        )

    if exp3_enabled:
        experiments3.add_experiments_json(
            load_json('other_static_resources_experiments.json'),
        )

    # three orders in db:
    # order_id1 - just created, check_in just happened
    # order_id2 - just created
    # order_id3 - same as order_id2, but have other user_phone_id

    # step1: no notifications
    await taxi_dispatch_check_in.run_task('distlock/order-checker')
    assert mock_client_notify.times_called == 0
    assert get_all_notified_orders(db) == []

    # step2: 5 minutes passes - still no notifications
    mocked_time.sleep(300)
    await taxi_dispatch_check_in.run_task('distlock/order-checker')
    assert mock_client_notify.times_called == 0
    assert get_all_notified_orders(db) == []

    # step3: more than 5 minutes passed - notification happens
    mocked_time.sleep(302)
    await taxi_dispatch_check_in.run_task('distlock/order-checker')
    assert mock_client_notify.times_called == 2
    assert get_all_notified_orders(db) == [('order_id2', 1), ('order_id3', 1)]

    # step3: notification should happen only once since cache update
    await taxi_dispatch_check_in.invalidate_caches()
    await taxi_dispatch_check_in.run_task('distlock/order-checker')
    assert mock_client_notify.times_called == 2
    assert get_all_notified_orders(db) == [('order_id2', 1), ('order_id3', 1)]

    await taxi_dispatch_check_in.invalidate_caches()
