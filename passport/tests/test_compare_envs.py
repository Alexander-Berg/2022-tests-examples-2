# -*- coding: utf-8 -*-
import netaddr
from nose.tools import eq_
from passport.backend.core.compare.compare import (
    compare_ip_with_subnet,
    compare_ips,
    compare_uas,
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_NOT_SET,
    UA_FACTOR_FULL_MATCH,
    UA_FACTOR_NO_MATCH,
)
from passport.backend.core.compare.test.compare import (
    compare_uas_factor,
    compared_user_agent,
)
from passport.backend.core.types.ip.ip import IPAddress


def test_compare_ips():
    values = (
        ('1.1.1.1', '1.1.1.1', FACTOR_BOOL_MATCH),
        ('1.1.1.1', IPAddress('1.1.1.1'), FACTOR_BOOL_MATCH),
        ('1.1.1.1', '1.1.1.2', FACTOR_BOOL_NO_MATCH),
        (None, '1.1.1.1', FACTOR_NOT_SET),
        ('1.1.1.1', None, FACTOR_NOT_SET),
        (None, None, FACTOR_NOT_SET),
    )

    for ip, other_ip, expected_factor in values:
        factor = compare_ips(ip, other_ip)
        eq_(factor, expected_factor)


def test_compare_ip_with_subnet():
    values = (
        ('1.1.1.1', netaddr.IPNetwork('1.1.1.0/24'), FACTOR_BOOL_MATCH),
        (IPAddress('1.1.1.1'), netaddr.IPNetwork('1.1.1.0/24'), FACTOR_BOOL_MATCH),
        ('1.1.2.1', netaddr.IPNetwork('1.1.1.0/24'), FACTOR_BOOL_NO_MATCH),
        (None, netaddr.IPNetwork('1.1.1.0/24'), FACTOR_NOT_SET),
        ('1.1.1.1', None, FACTOR_NOT_SET),
        (None, None, FACTOR_NOT_SET),
    )

    for ip, other_ip, expected_factor in values:
        factor = compare_ip_with_subnet(ip, other_ip)
        eq_(factor, expected_factor)


def test_compare_uas():
    values = (
        (compared_user_agent(), compared_user_agent(), UA_FACTOR_FULL_MATCH),
        (compared_user_agent(os='Ubuntu'), compared_user_agent(os='ubuntu'), UA_FACTOR_FULL_MATCH),
        (compared_user_agent(os='Ubuntu'), compared_user_agent(), compare_uas_factor('yandexuid', 'browser.name')),
        (compared_user_agent(os=None), compared_user_agent(), compare_uas_factor('yandexuid', 'browser.name')),
        (compared_user_agent(os=None), compared_user_agent(browser=None), compare_uas_factor('yandexuid')),
        (compared_user_agent(yandexuid=None), compared_user_agent(), compare_uas_factor('os.name', 'browser.name')),
        (compared_user_agent(yandexuid='123'), compared_user_agent(yandexuid='234', browser='ie'), compare_uas_factor('os.name')),
        (compared_user_agent(os=None, yandexuid=None), compared_user_agent(browser=None, yandexuid=None), UA_FACTOR_NO_MATCH),
        (compared_user_agent(), compared_user_agent(os='ubuntu', browser='firefox', yandexuid='321'), UA_FACTOR_NO_MATCH),
        (None, compared_user_agent(), FACTOR_NOT_SET),
        (None, None, FACTOR_NOT_SET),
    )

    for ua, other_ua, expected_factor in values:
        factor = compare_uas(ua, other_ua)
        eq_(factor, expected_factor)
