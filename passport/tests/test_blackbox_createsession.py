# -*- coding: utf-8 -*-
import time

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
)
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .test_blackbox import BaseBlackboxRequestTestCase


basic_createsession_args = (1, '127.0.0.1', 'yandex.ru', 5)


@with_settings_hosts(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestCreatesessionParse(BaseBlackboxRequestTestCase):

    def test_basic_createsession(self):
        self.set_blackbox_response_value('''{
            "authid":{"id":"1343389332357:1422501443:126","time":"1343389332357","ip":"84.201.166.67","host":"126"},
            "new-session":{"value":"2:session","domain":".yandex.ru","expires":0}}''')
        response = self.blackbox.createsession(*basic_createsession_args)
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
                'value': '2:session',
            },
        }
        eq_(response, wait_for)

    def test_ssl_createsession(self):
        self.set_blackbox_response_value('''{
            "authid":{"id":"1343389332357:1422501443:126","time":"1343389332357","ip":"84.201.166.67","host":"126"},
            "new-session":{"value":"2:session","domain":".yandex.ru","expires":0},
            "new-sslsession":{"value":"2:sslsession","domain":".yandex.ru","expires":1368715669,"secure":true}}''')
        response = self.blackbox.createsession(*basic_createsession_args)
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
                'value': '2:session',
            },
            'new-sslsession': {
                'domain': '.yandex.ru',
                'expires': 1368715669,
                'value': '2:sslsession',
                'secure': True,
            },
        }

        eq_(response, wait_for)

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value('''{"exception":{"value":"ACCESS_DENIED","id":21},
                       "error":"BlackBox error: Access denied: CreateSession"}''')
        self.blackbox.createsession(*basic_createsession_args)


@with_settings_hosts(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestCreatesessionUrl(BaseBlackboxRequestTestCase):
    def test_createsession_call(self):
        request_info = Blackbox().build_createsession_request(
            uid=1,
            ip='127.0.0.1',
            keyspace='yandex.ru',
            ttl='5',
            is_lite=True,
            get_login_id=True,
        )

        check_all_url_params_match(
            request_info.url,
            {
                'uid': '1',
                'userip': '127.0.0.1',
                'host_id': '7f',
                'ver': '3',
                'format': 'json',
                'method': 'createsession',
                'have_password': '0',
                'is_lite': '1',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'get_login_id': 'yes',
            },
        )

    def test_createsession_kwargs(self):
        request_info = Blackbox().build_createsession_request(
            uid=1,
            ip='127.0.0.1',
            keyspace='yandex.ru',
            ttl='5',
            password_check_time=time.time(),
            is_yastaff=True,
            is_betatester=True,
            social_id=3,
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru'],
            request_id='req-id',
        )

        check_all_url_params_match(
            request_info.url,
            {
                'uid': '1',
                'userip': '127.0.0.1',
                'host_id': '7f',
                'ver': '3',
                'password_check_time': TimeNow(),
                'format': 'json',
                'method': 'createsession',
                'is_yastaff': '1',
                'is_betatester': '1',
                'social_id': '3',
                'is_lite': '0',
                'have_password': u'0',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport.yandex.ru,mail.yandex.ru',
                'request_id': 'req-id',
            },
        )

    def test_createsession_guard_hosts_wo_duplicates(self):
        request_info = Blackbox().build_createsession_request(
            uid=1,
            ip='127.0.0.1',
            keyspace='yandex.ru',
            ttl='5',
            guard_hosts=['passport.yandex.ru', 'mail.yandex.ru', 'passport.yandex.ru'],
        )
        check_all_url_params_match(
            request_info.url,
            {
                'uid': '1',
                'userip': '127.0.0.1',
                'host_id': '7f',
                'ver': '3',
                'format': 'json',
                'method': 'createsession',
                'is_lite': '0',
                'have_password': u'0',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport.yandex.ru,mail.yandex.ru',
            },
        )

    @raises(TypeError)
    def test_createsession_without_args(self):
        Blackbox().build_createsession_request()

    @raises(TypeError)
    def test_createsession_without_uid(self):
        Blackbox().build_createsession_request(ip='127.0.0.1')

    @raises(TypeError)
    def test_createsession_without_ip(self):
        Blackbox().build_createsession_request(uid=1)

    def test_createsession_with_different_version(self):
        request_info = Blackbox().build_createsession_request(
            1,
            '127.0.0.1',
            'yandex.ru',
            5,
            password_check_time=100,
            ver=5,
        )
        check_url_contains_params(
            request_info.url,
            {
                'ver': '5',
                'uid': '1',
                'userip': '127.0.0.1',
                'password_check_time': '100',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
            },
        )

    def test_createsession_yateam_internal(self):
        request_info = Blackbox().build_createsession_request(
            1,
            '127.0.0.1',
            'yandex.ru',
            5,
            yateam_auth=True,
        )
        check_url_contains_params(
            request_info.url,
            {
                'ver': '3',
                'uid': '1',
                'userip': '127.0.0.1',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
                'yateam_auth': '1',
            },
        )

    def test_createsession_yateam_external(self):
        request_info = Blackbox().build_createsession_request(
            1,
            '127.0.0.1',
            'yandex.ru',
            5,
            yateam_auth=False,
        )
        check_url_contains_params(
            request_info.url,
            {
                'ver': '3',
                'uid': '1',
                'userip': '127.0.0.1',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'create_time': TimeNow(),
                'yateam_auth': '0',
            },
        )

    def test_is_scholar(self):
        request_info = self.build_request_info(is_scholar=True)
        check_all_url_params_match(request_info.url, self.createsession_params(is_scholar='1'))

        request_info = self.build_request_info(is_scholar=False)
        check_all_url_params_match(request_info.url, self.createsession_params())

        request_info = self.build_request_info()
        check_all_url_params_match(request_info.url, self.createsession_params())

    def build_request_info(self, **kwargs):
        defaults = dict(
            ip='127.0.0.1',
            is_lite=True,
            keyspace='yandex.ru',
            ttl='5',
            uid=1,
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Blackbox().build_createsession_request(**kwargs)

    def createsession_params(self, **kwargs):
        return self.base_params(
            dict(
                auth_time=TimeNow(as_milliseconds=True),
                create_time=TimeNow(),
                format='json',
                have_password='0',
                host_id='7f',
                is_lite='1',
                keyspace='yandex.ru',
                method='createsession',
                ttl='5',
                uid='1',
                userip='127.0.0.1',
                ver='3',
            ),
            **kwargs
        )
