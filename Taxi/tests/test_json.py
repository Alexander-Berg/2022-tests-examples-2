def test_json():
    from easytap import Tap

    tap = Tap(13)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp
    import json

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'GET', 'method')

            return {
                'status': 200,
                'body': json.dumps({
                    'hello': 'world',
                    'foo': {'bar': ('baz', 'help', 123)}
                })
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)

    t.json_has('foo.bar.0')
    t.json_hasnt('foo.bar.111')

    t.json_like('foo.bar.2', r'[23]')
    t.json_like('hello', r'w[oO]rld')

    t.json_unlike('hello', r'w[0]rld')

    t.json_is('hello', 'world')
    t.json_isnt('hello', 'world1')

    assert tap.done_testing()


def test_json_as_blob():
    from easytap import Tap

    tap = Tap(7)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp
    import json

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'GET', 'method')

            return {
                'status': 200,
                'body': json.dumps({
                    'hello': 'world',
                    'foo': {'bar': ('baz', 'help', 123)}
                }).encode()
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)

    t.json_has('foo.bar.0')

    assert tap.done_testing()


