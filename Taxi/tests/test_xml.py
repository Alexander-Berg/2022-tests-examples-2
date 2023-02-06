def test_content():
    from easytap import Tap

    tap = Tap(34)

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
                'body': """<?xml version="1.0" encoding="UTF-8"?>
                    <CATALOG>
                        <CD class="first">
                            <TITLE>Empire Burlesque</TITLE>
                            <ARTIST>Bob Dylan</ARTIST>
                            <COUNTRY>USA</COUNTRY>
                            <COMPANY>Columbia</COMPANY>
                            <PRICE>10.90</PRICE>
                            <YEAR>1985</YEAR>
                        </CD>
                        <CD class="second">
                            <TITLE>Hide your heart</TITLE>
                            <ARTIST>Bonnie Tyler</ARTIST>
                            <COUNTRY>UK</COUNTRY>
                            <COMPANY>CBS Records</COMPANY>
                            <PRICE>9.90</PRICE>
                            <YEAR>1988</YEAR>
                        </CD>
                    </CATALOG>
                """
            }

    t = easytaphttp.WebTest(tap, agent())
    tap.ok(t, 'test instance created')

    t.request_ok('get', 'http://google.com')
    t.status_is(200)
    t.content_type_like(r'text/html')

    t.xml_has('CD')
    t.xml_has('CD[@class="first"]')
    t.xml_has('CD/TITLE')
    t.xml_hasnt('CD/TITLE1')
    t.xml_hasnt('CD[@class="first1"]')
    t.xml_hasnt('foo/bar/baz')

    t.xml_is('CD/TITLE', 'Hide your heart')
    t.xml_is('(CD/TITLE)[2]', 'Hide your heart')
    t.xml_is('(CD/TITLE)[1]', 'Empire Burlesque')
    t.xml_is('CD/@class', 'first')
    t.xml_is('CD[@class="second"]/PRICE', '9.90')

    t.xml_isnt('CD/TITLE', 'Hide1 your heart')
    t.xml_isnt('(CD/TITLE)[1]', 'Hide your heart')
    t.xml_isnt('(CD/TITLE)[2]', 'Empire Burlesque')
    t.xml_isnt('CD/@class', 'first1')
    t.xml_isnt('CD[@class="second"]/PRICE', '10.90')
    t.xml_isnt('foo/bar/baz', '10.90')

    t.xml_like('CD/TITLE', 'Hide.*heart')
    t.xml_like('(CD/TITLE)[2]', 'Hide.*heart')
    t.xml_like('(CD/TITLE)[1]', 'Empire.*lesque')
    t.xml_like('CD/@class', 'fi[rR]st')
    t.xml_like('CD[@class="second"]/PRICE', r'\d\.90')

    t.xml_unlike('CD/TITLE', 'Hide.*heart1')
    t.xml_unlike('(CD/TITLE)[1]', 'Hide.*heart')
    t.xml_unlike('(CD/TITLE)[2]', 'Empire.*lesque')
    t.xml_unlike('CD/@class', 'fiPst')
    t.xml_unlike('CD[@class="second"]/PRICE', r'\D\.90')
    assert tap.done_testing()

