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
class TestBlackboxRequestFindPddAccounts(BaseBlackboxRequestTestCase):

    def test_find_pdd_accounts(self):
        self.set_blackbox_response_value('''
        {
            "uids": [
                "113000000000001",
                "113000000000002",
                "113000000000003"
            ],
            "total_count": "5",
            "count": "3"
        }
        ''')
        response = self.blackbox.find_pdd_accounts(domain_id=1, login='*')
        eq_(len(response['uids']), 3)
        eq_(response['total_count'], 5)
        eq_(response['count'], 3)

        response = self.blackbox.find_pdd_accounts(domain='okna.ru', login='*')
        eq_(len(response['uids']), 3)
        eq_(response['total_count'], 5)
        eq_(response['count'], 3)

    @raises(ValueError)
    def test_find_pdd_accounts_domain_and_id(self):
        self.blackbox.find_pdd_accounts(
            domain_id=1,
            domain='okna.ru',
            login='*',
        )

    @raises(ValueError)
    def test_find_pdd_accounts_nothing_at_all(self):
        self.blackbox.find_pdd_accounts()


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestFindPddAccountsUrl(BaseBlackboxTestCase):

    base_params = {
        'method': 'find_pdd_accounts',
        'format': 'json',
    }

    def test_find_pdd_accounts_url_descending(self):
        request_info = Blackbox().build_find_pdd_accounts_request(
            domain='domain.ru',
            login='*',
            descending_order=True,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                    'sort': 'uid.desc',
                    'login': '*',
                },
            ),
        )

    def test_find_pdd_accounts_url(self):
        request_info = Blackbox().build_find_pdd_accounts_request(
            domain='domain.ru',
            login='*',
            offset=1,
            limit=10,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                    'sort': 'uid.asc',
                    'login': '*',
                    'offset': '1',
                    'limit': '10',
                },
            ),
        )

    def test_find_pdd_accounts_sort_by_login(self):
        request_info = Blackbox().build_find_pdd_accounts_request(
            domain='domain.ru',
            login='*',
            sort_by='login',
            offset=1,
            limit=10,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain': 'domain.ru',
                    'sort': 'login.asc',
                    'login': '*',
                    'offset': '1',
                    'limit': '10',
                },
            ),
        )

    def test_find_pdd_accounts_domain_id(self):
        request_info = Blackbox().build_find_pdd_accounts_request(
            domain_id=1,
            login='*',
            sort_by='login',
            offset=1,
            limit=10,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain_id': '1',
                    'sort': 'login.asc',
                    'login': '*',
                    'offset': '1',
                    'limit': '10',
                },
            ),
        )

    def test_find_pdd_accounts_zero_limit(self):
        request_info = Blackbox().build_find_pdd_accounts_request(
            domain_id=1,
            login='*',
            limit=0,
        )
        url = urlparse(request_info.url)
        eq_(url.netloc, 'test.local')
        check_all_url_params_match(
            request_info.url,
            merge_dicts(
                self.base_params,
                {
                    'domain_id': '1',
                    'sort': 'uid.asc',
                    'login': '*',
                    'limit': '0',
                },
            ),
        )

    @raises(ValueError)
    def test_find_pdd_accounts_url_domain_and_domain_id(self):
        Blackbox().build_find_pdd_accounts_request(
            domain='domain.ru',
            domain_id=1,
            login='*',
        )

    @raises(ValueError)
    def test_find_pdd_accounts_url_without_params(self):
        Blackbox().build_find_pdd_accounts_request()
