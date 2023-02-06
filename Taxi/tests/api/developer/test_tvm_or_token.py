async def test_notoken(tap, api):
    with tap.plan(5):
        t = await api()

        await t.get_ok('api_developer_tvm_token')
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied', 'сообщение')
        t.json_is('details.message',
                  'Can not find valid service token or TVM2 ticket',
                  'уточнение')


async def test_wrong_token(tap, api, uuid):
    with tap.plan(5):
        t = await api()
        await t.get_ok('api_developer_tvm_token',
                       headers={'Authorization': f'bearer {uuid()}'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied', 'сообщение')
        t.json_is('details.message',
                  'Can not find valid service token or TVM2 ticket',
                  'уточнение')


async def test_valid_token(tap, api, cfg):
    with tap.plan(4):
        t = await api()

        token = cfg('web.external.tokens.0')
        await t.get_ok('api_developer_tvm_token',
                       headers={'Authorization': f'bearer {token}'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('message', 'okay', 'сообщение')


#@pytest.mark.skip(reason="no way of currently testing this")
async def test_wrong_tvm(tap, api, uuid):
    with tap.plan(3):
        t = await api()

        await t.get_ok('api_developer_tvm_token',
                       headers={'X-Ya-Service-Ticket': uuid()})
        t.status_is(504, diag=True)
        t.json_is('code', 'ER_TVM', 'код')


async def test_company_token(tap, api, dataset):
    with tap.plan(4, 'Токен из модели. Компания.'):

        company = await dataset.company()
        t = await api()

        await t.get_ok('api_developer_tvm_token',
                       headers={'Authorization': f'bearer {company.token}'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('message', 'okay', 'сообщение')


async def test_company_token_secret(tap, api, uuid, dataset):
    with tap.plan(7, 'Проверка отключения через секрет'):

        company = await dataset.company()
        old_token = company.token
        t = await api()

        await t.get_ok('api_developer_tvm_token',
                       headers={'Authorization': f'bearer {old_token}'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('message', 'okay', 'сообщение')

        company.secret = uuid()
        tap.ok(await company.save(), 'Сохранили с новым секретом')

        await t.get_ok('api_developer_tvm_token',
                       headers={'Authorization': f'bearer {old_token}'})
        t.status_is(403, diag=True)
