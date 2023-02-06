# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.exceptions import InvalidIpHeaderError
from passport.backend.core.portallib import (
    detect_user_agent,
    get_ipreg,
    get_net,
    get_uatraits,
    is_yandex_ip,
    is_yandex_server_ip,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from werkzeug.datastructures import Headers


@with_settings()
class TestIpReg(PassportTestCase):
    def setUp(self):
        self.headers = Headers([('Ya-Client-Accept-Language', 'ru'),
                                ('Ya-Client-Cookie', 'sessionid=foo'),
                                ('Ya-Consumer-Client-Ip', '1.1.1.1')])

    def test_ipreg(self):
        ok_(get_ipreg())

    def test_get_net(self):
        actual = get_net('8.8.8.8')

        ok_(not actual['is_yandex'])
        eq_(actual['real_ip'], '8.8.8.8')

        # текущий ip passport-dev
        actual = get_net('87.250.235.4')
        ok_(actual['is_yandex'])
        eq_(actual['real_ip'], '87.250.235.4')

    @raises(InvalidIpHeaderError)
    def test_get_net_invalid_header(self):
        get_net('8.8.8.8, 1.2.3.4', self.headers)

    def test_is_yandex_ip(self):
        eq_(is_yandex_ip(ip='37.9.101.188'), True)
        eq_(is_yandex_ip(ip='8.8.8.8'), False)
        eq_(is_yandex_ip(ip='127.0.0.1'), False)

    def test_is_yandex_server_ip(self):
        eq_(is_yandex_server_ip(ip='213.180.204.3'), True)
        eq_(is_yandex_server_ip(ip='37.9.101.188'), False)
        eq_(is_yandex_server_ip(ip='8.8.8.8'), False)
        eq_(is_yandex_server_ip(ip='127.0.0.1'), False)


class TestUatraits(PassportTestCase):

    def test_get_uatraits(self):
        ok_(get_uatraits())

    def test_detect_user_agent(self):
        headers_values = (
            Headers([
                (
                    'Ya-Client-User-Agent',
                    'Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10',
                ),
            ]),
            {
                'Ya-Client-User-Agent': 'Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10',
            },
            {
                'User-Agent': u'Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10',
            },
            {
                'User-Agent': u'АБВ Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10',
            },
        )
        for headers in headers_values:
            user_agent_info = detect_user_agent(headers)
            eq_(user_agent_info['OSFamily'], 'Java')
            eq_(user_agent_info['isMobile'], True)
            eq_(user_agent_info['BrowserName'], 'OperaMini')

    def test_detect_none_user_agent(self):
        headers_values = (
            Headers([
                (
                    'Ya-Client-User-Agent',
                    None,
                ),
            ]),
            {
                'Ya-Client-User-Agent': None,
            },
            {
                'User-Agent': None,
            },
        )
        for headers in headers_values:
            user_agent_info = detect_user_agent(headers)
            eq_(user_agent_info, {})
