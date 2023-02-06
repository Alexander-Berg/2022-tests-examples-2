from libstall import json_pp as json


async def test_over_fail(api):
    t = await api()
    t.tap.plan(4)
    await t.post_ok('api_developer_over', json={})
    t.status_is(403, diag=True)
    t.json_is('code', 'ER_ACCESS')
    t.json_is('message', 'Access denied')
    t.tap()


async def test_over_ok(api):
    t = await api()

    t.tap.plan(5)
    await t.post_ok('api_developer_over', json={'foo': {'bar': 'baz'}})
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('message', 'поле message есть')

    res = json.loads(t.res['json']['message'])

    t.tap.eq(res, {'over_test': 'baz'}, 'значение over попало в стеш')

    t.tap()


async def test_over_failkey(api):
    t = await api()

    t.tap.plan(4)
    await t.post_ok('api_developer_over', json={'foo': {'bar': 'wrong_key'}})
    t.status_is(403, diag=True)
    t.json_is('code', 'ER_ACCESS')
    t.json_has('message', 'Access denied')

    t.tap()
