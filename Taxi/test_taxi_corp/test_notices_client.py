import collections

import pytest

from taxi_corp import config
from taxi_corp.clients import notices_client
from taxi_corp.notifier.notices import notices_groups


@pytest.mark.parametrize(
    'corp_hold_notices',
    [
        pytest.param(False, id='do_not_hold_notices'),
        pytest.param(True, id='hold_notices'),
    ],
)
@pytest.mark.parametrize(['run_limit'], [pytest.param(5, id='run_limit_5')])
async def test_send_enqueued_notices(
        patch, db, loop, corp_hold_notices, run_limit,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch(
        'taxi_corp.clients.notices_client.'
        'NoticesClient.enqueue_client_poll_notices',
    )
    async def _enqueue(*args, **kwargs):
        pass

    cnt_before = await db.corp_notices_queue.count({})

    cfg = config.Config(db)
    setattr(cfg, 'CORP_HOLD_NOTICES', corp_hold_notices)
    client = notices_client.NoticesClient(db, loop, cfg)
    stats = collections.defaultdict(int)
    await client.send_enqueued_notices(run_limit, stats)

    cnt_after = await db.corp_notices_queue.count({})

    stq_calls = _put.calls
    if corp_hold_notices:
        assert not stq_calls
        assert cnt_before == cnt_after
        assert not stats['send_notices_from_queue']
        assert not stats['error_notices_from_queue']
    else:
        assert len(stq_calls) == run_limit
        assert cnt_before - run_limit == cnt_after
        assert stats['send_notices_from_queue'] == run_limit
        assert not stats['error_notices_from_queue']

    should_be_enqueued_cnt = 0
    for call in stq_calls:
        notice_name = call['kwargs']['kwargs']['notice_name']
        if notice_name in notices_groups.REGULAR_NOTICES:
            should_be_enqueued_cnt += 1

    enqueue_calls = _enqueue.calls
    assert len(enqueue_calls) == should_be_enqueued_cnt


@pytest.mark.parametrize(
    ['client_id'],
    [pytest.param('client1', id='enqueue_client_onboarding_notices')],
)
async def test_enqueue_client_onboarding(patch, db, loop, client_id):
    @patch('taxi_corp.clients.notices_client.NoticesClient._get_notice_offset')
    def _get(*args, **kwargs):
        return {'days_offset': 3, 'on_workday': True}

    cnt_before = await db.corp_notices_queue.count({})
    cfg = config.Config(db)
    client = notices_client.NoticesClient(db, loop, cfg)
    await client.enqueue_client_onboarding_notices(client_id)

    cnt_after = await db.corp_notices_queue.count({})
    should_be_enqueued = notices_groups.CLIENT_ONBOARDING_NOTICES

    assert cnt_before + len(should_be_enqueued) == cnt_after


@pytest.mark.parametrize(
    ['client_id', 'on_create', 'expected_enqueued_cnt'],
    [
        pytest.param('client_id', False, 1, id='enqueue_poll_notice'),
        pytest.param(
            'client_id',
            True,
            2,
            id='enqueue_poll_notice_after_client_creation',
        ),
    ],
)
async def test_enqueue_client_poll(
        patch, db, loop, client_id, on_create, expected_enqueued_cnt,
):
    @patch('taxi_corp.clients.notices_client.NoticesClient._get_notice_offset')
    def _get(*args, **kwargs):
        return {'days_offset': 3, 'on_workday': True}

    cnt_before = await db.corp_notices_queue.count({})
    cfg = config.Config(db)
    client = notices_client.NoticesClient(db, loop, cfg)
    await client.enqueue_client_poll_notices(client_id, on_create)

    cnt_after = await db.corp_notices_queue.count({})

    assert cnt_before + expected_enqueued_cnt == cnt_after
