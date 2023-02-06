# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name

import datetime
import typing

import pytest

from corp_notices.crontasks import process_queue
from corp_notices.generated.cron import run_cron
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


@pytest.fixture
def insert_notice(cron_context):
    async def inserter(kwargs):
        notice = notices_models.Notice.make(kwargs)
        await notices_db.insert(cron_context, notice)

    return inserter


@pytest.fixture
def send_mock(patch):
    @patch('corp_notices.notices.base.NoticeBroker._send')
    async def __send():
        pass

    return __send


@pytest.fixture
def notice_mock():
    from corp_notices.notices import base
    from corp_notices.notices import registry

    class TestNoticeBroker(base.ClientNoticeBroker):
        notice_name = 'TestNotice'

        async def send(self):
            await self.get_template_kwargs()
            await self._send()
            self.notice.status = notices_models.Status.sent
            await notices_db.update(self.context, self.notice)

        async def get_template_kwargs(self) -> typing.Optional[dict]:
            return None

    registry.add(TestNoticeBroker)


@pytest.fixture
def bad_notice_mock():
    from corp_notices.notices import base
    from corp_notices.notices import registry

    class BadNoticeBroker(base.ClientNoticeBroker):
        notice_name = 'BadNotice'

        async def send(self):
            await self.get_template_kwargs()
            await self._send()
            self.notice.status = notices_models.Status.sent
            await notices_db.update(self.context, self.notice)

        async def get_template_kwargs(self) -> typing.Optional[dict]:
            raise AttributeError

    registry.add(BadNoticeBroker)


@pytest.mark.parametrize(
    'notice_kwargs, has_calls',
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'status': 'pending',
                'notice_name': 'TestNotice',
                'send_at': NOW,
            },
            True,
            id='now',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'status': 'pending',
                'notice_name': 'TestNotice',
                'send_at': NOW + datetime.timedelta(days=1),
            },
            False,
            id='future',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'status': 'sent',
                'notice_name': 'TestNotice',
                'send_at': NOW,
            },
            False,
            id='already sent',
        ),
    ],
)
async def test_process_queue(
        cron_context,
        insert_notice,
        send_mock,
        notice_mock,
        notice_kwargs,
        has_calls,
):
    await insert_notice(notice_kwargs)
    await run_cron.main(['corp_notices.crontasks.process_queue', '-t', '0'])
    assert bool(send_mock.calls) == has_calls


async def test_unknown_notice(cron_context, insert_notice, send_mock):
    await insert_notice(
        {
            'client_id': 'client_id_1',
            'status': 'pending',
            'notice_name': 'unknown',
            'send_at': NOW,
        },
    )
    await run_cron.main(['corp_notices.crontasks.process_queue', '-t', '0'])

    assert bool(send_mock.calls) is False

    notices = await notices_db.fetch_client_notices(
        cron_context, 'client_id_1',
    )

    assert len(notices) == 1
    notice = notices[0]

    assert notice.status == notices_models.Status.failed
    assert notice.reason == 'Unexpected notice name'


async def test_bad_notice(
        cron_context, insert_notice, notice_mock, bad_notice_mock, send_mock,
):
    await insert_notice(
        {
            'client_id': 'client_id_1',
            'status': 'pending',
            'notice_name': 'TestNotice',
            'send_at': NOW,
        },
    )
    await insert_notice(
        {
            'client_id': 'client_id_1',
            'status': 'pending',
            'notice_name': 'BadNotice',
            'send_at': NOW,
        },
    )
    await insert_notice(
        {
            'client_id': 'client_id_1',
            'status': 'pending',
            'notice_name': 'TestNotice',
            'send_at': NOW,
        },
    )
    try:
        await run_cron.main(
            ['corp_notices.crontasks.process_queue', '-t', '0'],
        )
    except Exception as err:  # pylint: disable=W0703
        assert isinstance(err, process_queue.BadNoticesInQueueException)

    assert len(send_mock.calls) == 2

    notices = await notices_db.fetch_client_notices(
        cron_context, 'client_id_1',
    )

    assert len(notices) == 3
    for notice in notices:
        if notice.notice_name == 'TestNotice':
            assert notice.status == notices_models.Status.sent
        elif notice.notice_name == 'BadNotice':
            assert notice.status == notices_models.Status.pending
