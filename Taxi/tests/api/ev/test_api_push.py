from stall import cfg


# pylint: disable=unused-argument
async def test_push_wrong_token(mongo, uuid, api):
    t = await api()
    t.tap.plan(11)

    await t.post_ok('api_ev_push', json=[],
                    desc='без заголовка')

    t.status_is(403, diag=True)
    t.json_is('code', 'ER_AUTH')
    t.json_is('message', 'Wrong auth token')


    headers = {
        'Authorization': 'token ' + uuid()
    }

    await t.post_ok('api_ev_push', headers=headers, json=[],
                    desc='неверный токен')
    t.status_is(403, diag=True)
    t.json_is('code', 'ER_AUTH')
    t.json_is('message', 'Wrong auth token')


    headers = {
        'Authorization': uuid()
    }

    await t.post_ok('api_ev_push', headers=headers, json=[],
                    desc='неверный формат строки токена')
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')
    t.tap()

async def test_push(mongo, api): # pylint: disable=unused-argument
    t = await api()
    t.tap.plan(10)

    headers = {
        'Authorization': 'token ' + cfg('event.push.tokens.0')
    }

    await t.post_ok('api_ev_push', headers=headers, json=[],
                    desc='пустой список')
    t.status_is(200, diag=True)
    t.content_type_like('^application/json', 'content_type')
    t.json_is('code', 'OK', 'code')
    t.json_is('message', 'Success', 'message')

    event = {
        'key': ['hello', 'world'],
        'data': {
            'hello': 'world',
        }
    }
    await t.post_ok('api_ev_push',
                    json=[event],
                    headers=headers,
                    desc='одно событие')
    t.status_is(200, diag=True)
    t.content_type_like('^application/json', 'content_type')
    t.json_is('code', 'OK', 'code')
    t.json_is('message', 'Success', 'message')
    t.tap()
