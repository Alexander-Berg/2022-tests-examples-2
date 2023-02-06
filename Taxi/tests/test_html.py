def test_content():
    from easytap import Tap

    tap = Tap(18)

    tap.import_ok('easytaphttp', 'import easytaphttp')

    import easytaphttp

    class agent(easytaphttp.WebTestAgent):
        def request(self, method, url, headers, body, proto='1.0'):
            tap.eq_ok(url, 'http://google.com', 'url')
            tap.eq_ok(method, 'GET', 'method')

            return {
                'status': 200,
                'headers': {
                    'content-Type': 'text/html; charset=UTF-8'
                },
                'body': """
                    <html>
                        <head>
                            <title>Тестовая страница</title>
                        </head>
                        <body>
                            <p class="one">one p</p>
                            <p class="two">two p</p>
                        </body>
                    </html>
                """
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)
    t.content_type_like(r'text/html')

    t.html_has('body/p')
    t.html_hasnt('body/fieldset')

    t.html_is('body/p[@class="one"]', 'one p')
    t.html_is('body/p/@class', 'one')
    t.html_isnt('body/p[@class="one"]', 'two p')
    t.html_isnt('body/p/@class', 'one p')

    t.html_like('body/p[@class="two"]', r'two\sp')
    t.html_like('body/p/@class', r'tw[o]')

    t.html_unlike('body/p[@class="one"]', r'two\sp')
    t.html_unlike('body/p/@class', r'tW[o]')
    t.html_unlike('body/fieldset', r'tW[o]')

    assert tap.done_testing()

