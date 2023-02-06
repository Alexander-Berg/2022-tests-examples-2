# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    mock_headers,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.mail_apis.faker import husky_delete_user_response
from passport.backend.core.dbmanager.manager import DBError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)


@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=False,
)
class TestApi(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants())

        blackbox_response = blackbox_userinfo_response(uid=1, login='test')
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)
        self.env.db.serialize(blackbox_response)

        self.apis = {
            'post': [
                ('/1/account/1/', {'is_enabled': '0'}),
                ('/1/account/1/karma/', {'suffix': '100'}),
                ('/1/account/1/person/', {'firstname': 'vasya'}),
                ('/1/account/1/subscription/fotki/', {}),
            ],
            'delete': [
                ('/1/account/1/subscription/mail/', None),
            ],
            'put': [
                ('/1/account/1/subscription/fotki/', {}),
            ],
        }

    def tearDown(self):
        self.env.stop()
        del self.env

    def api_request(self, method, path, params, consumer=None):
        if consumer:
            path += '?consumer=%s' % consumer

        if method in ['post', 'put']:
            return getattr(self.env.client, method)(path=path, data=params)

        return getattr(self.env.client, method)(path=path, query_string=params)

    def test_status_ok(self):
        for path, qs in self.apis['post']:
            rv = self.api_request('post', path, qs, consumer='dev')
            eq_(rv.status_code, 200)
            eq_(json.loads(rv.data)['status'], 'ok')

    def test_with_invalid_params(self):
        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = self.api_request(method, path, qs)
                eq_(rv.status_code, 400, rv.data)
                eq_(json.loads(rv.data)['status'], 'error')

    def test_blackbox_error(self):
        bb_errors = [
            (blackbox.BaseBlackboxError('Blackbox failed'), 503),
            (blackbox.BlackboxTemporaryError('Blackbox failed'), 503),
            (blackbox.AccessDenied('Blackbox ACL failed'), 500),
        ]
        for method, apis in self.apis.items():
            for path, qs in apis:
                for bb_error, status_code in bb_errors:
                    self.env.blackbox.set_blackbox_response_side_effect('userinfo',
                                                                        bb_error)
                    rv = self.api_request(method, path, qs, consumer='dev')
                    eq_(rv.status_code, status_code, [path, method, rv.status_code, rv.data])
                    eq_(json.loads(rv.data)['status'], 'error')

    def test_unknownuid(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_response)
        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = self.api_request(method, path, qs, consumer='dev')
                eq_(rv.status_code, 404, rv.data)
                eq_(json.loads(rv.data)['status'], 'error')

    def test_dbmanager_error(self):
        blackbox_response = blackbox_userinfo_response(
            login='test', subscribed_to=[2],
            dbfields={'subscription.login_rule.8': '1', 'subscription.host_id.2': '1'},
        )
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_response)
        self.env.husky_api.set_response_value('delete_user', husky_delete_user_response())
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError)
        for method, apis in self.apis.items():
            for path, qs in apis:
                rv = self.api_request(method, path, qs, consumer='dev')
                eq_(rv.status_code, 503)
                eq_(json.loads(rv.data)['status'], 'error')

    def test_status_ok_with_consumer_in_body(self):
        for path, qs in self.apis['post']:
            qs.update({'consumer': 'mail'})
            rv = self.api_request('post', path, qs, consumer='dev')
            eq_(rv.status_code, 200)
            eq_(json.loads(rv.data)['status'], 'ok')


@with_settings_hosts()
class Test404(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_404(self):
        rv = self.env.client.post('/1/', data={})

        eq_(rv.status_code, 404, [rv.status_code, rv.data])


@with_settings_hosts()
class TestAccessLogging(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.access_logger.bind_entry(
            'access',
            consumer_ip='127.0.0.1',
            duration=TimeSpan(),
            tskv_format='passport-api-access-log',
            unixtime=TimeNow(),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_not_found(self):
        rv = self.env.client.post('/1/', data={})

        eq_(rv.status_code, 404, [rv.status_code, rv.data])
        self.env.access_logger.assert_contains(
            self.env.access_logger.entry(
                'access',
                method='POST',
                status_code='404',
                url='http://localhost/1/',
            ),
        )

    def test_invalid_ip(self):
        rv = self.env.client.post('/1/track/', data={}, headers=mock_headers(consumer_ip='1.1.1.1.1'))

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        self.env.access_logger.assert_contains(
            self.env.access_logger.entry(
                'access',
                consumer_ip='1.1.1.1.1',
                error='InvalidHeader',
                method='POST',
                status='error',
                status_code='400',
                url='http://localhost/1/track/',
            ),
        )

    def test_bundle_api(self):
        self.env.grants.set_grants_return_value(mock_grants())
        self.env.blackbox.set_blackbox_response_side_effect('sessionid', Exception)
        rv = self.env.client.post(
            '/1/bundle/auth/password/submit/?consumer=dev',
            data={},
            headers=mock_headers(
                user_agent='curl',
                cookie='yandexuid=123;Session_id=1234;sslsessionid=12345',
                user_ip='1.1.1.1',
                host='yandex.ru',
            ),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        self.env.access_logger.assert_contains(
            self.env.access_logger.entry(
                'access',
                consumer='dev',
                error='exception.unhandled',
                method='POST',
                status='error',
                status_code='200',
                user_agent='curl',
                url='http://localhost/1/bundle/auth/password/submit/?consumer=dev',
            ),
        )

    def test_legacy_api_5xx(self):
        self.env.grants.set_grants_return_value(mock_grants())
        bb_errors = [
            ('BlackboxFailed', blackbox.BlackboxTemporaryError('Blackbox failed'), 503),
            ('BlackboxACL', blackbox.AccessDenied('Blackbox ACL failed'), 500),
        ]
        for error, bb_error, status_code in bb_errors:
            self.env.blackbox.set_blackbox_response_side_effect('userinfo', bb_error)
            rv = self.env.client.post(
                '/1/account/1/karma/?consumer=dev',
                data={'suffix': '100'},
            )
            eq_(rv.status_code, status_code, [rv.status_code, rv.data])
            self.env.access_logger.assert_contains(
                self.env.access_logger.entry(
                    'access',
                    error=error,
                    consumer='dev',
                    method='POST',
                    status='error',
                    status_code=str(status_code),
                    url='http://localhost/1/account/1/karma/?consumer=dev',
                ),
                offset=-1,
            )
