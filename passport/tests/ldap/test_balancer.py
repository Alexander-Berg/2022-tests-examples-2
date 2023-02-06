# -*- coding: utf-8 -*-
from time import time

import mock
from passport.backend.perimeter.auth_api.ldap.balancer import LdapBalancer
from passport.backend.perimeter.auth_api.test import BaseTestCase
import pytest


SERVERS = ('host1', 'host2', 'host3')


class TestBalancer(BaseTestCase):
    def setUp(self):
        self.balancer = LdapBalancer(SERVERS)
        ts = int(time()) - 1
        self.redis_get_mock = mock.Mock(return_value={
            'host1': ['%s:1' % ts],
            'host2': ['%s:2' % ts],
            'host3': ['%s:3' % ts],
        })
        self.redis_push_mock = mock.Mock(return_value=None)
        self.balancer._redis = mock.Mock()
        self.balancer._redis.get_lists = self.redis_get_mock
        self.balancer._redis.push_to_list = self.redis_push_mock

    def test_get_random_server__ok(self):
        assert self.balancer.get_random_server() in SERVERS

    def test_get_best_server__ok(self):
        assert self.balancer.get_best_server(), 'host1'

    def test_get_best_server__use_old_results_if_redis_unavailable(self):
        self.balancer.get_best_server()  # сохраняем результаты в локальный кэш

        self.redis_get_mock.return_value = {}
        assert self.balancer.get_best_server() == 'host1'
        # TODO: по возможности проверить логи

    def test_get_best_server__servers_changed_error(self):
        self.redis_get_mock.return_value = {'host1': [], 'host2': []}
        with pytest.raises(ValueError):
            self.balancer.get_best_server()

    def test_get_best_server__time_exceeeds_limit(self):
        assert self.balancer.get_best_server(max_time=0.5) is None

    def test_get_timings__ok(self):
        assert self.balancer.get_timings() == {'host1': 1.0, 'host2': 2.0, 'host3': 3.0}

    def test_get_timings__ignore_old_timings(self):
        ts = int(time()) - 1
        self.redis_get_mock.return_value = {'host1': ['%s:10' % ts, '123:1', '121:1'], 'host2': ['%s:2' % ts], 'host3': []}
        assert self.balancer.get_timings() == {'host1': 10.0, 'host2': 2.0, 'host3': None}

    def test_report_time__ok(self):
        self.balancer.report_time('host1', 9)

    def test_report_time__unknown_server(self):
        with pytest.raises(ValueError):
            self.balancer.report_time('host4', 1)
