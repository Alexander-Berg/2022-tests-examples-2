# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    BaseBlackboxError,
    Blackbox,
    parse_blackbox_lrandoms_response,
)
from passport.backend.core.test.test_utils import with_settings

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestLRandomsParse(BaseBlackboxRequestTestCase):

    def test_basic_lrandoms(self):
        self.set_blackbox_response_value(b'''
            1000001;000000111111222222333333444444555555666666777777888888999999xxxx;1297400401
            1000002;000000111111222222333333444444555555666666777777888888999999yyyy;1297400401
        '''.strip())

        response = self.blackbox.lrandoms()
        eq_(len(response), 2)
        lrandoms = [
            {
                'id': '1000001',
                'created_timestamp': 1297400401,
                'body': '000000111111222222333333444444555555666666777777888888999999xxxx',
            },
            {
                'id': '1000002',
                'created_timestamp': 1297400401,
                'body': '000000111111222222333333444444555555666666777777888888999999yyyy',
            },
        ]
        eq_(response, lrandoms)

    @raises(BaseBlackboxError)
    def test_lrandoms_wrong_format_response(self):
        parse_blackbox_lrandoms_response(b'catch me error :-)')

    @raises(BaseBlackboxError)
    def test_lrandoms_wrong_int_format_response(self):
        parse_blackbox_lrandoms_response(b'1000001;0000001111112222223333334;error')


@with_settings(
    BLACKBOX_URL='http://test.local/',
)
class TestBlackboxRequestLRandomsUrl(BaseBlackboxTestCase):
    def test_basic_lrandoms(self):
        request_info = Blackbox().build_lrandoms_request()
        eq_(request_info.url, 'http://test.local/lrandoms.txt')
