def test_wsgi():
    from easytap import Tap

    requests = []
    tap = Tap(8)

    tap.import_ok('easytaphttp.wsgi', 'import easytaphttp.wsgi')

    import easytaphttp.wsgi

    def app(env, strt):
        requests.append(env)

        strt('200 OK', [
            ('Content-Type', 'text/plain'),
        ])
        return ['OK']

    t = easytaphttp.wsgi.WSGITest(tap, app)
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://test.domain?a=b', form={'c': 'd'})
    t.status_is(200)
    t.content_type_is('text/plain')
    t.content_type_isnt('text/plain2')
    t.content_type_like(r'^text/')
    t.content_type_unlike(r'^application/')

    assert tap.done_testing()
