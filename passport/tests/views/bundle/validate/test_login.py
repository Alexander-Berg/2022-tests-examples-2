# -*- coding: utf-8 -*-

from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.api.common.processes import PROCESS_WEB_REGISTRATION
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_LOGIN = 'login'
TEST_INVALID_LOGIN = '--!!login.-asd'

TEST_PDD_EMAIL = u'crunch@time.org'
TEST_PDD_INVALID_LOGIN = u'asd$&@time.org'
TEST_PDD_INVALID_DOMAIN = u'asd@~time.org'
TEST_PDD_CYRILLIC_DOMAIN = u'crunch@домен.директория.яндекс.рф'
TEST_PDD_LONG_LOGIN = u'#%s@hello.hi' % (u'a' * 41)
TEST_PDD_LONG_DOMAIN = u'hello@%s.org' % (u'p' * 250)
TEST_STRIP_LOGIN = u' rollercoaster-213 '

TEST_LITE_LOGIN = u'admin@gmail.com'


@with_settings_hosts()
class TestValidateLoginView(BaseMdapiTestCase):
    url = '/1/bundle/validate/login/?consumer=dev'

    def setUp(self):
        self.mocked_grants = {
            'login': ['validate'],
        }
        super(TestValidateLoginView, self).setUp()
        self.setup_trackid_generator()

    def tearDown(self):
        del self.track_id_generator
        super(TestValidateLoginView, self).tearDown()

    def set_blackbox_response_values(self, **kwargs):
        for method, response_values in kwargs.items():
            self.env.blackbox.set_blackbox_response_value(
                method,
                response_values,
            )

    def check_bb_request_queries(self, *queries):
        for i, query in enumerate(queries):
            self.env.blackbox.requests[i].assert_query_contains(query)

    def test_empty_request(self):
        resp = self.make_request(data={}, headers={})
        self.check_error_response(resp, ['track_id.empty'])

    def test_no_login(self):
        resp = self.make_request(data={'track_id': self.track_id})
        self.check_error_response(resp, ['login.empty'])

    def test_ok_login(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )

        resp = self.make_request(data={
            'login': TEST_LOGIN,
            'track_id': self.track_id,
        })
        self.check_response_ok(resp)

        eq_(self.env.blackbox.request.call_count, 1)
        self.check_bb_request_queries(
            dict(
                logins=TEST_LOGIN,
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.login, TEST_LOGIN)
        eq_(track.login_validation_count.get(), 1)

    def test_invalid_login(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_INVALID_LOGIN: 'free'}),
        )

        resp = self.make_request(data={
            'login': TEST_INVALID_LOGIN,
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            [
                'login.startswithhyphen',
                'login.doubledhyphen',
                'login.dothyphen',
                'login.prohibitedsymbols',
            ],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_ok_pdd_email(self):
        extra_grants = {
            'ignore_stoplist': ['*'],
        }
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants=dict(
                    self.mocked_grants,
                    **extra_grants
                ),
            ),
        )
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_EMAIL,
            'is_pdd': 'true',
            'ignore_stoplist': 'true',
            'track_id': self.track_id,
        })
        self.check_response_ok(resp)

        eq_(self.env.blackbox.request.call_count, 2)

        self.check_bb_request_queries(
            dict(
                domain=TEST_PDD_EMAIL.split('@', 1)[1],
            ),
            dict(
                logins=TEST_PDD_EMAIL,
                is_pdd='1',
                ignore_stoplist='1',
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.login, TEST_PDD_EMAIL)
        eq_(track.login_validation_count.get(), 1)

    def test_pdd_email_not_available(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'occupied'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_EMAIL,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['login.not_available'],
        )

        eq_(self.env.blackbox.request.call_count, 2)
        self.check_bb_request_queries(
            dict(
                domain=TEST_PDD_EMAIL.split('@', 1)[1],
            ),
            dict(
                logins=TEST_PDD_EMAIL,
                is_pdd='1',
            ),
        )

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_error_pdd_login(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_INVALID_LOGIN: 'free'}),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_INVALID_LOGIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['login.prohibitedsymbols'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_error_pdd_domain(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_INVALID_DOMAIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_INVALID_DOMAIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['domain.invalid'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_pdd_not_found_domain(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_EMAIL,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['domain.not_found'],
        )

        eq_(self.env.blackbox.request.call_count, 1)
        self.check_bb_request_queries(
            dict(
                domain=TEST_PDD_EMAIL.split('@', 1)[1],
            ),
        )

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_cyrillic_domain(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_CYRILLIC_DOMAIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_CYRILLIC_DOMAIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
            'strict': 'true',
        })
        self.check_error_response(
            resp,
            ['domain.invalid'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_login_too_long(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_LONG_LOGIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_LONG_LOGIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            [
                'login.long',
                'login.prohibitedsymbols',
            ],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_long_domain(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_LONG_DOMAIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_LONG_DOMAIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_response_ok(resp)

        eq_(self.env.blackbox.request.call_count, 2)

        self.check_bb_request_queries(
            dict(
                domain=TEST_PDD_LONG_DOMAIN.split('@', 1)[1],
            ),
            dict(
                logins=TEST_PDD_LONG_DOMAIN,
                is_pdd='1',
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.login, TEST_PDD_LONG_DOMAIN)
        eq_(track.login_validation_count.get(), 1)

    def test_domain_missing(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_LOGIN,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['domain.missing'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_space_in_pdd_login(self):
        login = 'login @domain.ru'
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({login: 'malformed'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': login,
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['login.invalid'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_invalid_login_part_in_pdd_login(self):
        resp = self.make_request(data={
            'login': '@@domain.ru',
            'is_pdd': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['login.prohibitedsymbols'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_no_ignore_grant(self):

        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )
        resp = self.make_request(
            data={
                'login': TEST_PDD_EMAIL,
                'is_pdd': 'true',
                'track_id': self.track_id,
                'ignore_stoplist': 'true',
            },
        )
        self.check_error_response(
            resp,
            ['access.denied'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_no_skip_domain_existence_grant(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )
        resp = self.make_request(
            data={
                'login': TEST_PDD_EMAIL,
                'is_pdd': 'true',
                'track_id': self.track_id,
                'require_domain_existence': 'f',
            },
        )
        self.check_error_response(
            resp,
            ['access.denied'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_skip_domain_existence_check(self):
        self.mocked_grants['login'].append('skip_domain_existence_check')
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants=self.mocked_grants,
            ),
        )
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_PDD_EMAIL: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(),
        )

        resp = self.make_request(data={
            'login': TEST_PDD_EMAIL,
            'is_pdd': 'true',
            'track_id': self.track_id,
            'require_domain_existence': 'false',
        })
        self.check_response_ok(resp)

        eq_(self.env.blackbox.request.call_count, 1)

        self.check_bb_request_queries(
            dict(
                logins=TEST_PDD_EMAIL,
                is_pdd='1',
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.login, TEST_PDD_EMAIL)
        eq_(track.login_validation_count.get(), 1)

    def test_lite_login_ok(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LITE_LOGIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(data={
            'login': TEST_LITE_LOGIN,
            'is_lite': 'true',
            'track_id': self.track_id,
        })
        self.check_response_ok(resp)

        eq_(self.env.blackbox.request.call_count, 2)

        self.check_bb_request_queries(
            dict(
                domain=TEST_LITE_LOGIN.split('@', 1)[1],
            ),
            dict(
                logins=TEST_LITE_LOGIN,
                ignore_stoplist='1',
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.login, TEST_LITE_LOGIN)
        eq_(track.login_validation_count.get(), 1)

    def test_lite_login_not_available(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LITE_LOGIN: 'occupied'}),
            hosted_domains=blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(data={
            'login': TEST_LITE_LOGIN,
            'is_lite': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['login.not_available'],
        )

        eq_(self.env.blackbox.request.call_count, 2)
        self.check_bb_request_queries(
            dict(
                domain=TEST_LITE_LOGIN.split('@', 1)[1],
            ),
            dict(
                logins=TEST_LITE_LOGIN,
                ignore_stoplist='1',
            ),
        )

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_lite_login_domain_missing(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(data={
            'login': TEST_LOGIN,
            'is_lite': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['domain.missing'],
        )

        eq_(self.env.blackbox.request.call_count, 0)

        assert_is_none(self.track_manager.read(self.track_id).login)

    def test_lite_login_pdd_domain_exists(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LITE_LOGIN: 'free'}),
            hosted_domains=blackbox_hosted_domains_response(count=1,),
        )

        resp = self.make_request(data={
            'login': TEST_LITE_LOGIN,
            'is_lite': 'true',
            'track_id': self.track_id,
        })
        self.check_error_response(
            resp,
            ['domain.invalid_type'],
        )

    def test_ok_with_process(self):
        self.set_blackbox_response_values(
            loginoccupation=blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.process_name = PROCESS_WEB_REGISTRATION

        resp = self.make_request(data={
            'login': TEST_LOGIN,
            'track_id': self.track_id,
        })
        self.check_response_ok(resp)
