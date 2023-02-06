# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.blackbox import (
    AccessDenied,
    Blackbox,
)
from passport.backend.core.test.test_utils import with_settings
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
)

from .test_blackbox import BaseBlackboxRequestTestCase


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestLoginoccupation(BaseBlackboxRequestTestCase):

    def test_basic_loginoccupation(self):
        self.set_blackbox_response_value(b'''{"logins": {"kolbacek" : "free",\n
                        "a" : "occupied",\n
                        "b.s" : "free",\n
                        "as-asas" : "occupied",\n
                        "a b" : "malformed",\n
                        "ya-delete" : "occupied",\n
                        "uid-bla-bla" : "free",\n
                        "bessporno" : "stoplist",\n
                        "superzhopa222" : "stoplist",\n
                        "chatsky" : "occupied",\n
                        "ya@mail.ru" : "free",\n
                        "bacek" : "stoplist",\n
                        "loginof" : "stoplist"\n}}''')
        response = self.blackbox.loginoccupation('login')
        wait_for = {'kolbacek': 'free',
                    'a': 'occupied',
                    'b.s': 'free',
                    'as-asas': 'occupied',
                    'a b': 'malformed',
                    'ya-delete': 'occupied',
                    'uid-bla-bla': 'free',
                    'bessporno': 'stoplist',
                    'superzhopa222': 'stoplist',
                    'chatsky': 'occupied',
                    'ya@mail.ru': 'free',
                    'bacek': 'stoplist',
                    'loginof': 'stoplist'}
        eq_(response, wait_for)

    @raises(AccessDenied)
    def test_blackbox_error_raises_exception(self):
        self.set_blackbox_response_value(b'''{"exception":{"value":"ACCESS_DENIED","id":21},
                       "error":"BlackBox error: Access denied: LoginOccupation()"}''')
        self.blackbox.loginoccupation('login')


@with_settings(BLACKBOX_URL='http://test.local/')
class TestBlackboxRequestLoginoccupationUrl(BaseBlackboxRequestTestCase):
    def test_loginoccupation_several_logins_url(self):
        logins = ['test1', 'test2', 'test3']
        request_info = Blackbox().build_loginoccupation_request(logins)
        url = urlparse(request_info.url)
        query = parse_qs(url.query)

        eq_(query['logins'][0].split(','), logins)
        ok_('ignore_stoplist' not in query)
        ok_('is_pdd' not in query)

    def test_loginoccupation_is_pdd(self):
        request_info = Blackbox().build_loginoccupation_request(['test'], is_pdd=True)

        url = urlparse(request_info.url)
        query = parse_qs(url.query)

        ok_('ignore_stoplist' not in query)
        ok_('is_pdd' in query)

    def test_loginoccupation_ignore_stoplist(self):
        request_info = Blackbox().build_loginoccupation_request(['test'], ignore_stoplist=True)

        url = urlparse(request_info.url)
        query = parse_qs(url.query)

        ok_('ignore_stoplist' in query)
        ok_('is_pdd' not in query)

    def test_loginoccupation_cyrillic_login(self):
        request_info = Blackbox().build_loginoccupation_request([u'логин'], ignore_stoplist=True)

        url = urlparse(request_info.url)
        query = parse_qs(url.query)

        ok_('ignore_stoplist' in query)
        ok_('is_pdd' not in query)

    @raises(ValueError)
    def test_loginoccupation_without_logins(self):
        Blackbox().build_loginoccupation_request(logins=[])

    def build_request_info(self, **kwargs):
        defaults = dict(
            logins=['test1', 'test2'],
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        return Blackbox().build_loginoccupation_request(**kwargs)

    def loginoccupation_params(self, **kwargs):
        return self.base_params(
            dict(
                format='json',
                logins='test1,test2',
                method='loginoccupation',
            ),
            **kwargs
        )
