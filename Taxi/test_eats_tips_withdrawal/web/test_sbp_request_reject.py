from aiohttp import web
import pytest

from eats_tips_withdrawal.generated.web import web_context as context
from test_eats_tips_withdrawal import conftest


REJECT_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['reject'][
    0
]


@pytest.mark.parametrize(
    'jwt, withdrawal_id, cancel_reason, expected_result, '
    'expected_status, expected_withdrawal_status, expected_admin_id,'
    'expected_push_text, expected_push_title',
    [
        pytest.param(
            conftest.JWT_USER_1,
            2,
            'because',
            {
                'code': 'not_allowed',
                'message': 'Method not allowed for this user group',
            },
            403,
            'sent to manual check',
            '',
            '',
            '',
            id='restricted for not admin',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            2,
            'because',
            {'result': True, 'message': 'Ok'},
            200,
            'manual rejected',
            27,
            REJECT_PUSH['text']['default'],
            REJECT_PUSH['title']['default'],
            id='success',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            3,
            'some comment',
            {'result': True, 'message': 'Ok'},
            200,
            'manual rejected',
            99,
            '',
            '',
            id='already rejected',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            1,
            'because',
            {'result': False, 'message': 'DB query error'},
            200,
            'precheck created',
            '',
            '',
            '',
            id='fail - precheck only',
        ),
        pytest.param(
            conftest.JWT_USER_27,
            99,
            'because',
            {'result': False, 'message': 'No such request'},
            200,
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
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_sbp_request_reject(
        taxi_eats_tips_withdrawal_web,
        mock_eats_tips_partners,
        web_context,
        stq,
        jwt,
        withdrawal_id,
        cancel_reason,
        expected_result,
        expected_status,
        expected_withdrawal_status,
        expected_admin_id,
        expected_push_text,
        expected_push_title,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    response = await taxi_eats_tips_withdrawal_web.post(
        '/v1/sbp/request-reject',
        json={'withdrawal_id': withdrawal_id, 'cancel_reason': cancel_reason},
        headers={'X-Chaevie-Token': jwt},
    )
    content = await response.json()
    assert content == expected_result
    assert response.status == expected_status

    if expected_withdrawal_status is None:
        return
    async with web_context.pg.master_pool.acquire() as conn:
        withdrawal_row = await conn.fetchrow(
            f'select * from eats_tips_withdrawal.withdrawals where '
            f'id=\'{withdrawal_id}\'',
        )
        if expected_result.get('result'):
            assert withdrawal_row['comment'] == cancel_reason
        assert withdrawal_row['admin'] == str(expected_admin_id)
        assert withdrawal_row['status'] == expected_withdrawal_status

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
