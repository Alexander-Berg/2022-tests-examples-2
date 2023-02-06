import json

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from taxi.stq import async_worker_ng

from eats_tips_payments.stq import transactions_report

ORDER_ID = 'uuid-1234'
USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
PLACE_1_ID = 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e'
PLACE_1 = {'id': PLACE_1_ID, 'title': 'заведение'}
PERSONAL_EMAIL_ID = 'ad75d457e3804s11aee24220av6925de'


@pytest.mark.config(
    EATS_TIPS_PAYMENTS_TRANSACTIONS_REPORT_SENDER={
        'account_slug': 'tips',
        'campaign_slug': 'WKAHBUB4-X9Y',
        'user': '0ca3a027ceeb46f9b4121d41d7f471d2',
    },
)
async def test_correct_task(
        stq3_context, mockserver, mock_eats_tips_partners, mock_sender,
):
    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        return web.json_response(
            {
                'places': [
                    {
                        'info': PLACE_1,
                        'partners': [
                            {
                                'partner_id': USER_ID_1,
                                'roles': ['admin', 'recipient'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
        )

    @mock_eats_tips_partners('/v1/partner/list')
    async def _mock_partner_list(request: http.Request):
        return web.json_response(
            {
                'has_more': False,
                'partners': [
                    {
                        'info': {
                            'id': USER_ID_1,
                            'display_name': 'ванька-встанька',
                            'full_name': 'Иван Иванов',
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '8',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
                        },
                        'places': [
                            {
                                'alias': '8',
                                'place_id': PLACE_1['id'],
                                'confirmed': True,
                                'show_in_menu': False,
                                'roles': ['admin', 'recipient'],
                                'address': '',
                                'title': '',
                            },
                        ],
                    },
                ],
            },
        )

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _mock_retrieve_email(request: http.Request):
        return {'id': PERSONAL_EMAIL_ID, 'value': 'email@email.com'}

    @mock_sender(r'/api/0/tips/transactional/WKAHBUB4-X9Y/send')
    def mock_send(request: http.Request):
        return {
            'result': {
                'status': 'ok',
                'task_id': 'task_id',
                'message_id': 'message_id',
            },
        }

    await transactions_report.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=ORDER_ID,
            exec_tries=1,
            reschedule_counter=1,
            queue='eats_tips_payments_transactions_report',
        ),
        order_id=ORDER_ID,
        **{'partner_id': 'partner_id', 'personal_email_id': PERSONAL_EMAIL_ID},
    )

    assert mock_send.times_called == 1

    async with stq3_context.pg.replica_pool.acquire() as connection:
        rows = list(
            await connection.fetch(
                'select * from eats_tips_payments.transactions_reports',
            ),
        )

    assert len(rows) == 1
    assert rows[0]['task_id'] == ORDER_ID
    assert json.loads(rows[0]['sender_response']) == {
        'status': 'ok',
        'task_id': 'task_id',
        'message_id': 'message_id',
    }
