def test_content():
    from easytap import Tap

    tap = Tap(10)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'POST', 'method')

            return {
                'status': 402,
                'headers': {
                    'content-Type': 'application/json; charset=UTF-8'
                },
                'body': 'Hello, world'
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('post', 'http://google.com', form={'foo': 'bar'})
    t.status_is(402, diag=True)

    t.content_is('Hello, world')
    t.content_isnt('Hello, World')
    t.content_like('[wW]orld')
    t.content_unlike('Uorld')

    assert tap.done_testing()


