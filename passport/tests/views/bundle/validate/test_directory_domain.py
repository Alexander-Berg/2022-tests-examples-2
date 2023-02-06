# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_hosted_domains_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_DOMAIN = 'domain.directory.yandex.ru'
TEST_CYRILLIC_DOMAIN = u'домен.директория.яндекс.рф'


@with_settings_hosts(
    DOMAINS_USED_BY_DIRECTORY=['directory.yandex.ru', u'директория.яндекс.рф'],
    RESTRICTED_DIRECTORY_SUBDOMAINS=[],
)
class TestDirectoryDomainView(BaseBundleTestViews):
    default_url = '/1/bundle/validate/directory_domain/'
    http_query_args = {
        'consumer': 'dev',
        'domain': TEST_DOMAIN,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'domain': ['validate']}))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok_domain_free(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request()
        self.assert_ok_response(resp)

    def test_domain_exists(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['domain.already_exists'],
        )

    def test_strict_mode_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request(query_args={
            'domain': TEST_CYRILLIC_DOMAIN,
            'strict': 'true',
        })
        self.assert_error_response(
            resp,
            ['domain.invalid'],
        )

    def test_long_domain(self):
        resp = self.make_request(query_args={
            'domain': 'ф' * 58,
        })
        self.assert_error_response(resp, ['domain.invalid'])

    def test_domain_not_suitable_for_directory(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request(query_args={
            'domain': 'test.google.com',
        })
        self.assert_error_response(resp, ['domain.invalid_type'])
