# pylint: disable=redefined-outer-name
import copy
import datetime

import bson
import pytest

TASK_KWARGS = {
    'order_id': 'order_id_1',
    'search_params': {'foo': {'bar': 'baz'}},
    'search_ts': '2020-01-01T00:00:00+00:00',
}

CANDIDATE = {
    'dbid': 'dbid1',
    'uuid': 'uuid1',
    'unique_driver_id': 'udid1',
    'is_satisfied': True,
    'car_number': 'A000AA00',
}


def get_settings(**override):
    return {
        'assign_driver_seconds': 60,
        'enable_defreeze': False,
        'new_way_enabled': True,
        'fail_on_reject': False,
        'old_way_fallback_enabled': False,
        **override,
    }


@pytest.fixture
def mock_order_satisfy(mockserver):
    context = {
        'expected_request': {
            'foo': 'bar',
            'order_id': 'order_id_1',
            'driver_ids': [{'dbid': 'dbid1', 'uuid': 'uuid1'}],
        },
        'candidate': copy.deepcopy(CANDIDATE),
    }

    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json == context['expected_request']
        return {'candidates': [context['candidate']]}

    context['handler'] = order_satisfy
    return context


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_set_search_params(
        stq_runner, create_order, get_order, mockserver,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_get_order_fields(request):
        assert request.json['order_id'] == 'order_id_1'
        return {
            'fields': {
                '_id': 'order_id_1',
                'order': {
                    'request': {
                        'source': {'short_text': 'улица Льва Толстого, 16'},
                    },
                },
            },
            'order_id': 'order_id_1',
            'replica': 'secondary',
            'version': 'any_string',
        }

    order = create_order(
        search_ts=None, search_params=None, order_id='order_id_1',
    )
    await stq_runner.manual_dispatch_set_search_params.call(
        task_id='task_1', kwargs=TASK_KWARGS,
    )
    assert (
        get_order(order['order_id'], projection=('search_ts', 'search_params'))
        == {
            'search_ts': datetime.datetime(
                2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'search_params': {'foo': {'bar': 'baz'}},
        }
    )


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_order_not_found(stq_runner, mockserver):
    # don't fail if no order: race is impossible, but this prevents forever
    # failing tasks
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def mock_get_order_fields(request):
        assert request.json['order_id'] == 'order_id_1'
        return {
            'fields': {
                '_id': 'order_id_1',
                'order': {
                    'request': {
                        'source': {'short_text': 'улица Льва Толстого, 16'},
                    },
                },
            },
            'order_id': 'order_id_1',
            'replica': 'secondary',
            'version': 'any_string',
        }

    await stq_runner.manual_dispatch_set_search_params.call(
        task_id='task_1', kwargs=TASK_KWARGS, expect_fail=False,
    )
    assert mock_get_order_fields.times_called == 0


@pytest.mark.parametrize(
    'original,expected',
    [
        (
            {
                'search_ts': datetime.datetime(
                    2020, 1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'search_params': {'notfoo': {}},
            },
            {
                'search_ts': datetime.datetime(
                    2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'search_params': {'notfoo': {}},
            },
        ),
        (
            {
                'search_ts': datetime.datetime(
                    2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc,
                ),
                'search_params': {'notfoo': {}},
            },
            {
                'search_ts': datetime.datetime(
                    2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc,
                ),
                'search_params': TASK_KWARGS['search_params'],
            },
        ),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_search_ts_race(
        stq_runner, create_order, get_order, original, expected, mockserver,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_get_order_fields(request):
        assert request.json['order_id'] == 'order_id_1'
        return {
            'fields': {
                '_id': 'order_id_1',
                'order': {
                    'request': {
                        'source': {'short_text': 'улица Льва Толстого, 16'},
                    },
                },
            },
            'order_id': 'order_id_1',
            'replica': 'secondary',
            'version': 'any_string',
        }

    order = create_order(**original, order_id='order_id_1')
    await stq_runner.manual_dispatch_set_search_params.call(
        task_id='task_1', kwargs=TASK_KWARGS,
    )
    assert (
        get_order(order['order_id'], projection=('search_ts', 'search_params'))
        == expected
    )


@pytest.mark.config(MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings())
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_mirror(taxi_manual_dispatch, stq, mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_get_order_fields(request):
        assert request.json['order_id'] == 'order_id_1'
        return {
            'fields': {
                '_id': 'order_id_1',
                'order': {
                    'request': {
                        'source': {'short_text': 'улица Льва Толстого, 16'},
                    },
                },
            },
            'order_id': 'order_id_1',
            'replica': 'secondary',
            'version': 'any_string',
        }

    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'doesntmatter'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert stq.manual_dispatch_set_search_params.times_called == 1
    call_args = stq.manual_dispatch_set_search_params.next_call()['kwargs']
    call_args.pop('log_extra')
    assert call_args == {
        'search_ts': '2020-01-01T00:00:00+00:00',
        'order_id': 'doesntmatter',
        'search_params': {'foo': 'bar', 'order_id': 'doesntmatter'},
    }


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(fail_on_reject=True),
)
@pytest.mark.parametrize(
    'history,should_reject',
    [
        (
            [
                {
                    'event_type': 'order',
                    'activity_value_change': -3,
                    'timestamp': '2020-01-01T00:00:00+00:00',
                    'order_id': 'order_id_1',
                    'id': 'foo',
                    'event_descriptor': {'type': 'reject_manual'},
                },
            ],
            True,
        ),
        ([], False),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_reject(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        mockserver,
        get_dispatch_attempt,
        stq,
        mock_order_satisfy,
        history,
        should_reject,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')

    @mockserver.json_handler('/driver-metrics-storage/v1/activity/history')
    def activity_history(request):
        if 'timestamp_from' in request.json:
            request.json['timestamp_from'] = datetime.datetime.strptime(
                request.json['timestamp_from'], '%Y-%m-%dT%H:%M:%S.%f%z',
            )
        assert request.json == {
            'order_ids': ['order_id_1'],
            'dbid_uuid': 'dbid1_uuid1',
            'udid': 'udid1',
            'timestamp_from': attempt['created_ts'],
        }
        return {'items': history}

    mock_order_satisfy['candidate']['is_satisfied'] = False
    mock_order_satisfy['candidate']['reasons'] = {'infra/driver_id': []}

    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    new_status = get_dispatch_attempt(attempt_id=attempt['id'])['status']
    assert mock_order_satisfy['handler'].times_called == 1
    assert activity_history.times_called == 1

    if should_reject:
        assert response.json() == {}
        assert new_status == 'declined'
        assert stq.manual_dispatch_update_attempt_info.times_called == 1
        call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()[
            'kwargs'
        ]
        del call_kwargs['log_extra']
        assert call_kwargs == {'attempt_id': attempt['id'], 'clear_only': True}
    else:
        mock_order_satisfy['candidate']['is_satisfied'] = True
        del mock_order_satisfy['candidate']['reasons']
        assert response.json() == {
            'candidate': mock_order_satisfy['candidate'],
        }
        assert new_status == 'pending'
        assert stq.manual_dispatch_update_attempt_info.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings())
@pytest.mark.parametrize(
    'with_fallback',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(
                        old_way_fallback_enabled=True,
                    ),
                ),
            ],
        ),
        pytest.param(False),
    ],
)
@pytest.mark.parametrize(
    'candidate_override',
    [
        {},
        {
            'is_satisfied': False,
            'reasons': {
                'corp/virtual_tariffs_classes': [],
                'product/cargo_limits': [],
            },
        },
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_satisfied(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        mock_order_satisfy,
        mockserver,
        get_dispatch_attempt,
        candidate_override,
        with_fallback,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        assert request.query['order_id'] == 'order_id_1'
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(
                {
                    'document': {
                        '_id': 'fa952069bc1560b2a37b6e7a364cc01a',
                        'manual_dispatch': {},
                    },
                    'order_id': 'fa952069bc1560b2a37b6e7a364cc01a',
                    'replica': 'secondary',
                    'revision': {
                        'version': 'DAAAAAAABgAMAAQABgAAAPFHWMZzAQAA',
                    },
                },
            ),
        )

    satisfied_candidate = copy.deepcopy(mock_order_satisfy['candidate'])
    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {'candidate': satisfied_candidate}

    assert _get_order_fields.times_called == with_fallback
    new_status = get_dispatch_attempt(attempt_id=attempt['id'])['status']
    assert new_status == 'pending'


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_filtered(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        stq,
        get_dispatch_attempt,
        mock_order_satisfy,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')
    mock_order_satisfy['candidate'].update(
        {'is_satisfied': False, 'reasons': {'infra/grade': []}},
    )
    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert mock_order_satisfy['handler'].times_called == 1
    assert stq.manual_dispatch_update_attempt_info.times_called == 1
    call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()['kwargs']
    del call_kwargs['log_extra']
    assert call_kwargs == {'attempt_id': attempt['id'], 'clear_only': True}
    assert get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status', 'message'),
    ) == {'status': 'filtered', 'message': 'infra/grade'}


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
@pytest.mark.now('2020-01-01T01:00:00+00:00')
async def test_expired(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        get_dispatch_attempt,
        stq,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(
        order_id='order_id_1', expiration_ts='2020-01-01T00:00:00+00:00',
    )
    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert stq.manual_dispatch_update_attempt_info.times_called == 1
    call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()['kwargs']
    del call_kwargs['log_extra']
    assert call_kwargs == {'attempt_id': attempt['id'], 'clear_only': True}
    assert (
        get_dispatch_attempt(attempt_id=attempt['id'])['status'] == 'expired'
    )


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_delayed(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        get_dispatch_attempt,
        mock_order_satisfy,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')
    mock_order_satisfy['candidate'].update(
        {
            'is_satisfied': False,
            'reasons': {'infra/meta_status_searchable': []},
        },
    )

    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert mock_order_satisfy['handler'].times_called == 1
    assert (
        get_dispatch_attempt(attempt_id=attempt['id'])['status'] == 'pending'
    )


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(enable_defreeze=True),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_frozen(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        get_dispatch_attempt,
        mock_order_satisfy,
        mockserver,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')
    mock_order_satisfy['candidate'].update(
        {'is_satisfied': False, 'reasons': {'infra/frozen': []}},
    )

    @mockserver.json_handler('/driver-freeze/defreeze')
    def mock_defreeze(request):
        assert request.json == {
            'order_id': 'order_id_1',
            'unique_driver_id': 'udid1',
            'car_id': 'A000AA00',
        }
        return {}

    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert mock_defreeze.times_called == 1
    assert mock_order_satisfy['handler'].times_called == 1
    assert (
        get_dispatch_attempt(attempt_id=attempt['id'])['status'] == 'pending'
    )


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_driver_not_found(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        get_dispatch_attempt,
        mock_order_satisfy,
        stq,
):
    create_order(order_id='order_id_1')
    attempt = create_dispatch_attempt(order_id='order_id_1')
    del mock_order_satisfy['candidate']['car_number']
    del mock_order_satisfy['candidate']['unique_driver_id']
    mock_order_satisfy['candidate']['is_satisfied'] = False
    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert mock_order_satisfy['handler'].times_called == 1
    assert get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status', 'message'),
    ) == {'status': 'filtered', 'message': 'not_found'}
    assert stq.manual_dispatch_update_attempt_info.times_called == 1
    call_kwargs = stq.manual_dispatch_update_attempt_info.next_call()['kwargs']
    del call_kwargs['log_extra']
    assert call_kwargs == {'attempt_id': attempt['id'], 'clear_only': True}


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_eda_courier_ignore_payment_filter(
        taxi_manual_dispatch,
        create_order,
        create_dispatch_attempt,
        stq,
        get_dispatch_attempt,
        mock_order_satisfy,
        load_json,
):
    search_params = load_json('search_params.json')
    search_params['allowed_classes'] = ['courier', 'express', 'eda', 'lavka']
    create_order(order_id='order_id_1', search_params=search_params)

    attempt = create_dispatch_attempt(order_id='order_id_1')
    mock_order_satisfy['candidate'].update(
        {
            'is_satisfied': False,
            'reasons': {'infra/payment_method': []},
            'classes': ['eda', 'lavka'],
        },
    )

    response = await taxi_manual_dispatch.post(
        'v1/lookup', json={'foo': 'bar', 'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'candidate': {
            'car_number': 'A000AA00',
            'classes': ['eda', 'lavka'],
            'dbid': 'dbid1',
            'is_satisfied': True,
            'unique_driver_id': 'udid1',
            'uuid': 'uuid1',
        },
    }
    assert mock_order_satisfy['handler'].times_called == 1
    assert get_dispatch_attempt(
        attempt_id=attempt['id'], projection=('status', 'message'),
    ) == {'status': 'pending', 'message': None}


@pytest.mark.config(
    MANUAL_DISPATCH_FILTER_BY_ADDRESS_ENABLED=True,
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_set_address(
        stq_runner,
        create_order,
        get_order,
        mockserver,
        experiments3,
        headers,
        taxi_manual_dispatch,
        address='Проспект Вернадского, д.13',
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def mock_get_order_fields(request):
        assert request.json['order_id'] == 'order_id_1'
        return {
            'fields': {
                '_id': 'order_id_1',
                'order': {'request': {'source': {'short_text': address}}},
            },
            'order_id': 'order_id_1',
            'replica': 'secondary',
            'version': 'any_string',
        }

    create_order(search_ts=None, search_params=None, order_id='order_id_1')
    await stq_runner.manual_dispatch_set_search_params.call(
        task_id='task_1', kwargs=TASK_KWARGS,
    )
    assert mock_get_order_fields.times_called == 1
    response = await taxi_manual_dispatch.post(
        '/v1/orders/list',
        headers=headers,
        json={
            'meta': {'offset': 0, 'limit': 5},
            'filter': {'state': 'pending', 'address_shortname': address},
            'order': {'field': 'search_start_ts', 'sequence': 'asc'},
        },
    )
    assert response.status_code == 200
    assert [x['order_id'] for x in response.json()['orders']] == ['order_id_1']
    await stq_runner.manual_dispatch_set_search_params.call(
        task_id='task_1', kwargs=TASK_KWARGS,
    )

    assert mock_get_order_fields.times_called == 1
