# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
import copy
import datetime
import json
import typing

import pytest

from corp_notices.notices import base
from corp_notices.notices import db
from corp_notices.notices import models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'TestClientNotice': {
                'enabled': True,
                'days_offset': 1,
                'hours_offset': 2,
                'minutes_offset': 30,
                'slugs': {'rus': 'SLUG'},
            },
        },
    ),
]

MOCK_CLIENT_RESPONSE = {
    'id': 'client_id_1',
    'name': 'Test client',
    'billing_name': 'None',
    'country': 'rus',
    'yandex_login': 'test-client',
    'description': 'Test',
    'is_trial': False,
    'email': 'test@email.com',
    'features': [],
    'billing_id': '101',
    'created': '2020-01-01T03:00:00+03:00',
}


NOTICE_KWARGS = {'notice_kwargs': 'test'}

TEMPLATE_KWARGS = {'template_kwargs': 'test', 'password': 'Qw123456'}


@pytest.fixture
async def enqueued_notice(cron_context):
    class TestClientNotice(base.ClientNoticeBroker):
        notice_name = 'TestClientNotice'

        async def get_template_kwargs(self) -> typing.Optional[dict]:
            return copy.copy(TEMPLATE_KWARGS)

        async def post_send(self) -> None:
            if self.notice.template_kwargs:
                self.notice.template_kwargs['password'] = 'XXXXXX'

    notice = TestClientNotice.make(
        cron_context, notice_kwargs=NOTICE_KWARGS, client_id='client_id_1',
    )
    await notice.enqueue()
    return notice


async def test_enqueue(cron_context, enqueued_notice):

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert notices == [
        models.Notice(
            id=1,
            status=models.Status.pending,
            notice_name='TestClientNotice',
            client_id='client_id_1',
            send_at=NOW + datetime.timedelta(days=1, hours=2, minutes=30),
            notice_kwargs=NOTICE_KWARGS,
        ),
    ]


async def test_send(
        cron_context, enqueued_notice, mock_corp_clients, mock_sender,
):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE

    await enqueued_notice.send()

    email = 'test@email.com'

    assert mock_sender.send_transactional.has_calls
    call = mock_sender.send_transactional.next_call()
    assert call['request'].query == {'to_email': email}
    assert call['request'].json == {
        'args': json.dumps(TEMPLATE_KWARGS),
        'async': True,
    }
    assert not mock_sender.send_transactional.has_calls

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == models.Status.sent
    assert notice.sent_at == NOW
    assert notice.sent_to == ['test@email.com']
    assert notice.sent_slug == 'SLUG'
    assert notice.template_kwargs == {
        'template_kwargs': 'test',
        'password': 'XXXXXX',
    }
    assert not notice.reason


async def test_send_email_not_exists(
        cron_context, enqueued_notice, mock_corp_clients, mock_sender,
):
    mock_corp_clients.data.get_client_response = dict(
        MOCK_CLIENT_RESPONSE, email=None,
    )

    await enqueued_notice.send()

    assert not mock_sender.send_transactional.has_calls

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == models.Status.rejected
    assert not notice.sent_at
    assert not notice.sent_to
    assert not notice.sent_slug
    assert not notice.template_kwargs
    assert notice.reason == 'Emails does not exists'


async def test_send_notice_disabled(
        cron_context, enqueued_notice, mock_corp_clients, mock_sender,
):
    settings = cron_context.config.CORP_NOTICES_SETTINGS['TestClientNotice']
    settings['enabled'] = False

    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE

    await enqueued_notice.send()

    assert not mock_sender.send_transactional.has_calls

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == models.Status.rejected
    assert not notice.sent_at
    assert not notice.sent_to
    assert not notice.sent_slug
    assert not notice.template_kwargs
    assert notice.reason == 'Notice disabled'


async def test_send_slug_not_exists(
        cron_context, enqueued_notice, mock_corp_clients, mock_sender,
):
    settings = cron_context.config.CORP_NOTICES_SETTINGS['TestClientNotice']
    settings['slugs'] = {}

    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE

    await enqueued_notice.send()

    assert not mock_sender.send_transactional.has_calls

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == models.Status.rejected
    assert not notice.sent_at
    assert not notice.sent_to
    assert not notice.sent_slug
    assert not notice.template_kwargs
    assert notice.reason == 'Slug does not exists'


async def test_default_moderator_emails(
        cron_context, enqueued_notice, mock_corp_clients, mock_sender,
):
    settings = cron_context.config.CORP_NOTICES_SETTINGS['TestClientNotice']
    settings['moderator_emails'] = {'__default__': ['mod@yandex.ru']}

    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE

    await enqueued_notice.send()

    assert mock_sender.send_transactional.has_calls

    notices = await db.fetch_client_notices(cron_context, 'client_id_1')

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == models.Status.sent
    assert notice.sent_at == NOW
    assert notice.sent_to == ['test@email.com', 'mod@yandex.ru']
    assert notice.sent_slug == 'SLUG'
    assert notice.template_kwargs == {
        'template_kwargs': 'test',
        'password': 'XXXXXX',
    }
    assert not notice.reason
