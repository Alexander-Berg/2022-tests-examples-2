# pylint: disable=W0612
from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from eats_tips_withdrawal.generated.web import web_context as context
from test_eats_tips_withdrawal import conftest


REJECT_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['reject'][
    0
]


@pytest.mark.parametrize(
    'service_name, order_id, partners_response, cancel_reason, '
    'expected_result, expected_status, expected_withdrawal_status, '
    'expected_admin_id, expected_push_text, expected_push_title',
    [
        pytest.param(
            None,
            '30',
            conftest.PARTNER_1,
            'because',
            {'code': 'not_allowed', 'message': 'not allowed'},
            403,
            'auto approved',
            '',
            '',
            '',
            id='not allowed',
        ),
        pytest.param(
            'eats-tips-payments',
            '30',
            conftest.PARTNER_1,
            'because',
            {'result': True},
            200,
            'rejected by B2P',
            -1,
            REJECT_PUSH['text']['default'],
            REJECT_PUSH['title']['default'],
            id='success',
        ),
        pytest.param(
            'eats-tips-payments',
            '32',
            conftest.PARTNER_1,
            'some comment 2',
            {'result': True},
            200,
            'rejected by B2P',
            -1,
            '',
            '',
            id='already rejected',
        ),
        pytest.param(
            'eats-tips-payments',
            '27',
            conftest.PARTNER_5,
            'because',
            {'result': True},
            200,
            'rejected by B2P',
            -1,
            REJECT_PUSH['text']['default'],
            REJECT_PUSH['title']['default'],
            id='success manual check',
        ),
        pytest.param(
            'eats-tips-payments',
            '26',
            conftest.PARTNER_2,
            'because',
            {'result': False},
            200,
            'precheck created',
            '',
            '',
            '',
            id='fail - precheck only',
        ),
        pytest.param(
            'eats-tips-payments',
            '99',
            '',
            'because',
            {'code': 'no_request', 'message': 'No such request'},
            404,
            None,
            '',
            '',
            '',
            id='no request',
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
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_sbp_callback_reject(
        taxi_eats_tips_withdrawal_web,
        web_app_client,
        web_context,
        mock_eats_tips_partners,
        patch,
        stq,
        service_name,
        order_id,
        partners_response,
        cancel_reason,
        expected_result,
        expected_status,
        expected_withdrawal_status,
        expected_admin_id,
        expected_push_text,
        expected_push_title,
):
    @patch(
        'eats_tips_withdrawal.api.callback_request_reject'
        '.get_src_service_name',
    )
    def get_service_name(request):
        return service_name

    @mock_eats_tips_partners('/v1/alias-to-object')
    async def _mock_alias_to_object(request: http.Request):
        return web.json_response(
            {'type': 'partner', 'partner': partners_response},
        )

    response = await web_app_client.post(
        '/v1/callback/reject-request',
        json={'order_id': order_id, 'cancel_reason': cancel_reason},
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
        if expected_result.get('result'):
            assert (
                withdrawal_row['comment'] == f'some error<br>{cancel_reason}'
                if order_id == '30'
                else cancel_reason
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
                'title': expected_push_title,
                'intent': 'withdrawal',
            },
        )
    else:
        assert not stq.eats_tips_partners_send_push.times_called
