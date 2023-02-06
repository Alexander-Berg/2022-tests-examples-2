# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.test import TestCase


class IssueFormCase(TestCase):
    fixtures = ['default.json']

    def test_consumer_list(self):
        self.client.login(username='test1', password='secret')
        context = self.client.get('/grants/consumer/?namespace_id=1').context

        self.assertEqual(json.loads(context['namespaces']), [
            {u'id': 7, u'name': u'blackbox'},
            {u'id': 10, u'name': u'blackbox_by_client'},
            {u'id': 11, u'name': u'historydb'},
            {u'id': 8, u'name': u'oauth'},
            {u'id': 1, u'name': u'passport'},
            {u'id': 4, u'name': u'social api'},
            {u'id': 5, u'name': u'social proxy'},
            {u'id': 2, u'name': u'space2'},
            {u'id': 13, u'name': u'takeout'},
            {u'id': 12, u'name': u'tvm-api'},
            {u'id': 6, u'name': u'yasms'},
        ])
        self.assertEqual(json.loads(context['environments']), [
            {'type': 'production', 'id': 1, 'name': 'localhost'},
            {'type': 'testing', 'id': 2, 'name': 'localhost'},
            {'type': 'development', 'id': 3, 'name': 'localhost'},
            {'type': 'production', 'id': 4, 'name': 'intranet'},
            {'type': 'testing', 'id': 5, 'name': 'intranet'},
            {'type': 'development', 'id': 6, 'name': 'intranet'},
            {'type': 'stress', 'id': 7, 'name': 'stress'},
        ])
        sorted_env_groups = sorted(json.loads(context['env_groups']))
        self.assertEqual(sorted_env_groups, [
            ['intranet', 'Yandex-Team'],
            ['localhost', 'Yandex'],
            ['other', 'Остальные'],
            ['stress', 'Стресс'],
        ])
