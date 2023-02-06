# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
    BLACKBOX_EDITSESSION_OP_ADD,
)
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_blackbox import BaseBlackboxRequestTestCase


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestEditsessionParse(BaseBlackboxRequestTestCase):

    def test_basic_editsession(self):
        self.set_blackbox_response_value('''{
            "authid":{"id":"1343389332357:1422501443:126","time":"1343389332357","ip":"84.201.166.67","host":"126"},
            "new-session":{"value":"3:session","domain":".yandex.ru","expires":0}}''')
        response = self.blackbox.editsession('add', 'sessionid', 'uid', 'ip', 'host')
        wait_for = {
            'authid': {
                'id': '1343389332357:1422501443:126',
                'time': '1343389332357',
                'ip': '84.201.166.67',
                'host': '126',
            },
            'new-session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'value': '3:session',
            },
        }
        eq_(response, wait_for)

    def test_ssl_editsession(self):
        self.set_blackbox_response_value('''{
            "authid":{"id":"1343389332357:1422501443:126","time":"1343389332357","ip":"84.201.166.67","host":"126"},
            "new-session":{"value":"3:session","domain":".yandex.ru","expires":0},
            "new-sslsession":{"value":"3:sslsession","domain":".yandex.ru","expires":1368715669,"secure":true}}''')
        response = self.blackbox.editsession('add', 'sessionid', 'uid', 'ip', 'host')
        wait_for = {
            'authid': {
                'id': '1343389332357:1422501443:126',
                'time': '1343389332357',
                'ip': '84.201.166.67',
                'host': '126',
            },
            'new-session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'value': '3:session',
            },
            'new-sslsession': {
                'domain': '.yandex.ru',
                'expires': 1368715669,
                'value': '3:sslsession',
                'secure': True,
            },
        }

        eq_(response, wait_for)

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''{"exception":{"value":"ACCESS_DENIED","id":21},
                       "error":"BlackBox error: Access denied: EditSession"}''')
        self.blackbox.editsession('add', 'sessionid', 'uid', 'ip', 'host')


@with_settings_hosts(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestEditsessionUrl(BaseBlackboxRequestTestCase):
    def test_editsession_call(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            get_login_id=True,
        )

        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sessionid': 'sessionid:',
                'create_time': TimeNow(),
                'get_login_id': 'yes',
            },
        )

    def test_editsession_call_guard_hosts_wo_duplicates(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru', 'passport.yandex.ru'],
        )
        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sessionid': 'sessionid:',
                'create_time': TimeNow(),
                'guard_hosts': 'passport.yandex.ru,mail.yandex.ru',
            },
        )

    def test_editsession_call_with_sslsessionid(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            sslsessionid='sslsessionid:',
            sessguard='guard',
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            request_id='req-id',
        )

        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sslsessionid': 'sslsessionid:',
                'sessionid': 'sessionid:',
                'create_time': TimeNow(),
                'sessguard': 'guard',
                'guard_hosts': 'passport.yandex.ru,mail.yandex.ru',
                'request_id': 'req-id',
            },
        )

    def test_editsession_call_with_specific_params(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            is_yastaff=True,
            is_betatester=True,
            social_id=33,
            new_default=2,
            password_check_time=11,
            is_lite=True,
        )

        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sessionid': 'sessionid:',
                'is_yastaff': '1',
                'is_betatester': '1',
                'social_id': '33',
                'new_default': '2',
                'password_check_time': '11',
                'is_lite': '1',
                'create_time': TimeNow(),
            },
        )

    def test_editsession_call_with_zero_password_check_time(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            is_yastaff=True,
            is_betatester=True,
            password_check_time=0,
        )

        check_url_contains_params(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'password_check_time': '0',
            },
        )

    def test_editsession_call_with_empty_password_check_time(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            is_yastaff=True,
            is_betatester=True,
            password_check_time=None,
        )

        check_url_contains_params(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
            },
        )

    @raises(TypeError)
    def test_editsession_without_args(self):
        Blackbox().build_editsession_request()

    @raises(TypeError)
    def test_editsession_without_uid(self):
        Blackbox().build_editsession_request(ip='127.0.0.1')

    @raises(TypeError)
    def test_editsession_without_ip(self):
        Blackbox().build_editsession_request(uid=1)

    @raises(TypeError)
    def test_editsession_without_sessionid(self):
        Blackbox().build_editsession_request(
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
        )

    @raises(TypeError)
    def test_editsession_without_op(self):
        Blackbox().build_editsession_request(uid=1, ip='127.0.0.1', session='session')

    @raises(ValueError)
    def test_editsession_with_wrong_op(self):
        Blackbox().build_editsession_request(
            uid=1,
            ip='127.0.0.1',
            op='invalid',
            host='yandex.ru',
            sessionid='session',
        )

    def test_editsession_yateam_internal(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            yateam_auth=True,
        )

        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sessionid': 'sessionid:',
                'create_time': TimeNow(),
                'yateam_auth': '1',
            },
        )

    def test_editsession_yateam_external(self):
        request_info = Blackbox().build_editsession_request(
            sessionid='sessionid:',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            uid=1,
            ip='127.0.0.1',
            host='yandex.ru',
            yateam_auth=False,
        )

        check_all_url_params_match(
            request_info.url,
            {
                'op': 'add',
                'uid': '1',
                'userip': '127.0.0.1',
                'host': 'yandex.ru',
                'format': 'json',
                'method': 'editsession',
                'sessionid': 'sessionid:',
                'create_time': TimeNow(),
                'yateam_auth': '0',
            },
        )

    def test_is_scholar(self):
        request_info = self.build_request_info(is_scholar=True)
        check_all_url_params_match(request_info.url, self.editsession_params(is_scholar='1'))

        request_info = self.build_request_info(is_scholar=False)
        check_all_url_params_match(request_info.url, self.editsession_params())

        request_info = self.build_request_info()
        check_all_url_params_match(request_info.url, self.editsession_params())

    def build_request_info(self, **kwargs):
        defaults = dict(
            host='yandex.ru',
            ip='127.0.0.1',
            op=BLACKBOX_EDITSESSION_OP_ADD,
            sessionid='sessionid:',
            uid=1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Blackbox().build_editsession_request(**kwargs)

    def editsession_params(self, **kwargs):
        return self.base_params(
            dict(
                create_time=TimeNow(),
                format='json',
                host='yandex.ru',
                method='editsession',
                op='add',
                sessionid='sessionid:',
                uid='1',
                userip='127.0.0.1',
            ),
            **kwargs
        )
