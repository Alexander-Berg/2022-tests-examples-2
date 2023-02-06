import http
import uuid

import pytest

from taxi.clients import personal

from support_info import settings


@pytest.mark.parametrize(
    'data',
    [
        {
            'request_id': '123',
            'eats_user_id': 'eats_user_id',
            'user_phone_pd_id': '123',
            'app': 'native',
            'feedback': {
                'comment': 'Random comment',
                'rating': 5,
                'predefined_comments': [],
                'is_feedback_requested': True,
            },
        },
        {
            'request_id': '123',
            'eats_user_id': 'eats_user_id',
            'user_phone_pd_id': '123',
            'app': 'superapp',
            'feedback': {
                'comment': '',
                'rating': 2,
                'predefined_comments': ['Predefined', 'Comment'],
                'is_feedback_requested': True,
            },
        },
    ],
)
async def test_eda_chat_ticket(support_info_client, patch, data):
    uuid_hex = '8fcb4acfee754679b72b66efb36c2a1d'

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        assert queue == settings.STQ_SUPPORT_INFO_EDA_CHAT_TICKET
        stq_kwargs = kwargs['kwargs']
        assert (
            stq_kwargs['request_id'] == data['request_id']
            and stq_kwargs['eats_user_id'] == data['eats_user_id']
            and stq_kwargs['user_phone_pd_id'] == data['user_phone_pd_id']
            and stq_kwargs['user_app'] == data['app']
            and stq_kwargs['locale'] == data.get('locale', 'ru')
            and stq_kwargs['feedback'] == data['feedback']
            and 'log_extra' in stq_kwargs
        )
        assert kwargs['task_id'] == uuid_hex

    @patch('uuid.uuid4')
    def _uuid4(*args, **kwargs):
        return uuid.UUID(hex=uuid_hex)

    response = await support_info_client.post(
        '/v1/eda/chat_tickets', json=data,
    )
    assert response.status == http.HTTPStatus.OK
    assert len(_put.calls) == 1


@pytest.mark.parametrize(
    'data, expected_status',
    [
        ({}, http.HTTPStatus.BAD_REQUEST),
        (
            {
                'request_id': '123',
                'eats_user_id': 'eats_user_id',
                'app': 'native',
                'feedback': {},
            },
            http.HTTPStatus.BAD_REQUEST,
        ),
    ],
)
async def test_eda_chat_ticket_error(
        support_info_client, patch, data, expected_status,
):
    response = await support_info_client.post(
        '/v1/eda/chat_tickets', json=data,
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'data, expected_status, expected_comment',
    [
        ({}, 400, ''),
        (
            {
                'request_id': '123',
                'personal_email_id': 'email_id',
                'comment': 'Ticket creation reason',
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            200,
            '',
        ),
        (
            {
                'request_id': '123',
                'personal_email_id': 'email_id',
                'comment': 'Ticket creation reason',
                'metadata': {'rating': 5, 'feedback': {'comment': 'test'}},
                'startrack_queue': 'TESTQUEUE',
                'destination_email': 'support@yandex.ru',
            },
            200,
            'test',
        ),
    ],
)
async def test_eda_mail_ticket(
        support_info_client,
        patch,
        mock_personal_single_email,
        data,
        expected_status,
        expected_comment,
):
    uuid_hex = '8fcb4acfee754679b72b66efb36c2a1d'
    expected_user_email = 'test@yandex.ru'
    mock_personal_single_email(expected_user_email)

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        assert queue == settings.STQ_SUPPORT_INFO_EDA_MAIL_TICKET
        stq_kwargs = kwargs['kwargs']
        assert (
            stq_kwargs['request_id'] == data['request_id']
            and stq_kwargs['user_email'] == expected_user_email
            and stq_kwargs['metadata'] == data.get('metadata', {})
            and stq_kwargs['message_text'] == expected_comment
            and stq_kwargs['tags'] == data.get('tags', [])
            and stq_kwargs['startrack_queue'] == data['startrack_queue']
            and stq_kwargs['destination_email'] == data['destination_email']
            and 'log_extra' in stq_kwargs
        )
        assert kwargs['task_id'] == uuid_hex

    @patch('uuid.uuid4')
    def _uuid4(*args, **kwargs):
        return uuid.UUID(hex=uuid_hex)

    response = await support_info_client.post(
        '/v1/eda/mail_tickets', json=data,
    )
    assert response.status == expected_status
    if expected_status == 200:
        assert len(_put.calls) == 1


async def test_eda_mail_ticket_exception(support_info_client, patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        raise personal.NotFoundError

    response = await support_info_client.post(
        '/v1/eda/mail_tickets',
        json={
            'request_id': '123',
            'personal_email_id': 'email_id',
            'comment': 'Ticket creation reason',
            'startrack_queue': 'TESTQUEUE',
            'destination_email': 'support@yandex.ru',
        },
    )
    assert response.status == 404
    answer = await response.json()
    assert answer == {
        'status': 'error',
        'error': 'Personal email by id email_id was not found',
    }
    assert _retrieve.calls
