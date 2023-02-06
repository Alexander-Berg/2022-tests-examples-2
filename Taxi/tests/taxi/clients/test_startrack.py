# pylint: disable=protected-access, redefined-outer-name, no-member
import json
import uuid

import pytest

from taxi import config
from taxi.clients import startrack


@pytest.fixture
def test_app(test_taxi_app):
    test_taxi_app.startrack = startrack.StartrackAPIClient(
        profile='support-taxi',
        session=test_taxi_app.session,
        secdist=test_taxi_app.secdist,
        config=test_taxi_app.config,
    )
    return test_taxi_app


@pytest.fixture
def mock_startrack_request(monkeypatch, mock):
    def _create_dummy_request(response):
        @mock
        async def _dummy_request(*args, **kwargs):
            return response

        monkeypatch.setattr(
            startrack.StartrackAPIClient, '_request', _dummy_request,
        )
        return _dummy_request

    return _create_dummy_request


@pytest.fixture
def mock_st_get_attachments(monkeypatch, mock):
    def _create_dummy_request(response):
        @mock
        async def _dummy_request(*args, **kwargs):
            return response

        monkeypatch.setattr(
            startrack.StartrackAPIClient, '_request', _dummy_request,
        )
        return _dummy_request

    return _create_dummy_request


@pytest.fixture
def mock_uuid(monkeypatch):
    class _DummyUuid:
        hex = 'dummy_uuid'

    monkeypatch.setattr(uuid, 'uuid4', _DummyUuid)


@pytest.mark.parametrize(
    'url,data,org_id,expected_result,expected_exception,error_messages',
    [
        # All OK
        ('some_url', {'some': 'data'}, 0, {}, None, None),
        # Wrong org_id
        (
            'some_url',
            {'some': 'data'},
            123456,
            None,
            startrack.AuthenticationError,
            None,
        ),
        # Wrong action
        (
            'forbidden_url',
            {'some': 'data'},
            0,
            None,
            startrack.PermissionsError,
            None,
        ),
        # Wrong URL
        (
            'wrong_url',
            {'some': 'data'},
            0,
            None,
            startrack.NotFoundError,
            None,
        ),
        # Wrong data
        (
            'some_url',
            {'wrong': 'data'},
            0,
            None,
            startrack.ValidationError,
            [],
        ),
        # Wrong data with error_message
        (
            'some_url',
            {'error_message': 'my_error_message'},
            0,
            None,
            startrack.ValidationError,
            ['my_error_message'],
        ),
    ],
)
async def test_request(
        test_app,
        monkeypatch,
        mock,
        url,
        data,
        org_id,
        expected_result,
        expected_exception,
        error_messages,
):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, status, result=None):
                self.status = status
                self.url = kwargs['url']
                self.method = kwargs['method']
                self.headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                self.result = result or {}

            async def json(self):
                return self.result

            async def text(self):
                return json.dumps(self.result)

        if kwargs['headers'].get('X-Org-Id') != '0':
            return _DummyResponse(401)
        if kwargs['url'] == 'http://test-startrack-url/forbidden_url':
            return _DummyResponse(403)
        if kwargs['url'] != 'http://test-startrack-url/some_url':
            return _DummyResponse(404)
        if 'error_message' in kwargs['json']:
            return _DummyResponse(
                422, {'errorMessages': [kwargs['json']['error_message']]},
            )
        if 'some' not in kwargs['json']:
            return _DummyResponse(422)

        return _DummyResponse(201)

    monkeypatch.setattr(test_app.startrack._session, 'request', _dummy_request)
    test_app.startrack._profile['org_id'] = org_id

    exception = None
    exception_type = None
    result = None
    try:
        result = await test_app.startrack._request(
            url, method='POST', json=data,
        )
    except startrack.BaseError as _e:
        exception = _e
        exception_type = type(_e)

    assert exception_type == expected_exception
    if error_messages is not None:
        assert exception.error_messages == error_messages
    assert result == expected_result

    if expected_exception is None:
        request_calls = _dummy_request.calls
        assert request_calls[0]['kwargs'] == {
            'url': 'http://test-startrack-url/some_url',
            'json': {'some': 'data'},
            'data': None,
            'method': 'POST',
            'params': None,
            'timeout': 5,
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': 'OAuth some_startrack_token',
                'X-Org-Id': '0',
            },
        }


@pytest.mark.parametrize(
    'ticket_kwargs,expected_request_kwargs',
    [
        (
            {
                'queue': 'TAXIBACKEND',
                'summary': 'some ticket',
                'description': 'some description',
            },
            {
                'method': 'POST',
                'url': 'issues',
                'json': {
                    'summary': 'some ticket',
                    'queue': {'key': 'TAXIBACKEND'},
                    'description': 'some description',
                    'type': {'key': 'task'},
                    'unique': 'dummy_uuid',
                },
                'log_extra': None,
            },
        ),
        (
            {
                'queue': 'TAXIBACKEND',
                'summary': 'some ticket',
                'description': 'some description',
                'ticket_type': 'bug',
                'parent': 'TAXIBACKEND-12',
                'sprints': ['SEPTEMBER-1', 'SEPTEMBER-2'],
                'priority': 'low',
                'assignee': 'manager0',
                'followers': ['manager1', 'manager2'],
                'tags': ['some', 'tags'],
                'custom_fields': {'some_field': 'some_value'},
                'unique': 'unique',
            },
            {
                'method': 'POST',
                'url': 'issues',
                'json': {
                    'summary': 'some ticket',
                    'queue': {'key': 'TAXIBACKEND'},
                    'description': 'some description',
                    'parent': {'key': 'TAXIBACKEND-12'},
                    'sprint': [{'key': 'SEPTEMBER-1'}, {'key': 'SEPTEMBER-2'}],
                    'priority': {'key': 'low'},
                    'assignee': 'manager0',
                    'followers': ['manager1', 'manager2'],
                    'type': {'key': 'bug'},
                    'tags': ['some', 'tags'],
                    'some_field': 'some_value',
                    'unique': 'unique',
                },
                'log_extra': None,
            },
        ),
    ],
)
async def test_create_ticket(
        test_app,
        mock_startrack_request,
        mock_uuid,
        ticket_kwargs,
        expected_request_kwargs,
):
    request = mock_startrack_request({'some': 'ticket'})
    result = await test_app.startrack.create_ticket(**ticket_kwargs)
    assert result == {'some': 'ticket'}

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_request_kwargs


@pytest.mark.parametrize(
    'comment_kwargs,expected_request_kwargs',
    [
        (
            {'ticket': 'TESTBACKEND-123', 'text': 'some test comment'},
            {
                'method': 'POST',
                'url': 'issues/TESTBACKEND-123/comments',
                'params': {'isAddToFollowers': 'true'},
                'json': {'text': 'some test comment'},
            },
        ),
        (
            {
                'ticket': 'TESTBACKEND-123',
                'summonees': [1, 2, 3],
                'attachment_ids': [4, 5, 6],
                'maillist_summonees': [7, 8, 9],
                'add_to_followers': False,
            },
            {
                'method': 'POST',
                'url': 'issues/TESTBACKEND-123/comments',
                'params': {'isAddToFollowers': 'false'},
                'json': {
                    'summonees': [1, 2, 3],
                    'attachmentIds': [4, 5, 6],
                    'maillistSummonees': [7, 8, 9],
                },
            },
        ),
        (
            {
                'ticket': 'TESTBACKEND-123',
                'text': 'some test comment',
                'email_from': 'from@email',
                'email_to': 'to@email',
                'email_subject': 'some email subject',
                'email_text': 'some email text',
                'signature_selection': True,
                'attachment_ids': None,
            },
            {
                'method': 'POST',
                'url': 'issues/TESTBACKEND-123/comments',
                'params': {
                    'isAddToFollowers': 'true',
                    'enableSignatureSelection': 'true',
                },
                'json': {
                    'text': 'some test comment',
                    'email': {
                        'text': 'some email text',
                        'subject': 'some email subject',
                        'info': {'from': 'from@email', 'to': 'to@email'},
                    },
                },
            },
        ),
    ],
)
async def test_create_comment(
        test_app,
        mock_startrack_request,
        comment_kwargs,
        expected_request_kwargs,
):
    request = mock_startrack_request({'some': 'comment'})
    result = await test_app.startrack.create_comment(**comment_kwargs)
    assert result == {'some': 'comment'}

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_request_kwargs


@pytest.mark.parametrize(
    'ticket,ticket_kwargs,expected_request_kwargs',
    [
        (
            'TAXIBACKEND-123',
            {'summary': 'new ticket summary'},
            {
                'method': 'PATCH',
                'url': 'issues/TAXIBACKEND-123',
                'json': {'summary': 'new ticket summary'},
            },
        ),
        (
            'TAXIBACKEND-123',
            {
                'queue': 'TAXIBACKEND',
                'summary': 'new ticket summary',
                'description': 'some description',
                'ticket_type': 'bug',
                'parent': 'TAXIBACKEND-12',
                'sprints': ['SEPTEMBER-1', 'SEPTEMBER-2'],
                'priority': 'low',
                'assignee': 'manager0',
                'followers': ['manager1', 'manager2'],
                'favorite': True,
                'tags': ['some', 'tags'],
                'custom_fields': {'some_field': 'some_value'},
            },
            {
                'method': 'PATCH',
                'url': 'issues/TAXIBACKEND-123',
                'json': {
                    'summary': 'new ticket summary',
                    'queue': {'key': 'TAXIBACKEND'},
                    'description': 'some description',
                    'parent': {'key': 'TAXIBACKEND-12'},
                    'sprint': [{'key': 'SEPTEMBER-1'}, {'key': 'SEPTEMBER-2'}],
                    'priority': {'key': 'low'},
                    'type': {'key': 'bug'},
                    'assignee': 'manager0',
                    'followers': ['manager1', 'manager2'],
                    'favorite': True,
                    'tags': ['some', 'tags'],
                    'some_field': 'some_value',
                },
            },
        ),
    ],
)
async def test_update_ticket(
        test_app,
        mock_startrack_request,
        ticket,
        ticket_kwargs,
        expected_request_kwargs,
):
    request = mock_startrack_request({'some': 'ticket'})
    result = await test_app.startrack.update_ticket(ticket, **ticket_kwargs)
    assert result == {'some': 'ticket'}

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_request_kwargs


async def test_get_ticket(test_app, mock_startrack_request):
    request = mock_startrack_request([{'some': 'ticket'}])
    result = await test_app.startrack.get_ticket('TESTBACKEND-123')
    assert result == [{'some': 'ticket'}]

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == {
        'method': 'GET',
        'url': 'issues/TESTBACKEND-123',
        'log_extra': None,
    }


@pytest.mark.parametrize(
    'kwargs, expected_request_kwargs',
    [
        (
            {},
            {
                'method': 'GET',
                'url': 'issues/TESTBACKEND-123/comments',
                'params': {},
                'log_extra': None,
            },
        ),
        (
            {'short_id': 123, 'per_page': 456},
            {
                'method': 'GET',
                'url': 'issues/TESTBACKEND-123/comments',
                'params': {'id': 123, 'perPage': 456},
                'log_extra': None,
            },
        ),
    ],
)
async def test_get_comments(
        test_app, mock_startrack_request, kwargs, expected_request_kwargs,
):
    request = mock_startrack_request([{'some': 'comment'}])
    result = await test_app.startrack.get_comments('TESTBACKEND-123', **kwargs)
    assert result == [{'some': 'comment'}]

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_request_kwargs


@pytest.mark.parametrize(
    'search_kwargs,expected_kwargs',
    [
        (
            {'json_filter': {'some': 'filter'}},
            {
                'method': 'POST',
                'url': 'issues/_search',
                'json': {'filter': {'some': 'filter'}},
                'params': {'perPage': 100},
            },
        ),
        (
            {'query': 'some query'},
            {
                'method': 'POST',
                'url': 'issues/_search',
                'json': {'query': 'some query'},
                'params': {'perPage': 100},
            },
        ),
        (
            {'queue': 'some queue'},
            {
                'method': 'POST',
                'url': 'issues/_search',
                'json': {'queue': 'some queue'},
                'params': {'perPage': 100},
            },
        ),
        (
            {'keys': ['TICKET-1', 'TICKET-2']},
            {
                'method': 'POST',
                'url': 'issues/_search',
                'json': {'keys': ['TICKET-1', 'TICKET-2']},
                'params': {'perPage': 100},
            },
        ),
    ],
)
async def test_search(
        test_app, mock_startrack_request, search_kwargs, expected_kwargs,
):
    request = mock_startrack_request([{'some': 'ticket'}])
    result = await test_app.startrack.search(**search_kwargs)
    assert result == [{'some': 'ticket'}]

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_kwargs


@pytest.mark.parametrize(
    'enable_sla, expected_params',
    [
        (None, None),
        ('true', {'enableSla': 'true'}),
        ('false', {'enableSla': 'false'}),
    ],
)
async def test_import_ticket(
        test_app,
        mock_startrack_request,
        mock_uuid,
        enable_sla,
        expected_params,
):
    request = mock_startrack_request({'some': 'ticket'})
    result = await test_app.startrack.import_ticket(
        data={'some': 'data'}, enable_sla=enable_sla,
    )
    assert result == {'some': 'ticket'}

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == {
        'method': 'POST',
        'url': 'issues/_import',
        'json': {'some': 'data', 'unique': 'dummy_uuid'},
        'params': expected_params,
    }


async def test_import_comment(test_app, mock_startrack_request):
    request = mock_startrack_request({'some': 'comment'})
    result = await test_app.startrack.import_comment(
        ticket_id='TESTBACKEND-123', data={'some': 'data'},
    )
    assert result == {'some': 'comment'}

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == {
        'method': 'POST',
        'url': 'issues/TESTBACKEND-123/comments/_import',
        'json': {'some': 'data'},
    }


@pytest.mark.parametrize(
    'ticket, transition, data, expected_data',
    [
        (
            'TESTBACKEND-123',
            'some_transition',
            None,
            {
                'method': 'POST',
                'url': (
                    'issues/TESTBACKEND-123/transitions/'
                    'some_transition/_execute'
                ),
                'json': {},
            },
        ),
        (
            'TESTBACKEND-456',
            'other_transition',
            {'some': 'data'},
            {
                'method': 'POST',
                'url': (
                    'issues/TESTBACKEND-456/transitions/'
                    'other_transition/_execute'
                ),
                'json': {'some': 'data'},
            },
        ),
    ],
)
async def test_execute_transition(
        test_app,
        mock_startrack_request,
        ticket,
        transition,
        data,
        expected_data,
):
    request = mock_startrack_request([])
    result = await test_app.startrack.execute_transition(
        ticket_id=ticket, transition=transition, data=data,
    )
    assert result == []

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_data


@pytest.mark.parametrize(
    'ticket, related_ticket, relationship, expected_data',
    [
        (
            'TESTBACKEND-123',
            'TESTBACKEND-456',
            None,
            {
                'method': 'POST',
                'url': 'issues/TESTBACKEND-123/links',
                'json': {
                    'relationship': 'relates',
                    'issue': 'TESTBACKEND-456',
                },
            },
        ),
        (
            'TESTBACKEND-456',
            'TESTBACKEND-789',
            'depends on',
            {
                'method': 'POST',
                'url': 'issues/TESTBACKEND-456/links',
                'json': {
                    'relationship': 'depends on',
                    'issue': 'TESTBACKEND-789',
                },
            },
        ),
    ],
)
async def test_create_link(
        test_app,
        mock_startrack_request,
        ticket,
        related_ticket,
        relationship,
        expected_data,
):
    request = mock_startrack_request([])
    result = await test_app.startrack.create_link(
        ticket_id=ticket,
        related_ticket_id=related_ticket,
        relationship=relationship,
    )
    assert result == []

    request_calls = request.calls
    assert request_calls[0]['kwargs'] == expected_data


@pytest.mark.parametrize(
    'api_response,excepted_exception',
    [
        ({'errorMessages': ['some_error']}, startrack.ValidationError),
        (
            {
                'errorMessages': [
                    'Задачи TESTBACKEND-1 и ADDITIONAL-2 уже связаны.',
                ],
            },
            startrack.AlreadyLinked,
        ),
        (
            {
                'errorMessages': [
                    'some_error',
                    'Задачи TESTBACKEND-1 и ADDITIONAL-2 уже связаны.',
                ],
            },
            startrack.ValidationError,
        ),
        ({}, startrack.ValidationError),
    ],
)
async def test_create_link_custom_error(
        patch, test_app, api_response, excepted_exception,
):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _dummy_request(*args, **kwargs):
        raise startrack.ValidationError('Some error', api_response)

    try:
        await test_app.startrack.create_link(
            ticket_id='TESTBACKEND-1', related_ticket_id='ADDITIONAL-2',
        )
    except startrack.BaseError as exc:
        exception_type = type(exc)

    assert exception_type == excepted_exception


@pytest.mark.config(
    STARTRACK_ERROR_MESSAGES={
        'already_linked': ['Задачи .+ и .+ уже связаны.'],
    },
)
@pytest.mark.parametrize(
    'api_response,excepted_exception',
    [
        (
            {
                'errorMessages': [
                    'Задачи TESTBACKEND-1 и NewADDITIONAL-2 уже связаны.',
                ],
            },
            startrack.AlreadyLinked,
        ),
        ({'errorMessages': ['уже связаны']}, startrack.ValidationError),
        ({}, startrack.ValidationError),
    ],
)
async def test_regex_error(patch, test_app, api_response, excepted_exception):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _dummy_request(*args, **kwargs):
        raise startrack.ValidationError('Some error', api_response)

    with pytest.raises(excepted_exception):
        await test_app.startrack.create_link(
            ticket_id='TESTBACKEND-1', related_ticket_id='ADDITIONAL-2',
        )


@pytest.mark.parametrize(
    'comment', [{'body': 'ticket body', 'public': True}, 'ticket body'],
)
def test_convert_zendesk_startrack(test_app, comment):
    ticket = {
        'ticket': {
            'requester': {
                'email': '79057472715@taxi.yandex.ru',
                'name': 'user',
            },
            'subject': 'ticket subject',
            'comment': comment,
            'tags': ['my', 'awesome', 'tag'],
            'form_id': 10,
            'group_id': 100500,
            'custom_fields': [
                {'id': 27946649, 'value': 'vip'},
                {'id': 32670029, 'value': '+79057472715'},
                {'id': 1000, 'value': '1000value'},
                {'id': 9999, 'value': '999value'},
                {'id': 200, 'value': None},
            ],
        },
    }

    class Config(config.Config):
        ZENDESK_FEEDBACK_CUSTOM_FIELDS_SPLITTED = {
            'yataxi': {
                'user_type': 27946649,
                'user_phone': 32670029,
                'tariff': 33990269,
                'order_date': 34109145,
            },
            'yutaxi': {
                'user_type': 279466490,
                'tariff': 339902690,
                'order_date': 341091450,
            },
        }
        STARTRACK_CUSTOM_FIELDS_MAP = {
            'support-taxi': {
                'user_type': 'userType',
                'tariff': 'tariff',
                'order_date': 'orderDate',
                'user_phone': 'userPhone',
                'requester_name': 'requesterName',
                'requester_email': 'requesterEmail',
            },
        }
        ZENDESK_STARTRACK_FIELDS_MAP = {
            'support-taxi': {
                '1000': 'field1000',
                '111111': 'someField',
                'requester_email': 'emailFrom',
                'requester_name': 'requesterName',
                'subject': 'summary',
                'comment': 'description',
                'tags': 'tags',
                '200': 'field200',
            },
        }

    st_ticket = test_app.startrack.convert_ticket_from_zendesk(
        ticket, 'TESTQUEUE', config=Config(),
    )
    assert st_ticket == {
        'summary': 'ticket subject',
        'queue': {'key': 'TESTQUEUE'},
        'description': 'ticket body',
        'tags': ['my', 'awesome', 'tag'],
        'requesterName': 'user',
        'emailFrom': '79057472715@taxi.yandex.ru',
        'userType': 'vip',
        'userPhone': '+79057472715',
        'field1000': '1000value',
    }


@pytest.mark.parametrize(
    'error_type,params,excepted_result',
    [
        (
            startrack.ERROR_TYPE_ALREADY_LINKED,
            {'ticket_id': 'TICKET-1', 'related_ticket_id': 'LINKED-1'},
            ['Задачи TICKET-1 и LINKED-1 уже связаны.'],
        ),
        (
            startrack.ERROR_TYPE_COMMENT_LIMIT,
            None,
            ['Нельзя добавить больше 1000 комментариев'],
        ),
        ('not_known_type', {}, []),
        (startrack.ERROR_TYPE_ALREADY_LINKED, {'bad_data': 'bad_data'}, []),
    ],
)
def test_get_error_texts(test_app, error_type, params, excepted_result):
    result = test_app.startrack.get_error_texts(error_type, params)
    assert result == excepted_result
