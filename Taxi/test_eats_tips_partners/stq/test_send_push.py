import datetime

from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from eats_tips_partners.stq import send_push
from test_eats_tips_partners import conftest


NOW = datetime.datetime(2021, 10, 11, 14, 30, 15, tzinfo=datetime.timezone.utc)


def _make_stat(status):
    return conftest.make_stat(
        {'sensor': send_push.STAT_SENSOR_NAME, 'status': status},
    )


@pytest.mark.parametrize(
    'text, partner_id, client_notify_status, '
    'expected_stats, stq_id, '
    'check_retry',
    (
        pytest.param(
            'text',
            '00000000-0000-0000-0000-000000000042',
            200,
            _make_stat('success'),
            1,
            False,
            id='success_push',
        ),
        pytest.param(
            'another text',
            '00000000-0000-0000-0000-000000000050',
            409,
            _make_stat('conflict'),
            2,
            False,
            id='push_already_sent',
        ),
        # partner_id as empty string
        pytest.param(
            'Hello darkness, my old friend',
            '',
            None,
            None,
            1,
            False,
            id='partner_id_empty_string',
        ),
        pytest.param(
            'Hello darkness, my old friend',
            '00000000-0000-0000-0000-0000000000501',
            None,
            None,
            1,
            False,
            id='partner_id-not_uuid',
        ),
    ),
)
@pytest.mark.now(NOW.isoformat())
async def test_send_push(
        stq3_context,
        mock_client_notify,
        stq,
        get_single_stat_by_label_values,
        text,
        partner_id,
        client_notify_status,
        stq_id,
        expected_stats,
        check_retry,
):
    @mock_client_notify('/v2/push')
    async def _send_notification(request):
        body = request.json
        if stq_id != 1:
            return web.json_response(
                status='409', data={'message': 'conflict', 'code': '409'},
            )
        assert body['service'] == 'eats-tips'
        assert body['notification']['text'] == text
        assert body['notification']['title'] == send_push.DEFAULT_PUSH_TITLE
        return web.json_response(
            data={'notification_id': 'id'}, status=client_notify_status,
        )

    await send_push.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=1,
            reschedule_counter=1,
            queue='eats_tips_partners_send_push',
        ),
        text=text,
        partner_id=partner_id,
    )

    stats = get_single_stat_by_label_values(
        stq3_context, {'sensor': send_push.STAT_SENSOR_NAME},
    )
    assert stats == expected_stats
