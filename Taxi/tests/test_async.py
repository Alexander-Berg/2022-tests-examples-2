import pytest


@pytest.mark.asyncio
async def test_content():
    from easytap import Tap

    tap = Tap(13)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        mode = 'async'

        async def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'GET', 'method')

            return {
                'status': 200,
                'headers': {
                    'content-Type': 'application/json; charset=UTF-8'
                },
                'body': 'Hello, world'
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    await t.request_ok('get', 'http://google.com')
    t.status_is(200)

    t.content_is('Hello, world')
    t.content_isnt('Hello, World')
    t.content_like('[wW]orld')
    t.content_unlike('Uorld')

    await t.get_ok('http://google.com')

    assert tap.done_testing()



