# -*- coding: utf-8 -*-

from django.test import TestCase

from passport_grants_configurator.apps.core.common_deserializers import (
    deserialize_grants,
    deserialize_macroses,
)
from passport_grants_configurator.apps.core.models import (
    Action,
    Macros,
    Namespace,
)


class DeserializersTestCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def test_grant_deserializer(self):
        namespace = Namespace.objects.get(name='passport')
        meta_grants = deserialize_grants(Action.objects.filter(grant__namespace=namespace))
        self.assertEqual(meta_grants, {
            u'captcha': {
                u'*': u'Запросы к серверу капчи',
            },
            u'login': {
                u'suggest': u'Предложить возможный вариант логина',
                u'validate': u'Проверить правильность логина',
            },
            u'password': {
                u'is_changing_required': u'Требование сменить пароль на аккаунте',
                u'validate': u'Валидация пароля',
            },
            u'session': {
                u'check': u'Проверка cookie session_id',
                u'create': u'Создание сессии',
            },
            u'subscription': {
                u'something.create': u'passport subscription grant',
            },
        })

    def test_macros_deserializer(self):
        meta_macroses = deserialize_macroses(Macros.objects.filter(name=u'some_macros1'))
        self.assertEqual(meta_macroses, {
            u'some_macros1': [
                {
                    u'captcha': {
                        u'*': u'Запросы к серверу капчи',
                    },
                    u'login': {
                        u'suggest': u'Предложить возможный вариант логина',
                    },
                    u'session': {
                        u'check': u'Проверка cookie session_id',
                        u'create': u'Создание сессии',
                    },
                },
                u'Группа грантов some_macros1',
            ],
        })
