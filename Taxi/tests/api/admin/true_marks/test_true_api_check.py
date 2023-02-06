from aiohttp import web
from stall.client.true_client import TrueClient, trueclient_dict


async def test_success(api, dataset, tap, ext_api):
    with tap.plan(6, 'Успешная сходили в True API'):
        company = await dataset.company()
        user = await dataset.user(company=company)
        api_response = [{'cisInfo': {'status': 'EMITTED_NO'}}]
        mark_requested = 'somerandomthing'
        token = 'lolkekcheburek'
        await dataset.stash(
            name=f'true_mark_token_1c_{company.company_id}',
            value={'true_mark_token': token},
        )
        true_client = TrueClient(company_id=company.company_id)
        trueclient_dict[company.company_id] = true_client

        async def handler(req):  # pylint: disable=unused-argument
            tap.ok(
                token in req.headers['Authorization'],
                'Токен в заголовке',
            )
            tap.ok(
                mark_requested in await req.json(),
                'Марка в теле запроса',
            )
            return web.json_response(
                status=200,
                data=api_response,
            )
        t = await api(user=user)
        async with await ext_api(true_client, handler):
            await t.post_ok(
                'api_admin_true_marks_true_api_check',
                json={
                    'true_mark': mark_requested,
                    'company_id': company.company_id,
                }
            )

        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('true_api_json_response', api_response)
