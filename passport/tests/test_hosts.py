# -*- coding: utf-8 -*-
import re

from passport.backend.api.settings.hosts import (
    __DBSCRIPTS_HOSTS,
    __DBSCRIPTS_TEST_HOSTS,
    __DBSCRIPTS_YATEAM_HOSTS,
    __DBSCRIPTS_YATEAM_TEST_HOSTS,
    __OTHER_HOSTS,
    __PASSPORT_HOSTS,
    __PASSPORT_RC_HOSTS,
    __PASSPORT_TEST_HOSTS,
    __PASSPORT_YATEAM_HOSTS,
    __PASSPORT_YATEAM_RC_HOSTS,
    __PASSPORT_YATEAM_TEST_HOSTS,
)
import pytest


# Какие риски закрывает этот файл?
# - id хоста одинаковый у разных хостов, из-за опечатки: например у s19 и у s20 айдишник 0x28: это ловится тестами
# - копипаста хостов (один и тот же хост встречается несколько раз): это ловится тестами
# - один и тот же айдишник в одном окружении более чем у 2 хостов: это ловится тестами


# дц и индекс машинки, например
# - s20.redis.passport.yandex.net
# - passport-s20.passport.yandex.net
# регулярка достанет "s20"
RE_DC_IDX = re.compile(r'(?:.+-)?([smfiv]\d+)\.')

RE_HOSTNAME = re.compile(r'^[a-z0-9.-]+$')


def get_dc_idx(hostname):
    m = RE_DC_IDX.match(hostname)
    if not m:
        return
    return m.groups()[0]


def test_regex():
    for host in ['s20.redis.passport.yandex.net', 'redis-s20.passport.yandex.net']:
        m = RE_DC_IDX.match(host)
        assert m
        assert m.groups() == ('s20',)


@pytest.mark.parametrize(
    'hosts',
    [
        __OTHER_HOSTS,
        __PASSPORT_HOSTS,
        __PASSPORT_TEST_HOSTS,
        __PASSPORT_RC_HOSTS,
        __PASSPORT_YATEAM_HOSTS,
        __PASSPORT_YATEAM_TEST_HOSTS,
        __PASSPORT_YATEAM_RC_HOSTS,
        __DBSCRIPTS_HOSTS,
        __DBSCRIPTS_TEST_HOSTS,
        __DBSCRIPTS_YATEAM_HOSTS,
        __DBSCRIPTS_YATEAM_TEST_HOSTS,
    ],
)
def test_hosts_sanity_check(hosts):
    # защита от опечаток в хостнеймах
    for host in hosts:
        assert RE_HOSTNAME.match(host.name), host

    # фильтруем все серверы, ноутбуки и прочее оставляем за скобками
    server_hosts = list(host for host in hosts if 'passport.yandex.net' in host.name)

    groups = dict()
    for host in server_hosts:
        dc_idx = get_dc_idx(host.name)
        if not dc_idx:
            continue

        # дц должны совпадать
        # startswith вместо ==, потому что помимо s есть s1, s1rc, так далее
        assert host.dc.startswith(dc_idx[0])

        try:
            groups[dc_idx].append(host)
        except KeyError:
            groups[dc_idx] = [host]

    seen_host_ids = set()
    for group_name, hosts_in_group in groups.items():
        _tmp_seen_host_ids = set()
        # сейчас под одним айдишником разрешены
        # - железный hostname
        # - redis hostname для TLS
        # поэтому не больше двух
        assert len(hosts_in_group) <= 2
        for host in hosts_in_group:
            # один и тот же айдишник не должен встречаться на разных хостах
            assert host.id not in seen_host_ids
            _tmp_seen_host_ids.add(host.id)
        # защита от опечаток типа redis-s20: id=99, s20-passport: id=9999 (кнопка залипла на маке)
        # у одинаковых хостов должен быть одинаковый айдишник => мощность множества 1
        assert len(_tmp_seen_host_ids) == 1
        seen_host_ids |= _tmp_seen_host_ids
