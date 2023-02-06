# -*- coding: utf-8 -*-
import json
import unittest

import netaddr
from netree import Lookup
from passport.backend.libs_checker.environment import StagingEnvironment


USER_FLAG = 0x1
TURBO_FLAG = 0x2


def init_ipreg(filename=None):
    lookup = Lookup()

    data = json.load(open(filename or StagingEnvironment.env['libipreg']['layout']))

    for line in data:
        low = netaddr.IPAddress(line['low'])
        high = netaddr.IPAddress(line['high'])

        is_user = USER_FLAG if line.get('flags', {}).get('user', False) else 0
        is_turbo = TURBO_FLAG if line.get('flags', {}).get('turbo', False) else 0

        mask = int(low) ^ int(high)
        length = mask.bit_length()

        lookup.add(low, length, is_user | is_turbo)

    return lookup


def get_net(ipreg, ip, headers):
    net = ipreg.get_net(ip)
    is_turbo = net['flags'] & TURBO_FLAG
    if is_turbo and 'X-Forwarded-For' in headers:
        net = ipreg.get_net(headers['X-Forwarded-For'].split(',')[0])
    net['is_user'] = bool(net['flags'] & USER_FLAG)
    return net


class TestLibIpreg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ipreg = init_ipreg()

    def setUp(self):
        self.headers = dict([
            ('Accept-Language', 'ru'),
            ('Cookie', 'sessionid=foo'),
            ('Ya-Consumer-Client-Ip', '1.1.1.1'),
        ])

    def test_ipreg(self):
        assert self.ipreg

    def test_get_net(self):
        actual = get_net(self.ipreg, '8.8.8.8', self.headers)

        assert not actual['is_yandex']
        assert actual['real_ip'] == '8.8.8.8'

        # текущий ip passport-dev
        actual = get_net(self.ipreg, '87.250.235.4', self.headers)
        assert actual['is_yandex']
        assert actual['real_ip'] == '87.250.235.4'

    def test_get_net_invalid_header(self):
        self.assertRaises(
            netaddr.AddrFormatError,
            get_net,
            self.ipreg,
            '8.8.8.8, 1.2.3.4',
            self.headers,
        )
