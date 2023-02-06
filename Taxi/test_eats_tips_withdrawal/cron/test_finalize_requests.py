from aiohttp import web
import pytest

from eats_tips_withdrawal.common import constants
from eats_tips_withdrawal.common import models
from eats_tips_withdrawal.common import utils
from eats_tips_withdrawal.common import withdrawal_card
from eats_tips_withdrawal.common import withdrawal_sbp
from eats_tips_withdrawal.generated.cron import run_cron

ORDER_NOT_FINISHED_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>1617603</id>
                <state>REGISTERED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>"""
ORDER_COMPLETE_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>1617603</id>
                <state>COMPLETED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>"""


@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.now('2021-06-22 20:12:25+03:00')
async def test_finalize_requests(mock_best2pay, mock_stats, pgsql):
    @mock_best2pay('/webapi/Order')
    async def _mock_get_order_info(request):
        return web.Response(
            body=ORDER_COMPLETE_RESPONSE
            if request.query['id'] == '31'
            else ORDER_NOT_FINISHED_RESPONSE,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    await run_cron.main(
        ['eats_tips_withdrawal.crontasks.finalize_requests', '-t', '0'],
    )

    await check_requests_status(pgsql)

    await check_sent_stats(mock_stats)


async def check_requests_status(pgsql):
    cursor = pgsql['eats_tips_withdrawal'].cursor()
    cursor.execute(
        'select id, admin, status, comment '
        'from eats_tips_withdrawal.withdrawals '
        'order by id',
    )
    rows = cursor.fetchall()
    assert [
        (
            1,
            '-2',
            models.WithdrawalRequestStatus.ERROR.value,
            f'Hanged task with status '
            f'{models.WithdrawalRequestStatus.PRECHECK.value}',
        ),
        (2, '', models.WithdrawalRequestStatus.MANUAL_CHECK.value, None),
        (3, '', models.WithdrawalRequestStatus.MANUAL_REJECTED.value, None),
        (4, '', models.WithdrawalRequestStatus.SENT_TO_B2P.value, None),
        (
            5,
            str(constants.CRON_ADMIN_ID),
            models.WithdrawalRequestStatus.ERROR.value,
            f'Hanged task with status '
            f'{models.WithdrawalRequestStatus.AUTO_APPROVED.value}',
        ),
        (
            6,
            str(constants.CRON_ADMIN_ID),
            models.WithdrawalRequestStatus.ERROR.value,
            f'Hanged task with status '
            f'{models.WithdrawalRequestStatus.PRECHECK.value}',
        ),
        (
            7,
            str(constants.CRON_ADMIN_ID),
            models.WithdrawalRequestStatus.SENT_TO_B2P.value,
            None,
        ),
        (14, '', models.WithdrawalRequestStatus.ERROR.value, None),
        (
            16,
            str(constants.CRON_ADMIN_ID),
            models.WithdrawalRequestStatus.ERROR.value,
            f'Hanged task with status '
            f'{models.WithdrawalRequestStatus.PRECHECK.value}',
        ),
        (17, '', models.WithdrawalRequestStatus.PRECHECK.value, None),
        (
            18,
            str(constants.CRON_ADMIN_ID),
            models.WithdrawalRequestStatus.ERROR.value,
            f'Hanged task with status '
            f'{models.WithdrawalRequestStatus.AUTO_APPROVED.value}',
        ),
    ] == rows


async def check_sent_stats(mock_stats):
    result = sorted(
        [sensor_to_dict(x) for senors in mock_stats for x in senors],
        key=sorting_dict_condition,
    )
    assert result == [
        {
            'labels': {
                'action': 'hang_release',
                'sensor': 'cron_finalize_requests',
                'status': utils.normalize_status(
                    models.WithdrawalRequestStatus.AUTO_APPROVED.value,
                ),
                'withdrawal_type': withdrawal_sbp.PAY_METHOD,
            },
            'value': 1.0,
        },
        {
            'labels': {
                'action': 'hang_release',
                'sensor': 'cron_finalize_requests',
                'status': utils.normalize_status(
                    models.WithdrawalRequestStatus.AUTO_APPROVED.value,
                ),
                'withdrawal_type': withdrawal_card.PAY_METHOD,
            },
            'value': 1.0,
        },
        {
            'labels': {
                'action': 'hang_release',
                'sensor': 'cron_finalize_requests',
                'status': utils.normalize_status(
                    models.WithdrawalRequestStatus.PRECHECK.value,
                ),
                'withdrawal_type': withdrawal_card.PAY_METHOD,
            },
            'value': 1.0,
        },
    ]


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


def sorting_dict_condition(item):
    return (
        item['labels']['sensor'],
        item['labels'].get('withdrawal_type', ''),
        item['labels'].get('status', ''),
        item['value'],
    )
