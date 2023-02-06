def test_content_type():
    from easytap import Tap

    tap = Tap(10, 'content-type tests')

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'POST', 'method')

            return {
                'status': 200,
                'headers': {
                    'content-Type': 'application/json; charset=UTF-8'
                }

            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('post', 'http://google.com')
    t.status_is(200)
    t.content_type_is('application/json; charset=UTF-8')
    t.content_type_isnt('application/json; charset=UTF-9')
    t.content_type_like('.*json; charset=UTF-8')
    t.content_type_unlike('text/html')

    assert tap.done_testing()


