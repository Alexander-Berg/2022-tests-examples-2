# -*- coding: utf-8 -*-

from datetime import datetime
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.models.domain import (
    ALIAS_DOMAIN,
    Domain,
    MASTER_DOMAIN,
    PartialPddDomain,
)
from passport.backend.core.undefined import Undefined


SLAVE_DOMAINS = [
    'slave1.ru',
    'slave2.ru',
]
INCORRECT_IDNA_DOMAIN = 'xn--a'


class TestPartialPddDomain(unittest.TestCase):

    def test_punycode_domain(self):
        domain = PartialPddDomain().parse({
            'domain': 'xn--80atjc.xn--p1ai',
        })
        eq_(domain.punycode_domain, 'xn--80atjc.xn--p1ai')

    def test_unicode_domain(self):
        domain = PartialPddDomain().parse({
            'domain': 'xn--80atjc.xn--p1ai',
        })
        eq_(domain.unicode_domain, u'окна.рф')

    def test_is_properties(self):
        domain = PartialPddDomain()
        domain.type = MASTER_DOMAIN
        ok_(domain.is_master)
        ok_(not domain.is_alias)

        domain.type = ALIAS_DOMAIN
        ok_(domain.is_alias)
        ok_(not domain.is_master)


class TestDomain(unittest.TestCase):

    def test_punycode_domain(self):
        domain = Domain().parse({
            'domain': 'xn--80atjc.xn--p1ai',
        })
        eq_(domain.punycode_domain, 'xn--80atjc.xn--p1ai')

    def test_unicode_domain(self):
        domain = Domain().parse({
            'domain': 'xn--80atjc.xn--p1ai',
        })
        eq_(domain.unicode_domain, u'окна.рф')

    def test_slave_domains(self):
        """
        Проверяем разбор и формирование списка алиасов для
        домена.
        """
        # > 1 домена
        domain = Domain().parse({
            'slaves': ','.join(SLAVE_DOMAINS),
        })
        eq_(domain.aliases, SLAVE_DOMAINS)

        # 1 домен
        domain = Domain().parse({
            'slaves': SLAVE_DOMAINS[0],
        })
        eq_(domain.aliases, SLAVE_DOMAINS[:1])

        # 2 кириллических домена: в юникоде и пуникоде
        domain = Domain().parse({
            'slaves': u'яндекс.ру,xn--c1aay4a.xn--p1ai',
        })
        eq_(domain.aliases, [u'яндекс.ру', u'гугл.рф'])

        # Пустой список
        domain = Domain().parse({
            'slaves': '',
        })
        eq_(domain.aliases, [])

        domain = Domain().parse({
            'slaves': None,
        })
        eq_(domain.aliases, [])

        # Некорректное значение поля (не строка)
        domain = Domain().parse({
            'slaves': 3,
        })
        eq_(domain.aliases, Undefined)

        # некорректно закодированный алиас
        with assert_raises(ValueError):
            Domain().parse({
                'slaves': 'xn--c1aay4a.xn--p1',
            })

    def test_get_alias_id(self):
        domain = Domain().parse({
            'slaves': ','.join(SLAVE_DOMAINS),
        })
        with assert_raises(ValueError):
            domain.get_alias_id(SLAVE_DOMAINS[0])

        domain.alias_to_id_mapping[SLAVE_DOMAINS[0]] = 1
        eq_(domain.get_alias_id(SLAVE_DOMAINS[0]), 1)

    def test_parse_enabled(self):
        """
        Проверяем обработку флага состояния домена.
        """

        # Разбор варианта из ответа userinfo
        domain = Domain().parse({
            'domain_ena': '1',
        })
        ok_(domain.is_enabled)

        # Разбор варианта из ответа hosted_domains
        domain = Domain().parse({
            'ena': '1',
        })
        ok_(domain.is_enabled)

        domain = Domain().parse({})
        eq_(domain.is_enabled, Undefined)

    @raises(ValueError)
    def test_parse_malformed_punycode(self):
        '''
        Проверка того, что при попытке конвертации некорректно закодированного
        в IDNA доменного имени мы выбрасываем ошибку.
        '''
        Domain().parse({
            'domain': INCORRECT_IDNA_DOMAIN,
        })

    def test_parse_domain_type(self):
        """
        Проверка обработки типа домена.
        """
        # У нас есть головной домен, следовательно мы - алиас
        domain = Domain().parse({
            'master_domain': u'master.ru'
        })
        eq_(domain.type, ALIAS_DOMAIN)
        ok_(not domain.is_master)
        ok_(domain.is_alias)

        # У нас нет головного домена, следовательно мы - полноценный домен
        domain = Domain().parse({
            'master_domain': u'',
        })
        eq_(domain.type, MASTER_DOMAIN)
        ok_(domain.is_master)
        ok_(not domain.is_alias)

        domain = Domain().parse({})
        eq_(domain.type, Undefined)

    def test_parse_user_change_password(self):
        """
        Проверяем, что флаг возможности смены пароля корректно
        обрабатывается.
        """
        # Специальный случай, когда мы скармливаем функции
        # parse результат вызова функции hosted_domains
        # для одного домена
        domain = Domain().parse({
            'hosted_domains': [
                {
                    'options': json.dumps({
                        'can_users_change_password': 1,
                    }),
                },
            ]
        })
        ok_(domain.can_users_change_password)

        domain = Domain().parse({
            'options': json.dumps({
                'can_users_change_password': 1,
            }),
        })
        ok_(domain.can_users_change_password)

        domain = Domain().parse({
            'options': json.dumps({
                'can_users_change_password': 0,
            }),
        })
        ok_(not domain.can_users_change_password)

        domain = Domain().parse({})
        ok_(domain.can_users_change_password)

    def test_parse_organization_name(self):
        domain = Domain().parse({
            'options': json.dumps({
                'organization_name': 'Organization',
            }),
        })
        eq_(domain.organization_name, 'Organization')

    def test_parse_generic_case(self):
        """
        Проверка обработки всего в комплексе.
        """
        domain = Domain().parse({
            'domid': u'1',
            'admin': u'2',
            'mx': u'1',
            'default_uid': u'1',
            'master_domain': u'yandex.ru',
            'domain': 'ya.ru',
            'domain_ena': u'1',
            'born_date': '2015-01-21 12:16:31',
            'options': u'{"can_users_change_password": 1}',
        })
        eq_(domain.id, 1)
        eq_(domain.admin_uid, 2)
        ok_(domain.is_yandex_mx)
        eq_(domain.default_uid, 1)
        eq_(domain.master_domain, 'yandex.ru')
        eq_(
            domain.registration_datetime,
            datetime(2015, 1, 21, 12, 16, 31),
        )
        ok_(domain.can_users_change_password)
        eq_(domain.domain, 'ya.ru')
        eq_(domain.organization_name, Undefined)

    def test_parse_invalid_hosted_domains(self):
        """
        Проверяем, что парсинг отсутствующих данных по домену или вообще к
        нему не относящихся данных не приводит к изменения объекта модели.
        """
        original = Domain().parse({
            'domid': u'1',
        })

        for data in (
            {'hosted_domains': []},
            {},
            {'answer': 42},
        ):
            domain = original.snapshot()
            domain.parse(data)
            eq_(domain, original)

    def test_parse_hosted_domains_heuristic(self):
        """
        Проверка отработки эвристики по разбору ответа от метода ЧЯ hosted_domains.
        В этом случае объекту домена должны присваиваться значения из первой записи
        возвращенного массива.
        """
        domain = Domain().parse({
            'hosted_domains': [
                {
                    'domid': u'1',
                    'admin': u'2',
                    'mx': u'1',
                    'default_uid': u'1',
                    'master_domain': u'yandex.ru',
                    'domain': 'ya.ru',
                    'domain_ena': u'1',
                    'born_date': '2015-01-21 12:16:31',
                    'options': u'{"can_users_change_password": 1}',
                },
                {
                    'domid': u'3',
                    'admin': u'42',
                    'mx': u'1',
                    'default_uid': u'1',
                    'master_domain': u'yandex.ru',
                    'domain': 'ya.ru',
                    'domain_ena': u'1',
                    'born_date': '2015-01-21 12:16:31',
                    'options': u'{"can_users_change_password": 1}',
                },
            ],
        })
        eq_(domain.id, 1)
        eq_(domain.admin_uid, 2)
        ok_(domain.is_yandex_mx)
        eq_(domain.default_uid, 1)
        eq_(domain.master_domain, 'yandex.ru')
        eq_(
            domain.registration_datetime,
            datetime(2015, 1, 21, 12, 16, 31),
        )
        ok_(domain.can_users_change_password)
        eq_(domain.domain, 'ya.ru')

    def test_double_parse_generic_case(self):
        """
        Проверяем, что двойная обработка одних и тех же
        входных данных не приводит к ошибкам.
        """
        incoming_data = {
            'domid': u'1',
            'admin': u'2',
            'mx': u'1',
            'default_uid': u'1',
            'master_domain': u'yandex.ru',
            'domain': 'ya.ru',
            'domain_ena': u'1',
            'born_date': '2015-01-21 12:16:31',
            'options': u'{"can_users_change_password": 1}',
        }

        domain = Domain().parse(incoming_data)
        domain = domain.parse(incoming_data)

        eq_(domain.id, 1)
        eq_(domain.admin_uid, 2)
        ok_(domain.is_yandex_mx)
        eq_(domain.default_uid, 1)
        eq_(domain.master_domain, 'yandex.ru')
        eq_(
            domain.registration_datetime,
            datetime(2015, 1, 21, 12, 16, 31),
        )
        ok_(domain.can_users_change_password)
        eq_(domain.domain, 'ya.ru')

    def test_parse_corrupt_options_json(self):
        """
        В случае, если поле options содержится некорректный
        JSON, ничего не происходит и поля принимают значения
        по умолчанию.
        """
        domain = Domain().parse({
            'options': 'asdkjaslkdjlkjklj323;'
        })

        ok_(domain.can_users_change_password)
