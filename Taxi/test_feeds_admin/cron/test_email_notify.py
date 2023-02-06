import aiohttp
import pytest

# pylint: disable=redefined-outer-name
from feeds_admin.generated.cron import run_cron


class CallCounter:
    count = 0

    def __new__(cls):
        cls.count += 1


@pytest.mark.now('2000-01-02T12:00:00+03:00')
@pytest.mark.config(
    FEEDS_ADMIN_MONITORING_SETTINGS={
        '__default__': {
            'email': {
                'enabled': False,
                'max_day_before_expire': 1,
                'template': (
                    'just text\n{soon_expire_template}\n{expired_template}\n'
                ),
            },
        },
        'test_service': {
            'email': {
                'enabled': True,
                'exact_days_before_expire': [3],
                'addresses': [
                    'adomogashev@yandex-team.ru',
                    'test@yandex-team.ru',
                ],
                'soon_expire_template': (
                    '{feed_id}\t{service}\t'
                    '{days_until_expiration}\t{expire_at}'
                ),
                'expired_template': '({feed_id})',
            },
        },
    },
)
@pytest.mark.pgsql('feeds_admin', files=['interval_schedules.sql'])
async def test_interval_schedules(web_app_client, mock_sticker):
    @mock_sticker('/send-internal/')
    async def _send_mail(request):
        CallCounter()
        body = request.json
        text = body.pop('body')
        assert body.pop('idempotence_token')
        assert text == (
            'just text\n'
            '22222222222222222222222222222222\ttest_service'
            '\t1\t2000-01-03 01:00:00+03:00\n'
            '44444444444444444444444444444444\ttest_service'
            '\t3\t2000-01-05 01:00:00+03:00\n'
            '(66666666666666666666666666666666)'
            '\n'
        )

        return aiohttp.web.json_response({})

    await run_cron.main(['feeds_admin.crontasks.expire_notify', '-t', '0'])
    assert CallCounter.count == 2
