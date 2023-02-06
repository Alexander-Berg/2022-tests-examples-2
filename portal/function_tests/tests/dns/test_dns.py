# -*- coding: utf-8 -*-
import itertools
import logging
from retry import retry
import allure
import dns.resolver
import pytest
import socket

from common import env
from dns_conf import hosts, name_servers

logger = logging.getLogger(__name__)
morda_env = env.morda_env()


def yasm_ok(rdata_type, name_server):
    return 'morda_dns_{}_{}_ok_tttt'.format(dns.rdatatype.to_text(rdata_type), name_server['id'])


def yasm_bad(rdata_type, name_server):
    return 'morda_dns_{}_{}_bad_tttt'.format(dns.rdatatype.to_text(rdata_type), name_server['id'])


def get_params():
    return list(itertools.product(
        [h for h in hosts if 'yandex.ua' not in h['host']],
        name_servers))


@retry(tries=3, delay=1)
def resolve_host(hostname):
    addr_info = socket.getaddrinfo(hostname, None)
    if not addr_info:
        raise Exception('Failed to resolve host ' + hostname)
    return addr_info[0][4][0]


@retry(tries=3, delay=1)
def get_dns(name_server, rdatatype, host):
    resolver = dns.resolver.Resolver()
    logger.debug('Resolving from: {}'.format(name_server['host']))

    resolver.nameservers = [resolve_host(name_server['host'])]
    logger.debug('Get data for {} from {}'.format(host, name_server['id']))

    dns_record = resolver.query(host, rdtype=rdatatype)
    result = [str(e) for e in list(dns_record)]
    logger.debug('Found ips: {}'.format(result))
    return result


def check_ips(yasm, host, name_server, rdatatype):
    yasm.add_to_signal(yasm_bad(rdatatype, name_server), 0)
    yasm.add_to_signal(yasm_ok(rdatatype, name_server), 0)
    rdatatype_text = dns.rdatatype.to_text(rdatatype)
    hostname = host['host']
    expected = host[rdatatype_text]

    if not expected:
        logger.debug('No {} record expected for host {}'.format(rdatatype_text, hostname))
        return

    logger.debug('Checking "{}" for {} at {}'.format(rdatatype_text, hostname, name_server['id']))
    try:
        ips = get_dns(name_server, rdatatype, hostname)
    except Exception as e:
        yasm.add_to_signal(yasm_bad(rdatatype, name_server), 1)
        raise e

    if not all(ip in expected for ip in ips):
        logger.error('Expected: {}, \ngot: {}'.format(expected, ips))
        yasm.add_to_signal(yasm_bad(rdatatype, name_server), 1)
        pytest.fail('Different ips for host {}'.format(hostname))

    yasm.add_to_signal(yasm_ok(rdatatype, name_server), 1)


def ids(param):
    if isinstance(param, (dict,)) and 'host' in param:
        return param['host']


@pytest.mark.yasm
@pytest.mark.skipif("morda_env != 'production'")
@pytest.mark.parametrize('host,name_server', get_params(), ids=ids)
@allure.feature('dns')
@allure.story('A')
def test_dns_a(yasm, host, name_server):
    check_ips(yasm, host, name_server, dns.rdatatype.A)


@pytest.mark.yasm
@pytest.mark.skipif("morda_env != 'production'")
@pytest.mark.parametrize('host,name_server', get_params(), ids=ids)
@allure.feature('dns')
@allure.story('AAAA')
def test_dns_aaaa(yasm, host, name_server):
    check_ips(yasm, host, name_server, dns.rdatatype.AAAA)
