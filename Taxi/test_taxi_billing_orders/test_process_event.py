import pytest

from taxi import discovery

from taxi_billing_orders import config as orders_config
from taxi_billing_orders.resource_classifiers import (
    process_event_classifier as res_cls,
)


@pytest.mark.parametrize(
    'request_data_path,expected_event_id',
    [
        ('order_completed.json', 1002),
        ('order_completed_enriched_for_subventions.json', 1002),
    ],
)
async def test_insert_event(
        request_data_path,
        expected_event_id,
        load_json,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'create' in url
        return response_mock(json={'doc_id': 1002, 'kind': json['kind']})

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(
            method, url, headers, json, **kwargs,
    ):
        assert 'process_doc' in url
        assert json['doc']['id'] == 1002
        return response_mock(json=json)

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'doc': {'id': expected_event_id}}


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_PROCESS_MANUAL_SUBVENTION_EVENT=True,
)
@pytest.mark.parametrize(
    'request_data_path, calc_calls, subv_calls',
    [
        ('order_paid.json', 1, 0),
        ('workshift_bought.json', 1, 0),
        ('taximeter_payment_with_order.json', 1, 0),
        ('taximeter_payment_wo_order.json', 1, 0),
        ('driver_geoarea_activity.json', 0, 1),
        ('manual_subvention.json', 0, 1),
        ('driver_referral_payment.json', 0, 1),
        ('b2b_trip_payment.json', 1, 0),
    ],
)
async def test_insert_doc(
        monkeypatch,
        request_data_path,
        calc_calls,
        subv_calls,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'create' in url
        return response_mock(json={'doc_id': 1002, 'kind': json['kind']})

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 200

    assert len(_patch_billing_docs_request.calls) == 1
    assert len(_patch_billing_calculators_request.calls) == calc_calls
    assert len(_patch_billing_subventions_request.calls) == subv_calls
    content = await response.json()
    assert content == {'doc': {'id': 1002}}


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_PROCESS_MANUAL_SUBVENTION_EVENT=True,
    BILLING_ORDERS_PROCESS_NG={'__default__': True},
)
@pytest.mark.parametrize(
    'request_data_path, docs_calls, stq_calls',
    [
        ('b2b_trip_payment.json', 1, 2),
        ('driver_geoarea_activity.json', 1, 2),
        ('driver_referral_payment.json', 1, 2),
        ('manual_subvention.json', 1, 2),
        ('order_completed.json', 1, 2),
        ('order_completed_enriched_for_subventions.json', 1, 2),
        ('order_completed_for_smart_subventions.json', 1, 2),
        ('order_paid.json', 1, 2),
        ('taximeter_payment_with_order.json', 1, 2),
        ('taximeter_payment_wo_order.json', 1, 2),
        ('workshift_bought.json', 1, 2),
    ],
)
async def test_insert_doc_ng(
        docs_calls,
        stq_calls,
        monkeypatch,
        request_data_path,
        load_json,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'create' in url
        return response_mock(json={'doc_id': 1002})

    @patch('taxi.stq.client.put')
    async def _patch_stq_client_put(*args, **kwargs):
        return

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 200

    assert len(_patch_billing_docs_request.calls) == docs_calls
    assert len(_patch_stq_client_put.calls) == stq_calls

    await _compare_resources(data, response)


async def _compare_resources(data, response):
    requested_resources = (
        res_cls.ProcessEventResourceClassifier.get_resources_from_query_params(
            data,
        )
    )
    spent_resources = await (
        res_cls.ProcessEventResourceClassifier().get_spent_resources(response)
    )

    def _sorted_res(resources):
        return sorted(resources, key=lambda res: res.name)

    assert _sorted_res(requested_resources) == _sorted_res(spent_resources)


@pytest.mark.parametrize('request_data_path', ['malformed_events.json'])
async def test_reject_malformed_events(
        request_data_path,
        load_json,
        patch,
        taxi_billing_orders_client,
        request_headers,
):
    data = load_json(request_data_path)
    for event in data:
        response = await taxi_billing_orders_client.post(
            '/v1/process_event', headers=request_headers, json=event,
        )
        assert response.status == 400


@pytest.mark.config(
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'request_data_path', ['malformed_driver_geoarea_activity.json'],
)
# pylint: disable=invalid-name
async def test_malformed_driver_geoarea_activity_is_stored(
        monkeypatch,
        request_data_path,
        load_json,
        taxi_billing_orders_client,
        patch_aiohttp_session,
        response_mock,
        request_headers,
):
    event = load_json(request_data_path)

    docs = []

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'create' in url
        nonlocal docs
        docs.append(json)
        return response_mock(json={'doc_id': 1002})

    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )
    assert response.status == 400
    assert len(docs) == 1
    assert 'validation_error' in docs[0]


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'request_data_path', ['taximeter_payment_with_absent_account.json'],
)
async def test_taximeter_payment_account_doesnt_exist(
        monkeypatch,
        request_data_path,
        load_json,
        taxi_billing_orders_client,
        mockserver,
        request_headers,
):
    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _handler_accounts_search(request):
        return mockserver.make_response(json=[])

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 400


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'request_data_path', ['taximeter_payment_wrong_amount.json'],
)
async def test_taximeter_wrong_amount(
        monkeypatch,
        request_data_path,
        load_json,
        taxi_billing_orders_client,
        request_headers,
):
    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 400


@pytest.mark.config(BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 1})
@pytest.mark.parametrize('request_data_path', ['workshift_bought.json'])
async def test_reject_old_event(
        monkeypatch,
        request_data_path,
        load_json,
        taxi_billing_orders_client,
        request_headers,
):
    """Checks filtering requests  by event_at parameter"""

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 400


@pytest.mark.parametrize('request_data_path', ['workshift_bought.json'])
async def test_approve_and_reject_old_event_with_kind(
        monkeypatch,
        request_data_path,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
):
    """
    Checks filtering requests by event_at parameter and logic of kind's limit
    select. Fails with small time gap and works fine with a big one.
    """

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 24, 'workshift_bought': 1},
    )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        return response_mock(json={'doc_id': 1002, 'kind': json['kind']})

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 400

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 24, 'workshift_bought': 10 ** 6},
    )

    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'request_data_path',
    [
        'b2b_trip_payment.json',
        'driver_geoarea_activity.json',
        'driver_referral_payment.json',
        'manual_subvention.json',
        'order_paid.json',
        'taximeter_payment_with_order.json',
        'taximeter_payment_wo_order.json',
        'workshift_bought.json',
    ],
)
async def test_validation_without_event_at(
        request_data_path,
        load_json,
        taxi_billing_orders_client,
        request_headers,
):
    """
    Checks that all decorators work in proper order and
    scheme for event validation without event_at attribute when it should be
    """

    data = load_json(request_data_path)
    del data['event_at']
    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=data,
    )
    assert response.status == 400


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_SEND_ACTIVITY_TO_TIME_EVENTS=True,
    BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES=['driver_fix'],
    TIME_EVENTS_MIGRATION_BY_ZONE={
        'driver_fix': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
    TIME_EVENTS_MIGRATION_BY_PARK={
        'driver_fix': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
)
@pytest.mark.parametrize(
    'request_data_path, expected_event_path, expected_token',
    [
        (
            'driver_geoarea_activity.json',
            'time_event.json',
            '32147a35d8b81b64e3a01699cc60729a',
        ),
    ],
)
# pylint: disable=invalid-name
async def test_driver_geoarea_activity_sent_to_time_events(
        monkeypatch,
        request_data_path,
        expected_event_path,
        expected_token,
        load_json,
        taxi_billing_orders_client,
        patch_aiohttp_session,
        response_mock,
        request_headers,
        _docs_patch_1002,
        _subventions_patch,
):
    event = load_json(request_data_path)
    expected_event = load_json(expected_event_path)

    pushed_events = []
    actual_token = None

    @patch_aiohttp_session(
        discovery.find_service('billing_time_events').url, 'POST',
    )
    def _patch_billing_time_events(method, url, headers, json, **kwargs):
        assert 'push' in url
        nonlocal actual_token
        actual_token = headers.get('X-Idempotency-Token')
        nonlocal pushed_events
        pushed_events.append(json)
        return response_mock(json={})

    response = await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )

    def _sorted_fields(event):
        for activity in event['activities']:
            activity['tags'].sort()
            activity['available_tariff_classes'].sort()
            activity['geoareas'].sort()
        return event

    assert response.status == 200
    assert [_sorted_fields(event) for event in pushed_events] == [
        expected_event,
    ]
    assert actual_token == expected_token


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_SEND_ACTIVITY_TO_TIME_EVENTS=True,
    BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES=['driver_fix'],
    TIME_EVENTS_MIGRATION_BY_ZONE={
        'driver_fix': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
    TIME_EVENTS_MIGRATION_BY_PARK={
        'driver_fix': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
)
@pytest.mark.parametrize(
    'rule_types, subv_call_rule_types, '
    'subventions_num_calls, time_events_num_calls, ',
    [
        # test rule_types
        ([], [], 1, 0),
        (['geo_booking'], ['geo_booking'], 1, 0),
        (['driver_fix'], [], 0, 1),
        (['geo_booking', 'driver_fix'], ['geo_booking'], 1, 1),
    ],
)
# pylint: disable=invalid-name
async def test_driver_geoarea_activity_dispatching_by_rule_type(
        rule_types,
        subv_call_rule_types,
        subventions_num_calls,
        time_events_num_calls,
        *,
        monkeypatch,
        load_json,
        taxi_billing_orders_client,
        request_headers,
        patch_aiohttp_session,
        response_mock,
        _docs_patch_1002,
        _time_events_patch,
):
    event = load_json('driver_geoarea_activity_dispatching.json')
    event['data']['rule_types'] = rule_types

    subventions_url = discovery.find_service('billing_subventions').url

    @patch_aiohttp_session(subventions_url, 'POST')
    def _subventions_patch(method, url, headers, json, **kwargs):
        assert json['data']['rule_types'] == subv_call_rule_types
        return response_mock(json=json)

    await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )
    assert len(_subventions_patch.calls) == subventions_num_calls
    assert len(_time_events_patch.calls) == time_events_num_calls


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_SEND_ACTIVITY_TO_TIME_EVENTS=True,
    BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES=['driver_fix'],
    TIME_EVENTS_MIGRATION_BY_ZONE={
        'driver_fix': {
            'enabled': {'kursk': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
)
@pytest.mark.parametrize(
    'geoareas, subventions_num_calls, time_events_num_calls',
    [(['moscow'], 1, 0), (['kursk'], 0, 1)],
)
# pylint: disable=invalid-name
async def test_driver_geoarea_activity_dispatching_by_zone(
        geoareas,
        subventions_num_calls,
        time_events_num_calls,
        *,
        monkeypatch,
        load_json,
        taxi_billing_orders_client,
        request_headers,
        _subventions_patch,
        _docs_patch_1002,
        _time_events_patch,
):
    event = load_json('driver_geoarea_activity_dispatching.json')
    for activity in event['data']['geoarea_activities']:
        activity['geoareas'] = geoareas

    await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )
    assert len(_subventions_patch.calls) == subventions_num_calls
    assert len(_time_events_patch.calls) == time_events_num_calls


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_SEND_ACTIVITY_TO_TIME_EVENTS=True,
    BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES=['driver_fix'],
    TIME_EVENTS_MIGRATION_BY_PARK={
        'driver_fix': {'enabled': {'2': [{'since': '1999-01-01T00:00:00'}]}},
    },
)
@pytest.mark.parametrize(
    'park, subventions_num_calls, time_events_num_calls',
    [('1', 1, 0), ('2', 0, 1)],
)
# pylint: disable=invalid-name
async def test_driver_geoarea_activity_dispatching_by_park(
        park,
        subventions_num_calls,
        time_events_num_calls,
        *,
        monkeypatch,
        load_json,
        taxi_billing_orders_client,
        request_headers,
        _subventions_patch,
        _docs_patch_1002,
        _time_events_patch,
):
    event = load_json('driver_geoarea_activity_dispatching.json')
    event['data']['driver_dbid'] = park

    await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )
    assert len(_subventions_patch.calls) == subventions_num_calls
    assert len(_time_events_patch.calls) == time_events_num_calls


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_PROCESS_DRIVER_GEOAREA_ACTIVITY_EVENT=True,
    BILLING_ORDERS_SEND_ACTIVITY_TO_TIME_EVENTS=True,
    TIME_EVENTS_MIGRATION_BY_PARK={
        'driver_fix': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
        'geo_booking': {
            'enabled': {'__default__': [{'since': '1999-01-01T00:00:00'}]},
        },
    },
)
@pytest.mark.parametrize(
    'supported_rule_types, test_rule_types, event_rule_types, '
    'subventions_num_calls, time_events_num_calls',
    # event rule is tested in time-events
    [
        (['driver_fix'], ['driver_fix'], ['driver_fix'], 1, 1),
        (
            ['driver_fix', 'geo_booking'],
            ['geo_booking'],
            ['geo_booking'],
            1,
            1,
        ),
        # event rule is fully supported by time-events
        (['driver_fix', 'geo_booking'], ['geo_booking'], ['driver_fix'], 0, 1),
        (
            ['driver_fix', 'geo_booking'],
            [],
            ['driver_fix', 'geo_booking'],
            0,
            1,
        ),
        # all rules are tested
        (
            ['driver_fix', 'geo_booking'],
            ['driver_fix', 'geo_booking'],
            ['driver_fix', 'geo_booking'],
            1,
            1,
        ),
    ],
)
# pylint: disable=invalid-name
async def test_driver_geoarea_activity_test_rules(
        supported_rule_types,
        test_rule_types,
        event_rule_types,
        subventions_num_calls,
        time_events_num_calls,
        *,
        monkeypatch,
        load_json,
        taxi_billing_orders_client,
        request_headers,
        _subventions_patch,
        _docs_patch_1002,
        _time_events_patch,
):
    def _patch_config(key, value):
        monkeypatch.setattr(orders_config.Config, key, value)

    _patch_config('BILLING_TIME_EVENTS_TEST_RULE_TYPES', test_rule_types)
    _patch_config(
        'BILLING_TIME_EVENTS_SUPPORTED_RULE_TYPES', supported_rule_types,
    )
    event = load_json('driver_geoarea_activity_dispatching.json')
    event['data']['rule_types'] = event_rule_types

    await taxi_billing_orders_client.post(
        '/v1/process_event', headers=request_headers, json=event,
    )
    assert len(_subventions_patch.calls) == subventions_num_calls
    assert len(_time_events_patch.calls) == time_events_num_calls


@pytest.fixture()
def _subventions_patch(patch_aiohttp_session, response_mock):
    subventions_url = discovery.find_service('billing_subventions').url

    @patch_aiohttp_session(subventions_url, 'POST')
    def _patch_subventions(method, url, headers, json, **kwargs):
        return response_mock(json=json)

    yield _patch_subventions


@pytest.fixture()
def _docs_patch_1002(patch_aiohttp_session, response_mock):
    docs_url = discovery.find_service('billing_docs').url

    @patch_aiohttp_session(docs_url, 'POST')
    def _patch_docs(method, url, headers, json, **kwargs):
        return response_mock(json={'doc_id': 1002, 'kind': json['kind']})

    yield _patch_docs


@pytest.fixture()
def _time_events_patch(patch_aiohttp_session, response_mock):
    time_events_url = discovery.find_service('billing_time_events').url

    @patch_aiohttp_session(time_events_url, 'POST')
    def _patch_time_events(method, url, headers, json, **kwargs):
        return response_mock(json={})

    yield _patch_time_events
