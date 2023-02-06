from urllib.parse import urlencode

import pytest


@pytest.mark.parametrize('seregaapi', ['no', 'yes'])
async def test_x_www_form(http_api, tap, cfg, seregaapi):
    cfg.set('seregaapi', seregaapi)
    with tap.plan(18):
        t = await http_api()

        await t.post_ok('api_developer_form',
                        form={'field1': 'Здравствуй', 'field2': 'мир'})
        t.status_is(200, diag=True)
        t.json_is('code', 'TEST')
        t.json_is('received_data.field1', ['Здравствуй'])
        t.json_is('received_data.field2', ['мир'])

        await t.post_ok(
            'api_developer_form',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; '
                                'charset=cp500',
            },
            data=urlencode({
                'field1': 'Здравствуй',
                'field2': 'мир'}).encode('cp500'),
        )
        t.status_is(200, diag=True, desc='Not only UTF-8 is supported')
        t.json_is('code', 'TEST')
        t.json_is('received_data.field1', ['Здравствуй'])
        t.json_is('received_data.field2', ['мир'])

        await t.post_ok(
            'api_developer_form',
            data=b'\x80\x00',  # byte string that cannot be UTF-8 decoded
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        t.status_is(400, diag=True,
                    desc='Incorrect data does not break application')
        t.json_is('code', 'BAD_REQUEST')
        t.json_is('message', 'Bad request')

        await t.post_ok(
            'api_developer_form', data=b'abrakadabra',
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        t.status_is(200, diag=True,
                    desc='Incorrect data does not break application')
        t.json_is('code', 'TEST')
        t.json_is('received_data', {})
