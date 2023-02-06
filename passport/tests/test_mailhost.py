# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.models.mailhost import MailHost
from passport.backend.core.undefined import Undefined


class TestMailHost(unittest.TestCase):

    def test_parse_empty__undefined(self):
        host = MailHost().parse({})

        for field_name in ['id', 'db_id', 'sid', 'priority', 'mx', 'number', 'name', 'ip']:
            field_value = getattr(host, field_name)
            eq_(field_value, Undefined)

    def test_parse_all_fields__ok(self):
        host = MailHost().parse({
            'mx': 'mx01.dns.yandex.net',
            'sid': '99',
            'prio': '-10',
            'db_id': 'mdb666',
            'host_id': '999',
            'host_ip': 'something',
            'host_name': 'host.domain.com',
            'host_number': '123',
        })

        eq_(host.mx, 'mx01.dns.yandex.net')
        eq_(host.sid, 99)
        eq_(host.priority, -10)
        eq_(host.db_id, 'mdb666')
        eq_(host.id, 999)
        eq_(host.ip, 'something')
        eq_(host.name, 'host.domain.com')
        eq_(host.number, 123)

    def test_parse_twice__ok(self):
        host_data = dict(
            host_id=1,
            db_id='db-id',
        )
        host = MailHost().parse(host_data)

        eq_(host.id, 1)
        eq_(host.db_id, 'db-id')

        domains_hosts_data = dict(
            db_id='new-db-id',
            host_number=15,
            host_name='terminator.ya.ru',
            host_ip='127.0.0.10',
        )
        host.parse(domains_hosts_data)

        eq_(host.id, 1)
        eq_(host.db_id, 'new-db-id')
        eq_(host.number, 15)
        eq_(host.name, 'terminator.ya.ru')
        eq_(host.ip, '127.0.0.10')

    def test_parse_string_fields__ok(self):
        data_to_atrrs = {
            'mx': 'mx',
            'db_id': 'db_id',
            'host_name': 'name',
            'host_ip': 'ip',
        }

        for data_field, attr_name in data_to_atrrs.items():
            host = MailHost().parse({})
            value = getattr(host, attr_name)
            eq_(value, Undefined)

            host = MailHost().parse({data_field: ''})
            value = getattr(host, attr_name)
            eq_(value, '')

            host = MailHost().parse({data_field: 'mx666.mail.yandex.ru'})
            value = getattr(host, attr_name)
            eq_(value, 'mx666.mail.yandex.ru')

    def test_parse_integer_fields__ok(self):
        data_to_atrrs = {
            'host_id': 'id',
            'sid': 'sid',
            'host_number': 'number',
            'prio': 'priority',
        }

        for data_field, attr_name in data_to_atrrs.items():
            host = MailHost().parse({})
            value = getattr(host, attr_name)
            eq_(value, Undefined)

            host = MailHost().parse({data_field: 0})
            value = getattr(host, attr_name)
            eq_(value, 0)

            host = MailHost().parse({data_field: 999})
            value = getattr(host, attr_name)
            eq_(value, 999)

            host = MailHost().parse({data_field: -5})
            value = getattr(host, attr_name)
            eq_(value, -5)
