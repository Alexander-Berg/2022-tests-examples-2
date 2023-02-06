from aiohttp import web
import pytest

from eats_tips_payments.generated.cron import run_cron
from test_eats_tips_payments import conftest

ALIAS_TO_PARTNER = {'1': conftest.PARTNER_ID_1, '2': conftest.PARTNER_ID_2}


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.config(
    EATS_TIPS_PAYMENTS_CRON_SYNC_PAYMENTS={
        'long': {'period_hours': 2, 'step_hours': 1, 'sleep': 0},
        'short': {'period_minutes': 60},
    },
)
@pytest.mark.now('1970-01-31 03:04:01')
async def test_sync_mysql_pg_payments_long(
        patch, mock_eats_tips_partners, cron_context,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'id': ALIAS_TO_PARTNER[request.query['alias']],
                'alias': request.query['alias'],
            },
        )

    # test just no failing - other tests in short cron
    await run_cron.main(
        [
            'eats_tips_payments.crontasks.sync_mysql_pg_payments_long',
            '-t',
            '0',
        ],
    )
