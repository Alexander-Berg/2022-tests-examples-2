# -*- coding: utf-8 -*-
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.exceptions import WrongHostError
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.utils.domains import get_keyspace_by_host


@with_settings(
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.com', 'yandex.com'),
        ('yandex.com.tr', 'yandex.com.tr'),
    )
)
def test_get_keyspace_by_host():
    valid_hosts = (
        ('yandex.ru', 'yandex.ru'),
        ('yandex.com', 'yandex.com'),
        ('yandex.com.tr', 'yandex.com.tr'),
    )
    invalid_hosts = (
        u'somesite.com',
        u'blogs.yandex.ru/derpina/?blobpost=duckface3',
        u'b91647b&^(B$B%7',
        u'.ru',
        u'com.tr',
        u'yandex.ru.zloyvasya.ru',
        u'nyandex.ru',
        u'уаndex.ru',  # cyrillic 'у, a, е'
        u'yandex.kewlhaxxor.ru',
        u'yandex.ru.ru',
        u'yandex.ru//dobryvasya.com',
        u'yandex.zz',
        u'yandex-team.ru',
    )

    for host, keyspace in valid_hosts:
        eq_(get_keyspace_by_host(host), keyspace)

    for host in invalid_hosts:
        assert_raises(WrongHostError, get_keyspace_by_host, host)
