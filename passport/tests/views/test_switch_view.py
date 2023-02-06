# -*- coding: utf-8 -*-

from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestSwitchView(BaseTestClass):
    fill_database = True

    def test_switch(self):
        r = self.client.switch(uids=[100, 101], abc_ids=[22, 25], staff_ids=[24936, 64])
        self.assertDictEqual(r, {
            u'abc_ids': [{
                u'display_name': u'\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 '
                                 u'\u043f\u043e\u0440\u0442\u0430\u043b\u0430',
                u'id': 22,
                u'unique_name': u'custom'
            }, {
                u'display_name': u'\u041a\u0430\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0438\u0441\u043a\u0430',
                u'id': 25,
                u'unique_name': u'search-quality',
            }],
            u'staff_ids': [{
                u'display_name': u'\u041e\u0442\u0434\u0435\u043b '
                                 u'\u0440\u0430\u043d\u0436\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
                u'id': 64,
                u'unique_name': u'yandex_search_tech_quality',
            }, {
                u'display_name': u'\u041e\u0442\u0434\u0435\u043b '
                                 u'\u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u043f\u043e\u0438\u0441\u043a\u0430',
                u'id': 24936,
                u'unique_name': u'yandex_search_tech_quality_func',
            }],
            u'status': u'ok',
            u'uids': [{
                u'first_name': u'Vault',
                u'last_name': u'Test100',
                u'login': u'vault-test-100',
                u'uid': 100,
            }, {
                u'first_name': u'Vault',
                u'last_name': u'Test101',
                u'login': u'vault-test-101',
                u'uid': 101,
            }],
        })
