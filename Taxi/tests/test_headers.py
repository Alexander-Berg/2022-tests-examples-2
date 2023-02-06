def test_headers():
    from easytap import Tap
    tap = Tap(19)
    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'GET', 'method')

            return {
                'status': 200,
                'headers': {
                    'Foo': ('bar', 'baz'),
                    'Hello': 'world'
                }
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')

    t.header_has('foo')
    t.header_has('Hello')
    t.header_hasnt('Bar')

    t.header_is('hello', 'world')
    t.header_is('foo', 'bar')
    t.header_is('foo', 'baz')

    t.header_isnt('hello', 'world1')
    t.header_isnt('foo', 'bar1')
    t.header_isnt('foo', 'baz1')

    t.header_like('foo', '[Bb]ar')
    t.header_like('foo', '[Bb]az')
    t.header_like('Hello', 'w[oO]rld')

    t.header_unlike('foo1', '[Bb]ar')
    t.header_unlike('foo', '[Bb]ar1')
    assert tap.done_testing()


