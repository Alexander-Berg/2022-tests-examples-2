import copy
import datetime
import json
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_index import utils

TIME_MIN = datetime.datetime.min

MOCK_NOW = datetime.datetime(2016, 5, 1, 9, 0, 0, tzinfo=datetime.timezone.utc)

MOCK_START = datetime.datetime(
    2016, 5, 1, 0, 0, 0, tzinfo=datetime.timezone.utc,
)

MOCK_EVENT_AT = datetime.datetime(
    2016, 5, 1, 12, 0, 0, tzinfo=datetime.timezone.utc,
)

MOCK_END = datetime.datetime(2016, 5, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)

MOCK_EVENT_AT2 = datetime.datetime(
    2016, 5, 5, 12, 0, 0, tzinfo=datetime.timezone.utc,
)


def _validate_billing_request(
        request,
        billing_mode: str,
        park_id: str,
        driver_profile_id: str,
        settings: Optional[str],
        event_at: datetime.datetime,
        billing_mode_rule: str,
        subscription: Dict[str, str],
):
    expected: Dict = {
        'data': {
            'driver': {'driver_id': driver_profile_id, 'park_id': park_id},
            'mode': billing_mode,
            'subscription': subscription,
            'mode_rule': billing_mode_rule,
        },
        'event_at': event_at.isoformat(),
        'external_ref': 'test_external_ref',
        'kind': 'driver_mode_subscription',
    }
    if settings is not None:
        expected['data']['settings'] = settings

    assert request == expected


@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.parametrize(
    'fail_bo, driver_mode, event_at, '
    'expected_billing_mode, expected_billing_mode_rule, '
    'expected_subscription, source, reason',
    [
        pytest.param(
            False,
            'uberdriver',
            MOCK_EVENT_AT,
            'uberdriver_mode',
            'uberdriver_mode_rule',
            {'driver_mode': 'uberdriver'},
            None,
            None,
            id='uberdriver billing ok',
        ),
        pytest.param(
            True,
            'driver_fix',
            MOCK_EVENT_AT,
            'driver_fix_mode',
            'driver_fix_mode_rule',
            {'driver_mode': 'driver_fix'},
            None,
            None,
            id='driver_fix billing fail',
        ),
        pytest.param(
            False,
            'uberdriver',
            MOCK_EVENT_AT,
            'uberdriver_mode',
            'uberdriver_mode_rule',
            {'driver_mode': 'uberdriver', 'reason': 'rzn', 'source': 'src'},
            'src',
            'rzn',
            id='uberdriver w/ source billing ok',
        ),
    ],
)
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_subscribe(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        taxi_config,
        driver_mode: str,
        event_at,
        expected_billing_mode: str,
        expected_billing_mode_rule: str,
        source,
        reason,
        expected_subscription: Dict[str, str],
        fail_bo: bool,
):
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        None if fail_bo else MOCK_NOW,
        'test_external_ref',
        driver_mode,
        {'rule_id': 'test_rule_id'},
        expected_billing_mode,
        expected_billing_mode_rule,
        True,
        source,
        reason,
    )

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        _validate_billing_request(
            request.json,
            expected_billing_mode,
            'test_park_id',
            'test_driver_id',
            {'rule_id': 'test_rule_id'},
            event_at,
            expected_billing_mode_rule,
            expected_subscription,
        )

        if fail_bo:
            return mockserver.make_response('fail', status=500)

        return data.as_billing_orders_response()

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    assert v1_execute.times_called >= 1
    assert response.json() == data.as_mode_subscribe_response()

    db = utils.validate_items_count_in_db(1, pgsql)

    assert db[0] == data.as_db_row(include_billing=True)

    response = await taxi_driver_mode_index.post(
        'v1/mode/history',
        json={
            'driver': {
                'park_id': 'test_park_id',
                'driver_profile_id': 'test_driver_id',
            },
            'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'external_ref': 'test_external_ref',
            'limit': 1,
            'sort': 'desc',
        },
    )
    assert response.status_code == 200
    assert response.json()['docs'] == [data.as_history_entry()]


@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_subscribe_same_ext_ref(
        mockserver, taxi_driver_mode_index, pgsql,
):
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_EVENT_AT,
        MOCK_NOW,
        MOCK_EVENT_AT,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        {'rule_id': 'test_rule_id'},
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    data_same_ext = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_EVENT_AT2,
        MOCK_NOW,
        MOCK_EVENT_AT2,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        {'rule_id': 'test_rule_id'},
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        _validate_billing_request(
            request.json,
            'driver_fix_mode',
            'test_park_id',
            'test_driver_id',
            {'rule_id': 'test_rule_id'},
            MOCK_EVENT_AT,
            'driver_fix_mode_rule',
            {'driver_mode': 'driver_fix'},
        )

        return data.as_billing_orders_response()

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    assert v1_execute.times_called == 1
    assert response.json() == data.as_mode_subscribe_response()

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0] == data.as_db_row(include_billing=True)

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data_same_ext.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    assert response.json() == data.as_mode_subscribe_response()
    assert v1_execute.times_called == 1

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0] == data.as_db_row(include_billing=True)


@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
)
async def test_subscribe_disabled_bo_sync(
        mockserver, taxi_driver_mode_index, pgsql,
):
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_EVENT_AT,
        MOCK_NOW,
        MOCK_EVENT_AT,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        {'rule_id': 'test_rule_id'},
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        _validate_billing_request(
            request.json,
            'driver_fix_mode',
            'test_park_id',
            'test_driver_id',
            {'rule_id': 'test_rule_id'},
            MOCK_EVENT_AT,
            'driver_fix_mode_rule',
            {'driver_mode': 'driver_fix'},
        )
        return mockserver.make_response('fail', status=500)

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    assert v1_execute.times_called == 0
    assert response.json() == data.as_mode_subscribe_response()

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0] == data.as_db_row(not_yet_synced=True, include_billing=True)


@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.suspend_periodic_tasks('billing-sync-job')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        billing_sync_enabled=True,
        billing_sync_job={'enabled': True, 'batch_size': 100},
    ),
)
@pytest.mark.parametrize(
    'billing_mode, billing_mode_rule, expected_subscription',
    [
        pytest.param(
            'driver_fix',
            'driver_fix',
            {'driver_mode': 'driver_fix'},
            id='new billing api',
        ),
    ],
)
async def test_subscribe_with_job(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        mocked_time,
        taxi_config,
        expected_subscription: Dict[str, str],
        billing_mode: str,
        billing_mode_rule: str,
):
    _driver_mode = 'driver_fix'
    syned_at = datetime.datetime(2019, 5, 1, 10, 0, 0)
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_EVENT_AT,
        MOCK_NOW,
        MOCK_EVENT_AT,
        syned_at,
        'test_external_ref',
        _driver_mode,
        {'rule_id': 'test_rule_id'},
        billing_mode,
        billing_mode_rule,
    )

    fail_bo = True

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        _validate_billing_request(
            request.json,
            billing_mode,
            'test_park_id',
            'test_driver_id',
            {'rule_id': 'test_rule_id'},
            MOCK_EVENT_AT,
            billing_mode_rule,
            expected_subscription,
        )
        if fail_bo:
            return mockserver.make_response('fail', status=500)

        return data.as_billing_orders_response()

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    failed_bo_requests = v1_execute.times_called
    assert v1_execute.times_called >= 1
    assert response.json() == data.as_mode_subscribe_response()

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0] == data.as_db_row(not_yet_synced=True, include_billing=True)

    mocked_time.set(syned_at)
    data.updated_at = syned_at
    fail_bo = False
    await taxi_driver_mode_index.run_periodic_task('billing-sync-job')
    assert (failed_bo_requests + 1) == v1_execute.times_called

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0] == data.as_db_row(include_billing=True)


@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.parametrize(
    'ext_ref1, ext_ref2', (('ext_ref', 'ext_ref'), ('ext_ref1', 'ext_ref2')),
)
@pytest.mark.parametrize(
    'time2',
    (
        MOCK_NOW,
        MOCK_NOW + datetime.timedelta(seconds=1),
        MOCK_NOW - datetime.timedelta(seconds=1),
    ),
)
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_is_active(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        taxi_config,
        ext_ref1: str,
        ext_ref2: str,
        time2: datetime.datetime,
):
    current_data = None

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        return current_data.as_billing_orders_response()

    async def _set_mode(time, external_ref):
        nonlocal current_data
        data = utils.TestData(
            'test_park_id',
            'test_driver_id',
            time,
            MOCK_NOW,
            MOCK_NOW,
            MOCK_NOW,
            external_ref,
            'driver_fix',
            {'rule_id': 'test_rule_id'},
            billing_mode='driver_fix',
            billing_mode_rule='not_used',
        )

        current_data = data
        response = await taxi_driver_mode_index.post(
            'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
        )

        assert v1_execute.times_called >= 1
        return data, response

    time1 = MOCK_NOW
    data1, response = await _set_mode(time1, ext_ref1)
    assert response.status_code == 200
    assert response.json() == data1.as_mode_subscribe_response()

    db1 = utils.validate_items_count_in_db(1, pgsql)

    assert db1[0] == data1.as_db_row(include_billing=True)

    data2, response = await _set_mode(time2, ext_ref2)

    if time2 == time1 and ext_ref2 != ext_ref1:
        assert response.status_code == 500
        return

    assert response.status_code == 200

    if ext_ref1 == ext_ref2:
        assert response.json() == data1.as_mode_subscribe_response()
        db2 = utils.validate_items_count_in_db(1, pgsql)
        assert db2 == db1
        return

    assert response.json() == data2.as_mode_subscribe_response()
    db2 = utils.validate_items_count_in_db(2, pgsql)

    if time2 > time1:
        data1.is_active = False
    else:
        data2.is_active = False

    assert db2[0] == data1.as_db_row(include_billing=True)
    assert db2[1] == data2.as_db_row(include_billing=True)


def _check_request(data, v1_docs_select):
    expected_request = {
        'begin_time': data.event_at.isoformat(),
        'end_time': (MOCK_NOW + datetime.timedelta(seconds=10)).isoformat(),
        'external_obj_id': (
            'taxi/driver_mode_subscription/test_park_id/test_driver_id'
        ),
        'sort': 'desc',
        'limit': 1,
    }

    request = v1_docs_select.next_call()['request'].json
    assert all(item in request for item in expected_request)


DRIVER_FIX_SETTINGS = {
    'rule_id': 'subvention_rule_id',
    'shift_close_time': '00:00:00+03:00',
}


@pytest.mark.parametrize(
    'billing_has_more_recent_subscription, expected_result, driver_exists',
    [
        pytest.param(True, 200, True, id='billing is not used driver exists'),
        pytest.param(
            True, 200, False, id='billing is not used driver not exists',
        ),
    ],
)
@pytest.mark.now('2016-05-01T9:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
    DRIVER_MODE_INDEX_CHECK_SUBSCRIPTION_TIME_V2={
        'enabled': True,
        'future_threshold_seconds': 10,
    },
)
async def test_subscription_time_check_subscription(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        taxi_config,
        billing_has_more_recent_subscription,
        expected_result,
        driver_exists,
):
    event_at = MOCK_NOW + datetime.timedelta(seconds=5)

    if driver_exists:
        old_time = MOCK_NOW - datetime.timedelta(days=1)
        utils.insert_values(
            pgsql,
            'test_park_id',
            'test_driver_id',
            'ext_ref',
            'orders',
            json.dumps(None),
            'orders_mode',
            'orders_mode_rule',
            old_time,
            '\'{}\''.format(old_time),
            old_time,
            True,
        )

    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        DRIVER_FIX_SETTINGS,
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == expected_result
    if expected_result == 200:
        assert response.json() == data.as_mode_subscribe_response()
    subscription_was_added_to_db = (expected_result == 200) + driver_exists
    utils.validate_items_count_in_db(subscription_was_added_to_db, pgsql)


@pytest.mark.now('2016-05-01T9:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
    DRIVER_MODE_INDEX_CHECK_SUBSCRIPTION_TIME_V2={
        'enabled': True,
        'future_threshold_seconds': 10,
    },
)
async def test_subscriptions_time_check_subscription_in_db(
        taxi_driver_mode_index, pgsql, mockserver,
):
    event_at = MOCK_NOW - datetime.timedelta(seconds=5)

    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        DRIVER_FIX_SETTINGS,
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    def add_subscription_to_db():
        data_to_add = copy.deepcopy(data)
        data_to_add.external_ref = 'other_external_ref'
        data_to_add.event_at += datetime.timedelta(seconds=1)
        data_to_add.add_to_pgsql(pgsql)

    add_subscription_to_db()
    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    expected_result = 400
    assert response.status_code == expected_result
    utils.validate_items_count_in_db(1, pgsql)


@pytest.mark.now('2016-05-01T9:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
    DRIVER_MODE_INDEX_CHECK_SUBSCRIPTION_TIME_V2={
        'enabled': True,
        'future_threshold_seconds': 10,
    },
)
async def test_forbid_subscriptions_from_future(taxi_driver_mode_index):
    event_at = MOCK_NOW + datetime.timedelta(seconds=11)
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        DRIVER_FIX_SETTINGS,
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('time_delta', (1, -1, 0))
@pytest.mark.now('2016-05-01T9:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
    DRIVER_MODE_INDEX_CHECK_SUBSCRIPTION_TIME_V2={
        'enabled': True,
        'future_threshold_seconds': 10,
    },
)
async def test_add_existed_subscription(
        taxi_driver_mode_index, pgsql, time_delta,
):
    event_at = MOCK_NOW - datetime.timedelta(seconds=5)

    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        DRIVER_FIX_SETTINGS,
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
    )

    data.add_to_pgsql(pgsql)

    data_other = utils.TestData(
        'test_park_id',
        'test_driver_id',
        event_at,
        MOCK_NOW,
        event_at,
        MOCK_NOW,
        'test_external_ref',
        'orders',
        {'test': 'value'},
        billing_mode='orders_mode',
        billing_mode_rule='orders_mode_rule',
    )
    if time_delta > 0:
        data_other.event_at += datetime.timedelta(seconds=time_delta)
    else:
        data_other.event_at -= datetime.timedelta(seconds=abs(time_delta))

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )

    assert response.status_code == 200
    assert response.json() == data.as_mode_subscribe_response()


@pytest.mark.parametrize(
    'properties, expected_properties',
    (
        (['time_based_subvention'], ['time_based_subvention']),
        (
            ['time_based_subvention', 'time_based_subvention'],
            ['time_based_subvention'],
        ),
        (None, None),
    ),
)
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(billing_sync_enabled=False),
)
async def test_subscribe_with_mode_properties(
        taxi_driver_mode_index, pgsql, properties, expected_properties,
):
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_EVENT_AT,
        MOCK_NOW,
        MOCK_EVENT_AT,
        MOCK_NOW,
        'test_external_ref',
        'driver_fix',
        {'rule_id': 'test_rule_id'},
        billing_mode='driver_fix_mode',
        billing_mode_rule='driver_fix_mode_rule',
        mode_properties=properties,
    )

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
    )
    assert response.status_code == 200

    db = utils.validate_items_count_in_db(1, pgsql)
    assert db[0][-1] == expected_properties

    if properties:
        utils.validate_properties_table_size(1, pgsql)

        data.work_mode = 'driver_fix_new'
        response = await taxi_driver_mode_index.post(
            'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
        )
        assert response.status_code == 200

        db = utils.validate_items_count_in_db(1, pgsql)
        assert db[0][-1] == expected_properties
        utils.validate_properties_table_size(1, pgsql)


LOGISTIC_MODE_SETTIGNS = {
    'slot_id': 'b1aca90a-360f-499c-87bc-53fa41e58470',
    'rule_version': 1,
}


@pytest.mark.parametrize('test_mode', ['sync_on_request', 'sync_from_db'])
@pytest.mark.parametrize(
    'settings,expected_billing_settings',
    [
        (LOGISTIC_MODE_SETTIGNS, None),
        (DRIVER_FIX_SETTINGS, DRIVER_FIX_SETTINGS),
    ],
)
@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        billing_sync_job={'enabled': True, 'batch_size': 100},
    ),
)
@pytest.mark.suspend_periodic_tasks('billing-sync-job')
async def test_dont_pass_bad_mode_settings_to_billing(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        test_mode,
        settings,
        expected_billing_settings,
):
    data = utils.TestData(
        park_id='test_park_id',
        driver_id='test_driver_id',
        event_at=MOCK_EVENT_AT,
        updated_at=MOCK_NOW,
        created_at=MOCK_EVENT_AT,
        billing_synced_at=None,
        external_ref='test_external_ref',
        work_mode='logistic_workshifts_auto',
        settings=settings,
        billing_mode='orders',
        billing_mode_rule='orders',
        is_active=True,
    )

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        _validate_billing_request(
            request=request.json,
            billing_mode='orders',
            park_id='test_park_id',
            driver_profile_id='test_driver_id',
            settings=expected_billing_settings,
            event_at=MOCK_EVENT_AT,
            billing_mode_rule='orders',
            subscription={'driver_mode': 'logistic_workshifts_auto'},
        )
        return data.as_billing_orders_response()

    if test_mode == 'sync_on_request':
        response = await taxi_driver_mode_index.post(
            'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
        )
        assert response.status_code == 200
        assert response.json() == data.as_mode_subscribe_response()
    else:
        data.add_to_pgsql(pgsql)
        await taxi_driver_mode_index.run_periodic_task('billing-sync-job')

    assert v1_execute.times_called >= 1


@pytest.mark.parametrize('test_mode', ['sync_on_request', 'sync_from_db'])
@pytest.mark.parametrize(
    'our_settings,bo_settings,bo_extra_settings',
    [
        (LOGISTIC_MODE_SETTIGNS, None, LOGISTIC_MODE_SETTIGNS),
        (DRIVER_FIX_SETTINGS, DRIVER_FIX_SETTINGS, None),
        (
            # our_settings
            {'shift_close_time': '00:00:00+03:00'},
            # bo_settings
            {'shift_close_time': '00:00:00+03:00'},
            # bo_extra_settings
            None,
        ),
        (
            # our_settings
            {'shift_close_time': '00:00:00+03:00', 'new_setting': 'new_value'},
            # bo_settings
            {'shift_close_time': '00:00:00+03:00'},
            # bo_extra_settings
            {'new_setting': 'new_value'},
        ),
    ],
)
@pytest.mark.now('2016-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        billing_sync_job={'enabled': True, 'batch_size': 100},
    ),
    DRIVER_MODE_INDEX_ALLOW_EXTRA_SETTINGS_IN_BILLING=True,
)
@pytest.mark.suspend_periodic_tasks('billing-sync-job')
async def test_pass_additional_settings_to_billing(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        test_mode,
        our_settings,
        bo_settings,
        bo_extra_settings,
):
    data = utils.TestData(
        park_id='test_park_id',
        driver_id='test_driver_id',
        event_at=MOCK_EVENT_AT,
        updated_at=MOCK_NOW,
        created_at=MOCK_EVENT_AT,
        billing_synced_at=None,
        external_ref='test_external_ref',
        work_mode='logistic_workshifts_auto',
        settings=our_settings,
        billing_mode='orders',
        billing_mode_rule='orders',
        is_active=True,
    )

    @mockserver.json_handler('/billing-orders/v1/execute')
    def v1_execute(request):
        expected_subscription = {'driver_mode': 'logistic_workshifts_auto'}
        if bo_extra_settings is not None:
            expected_subscription['extra_settings'] = bo_extra_settings

        _validate_billing_request(
            request=request.json,
            billing_mode='orders',
            park_id='test_park_id',
            driver_profile_id='test_driver_id',
            settings=bo_settings,
            event_at=MOCK_EVENT_AT,
            billing_mode_rule='orders',
            subscription=expected_subscription,
        )
        return data.as_billing_orders_response()

    if test_mode == 'sync_on_request':
        response = await taxi_driver_mode_index.post(
            'v1/mode/subscribe', json=data.as_mode_subscribe_request(),
        )
        assert response.status_code == 200
        assert response.json() == data.as_mode_subscribe_response()
    else:
        data.add_to_pgsql(pgsql)
        await taxi_driver_mode_index.run_periodic_task('billing-sync-job')

    assert v1_execute.times_called >= 1


async def test_bad_settings(taxi_driver_mode_index):
    data = {
        'event_at': '2016-05-01T12:00:00+00:00',
        'external_ref': 'test_external_ref',
        'data': {
            'driver': {
                'driver_profile_id': 'test_driver_id',
                'park_id': 'test_park_id',
            },
            'work_mode': 'logistic_workshifts_auto',
            'settings': {
                'shift_close_time': '00:01',  # wrong format
                'rule_id': 'mock_rule_id',
            },
            'billing_settings': {'mode': 'orders', 'mode_rule': 'orders'},
        },
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/subscribe', json=data,
    )
    assert response.status_code == 400
