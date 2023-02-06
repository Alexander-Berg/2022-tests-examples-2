import json


def test_cookie():
    from easytap import Tap

    tap = Tap(8)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            return {
                'status': 200,
                'headers': {
                    'content-Type': 'application/json; charset=UTF-8',
                    'Set-Cookie': 'a=b; Path=/'
                },
                'body': json.dumps({
                    'cookie': headers.get('Cookie', '')
                })
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)

    t.json_is('cookie', '', 'no cookies received')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)
    t.json_is('cookie', 'a=b', 'no cookies received')

    assert tap.done_testing()



