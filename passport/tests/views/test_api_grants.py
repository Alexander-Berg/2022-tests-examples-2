# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.track_manager import create_track_id
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)


@with_settings_hosts()
class TestApiGrants(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={}))

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}))
        self.track_id = create_track_id()

        self.apis = {
            'post': (
                ({'path': '/1/account/1/',
                  'data': {'is_enabled': '0'}},
                 ['account.is_enabled']),
                ({'path': '/1/account/1/',
                  'data': {'is_enabled': '1'}},
                 ['account.is_enabled']),
                ({'path': '/1/account/1/',
                  'data': {'is_enabled_app_password': '0'}},
                 ['account.enable_app_password__full_control']),
                ({'path': '/1/account/1/',
                  'data': {'is_enabled_app_password': '1'}},
                 ['account.enable_app_password__full_control']),
                ({'path': '/1/account/1/karma/',
                  'data': {'suffix': '100'}},
                 ['karma']),
                ({'path': '/1/account/1/person/',
                  'data': {'firstname': 'vasya'}},
                 ['person']),
                ({'path': '/1/account/1/subscription/fotki/'},
                 ['subscription.update.fotki', 'subscription.create.fotki']),
                ({'path': '/1/validation/phone_number/',
                  'data': {'phone_number': '+74951234567', 'track_id': self.track_id}},
                 ['phone_number.validate']),
                ({'path': '/1/validation/login/',
                  'data': {'login': 'test', 'track_id': self.track_id},
                  'headers': {'Ya-Consumer-Client-Ip': '127.0.0.1'}},
                 ['login.validate']),
                ({'path': '/1/validation/password/',
                  'data': {'login': 'invisible', 'password': 'aaa1bbbccc'}},
                 ['password.validate']),
                ({'path': '/1/suggest/name/',
                  'data': {'name': 'Adam Smith'}},
                 ['name.suggest']),
                ({'path': '/1/suggest/login/',
                  'data': {'firstname': 'al', 'lastname': 'bl',
                           'language': 'ru', 'login': 'aaa'}},
                 ['login.suggest']),
                ({'path': '/1/suggest/gender/',
                  'data': {'name': 'Adam Smith'}},
                 ['gender.suggest']),
                ({'path': '/1/suggest/country/'},
                 ['country.suggest']),
                ({'path': '/1/suggest/timezone/',
                  'headers': {'Ya-Consumer-Client-Ip': '127.0.0.1'}},
                 ['timezone.suggest']),
                ({'path': '/1/suggest/language/',
                  'headers': {'Ya-Client-Host': 'passport.yandex.com.tr',
                              'X-Real-IP': '127.0.0.1'}},
                 ['language.suggest']),
                ({'path': '/1/questions/',
                  'data': {'display_language': 'ru'}},
                 ['control_questions']),
                ({'path': '/1/track/'},
                 ['track']),
                ({'path': '/1/track/%s/' % self.track_id,
                  'data': {'country': 'ru'}},
                 ['track']),
                ({'path': '/1/captcha/generate/',
                  'data': {'display_language': 'ru', 'track_id': self.track_id}},
                 ['captcha']),
                ({'path': '/1/captcha/check/',
                  'headers': {'Ya-Consumer-Client-Ip': '127.0.0.1'},
                  'data': {'track_id': self.track_id,
                           'answer': 'asdf', 'key': 'asdf'}},
                 ['captcha']),
                ({'path': '/1/validation/retpath/',
                  'data': {'retpath': '//yandex.ru'}},
                 ['retpath.validate']),
                # account_register_alternative
                ({'path': '/1/account/register/alternative/',
                  'data': {'login': 'test', 'password': 'aaa1bbbccc',
                           'country': 'ru', 'firstname': 'john',
                           'lastname': 'smith', 'track_id': self.track_id,
                           'language': 'ru', 'display_language': 'ru',
                           'mode': 'simplereg', 'validation_method': 'phone',
                           'eula_accepted': 'True'},
                  'headers': {
                      'Ya-Client-Host': '_', 'Ya-Client-X-Forwarded-For': '_',
                      'Ya-Client-User-Agent': '_', 'X-Real-IP': '127.0.0.1',
                      'Ya-Consumer-Client-Ip': '127.0.0.1',
                  }},
                 ['account.register_alternative']),
                # account_register_uncompleted
                ({'path': '/1/account/register/uncompleted/',
                  'data': {'login': 'test', 'country': 'ru',
                           'firstname': 'john', 'lastname': 'smith',
                           'track_id': self.track_id,
                           'language': 'ru'},
                  'headers': {
                      'Ya-Client-Host': '_', 'Ya-Client-X-Forwarded-For': '_',
                      'Ya-Client-User-Agent': '_', 'X-Real-IP': '127.0.0.1',
                      'Ya-Consumer-Client-Ip': '127.0.0.1',
                  }},
                 ['account.register_uncompleted']),
                ({'path': '/1/account/register/uncompleted/setpassword/',
                  'data': {'password': '123456!', 'track_id': self.track_id, 'eula_accepted': '1'},
                  'headers': {
                      'Ya-Consumer-Client-Ip': '127.0.0.1',
                      'Ya-Client-User-Agent': '_',
                  }},
                 ['account.uncompleted_set_password']),
                ({'path': '/1/statbox/',
                  'data': {'data': 'somedata', 'action': 'open'}},
                 ['statbox']),
                ({'path': '/1/session/',
                  'data': {'login': 'somelogin', 'language': 'ru',
                           'track_id': self.track_id, 'uid': 1},
                  'headers': {'Ya-Client-Host': '_',
                              'Ya-Consumer-Client-Ip': '127.0.0.1',
                              'Ya-Client-X-Forwarded-For': '_'}},
                 ['session.create']),
                ({'path': '/1/session/check/',
                  'data': {'session': '_', 'track_id': self.track_id}},
                 ['session.check']),
                # Выписывание oauth-токена
                ({'path': '/1/oauth/token/',
                  'data': {'client_id': 'id', 'client_secret': 'secret',
                           'track_id': self.track_id},
                  'headers': {'Ya-Client-Host': '_',
                              'Ya-Consumer-Client-Ip': '127.0.0.1',
                              'Ya-Client-X-Forwarded-For': '_'}},
                 ['oauth.token_create']),
            ),
            'delete': (
                ({'path': '/1/account/1/subscription/mail/'},
                 ['subscription.delete.mail']),
                ({'path': '/1/track/%s/' % self.track_id},
                 ['track']),
            ),
            'put': (
                ({'path': '/1/account/1/subscription/fotki/'},
                 ['subscription.update.fotki', 'subscription.create.fotki']),
            ),
            'get': (
                ({'path': '/1/track/%s/' % self.track_id},
                 ['track']),
            ),
        }

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.env.stop()
        del self.fake_tvm_credentials_manager
        del self.env

    def test_without_grants(self):
        self.env.grants.set_grants_return_value({'dev': {}})

        for method, apis in self.apis.items():
            for api, missing in apis:
                api.setdefault('query_string', {}).update({'consumer': 'dev'})
                rv = getattr(self.env.client, method)(**api)
                eq_(rv.status_code, 403, [api['path'], rv.data])
                eq_(
                    json.loads(rv.data)['errors'][0]['message'],
                    'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: %r' % missing,
                )

    def test_with_invalid_ticket(self):
        blackbox_response = blackbox_userinfo_response(uid=1)
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'account': ['is_enabled']}, client_id=TEST_CLIENT_ID_2)
        )
        rv = self.env.client.post(
            path='/1/account/1/',
            query_string={'consumer': 'dev'},
            headers={'X-Ya-Service-Ticket': 'invalid'},
            data={'is_enabled': '0'},
        )
        eq_(rv.status_code, 403)
        eq_(
            json.loads(rv.data)['errors'][0]['message'],
            'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None',
        )

    def test_with_empty_ticket(self):
        blackbox_response = blackbox_userinfo_response(uid=1)
        self.env.blackbox.set_blackbox_response_value('userinfo',
                                                      blackbox_response)
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'account': ['is_enabled']}, client_id=TEST_CLIENT_ID_2)
        )
        rv = self.env.client.post(
            path='/1/account/1/',
            query_string={'consumer': 'dev'},
            headers={'X-Ya-Service-Ticket': ''},
            data={'is_enabled': '0'},
        )
        eq_(rv.status_code, 403)
        eq_(
            json.loads(rv.data)['errors'][0]['message'],
            'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None',
        )
