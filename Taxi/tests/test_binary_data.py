# small but correct PNG file
PNG_FILE = (
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52'
    b'\x00\x00\x01\x00\x00\x00\x01\x00\x01\x03\x00\x00\x00\x66\xBC\x3A'
    b'\x25\x00\x00\x00\x03\x50\x4C\x54\x45\xB5\xD0\xD0\x63\x04\x16\xEA'
    b'\x00\x00\x00\x1F\x49\x44\x41\x54\x68\x81\xED\xC1\x01\x0D\x00\x00'
    b'\x00\xC2\xA0\xF7\x4F\x6D\x0E\x37\xA0\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\xBE\x0D\x21\x00\x00\x01\x9A\x60\xE1\xD5\x00\x00\x00\x00\x49'
    b'\x45\x4E\x44\xAE\x42\x60\x82'
)


def test_png():
    from easytap import Tap

    tap = Tap(6)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class MyAgent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'POST', 'method')

            return {
                'status': 200,
                'body': PNG_FILE,
                'headers': {'Conent-Type': 'image/png'},
            }

    t = easytaphttp.WebTest(tap, MyAgent())
    tap.ok(t, 'test instance created')

    t.request_ok('POST', 'http://google.com',
                 data=PNG_FILE,
                 headers={'Conent-Type': 'image/png'})
    t.status_is(200)

    assert tap.done_testing()
