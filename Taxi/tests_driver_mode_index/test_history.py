import copy
import datetime
import json
import random

import pytest

from tests_driver_mode_index import utils

MOCK_START = datetime.datetime(
    2016, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
MOCK_NOW = datetime.datetime(
    2016, 6, 13, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
MOCK_END = datetime.datetime(
    2016, 6, 27, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
MOCK_END_BEFORE_SUBSCRIPTION = datetime.datetime(
    2016, 6, 10, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
TIME_DELTA = datetime.timedelta(hours=1)


def _generate_subscription_data(pgsql, count: int):
    event_at = MOCK_NOW

    data = []

    for i in range(0, count):
        data.append(
            utils.TestData(
                'test_park_id',
                'test_driver_id',
                event_at,
                event_at,
                event_at,
                event_at,
                'ext_{}'.format(i + 1),
                'driver_fix',
                {'rule_id': 'some_id', 'shift_close_time': '00:00'},
                'not_used_billing_mode',
                'not_used_billing_mode_rule',
            ),
        )
        event_at = event_at + TIME_DELTA

    return [i for i in reversed(data)]


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'entries,limit,request_count', [(3, 1, 3), (3, 2, 2), (3, 3, 1)],
)
@pytest.mark.parametrize('revers', [True, False])
@pytest.mark.parametrize('random_order', [True, False])
@pytest.mark.parametrize('source', ['pg', 'bs'])
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_only_one_source_history(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        entries,
        limit,
        request_count,
        source,
        revers,
        random_order,
):
    if source == 'bs':
        if random_order:
            return

    data = _generate_subscription_data(pgsql, entries)

    if source == 'pg':
        tmp_data = copy.deepcopy(data)
        if random_order:
            random.shuffle(tmp_data)

        for data_entry in tmp_data:
            data_entry.add_to_pgsql(pgsql)

    if not revers:
        data = [i for i in reversed(data)]

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def v1_execute(request):
        if source == 'pg':
            if entries % limit != 0 or not revers:
                return {'docs': [], 'cursor': {}}

            return mockserver.make_response('fail', status=500)

        start_index = 1
        if 'cursor' in request.json:
            start_index = int(request.json['cursor']['offset'])
        end_index = min(start_index + int(request.json['limit']), entries + 1)

        expected_request = {
            'begin_time': MOCK_START.isoformat(),
            'end_time': MOCK_END.isoformat(),
            'external_obj_id': (
                'taxi/driver_mode_subscription/test_park_id/test_driver_id'
            ),
            'limit': limit,
            'sort': 'desc' if revers else 'asc',
        }

        assert all(
            item in request.json.items() for item in expected_request.items()
        )

        documents = []
        for i in range(start_index, end_index):
            documents.append(data[i - 1].as_billing_report_entry())

        return {'docs': documents, 'cursor': {'offset': end_index}}

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': limit,
        'sort': 'desc' if revers else 'asc',
    }

    event_at = MOCK_NOW
    time_delta = TIME_DELTA
    if revers:
        event_at = event_at + time_delta * entries
        time_delta = -time_delta
    else:
        event_at = event_at - time_delta

    for retry in range(1, request_count + 1):
        response = await taxi_driver_mode_index.post(
            'v1/mode/history', json=request,
        )

        assert response.status_code == 200
        response_json = response.json()
        docs = response_json['docs']

        if source == 'pg' or not revers:
            expected_docs = min(entries - (retry - 1) * limit, limit)
            event_at = event_at + time_delta * expected_docs

            if revers and entries % limit == 0:
                assert v1_execute.times_called == 0

            assert len(docs) == expected_docs
            for i, doc in enumerate(docs):
                assert doc == data[(retry - 1) * limit + i].as_history_entry()

            if source == 'pg':
                assert (
                    json.loads(response_json['cursor'])['index_cursor'][
                        'last_document_at'
                    ]
                    == event_at.isoformat()
                )

        else:  # source == 'bs' and revers
            assert v1_execute.times_called == 0
            expected_docs = retry == 1

            assert len(docs) == expected_docs

            if docs:
                fake_data = utils.TestData(
                    'test_park_id',
                    'test_driver_id',
                    MOCK_START,
                    MOCK_NOW,
                    MOCK_NOW,
                    MOCK_NOW,
                    'ext_ref',
                    'orders',
                    None,
                    'not_used_billing_mode',
                    'not_used_billing_mode_rule',
                ).as_history_entry()
                fake_data.pop('external_event_ref')
                fake_data['data'].pop('settings')
                doc = docs[0]
                doc.pop('external_event_ref')
                assert doc == fake_data

        request['cursor'] = response_json['cursor']


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'entries,pg_entries,limit,request_count',
    [(3, 1, 1, 3), (4, 2, 3, 2), (3, 1, 3, 1)],
)
@pytest.mark.parametrize('revers', [True, False])
@pytest.mark.parametrize('add_all_to_pg', [True, False])
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_mixed_history(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        entries,
        pg_entries,
        limit,
        request_count,
        revers,
        add_all_to_pg,
):
    if revers and add_all_to_pg:
        return

    data = _generate_subscription_data(pgsql, entries)

    for i in range(0, entries if add_all_to_pg else pg_entries):
        data[i].add_to_pgsql(pgsql)

    if not revers:
        data = [i for i in reversed(data)]

    returned_docs = []

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _v1_execute(request):
        documents = []

        begin_time = MOCK_START
        end_time = MOCK_END
        begin_time_str = begin_time.isoformat()
        end_time_str = end_time.isoformat()
        if revers:
            end_time = MOCK_NOW + TIME_DELTA * (entries - pg_entries)
            end_time_str = end_time.isoformat()

        expected_request = {
            'begin_time': begin_time_str,
            'end_time': end_time_str,
            'external_obj_id': (
                'taxi/driver_mode_subscription/test_park_id/test_driver_id'
            ),
            'sort': 'desc' if revers else 'asc',
        }

        assert all(
            item in request.json.items() for item in expected_request.items()
        )

        start_index = 0
        if revers:
            start_index = pg_entries

        if 'cursor' in request.json:
            start_index = int(request.json['cursor']['offset'])
        end_index = min(start_index + int(request.json['limit']), entries)
        for i in range(start_index, end_index):
            documents.append(data[i].as_billing_report_entry())

        return {'docs': documents, 'cursor': {'offset': end_index}}

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': limit,
        'sort': 'desc' if revers else 'asc',
    }

    event_at = MOCK_NOW
    time_delta = TIME_DELTA
    if revers:
        event_at = event_at + time_delta * (entries - 1)
        time_delta = -time_delta

    for retry in range(1, request_count + 1):
        expected_docs = min(entries - (retry - 1) * limit, limit)
        event_at = event_at + time_delta * expected_docs

        response = await taxi_driver_mode_index.post(
            'v1/mode/history', json=request,
        )

        assert response.status_code == 200
        response_json = response.json()

        docs = response_json['docs']
        assert len(docs) == expected_docs
        for i, doc in enumerate(docs):
            returned_docs.append(doc)
            assert doc == data[(retry - 1) * limit + i].as_history_entry()

        request['cursor'] = response_json['cursor']
        event_at = event_at + time_delta

    assert returned_docs == [i.as_history_entry() for i in data]


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_overlapping_history(mockserver, taxi_driver_mode_index, pgsql):
    data = _generate_subscription_data(pgsql, 4)

    for i in range(0, 2):
        data[i].add_to_pgsql(pgsql)

    data = [i for i in reversed(data)]

    returned_docs = []

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _v1_execute(request):
        documents = []

        start_index = 0
        if 'cursor' in request.json:
            start_index = int(request.json['cursor']['offset'])

        if start_index < 3:
            documents.append(data[start_index].as_billing_report_entry())

        result = {'docs': documents, 'cursor': {'offset': (start_index + 1)}}
        return result

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 1,
        'sort': 'asc',
    }

    for _ in range(0, 4):
        response = await taxi_driver_mode_index.post(
            'v1/mode/history', json=request,
        )

        assert response.status_code == 200
        response_json = response.json()
        request['cursor'] = response_json['cursor']

        docs = response_json['docs']
        for i, doc in enumerate(docs):
            returned_docs.append(doc)

    assert returned_docs == [i.as_history_entry() for i in data]


@pytest.mark.parametrize(
    'use_old_billing_format, expected_work_mode',
    [
        pytest.param(False, 'driver_fix', id='normal'),
        pytest.param(True, 'fallback_billing_mode', id='fallback'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_history_fallback_to_billing_mode(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        use_old_billing_format: bool,
        expected_work_mode: str,
):
    data = utils.TestData(
        'test_park_id',
        'test_driver_id',
        MOCK_NOW,
        MOCK_NOW,
        MOCK_NOW,
        MOCK_NOW,
        'some_external_ref',
        'driver_fix',
        {'rule_id': 'some_id', 'shift_close_time': '00:00'},
        'fallback_billing_mode',
        'not_used_billing_mode_rule',
    )

    data_expected = copy.deepcopy(data)
    data_expected.work_mode = expected_work_mode

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def v1_docs_select(request):
        documents = []

        documents.append(data.as_billing_report_entry(use_old_billing_format))

        return {'docs': documents, 'cursor': {'offset': 0}}

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 1,
        'sort': 'asc',
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/history', json=request,
    )

    assert v1_docs_select.times_called == 1

    assert response.status_code == 200
    response_json = response.json()
    docs = response_json['docs']

    assert len(docs) == 1
    assert docs[0] == data_expected.as_history_entry()


@pytest.mark.parametrize(
    'billing_settings,billing_extra_settings,expected_settings',
    [
        (
            # billing_settings
            {'rule_id': 'some_id', 'shift_close_time': '00:00'},
            # billing_extra_settings
            {'extra_key': 'extra_value'},
            # expected_settings
            {
                'rule_id': 'some_id',
                'shift_close_time': '00:00',
                'extra_key': 'extra_value',
            },
        ),
        (
            # billing_settings
            {'rule_id': 'true_rule_id', 'shift_close_time': '00:15'},
            # billing_extra_settings
            {'rule_id': 'extra_rule_id', 'shift_close_time': '00:30'},
            # expected_settings
            {'rule_id': 'true_rule_id', 'shift_close_time': '00:15'},
        ),
        (
            # billing_settings
            {'rule_id': 'mock_rule_id', 'shift_close_time': '00:00'},
            # billing_extra_settings
            {'brand_new': 'setting'},
            # expected_settings
            {
                'rule_id': 'mock_rule_id',
                'brand_new': 'setting',
                'shift_close_time': '00:00',
            },
        ),
        (
            # billing_settings
            None,
            # billing_extra_settings
            {'brand_new': 'setting'},
            # expected_settings
            {'brand_new': 'setting'},
        ),
        (
            # billing_settings
            {'rule_id': 'mock_rule_id', 'shift_close_time': '00:00'},
            # billing_extra_settings
            None,
            # expected_settings
            {'rule_id': 'mock_rule_id', 'shift_close_time': '00:00'},
        ),
        (
            # billing_settings
            None,
            # billing_extra_settings
            None,
            # expected_settings
            None,
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
async def test_extra_settings(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        billing_settings,
        billing_extra_settings,
        expected_settings,
):
    doc_in_db = utils.TestData(
        park_id='test_park_id',
        driver_id='test_driver_id',
        event_at=MOCK_NOW,
        updated_at=MOCK_NOW,
        created_at=MOCK_NOW,
        billing_synced_at=MOCK_NOW,
        external_ref='ext_0',
        work_mode='driver_trix',
        settings=expected_settings,
        billing_mode='some_billing_mode',
        billing_mode_rule='some_billing_mode_rule',
    )
    doc_in_db.add_to_pgsql(pgsql)

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _docs_select(request):
        doc_from_br = {
            'doc_id': 1,
            'kind': 'driver_mode_subscription',
            'external_obj_id': 'taxi/driver_mode_subscription/park_id_0/uuid',
            'external_event_ref': 'some_external_ref',
            'event_at': '2016-06-13T12:00:00+0000',
            'process_at': '2016-06-13T12:00:00+0000',
            'service': 'test',
            'service_user_id': 'some_id',
            'data': {
                'driver': {
                    'park_id': 'test_park_id',
                    'driver_id': 'test_driver_id',
                },
                'mode': 'fallback_billing_mode',
                'settings': billing_settings,
                'subscription': {
                    'driver_mode': 'driver_fix',
                    'extra_settings': billing_extra_settings,
                },
            },
            'created': '2016-06-13T12:00:00+0000',
            'status': 'complete',
            'tags': ['test_tag'],
        }
        if billing_settings is None:
            del doc_from_br['data']['settings']
        if billing_extra_settings is None:
            del doc_from_br['data']['subscription']['extra_settings']
        return {'docs': [doc_from_br], 'cursor': {}}

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 100,
        'sort': 'desc',
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/history', json=request,
    )

    assert response.status_code == 200
    response_json = response.json()

    docs = response_json['docs']
    assert len(docs) == 2
    for i, doc in enumerate(docs):
        if expected_settings is None:
            assert 'settings' not in doc['data']
        else:
            assert (
                doc['data']['settings'] == expected_settings
            ), 'Unexpected settings in doc {}'.format(i)


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.config(DRIVER_MODE_INDEX_USE_BILLING_ONLY_WHEN_NEEDED=True)
@pytest.mark.parametrize(
    'pg_entries, sort_mode, expected_calls',
    [(0, 'desc', 0), (0, 'asc', 1), (1, 'desc', 1)],
)
async def test_not_going_to_billing_if_pg_is_empty(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        pg_entries,
        sort_mode,
        expected_calls,
):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _v1_execute(request):
        _v1_execute.calls += 1
        return {'docs': [], 'cursor': {'offset': ''}}

    _v1_execute.calls = 0

    if pg_entries:
        data = _generate_subscription_data(pgsql, pg_entries)
        for data_entry in data:
            data_entry.add_to_pgsql(pgsql)

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 10,
        'sort': sort_mode,
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/history', json=request,
    )

    assert response.status_code == 200

    assert _v1_execute.calls == expected_calls


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.config(DRIVER_MODE_INDEX_USE_BILLING_ONLY_WHEN_NEEDED=True)
async def test_efficiencydev_14517_bugfix(
        mockserver, taxi_driver_mode_index, pgsql,
):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _v1_execute(request):
        _v1_execute.calls += 1

        doc_from_br = {
            'doc_id': 1,
            'kind': 'driver_mode_subscription',
            'external_obj_id': 'taxi/driver_mode_subscription/park_id_0/uuid',
            'external_event_ref': 'some_external_ref',
            'event_at': '2016-06-13T12:00:00+0000',
            'process_at': '2016-06-13T12:00:00+0000',
            'service': 'test',
            'service_user_id': 'some_id',
            'data': {
                'driver': {
                    'park_id': 'test_park_id',
                    'driver_id': 'test_driver_id',
                },
                'mode': 'fallback_billing_mode',
                'settings': {
                    'rule_id': 'mock_rule_id',
                    'shift_close_time': '00:00',
                },
                'subscription': {'driver_mode': 'driver_fix'},
            },
            'created': '2016-06-13T12:00:00+0000',
            'status': 'complete',
            'tags': ['test_tag'],
        }

        return {'docs': [doc_from_br], 'cursor': {}}

    _v1_execute.calls = 0

    data = _generate_subscription_data(pgsql, 1)
    for data_entry in data:
        data_entry.add_to_pgsql(pgsql)

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END_BEFORE_SUBSCRIPTION.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 10,
        'sort': 'desc',
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/history', json=request,
    )

    assert response.status_code == 200

    assert _v1_execute.calls == 1

    response_json = response.json()

    docs = response_json['docs']
    assert len(docs) == 1
    for doc in docs:
        settings = doc['data']['settings']
        assert settings['rule_id'] == 'mock_rule_id'


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(),
    DRIVER_MODE_INDEX_ENABLE_SOURCE_REASON_EXTRACTING=True,
)
@pytest.mark.parametrize(
    'reason,source,expected_subscription_data',
    [
        (
            'mock_reason',
            'mock_source',
            {'source': 'mock_source', 'reason': 'mock_reason'},
        ),
        ('mock_reason', None, None),
        (None, 'mock_source', None),
        (None, None, None),
    ],
)
async def test_source_and_reason(
        mockserver,
        taxi_driver_mode_index,
        pgsql,
        reason,
        source,
        expected_subscription_data,
):
    doc_in_db = utils.TestData(
        park_id='test_park_id',
        driver_id='test_driver_id',
        event_at=MOCK_NOW,
        updated_at=MOCK_NOW,
        created_at=MOCK_NOW,
        billing_synced_at=MOCK_NOW,
        external_ref='ext_0',
        work_mode='driver_trix',
        settings={'rule_id': 'mock_rule_id', 'shift_close_time': '00:00'},
        billing_mode='some_billing_mode',
        billing_mode_rule='some_billing_mode_rule',
        source=source,
        reason=reason,
    )
    doc_in_db.add_to_pgsql(pgsql)

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _docs_select(request):
        doc_from_br = {
            'doc_id': 1,
            'kind': 'driver_mode_subscription',
            'external_obj_id': 'taxi/driver_mode_subscription/park_id_0/uuid',
            'external_event_ref': 'some_external_ref',
            'event_at': '2016-06-13T12:00:00+0000',
            'process_at': '2016-06-13T12:00:00+0000',
            'service': 'test',
            'service_user_id': 'some_id',
            'data': {
                'driver': {
                    'park_id': 'test_park_id',
                    'driver_id': 'test_driver_id',
                },
                'mode': 'fallback_billing_mode',
                'settings': {
                    'rule_id': 'mock_rule_id',
                    'shift_close_time': '00:00',
                },
                'subscription': {'driver_mode': 'driver_fix'},
            },
            'created': '2016-06-13T12:00:00+0000',
            'status': 'complete',
            'tags': ['test_tag'],
        }
        if source is not None:
            doc_from_br['data']['subscription']['source'] = source
        if reason is not None:
            doc_from_br['data']['subscription']['reason'] = reason
        return {'docs': [doc_from_br], 'cursor': {}}

    request = {
        'driver': {
            'park_id': 'test_park_id',
            'driver_profile_id': 'test_driver_id',
        },
        'begin_at': MOCK_START.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'end_at': MOCK_END.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'external_ref': 'test_external_ref',
        'limit': 100,
        'sort': 'desc',
    }

    response = await taxi_driver_mode_index.post(
        'v1/mode/history', json=request,
    )

    assert response.status_code == 200
    response_json = response.json()

    docs = response_json['docs']
    assert len(docs) == 2
    for i, doc in enumerate(docs):
        assert (
            doc['data'].get('subscription_data', None)
            == expected_subscription_data
        ), 'In doc #{}'.format(i)
