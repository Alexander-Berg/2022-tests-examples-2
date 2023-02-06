from aiohttp import web
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


async def tasks(context):
    async with context.pg.master_pool.acquire() as connection:
        return await connection.fetch(
            'SELECT * FROM eats_tips_admin.transactions_report_task',
        )


async def test_status_200(
        web_context,
        stq,
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_personal,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {'partners_ids': conftest.USER_ID_1}
        return web.json_response(
            {
                'places': [
                    {
                        'info': conftest.PLACE_1,
                        'partners': [
                            {
                                'partner_id': conftest.USER_ID_1,
                                'roles': ['admin', 'recipient'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
        )

    @mock_personal('/v1/emails/find')
    async def _mock_emails_find(request: http.Request):
        return web.json_response(
            {'id': 'A1234567890', 'value': request.json['value']},
        )

    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': conftest.JWT_USER_1,
            'X-Idempotency-Token': 'X-Idempotency-Token',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 200
    content1 = await response.json()
    assert stq.eats_tips_payments_transactions_report.times_called == 1

    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': conftest.JWT_USER_1,
            'X-Idempotency-Token': 'X-Idempotency-Token',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 200
    assert len(await tasks(web_context)) == 1
    content2 = await response.json()
    assert content1 == content2
    assert stq.eats_tips_payments_transactions_report.times_called == 1


async def test_status_400(
        taxi_eats_tips_admin_web, stq, mock_eats_tips_partners,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {'partners_ids': conftest.USER_ID_1}
        return web.json_response(
            {
                'places': [
                    {
                        'info': conftest.PLACE_1,
                        'partners': [
                            {
                                'partner_id': conftest.USER_ID_1,
                                'roles': ['recipient'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
        )

    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': conftest.JWT_USER_1,
            'X-Idempotency-Token': 'X-Idempotency-Token',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 400
    assert stq.eats_tips_payments_transactions_report.times_called == 0


async def test_status_401(taxi_eats_tips_admin_web, stq):
    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': 'unauthorized',
            'X-Idempotency-Token': 'X-Idempotency-Token',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 401
    assert stq.eats_tips_payments_transactions_report.times_called == 0


async def test_status_429(
        web_context,
        stq,
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_personal,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {'partners_ids': conftest.USER_ID_1}
        return web.json_response(
            {
                'places': [
                    {
                        'info': conftest.PLACE_1,
                        'partners': [
                            {
                                'partner_id': conftest.USER_ID_1,
                                'roles': ['recipient', 'admin'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
        )

    @mock_personal('/v1/emails/find')
    async def _mock_emails_find(request: http.Request):
        return web.json_response(
            {'id': 'A1234567890', 'value': request.json['value']},
        )

    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': conftest.JWT_USER_1,
            'X-Idempotency-Token': 'X-Idempotency-Token',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 200
    assert len(await tasks(web_context)) == 1
    assert stq.eats_tips_payments_transactions_report.times_called == 1

    response = await taxi_eats_tips_admin_web.post(
        '/v1/transactions/report-task',
        headers={
            'X-Chaevie-Token': conftest.JWT_USER_1,
            'X-Idempotency-Token': 'X-Idempotency-Token2',
        },
        json={'email': 'test@test.test'},
    )
    assert response.status == 429
    assert len(await tasks(web_context)) == 1
    assert stq.eats_tips_payments_transactions_report.times_called == 1
