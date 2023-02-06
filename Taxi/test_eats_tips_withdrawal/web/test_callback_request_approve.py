# pylint: disable=W0612
import decimal

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from eats_tips_withdrawal.generated.web import web_context as context
from test_eats_tips_withdrawal import conftest


SUCCESS_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS[
    'success'
][0]


@pytest.mark.parametrize(
    'service_name, order_id, set_restricted_response, partners_response, '
    'expected_result, expected_status, expected_withdrawal_status, '
    'expected_admin_id, expected_b2p_block_mcc, expected_push_text, '
    'expected_push_title',
    [
        pytest.param(
            None,
            '30',
            '',
            conftest.PARTNER_1,
            {'code': 'not_allowed', 'message': 'not allowed'},
            403,
            'auto approved',
            '',
            0,
            '',
            '',
            id='no src service name',
        ),
        pytest.param(
            'eats-tips-payments',
            '30',
            """<?xml version="1.0" encoding="UTF-8"?><response>
                    <code>1</code>
                    <description>Successful financial transaction</description>
                </response>""",
            conftest.PARTNER_1,
            {'result': True},
            200,
            'success',
            -1,
            1,
            SUCCESS_PUSH['text']['default'],
            SUCCESS_PUSH['title']['default'],
            id='success + restict fine',
        ),
        pytest.param(
            'eats-tips-payments',
            '30',
            """<?xml version="1.0" encoding="UTF-8"?><error>
                <description>Ошибка: неверная цифровая подпись.</description>
                <code>109</code>
                </error>""",
            conftest.PARTNER_1,
            {'result': True},
            200,
            'success',
            -1,
            0,
            SUCCESS_PUSH['text']['default'],
            SUCCESS_PUSH['title']['default'],
            id='success + restict fail',
        ),
        pytest.param(
            'eats-tips-payments',
            '29',
            '',
            conftest.PARTNER_2,
            {'result': True},
            200,
            'successfully sent to B2P',
            -1,
            0,
            '',
            '',
            id='already success card callback',
        ),
        pytest.param(
            'eats-tips-payments',
            '28',
            '',
            conftest.PARTNER_2,
            {'result': True},
            200,
            'successfully sent to B2P',
            20,
            0,
            '',
            '',
            id='already success by admin',
        ),
        pytest.param(
            'eats-tips-payments',
            '27',
            '',
            conftest.PARTNER_1,
            {'result': True},
            200,
            'success',
            -1,
            0,
            SUCCESS_PUSH['text']['default'],
            SUCCESS_PUSH['title']['default'],
            id='success after sent to manual check',
        ),
        pytest.param(
            'eats-tips-payments',
            '26',
            '',
            conftest.PARTNER_2,
            {'result': False},
            200,
            'precheck created',
            '',
            0,
            '',
            '',
            id='no approve - only precheck have',
        ),
        pytest.param(
            'eats-tips-payments',
            '99',
            '',
            '',
            {'code': 'no_request', 'message': 'No such request'},
            404,
            None,
            0,
            0,
            '',
            '',
            id='no such withdrawal request',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/what-db-use-for-user',
    experiment_name='eda_tips_withdrawals_what_db_use',
    args=[{'name': 'user_id', 'type': 'int', 'value': 1}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/what-db-use-for-user',
    experiment_name='eda_tips_withdrawals_what_db_use',
    args=[{'name': 'user_id', 'type': 'int', 'value': 2}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/what-db-use-for-user',
    experiment_name='eda_tips_withdrawals_what_db_use',
    args=[{'name': 'user_id', 'type': 'int', 'value': 5}],
    value={'enabled': True},
)
@pytest.mark.now('2021-05-04T12:12:44.477345+03:00')
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_sbp_callback_approve(
        taxi_eats_tips_withdrawal_web,
        web_app_client,
        mock_best2pay,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        web_context,
        patch,
        stq,
        service_name,
        order_id,
        set_restricted_response,
        partners_response,
        expected_result,
        expected_status,
        expected_withdrawal_status,
        expected_admin_id,
        expected_b2p_block_mcc,
        expected_push_text,
        expected_push_title,
):
    @patch(
        'eats_tips_withdrawal.api.callback_request_approve'
        '.get_src_service_name',
    )
    def get_service_name(request):
        return service_name

    @mock_eats_tips_partners('/v1/partner/block')
    async def _mock_block_user(request):
        return web.json_response()

    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    @mock_eats_tips_partners('/v1/alias-to-object')
    async def _mock_alias_to_object(request: http.Request):
        return web.json_response(
            {'type': 'partner', 'partner': partners_response},
        )

    @mock_eats_tips_payments('/internal/v1/payments/max-pays-from-one-card')
    async def _mock_transactions(request: http.Request):
        assert dict(request.query) == {
            'start_check_time': '2021-05-03T12:12:44.477345+03:00',
            'recipient_id': conftest.USER_ID_1,
        }
        return web.json_response({'count': 3 if expected_b2p_block_mcc else 0})

    response = await web_app_client.post(
        '/v1/callback/approve-request', json={'order_id': order_id},
    )
    content = await response.json()
    assert content == expected_result
    assert response.status == expected_status

    if expected_withdrawal_status is None:
        return
    async with web_context.pg.master_pool.acquire() as conn:
        withdrawal_row = await conn.fetchrow(
            f'select * from eats_tips_withdrawal.withdrawals where '
            f'bp2_order_id=\'{order_id}\'',
        )
        assert withdrawal_row['status'] == expected_withdrawal_status
        assert withdrawal_row['admin'] == str(expected_admin_id)

    if expected_push_text:
        assert stq.eats_tips_partners_send_push.times_called == 1
        conftest.check_task_queued(
            stq,
            stq.eats_tips_partners_send_push,
            {
                'text': expected_push_text,
                'partner_id': str(withdrawal_row['partner_id']),
                'title': expected_push_title.format(
                    amount=decimal.Decimal(withdrawal_row['amount']),
                ),
                'intent': 'withdrawal',
            },
        )
    else:
        assert not stq.eats_tips_partners_send_push.times_called
