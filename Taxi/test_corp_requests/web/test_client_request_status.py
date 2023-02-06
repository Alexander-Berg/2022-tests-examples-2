# pylint: disable=invalid-name

import datetime

import pytest

from corp_requests import consts

HEADERS = {'X-Yandex-UID': '666', 'AcceptLanguage': 'ru'}


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'fr'])
@pytest.mark.parametrize(
    ['request_id'],
    [
        pytest.param('92d0e2c87a0c4232ab13759b094ec638', id='russian offer'),
        pytest.param('95b3c932435f4f008a635faccb6454f6', id='israel offer'),
    ],
)
async def test_client_requests_status_accept(
        mockserver, db, taxi_corp_requests_web, territories_mock, request_id,
):
    expected_client_request = await db.corp_client_requests.find_one(
        {'_id': request_id},
    )
    # fix timestamps
    for field in ['created', 'updated', 'company_registration_date']:
        date = expected_client_request.pop(field, None)
        if not date:
            continue
        stamp = int(
            date.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000,
        )
        expected_client_request[field] = {'$date': stamp}
    # add geo fixture data
    expected_client_request['country_id'] = consts.COUNTRY_IDS_BY_NAMES[
        expected_client_request['country']
    ]

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue>\w+)', regex=True,
    )
    def _stq_agent_put_task(request, queue):
        assert request.method == 'POST'
        assert queue == 'corp_accept_client_request'
        kwargs = request.json['kwargs']
        assert request.json['task_id']
        assert request.json['args'] == []
        assert kwargs == dict(
            client_request=expected_client_request,
            status='accepted',
            operator_uid='666',
            x_remote_ip=None,
        )

    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/status/update',
        params={'request_id': request_id},
        json={'status': 'accepted'},
        headers=HEADERS,
    )

    assert response.status == 200

    response_dict = await response.json()
    assert response_dict.pop('task_id')
    assert response_dict == {'status': 'pending'}
    assert _stq_agent_put_task.has_calls


@pytest.mark.config(
    LOCALES_SUPPORTED=['ru', 'en', 'fr'],
    CORP_CLIENT_REQUEST_REJECTION_REASONS=['kek'],
    CORP_SEND_FORMAL_REASON_NOTICE=True,
)
@pytest.mark.parametrize(
    ['request_id'],
    [
        pytest.param('92d0e2c87a0c4232ab13759b094ec638', id='russian offer'),
        pytest.param('95b3c932435f4f008a635faccb6454f6', id='israel offer'),
    ],
)
async def test_client_requests_status_reject(
        mockserver, db, taxi_corp_requests_web, territories_mock, request_id,
):
    expected_client_request = await db.corp_client_requests.find_one(
        {'_id': request_id},
    )
    # fix timestamps
    for field in ['created', 'updated', 'company_registration_date']:
        date = expected_client_request.pop(field, None)
        if not date:
            continue
        stamp = int(
            date.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000,
        )
        expected_client_request[field] = {'$date': stamp}
    # add geo fixture data
    expected_client_request['country_id'] = consts.COUNTRY_IDS_BY_NAMES[
        expected_client_request['country']
    ]

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue>\w+)', regex=True,
    )
    def _stq_agent_put_task(request, queue):
        assert request.method == 'POST'
        assert queue == 'corp_notices_process_event'

    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/status/update',
        params={'request_id': request_id},
        json={'status': 'rejected', 'reason': 'kek', 'formal_reason': 'kek'},
        headers=HEADERS,
    )

    response_dict = await response.json()

    assert response.status == 200
    assert response_dict == {'status': 'rejected'}
    assert _stq_agent_put_task.has_calls
    while _stq_agent_put_task.times_called:
        stq_call = _stq_agent_put_task.next_call()
        kwargs = stq_call['request'].json['kwargs']
        assert kwargs == {
            'event_name': 'ClientRequestStatusChanged',
            'data': {
                'request_id': request_id,
                'old': {'status': 'pending'},
                'new': {'status': 'rejected', 'reject_reason': 'kek'},
            },
        }


@pytest.mark.parametrize(
    ['request_id', 'request_params', 'expected_result', 'status_code'],
    [
        pytest.param(
            'not_found_id',
            {'status': 'accepted'},
            {
                'message': 'client request not found',
                'code': 'client-request-not-found',
                'details': {},
            },
            404,
            id='not found',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {'status': 'accepted'},
            {
                'message': 'invalid status transition',
                'code': 'invalid-status-transition',
                'details': {},
            },
            409,
            id='invalid transition',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {'status': 'status'},
            {
                'message': 'Some parameters are invalid',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for status: \'status\''
                        ' must be one of [\'accepted\', \'rejected\']'
                    ),
                },
            },
            400,
            id='invalid status value',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {'status': 'rejected'},
            {
                'message': 'something went wrong with statuses or reasons',
                'code': 'validate-client-request-status-failed',
                'details': {
                    'fields': [
                        {
                            'field': 'reason',
                            'messages': [
                                'reason is required for rejected status',
                            ],
                        },
                        {
                            'field': 'formal_reason',
                            'messages': [
                                'formal_reason_should_match_with_config',
                            ],
                        },
                    ],
                },
            },
            400,
            id='wrong status, formal reason',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {'status': 'rejected', 'reason': 'kek', 'formal_reason': 'lol'},
            {
                'message': 'something went wrong with statuses or reasons',
                'code': 'validate-client-request-status-failed',
                'details': {
                    'fields': [
                        {
                            'field': 'formal_reason',
                            'messages': [
                                'formal_reason_should_match_with_config',
                            ],
                        },
                    ],
                },
            },
            400,
            id='wrong formal reason',
        ),
        pytest.param(
            'f4d44610f5894352817595f6311d95cc',
            {'somefield': 'somevalue'},
            {
                'message': 'Some parameters are invalid',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'Unexpected fields: [\'somefield\']'},
            },
            400,
            id='extra field',
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.invalid_status_transition': {
            'ru': 'Недействительный статус перехода',
        },
    },
)
@pytest.mark.config(
    CORP_CLIENT_REQUEST_REJECTION_REASONS=['kek'],
    CORP_SEND_FORMAL_REASON_NOTICE=True,
)
async def test_client_requests_status_fail(
        patch,
        taxi_corp_requests_web,
        territories_mock,
        request_id,
        request_params,
        expected_result,
        status_code,
):
    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/status/update',
        params={'request_id': request_id},
        json=request_params,
        headers=HEADERS,
    )

    assert response.status == status_code
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    'request_id, data',
    [('92d0e2c87a0c4232ab13759b094ec638', {'status': 'accepted'})],
)
async def test_client_request_status_accept_lock(
        db, taxi_corp_requests_web, territories_mock, request_id, data,
):
    assert 'locked' not in (
        await db.corp_client_requests.find_one({'_id': request_id})
    )

    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/status/update',
        params={'request_id': request_id},
        json=data,
        headers=HEADERS,
    )

    assert response.status == 200
    assert 'locked' in (
        await db.corp_client_requests.find_one({'_id': request_id})
    )


@pytest.mark.parametrize(
    'request_id, data',
    [
        (
            '92d0e2c87a0c4232ab13759b094ec638',
            {'status': 'rejected', 'reason': 'test', 'formal_reason': 'kek'},
        ),
    ],
)
@pytest.mark.config(CORP_CLIENT_REQUEST_REJECTION_REASONS=['kek'])
async def test_client_request_status_reject_lock(
        db, taxi_corp_requests_web, request_id, data,
):
    assert 'locked' not in (
        await db.corp_client_requests.find_one({'_id': request_id})
    )

    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/status/update',
        params={'request_id': request_id},
        json=data,
        headers=HEADERS,
    )

    assert response.status == 200
    assert 'locked' not in (
        await db.corp_client_requests.find_one({'_id': request_id})
    )
