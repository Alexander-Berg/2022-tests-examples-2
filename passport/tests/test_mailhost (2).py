# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    domains_hosts_table as dht,
    hosts_table as ht,
)
from passport.backend.core.db.utils import encode_params_for_db
from passport.backend.core.differ import diff
from passport.backend.core.models.mailhost import MailHost
from passport.backend.core.processor import run_eav
from passport.backend.core.serializers.mailhost import MailhostSerializer


HOST_ID = 1


class TestMailHostSerializer(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()
        self.serializer = MailhostSerializer()
        self.model_data = {
            'host_id': 14,
            'prio': -20,
            'mx': u'mx001.yandex.net',
            'db_id': u'mdb666',
            'sid': 99,
            'host_number': 42,
            'host_name': 'hostname.domain.ru',
            'host_ip': '123.123.13.13',
        }

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_no_action_required(self):
        host = MailHost().parse(self.model_data)
        s1 = host.snapshot()
        queries = self.serializer.serialize(
            s1,
            host,
            diff(s1, host),
        )

        eq_eav_queries(queries, [])

    def test_insert(self):
        self.model_data.pop('host_id', None)
        host = MailHost().parse(self.model_data)

        queries = self.serializer.serialize(
            None,
            host,
            diff(None, host),
        )

        raw_data = {
            'db_id': host.db_id,
            'mx': host.mx,
            'prio': host.priority,
            'sid': host.sid,
            'host_number': host.number,
            'host_name': host.name,
            'host_ip': host.ip,
        }
        domains_data = dict(raw_data, host_id=HOST_ID)

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                ht.insert().values(**encode_params_for_db(raw_data)),
                dht.insert().values(**encode_params_for_db(domains_data)),
                'COMMIT',
            ],
            inserted_keys=[HOST_ID],
        )

        # Здесь непосредственно выполним запросы на БД и проверим что будет записано
        run_eav(None, host, diff(None, host))

        self.db.check('hosts', 'host_id', HOST_ID, db='passportdbcentral', **raw_data)
        self.db.check('domains_hosts', 'host_id', HOST_ID, db='passportdbcentral', **raw_data)

    def test_delete(self):
        host = MailHost().parse(self.model_data)
        queries = self.serializer.serialize(
            host,
            None,
            diff(host, None),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                ht.delete().where(ht.c.db_id == host.db_id.encode('utf8')),
                dht.delete().where(dht.c.db_id == host.db_id.encode('utf8')),
                'COMMIT',
            ],
        )

    def test_update_all_fields__ok(self):
        host = MailHost().parse(self.model_data)
        s1 = host.snapshot()
        db_id = host.db_id

        host.priority = 0
        host.mx = 'some-new-value'
        host.db_id = '1234'
        host.id = 4321
        host.sid = 2
        host.ip = '22.22.22.22'
        host.name = 'new-name.yandex.ru'
        host.number = 321

        queries = self.serializer.serialize(
            s1,
            host,
            diff(s1, host),
        )

        raw_data = {
            'host_id': host.id,
            'db_id': host.db_id,
            'mx': host.mx,
            'prio': host.priority,
            'sid': host.sid,
            'host_number': host.number,
            'host_name': host.name,
            'host_ip': host.ip,
        }
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                ht.update().values(**encode_params_for_db(raw_data)).where(ht.c.db_id == db_id.encode('utf8')),
                dht.update().values(**encode_params_for_db(raw_data)).where(dht.c.db_id == db_id.encode('utf8')),
                'COMMIT',
            ],
        )

    def test_update_some_fields__ok(self):
        host = MailHost().parse(self.model_data)
        s1 = host.snapshot()
        db_id = host.db_id

        host.priority = 0
        host.mx = 'some-new-value'

        queries = self.serializer.serialize(
            s1,
            host,
            diff(s1, host),
        )

        raw_data = {
            'mx': host.mx,
            'prio': host.priority,
        }
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                ht.update().values(**encode_params_for_db(raw_data)).where(ht.c.db_id == db_id.encode('utf8')),
                dht.update().values(**encode_params_for_db(raw_data)).where(dht.c.db_id == db_id.encode('utf8')),
                'COMMIT',
            ],
        )
