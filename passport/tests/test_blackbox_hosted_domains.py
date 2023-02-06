# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestHostedDomains(BaseBlackboxRequestTestCase):

    def test_hosted_domains(self):
        self.set_blackbox_response_value(b'''
        {
            "hosted_domains": [
                {
                    "born_date": "2010-10-12 15:03:24",
                    "defaul_uid": "0",
                    "admin": "42",
                    "domid": "1",
                    "options": {
                        "can_users_change_password": false,
                        "change_password_url": ""
                    },
                    "slaves": "",
                    "master_domain": "",
                    "mx": "0",
                    "domain": "domain.ru",
                    "ena": "0"
                }
            ]
        }
        ''')
        response = self.blackbox.hosted_domains(domain_id=1)
        eq_(len(response['hosted_domains']), 1)
        eq_(response['hosted_domains'][0]['born_date'], '2010-10-12 15:03:24')
        eq_(response['hosted_domains'][0]['defaul_uid'], '0')
        eq_(response['hosted_domains'][0]['admin'], '42')
        eq_(response['hosted_domains'][0]['domid'], '1')
        eq_(response['hosted_domains'][0]['options'], {
            'change_password_url': '',
            'can_users_change_password': False,
        })
        eq_(response['hosted_domains'][0]['slaves'], '')
        eq_(response['hosted_domains'][0]['master_domain'], '')
        eq_(response['hosted_domains'][0]['mx'], '0')
        eq_(response['hosted_domains'][0]['domain'], 'domain.ru')
        eq_(response['hosted_domains'][0]['ena'], '0')

    def test_hosted_domains_empty_options(self):
        self.set_blackbox_response_value(b'''
        {
            "hosted_domains": [
                {
                    "born_date": "2010-10-12 15:03:24",
                    "defaul_uid": "0",
                    "admin": "42",
                    "domid": "1",
                    "options": "",
                    "slaves": "",
                    "master_domain": "",
                    "mx": "0",
                    "domain": "domain.ru",
                    "ena": "0"
                }
            ]
        }
        ''')
        response = self.blackbox.hosted_domains(domain_id=1)
        eq_(len(response['hosted_domains']), 1)
        eq_(response['hosted_domains'][0]['born_date'], '2010-10-12 15:03:24')
        eq_(response['hosted_domains'][0]['defaul_uid'], '0')
        eq_(response['hosted_domains'][0]['admin'], '42')
        eq_(response['hosted_domains'][0]['domid'], '1')
        eq_(response['hosted_domains'][0]['options'], "")
        eq_(response['hosted_domains'][0]['slaves'], '')
        eq_(response['hosted_domains'][0]['master_domain'], '')
        eq_(response['hosted_domains'][0]['mx'], '0')
        eq_(response['hosted_domains'][0]['domain'], 'domain.ru')
        eq_(response['hosted_domains'][0]['ena'], '0')


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestHostedDomainsUrl(BaseBlackboxTestCase):

    base_params = {
        'method': 'hosted_domains',
        'format': 'json',
    }

    def test_hosted_domains_url(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain='domain.ru',
            domain_id=1,
            domain_admin=42,
            aliases=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                    'domain_id': '1',
                    'domain_admin': '42',
                    'aliases': 'True',
                },
            ),
        )

    def test_hosted_domains_url_idna_domain(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain=u'окна.рф',
            domain_id=1,
            domain_admin=42,
            aliases=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'xn--80atjc.xn--p1ai',
                    'domain_id': '1',
                    'domain_admin': '42',
                    'aliases': 'True',
                },
            ),
        )

    def test_hosted_domains_domain_id_url(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain_id=1,
            aliases=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain_id': '1',
                    'aliases': 'True',
                },
            ),
        )

    def test_hosted_domains_domain_url(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain='domain.ru',
            aliases=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                    'aliases': 'True',
                },
            ),
        )

    def test_hosted_domains_admin_url(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain_admin=42,
            aliases=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain_admin': '42',
                    'aliases': 'True',
                },
            ),
        )

    def test_hosted_domains_url_no_alias(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain='domain.ru',
            aliases=False,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                },
            ),
        )

    def test_hosted_domains_url_with_idna_domain(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain=u'окна.рф',
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'xn--80atjc.xn--p1ai'
                }
            ),
        )

    def test_hosted_domains_url_with_bad_idna_domain(self):
        request_info = Blackbox().build_hosted_domains_request(
            domain=u'.рф',
        )

        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': u'.рф',
                },
            ),
        )

    @raises(ValueError)
    def test_hosted_domains_url_without_params(self):
        Blackbox().build_hosted_domains_request()
