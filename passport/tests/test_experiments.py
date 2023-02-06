# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import ok_
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.utils.experiments import (
    is_experiment_enabled_by_login,
    is_experiment_enabled_by_phone,
    is_experiment_enabled_by_time,
    is_experiment_enabled_by_uid,
)


class TestExperiments(unittest.TestCase):
    def test_enable_user_experiment_by_time(self):
        with mock.patch('time.time') as time_mock:
            time_mock.return_value = 6
            ok_(is_experiment_enabled_by_time(3))
            ok_(not is_experiment_enabled_by_time(5))
            ok_(not is_experiment_enabled_by_time(0))

            time_mock.return_value = 1106
            ok_(is_experiment_enabled_by_time(3))
            ok_(not is_experiment_enabled_by_time(5))
            ok_(not is_experiment_enabled_by_time(0))

    def test_enable_user_experiment_by_uid(self):
        uid = 123456
        ok_(is_experiment_enabled_by_uid(uid, 2))
        ok_(not is_experiment_enabled_by_uid(uid, 5))
        ok_(not is_experiment_enabled_by_uid(uid, 0))

    def test_enable_user_experiment_by_login(self):
        login = 'c_user'
        ok_(not is_experiment_enabled_by_login(login, 2))
        ok_(is_experiment_enabled_by_login(login, 3))
        ok_(is_experiment_enabled_by_login(login, 39))
        ok_(not is_experiment_enabled_by_login(login, 0))

    def test_enable_user_experiment_by_phone(self):
        phone = PhoneNumber.parse('+7 985 4567890')
        ok_(is_experiment_enabled_by_phone(phone, 2))
        ok_(is_experiment_enabled_by_phone(phone, 3))
        ok_(not is_experiment_enabled_by_phone(phone, 7))
        ok_(not is_experiment_enabled_by_phone(phone, 0))
