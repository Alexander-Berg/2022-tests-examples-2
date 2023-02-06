# -*- coding: utf-8 -*-

from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestSuggestView(BaseTestClass):
    fill_database = True
    send_user_ticket = True

    def test_suggest(self):
        r = self.client.suggest(query=u'Пер')
        self.assertDictEqual(r, {
            'abc_departments': [{
                'display_name': u'\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u0441\u0430\u0434\u0436\u0435\u0441\u0442\u0430',
                'id': 50,
                'unique_name': 'suggest',
                'roles': [
                    {
                        u'display_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u0447\u0438\u043a',
                        u'id': 8,
                    },
                    {
                        u'display_name': u'\u0421\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0439 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440',
                        u'id': 16,
                    },
                ],
                'scopes': [
                    {
                        'display_name': u'\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435',
                        'unique_name': u'administration',
                    },
                    {
                        'display_name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                        u'unique_name': u'development',
                    },
                ],
            }],
            'staff_departments': [],
            'status': 'ok',
            'users': [{
                'first_name': u'\u041f\u0430\u0448\u0430',
                'last_name': u'\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u0446\u0435\u0432',
                'login': 'ppodolsky',
                'uid': 1120000000038274,
                'staff_info': {
                    u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 '
                                     u'\u0438 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438 '
                                     u'\u0441\u0438\u0441\u0442\u0435\u043c \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                    u'id': 2864,
                    u'unique_name': u'yandex_personal_com_aux_sec',
                },
            }],
        })

    def test_find_abc_services(self):
        r = self.client.suggest(query=u'портал')
        self.assertListEqual(
            r['abc_departments'],
            [{u'display_name': u'\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043f\u043e\u0440\u0442\u0430\u043b\u0430',
              u'id': 22,
              u'roles': [],
              u'scopes': [],
              u'unique_name': u'custom'},
             {u'display_name': u'\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u043f\u043e\u0440\u0442\u0430\u043b\u0443 (stat.yandex.ru)',
              u'id': 20,
              u'roles': [],
              u'scopes': [],
              u'unique_name': u'stat'}],
        )

    def test_find_abc_services_by_abc_id(self):
        r = self.client.suggest(query=u'20')
        self.assertListEqual(
            r['abc_departments'],
            [{u'display_name': u'\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e \u043f\u043e\u0440\u0442\u0430\u043b\u0443 (stat.yandex.ru)',
              u'id': 20,
              u'roles': [],
              u'scopes': [],
              u'unique_name': u'stat'}],
        )

    def test_find_staff_departments(self):
        r = self.client.suggest(query=u'поиск')
        self.assertListEqual(
            r['staff_departments'],
            [{u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0434\u0438\u0437\u0430\u0439\u043d\u0430 '
                               u'\u0432\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0445 '
                               u'\u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432 \u043f\u043e\u0438\u0441\u043a\u0430',
              u'id': 29453,
              u'unique_name': u'yandex_design_search_vertical'},
             {u'display_name': u'\u041e\u0442\u0434\u0435\u043b \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0433\u043e '
                               u'\u043f\u043e\u0438\u0441\u043a\u0430',
              u'id': 236,
              u'unique_name': u'yandex_search_tech_spam'},
             {u'display_name': u'\u041e\u0442\u0434\u0435\u043b \u0444\u0443\u043d\u043a\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 '
                               u'\u043f\u043e\u0438\u0441\u043a\u0430',
              u'id': 24936,
              u'unique_name': u'yandex_search_tech_quality_func'},
             {u'display_name': u'\u0421\u043b\u0443\u0436\u0431\u0430 \u0433\u0435\u043e\u043f\u043e\u0438\u0441\u043a\u0430 '
                               u'\u0438 \u0441\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u0430',
              u'id': 80036,
              u'unique_name': u'yandex_search_tech_sq_3452'},
             {u'display_name': u'\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430 '
                               u'\u043f\u043e\u0438\u0441\u043a\u043e\u0432\u044b\u0445 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u043e\u0432',
              u'id': 38096,
              u'unique_name': u'yandex_search_tech_sq'}],
        )

    def test_find_users_by_login(self):
        r = self.client.suggest(query=u'ppodol')
        self.assertListEqual(
            r['users'],
            [{
                'first_name': u'\u041f\u0430\u0448\u0430',
                'last_name': u'\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u0446\u0435\u0432',
                'login': 'ppodolsky',
                'uid': 1120000000038274,
                'staff_info': {
                    u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 '
                                     u'\u0438 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438 '
                                     u'\u0441\u0438\u0441\u0442\u0435\u043c \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                    u'id': 2864,
                    u'unique_name': u'yandex_personal_com_aux_sec',
                },
            }],
        )

        r = self.client.suggest(query=u'podolsky')
        self.assertListEqual(
            r['users'],
            [],
        )

    def test_find_users_by_name(self):
        r = self.client.suggest(query=u'Паша Переведен')
        self.assertListEqual(
            r['users'],
            [{
                'first_name': u'\u041f\u0430\u0448\u0430',
                'last_name': u'\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u0446\u0435\u0432',
                'login': 'ppodolsky',
                'uid': 1120000000038274,
                'staff_info': {
                    u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 '
                                     u'\u0438 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438 '
                                     u'\u0441\u0438\u0441\u0442\u0435\u043c \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                    u'id': 2864,
                    u'unique_name': u'yandex_personal_com_aux_sec',
                },
            }],
        )

        r = self.client.suggest(query=u'  Переведенцев   Паша  ')
        self.assertListEqual(
            r['users'],
            [{
                'first_name': u'\u041f\u0430\u0448\u0430',
                'last_name': u'\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u0446\u0435\u0432',
                'login': 'ppodolsky',
                'uid': 1120000000038274,
                'staff_info': {
                    u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 '
                                     u'\u0438 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438 '
                                     u'\u0441\u0438\u0441\u0442\u0435\u043c \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                    u'id': 2864,
                    u'unique_name': u'yandex_personal_com_aux_sec',
                },
            }],
        )

    def test_find_users_by_uid(self):
        r = self.client.suggest(query=u'1120000000038274')
        self.assertListEqual(
            r['users'],
            [{
                'first_name': u'\u041f\u0430\u0448\u0430',
                'last_name': u'\u041f\u0435\u0440\u0435\u0432\u0435\u0434\u0435\u043d\u0446\u0435\u0432',
                'login': 'ppodolsky',
                'uid': 1120000000038274,
                'staff_info': {
                    u'display_name': u'\u0413\u0440\u0443\u043f\u043f\u0430 \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0438 '
                                     u'\u0438 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438 '
                                     u'\u0441\u0438\u0441\u0442\u0435\u043c \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438',
                    u'id': 2864,
                    u'unique_name': u'yandex_personal_com_aux_sec',
                },
            }],
        )

    def test_tvm_suggest(self):
        self.assertListEqual(
            self.client.suggest_tvm(u'Test', abc_state='granted', limit=2)['tvm_apps'],
            [{u'abc_state': u'granted',
              u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
              u'name': u'Test app',
              u'tvm_client_id': 2000371},
             {u'abc_state': u'granted',
              u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
              u'name': u'test-moodle',
              u'tvm_client_id': 2000368}],
        )

        self.assertListEqual(
            self.client.suggest_tvm(u'003', abc_state='granted', limit=2)['tvm_apps'],
            [{u'abc_state': u'granted',
              u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
              u'name': u'Test app',
              u'tvm_client_id': 2000371},
             {u'abc_department': {u'display_name': u'\u041f\u0430\u0441\u043f\u043e\u0440\u0442',
                                  u'id': 14,
                                  u'unique_name': u'passp'},
              u'abc_state': u'granted',
              u'abc_state_display_name': u'\u0412\u044b\u0434\u0430\u043d',
              u'name': u'passport_likers3',
              u'tvm_client_id': 2000355}],
        )
