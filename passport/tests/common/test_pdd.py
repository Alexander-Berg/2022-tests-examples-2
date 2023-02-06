# -*- coding: utf-8 -*-


from nose.tools import ok_
from passport.backend.api.common.pdd import is_domain_suitable_for_directory
from passport.backend.api.test.views import BaseTestViews
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    DOMAINS_USED_BY_DIRECTORY=['directory.ru'],
    RESTRICTED_DIRECTORY_SUBDOMAINS=['spam'],
)
class TestIsDomainSuitableForDirectory(BaseTestViews):
    def test_ok(self):
        for domain in (
            'domain.directory.ru',
        ):
            ok_(is_domain_suitable_for_directory(domain))

    def test_error(self):
        for domain in (
            'ru',  # домен первого уровня
            'directory.ru',  # нет поддомена
            'foo.other-directory.ru',  # неверный домен верхнего уровня
            'spam.directory.ru',  # поддомен в стоп-листе
        ):
            ok_(not is_domain_suitable_for_directory(domain))
