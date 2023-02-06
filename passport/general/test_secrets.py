# -*- coding: utf-8 -*-
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.secrets import secrets
from passport.backend.qa.autotests.base.testcase import BaseTestCase


@allure_setup(feature='Автотесты', story='Работа с секретами')
class SecretsTestCase(BaseTestCase):
    def test_getitem_ok(self):
        assert secrets['test_secret'] == 'test value'
        assert secrets['test_secret_2'] == 'Кириллица'

    def test_getattr_ok(self):
        assert secrets.test_secret == 'test value'
        assert secrets.test_secret_2 == 'Кириллица'

    def test_other_case_ok(self):
        assert secrets['TeSt_SeCrEt'] == 'test value'
        assert secrets.TeSt_SeCrEt == 'test value'

    def test_secret_not_found(self):
        with self.assertRaises(KeyError):
            secrets.unexistent_secret
