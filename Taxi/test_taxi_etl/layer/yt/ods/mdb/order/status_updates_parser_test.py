# coding: utf-8
from unittest import TestCase

from taxi_etl.layer.yt.ods.mdb.order.status_updates_parser import UserStatusParser
from test_taxi_etl.layer.yt.ods.mdb.order.utils import create_order_proc, \
    create_user_status_update


class TestUserStatusParser(TestCase):
    def setUp(self):
        self.parser = UserStatusParser()

    def test_get_timedelta_in_status(self):
        status_updates = [
            create_user_status_update('2018-06-10 23:23:23.123000', 'pending'),
            create_user_status_update('2018-06-10 23:23:24.125000', None)
        ]
        data = create_order_proc(status_updates=status_updates)
        result = self.parser.get_timedelta_in_status(data, 'pending')
        self.assertEqual(1.002, result.total_seconds())

        status_updates = [
            create_user_status_update('2018-06-10 23:23:23.123000', 'pending'),
            create_user_status_update('2018-06-10 23:23:24.125000', None),
            create_user_status_update('2018-06-10 23:23:26.111000', 'assigned'),
            create_user_status_update('2018-06-10 23:24:10.000000', 'pending'),
            create_user_status_update('2018-06-10 23:25:20.125000', None),
            create_user_status_update('2018-06-10 23:27:10.000000', 'pending')
        ]
        data = create_order_proc(status_updates=status_updates)
        result = self.parser.get_timedelta_in_status(data, 'pending')
        self.assertEqual(71.127, result.total_seconds())

        status_updates = [
            create_user_status_update('2018-06-10 23:23:23.123000', 'pending')
        ]
        data = create_order_proc(status_updates=status_updates)
        result = self.parser.get_timedelta_in_status(data, 'pending')
        self.assertEqual(0, result.total_seconds())

        status_updates = []
        data = create_order_proc(status_updates=status_updates)
        result = self.parser.get_timedelta_in_status(data, 'pending')
        self.assertEqual(0, result.total_seconds())
