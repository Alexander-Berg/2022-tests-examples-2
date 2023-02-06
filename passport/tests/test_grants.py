# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    assert_false,
    assert_raises,
    assert_true,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.conf import settings
from passport.backend.core.grants import (
    check_grant as check_grant_grant,
    get_grants_config,
    Grants,
    GrantsError,
    InvalidSourceError,
    LoadGrantsError,
    MissingGrantsError,
    MissingOptionalGrantsError,
    MissingRequiredGrantsError,
    MissingTicketError,
    TicketParsingError,
    UnknownConsumerError,
)
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.grants.grants_config import (
    check_grant,
    check_specialtest_yandex_login_grant,
    check_substitute_consumer_ip_grant,
    check_substitute_user_ip_grant,
    get_yenv_type,
    GrantsConfig,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.logging_utils.faker.fake_tskv_logger import GraphiteLoggerFaker
from passport.backend.core.logging_utils.loggers import GraphiteLogger
from passport.backend.core.test.test_utils import (
    OPEN_PATCH_TARGET,
    settings_context,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
    TEST_INVALID_TICKET,
    TEST_TICKET,
)


TEST_GRANTS_FILES = [
    {
        'grants_dir': '/usr/lib/yandex/a/',
        'mask': 'consumer_grants.{env_type}.json',
    },
    {
        'grants_dir': '/usr/lib/yandex/b/',
        'mask': 'yasms_for_passport.{env_type}.json',
    },
    {
        'grants_dir': '/usr/lib/yandex/c/',
        'mask': '{env_type}.json',
    },
]


class TestGrants(TestCase):
    def test_grant_entity(self):
        eq_(check_grant('karma', {'karma': ['*']}), True)
        eq_(check_grant('k', {'karma': ['*']}), False)
        eq_(check_grant('', {'karma': ['*']}), False)

    def test_empty_grants(self):
        eq_(check_grant('karma', {}), False)
        eq_(check_grant('karma.*', {}), False)
        eq_(check_grant('karma.value', {}), False)

    def test_star_grant(self):
        eq_(check_grant('karma', {'karma': ['*']}), True)
        eq_(check_grant('karma', {'karma': ['more', '*']}), True)
        eq_(check_grant('karma.*', {'karma': ['*']}), True)
        eq_(check_grant('karma.*', {'karma': ['more', '*']}), True)
        eq_(check_grant('karma.value', {'karma': ['*']}), True)
        eq_(check_grant('karma.value', {'karma': ['more', '*']}), True)

    def test_precise_grant(self):
        eq_(check_grant('karma.precise', {'karma': ['precise']}), True)
        eq_(check_grant('karma.precise', {'karma': ['more', 'precise']}), True)

        eq_(check_grant('karma', {'karma': ['precise']}), False)
        eq_(check_grant('karma.*', {'karma': ['precise']}), False)
        eq_(check_grant('karma.pr', {'karma': ['precise']}), False)
        eq_(check_grant('karma.pr', {'karma': ['more', 'precise']}), False)

    def test_subscription_star_grant(self):
        eq_(check_grant('sub.*.narod', {'sub': {'mail': ['*']}}), False)
        eq_(check_grant('sub.update.narod', {'sub': {'mail': ['*']}}), False)
        eq_(check_grant('sub.*.mail', {'sub': {'mail': ['more']}}), False)

        eq_(check_grant('sub.*.mail', {'sub': {'mail': ['*']}}), True)
        eq_(check_grant('sub.more.mail', {'sub': {'mail': ['more', '*']}}), True)
        eq_(check_grant('sub.*.mail', {'sub': {'mail': ['*']}}), True)
        eq_(check_grant('sub.*.mail', {'sub': {'mail': ['more', '*']}}), True)
        eq_(check_grant('sub.update.mail', {'sub': {'mail': ['*']}}), True)
        eq_(check_grant('sub.update.mail', {'sub': {'mail': ['more', '*']}}), True)

    def test_subscription_precise_grant(self):
        eq_(check_grant('sub.update.mail', {'sub': {'mail': ['update']}}), True)
        eq_(check_grant('sub.update.mail', {'sub': {'mail': ['more', 'update']}}), True)

        eq_(check_grant('sub.*mail', {'sub': {'mail': ['update']}}), False)
        eq_(check_grant('sub.*.mail', {'sub': {'mail': ['update']}}), False)
        eq_(check_grant('sub.upd.mail', {'sub': {'mail': ['update']}}), False)
        eq_(check_grant('sub.upd.mail', {'sub': {'mail': ['more', 'update']}}), False)

    def test_empty_subscription_grants(self):
        eq_(check_grant('sub.*.mail', {'sub': {}}), False)
        eq_(check_grant('sub.*.mail', {'sub': {}}), False)
        eq_(check_grant('sub.upd.mail', {'sub': {}}), False)

    def test_check_grant_doesnt_iterate_over_strings(self):
        eq_(check_grant('karma', {'karma': 'str*ng'}), False)
        eq_(check_grant('karma.*', {'karma': 'str*ng'}), False)
        eq_(check_grant('karma.precise', {'karma': 'str*ng'}), False)

        eq_(check_grant('karma', {'karma': ['str*ng']}), False)
        eq_(check_grant('karma.*', {'karma': ['str*ng']}), False)
        eq_(check_grant('karma.precise', {'karma': ['str*ng']}), False)


@with_settings
class TestIPValidation(TestCase):
    def setUp(self):
        self.grants = FakeGrants()
        self.grants.start()

    def tearDown(self):
        self.grants.stop()
        del self.grants

    def test_ipv4(self):
        self.grants.set_grants_return_value(
            {'dev': {'networks': ['127.0.0.1', '127.0.0.2']}},
        )

        eq_(get_grants_config().is_valid_ip('127.0.0.2', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('127.0.0.3', 'dev'), False)

    def test_ipv4_cidr(self):
        self.grants.set_grants_return_value(
            {'dev': {'networks': ['127.0.0.0/31', '192.168.0.1/24']}},
        )

        eq_(get_grants_config().is_valid_ip('127.0.0.1', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('127.0.0.2', 'dev'), False)

        eq_(get_grants_config().is_valid_ip('192.168.0.2', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('192.168.1.2', 'dev'), False)

    def test_ipv6(self):
        self.grants.set_grants_return_value({'dev': {'networks': ['::1', '::2']}})

        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:2', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:3', 'dev'), False)

    def test_ipv6_cidr(self):
        self.grants.set_grants_return_value({'dev': {'networks': ['00::1/127', 'ff::1/120']}})

        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:1', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:2', 'dev'), False)

        eq_(get_grants_config().is_valid_ip('ff::1', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('ff::1:1', 'dev'), False)

    def test_ipv4_mapped(self):
        self.grants.set_grants_return_value({'dev': {'networks': ['77.75.158.64/26']}})
        eq_(get_grants_config().is_valid_ip('::ffff:77.75.158.119', 'dev'), True)

    def test_mixed(self):
        self.grants.set_grants_return_value({'dev': {'networks': ['127.0.0.1', '::1']}})

        eq_(get_grants_config().is_valid_ip('127.0.0.1', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:1', 'dev'), True)

    def test_mixed_cidr(self):
        self.grants.set_grants_return_value({'dev': {'networks': ['127.0.0.1/31', '::1/127']}})

        eq_(get_grants_config().is_valid_ip('127.0.0.1', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:1', 'dev'), True)

        eq_(get_grants_config().is_valid_ip('127.0.0.2', 'dev'), False)
        eq_(get_grants_config().is_valid_ip('0:0:0:0:0:0:0:2', 'dev'), False)


@with_settings()
class TestGrantsConfigBase(TestCase):
    def setUp(self):
        self.grants_config = FakeGrants()
        self.grants_config.start()

        self.grants_config.set_grants_return_value({
            'test': {
                'client': {},
                'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
                'grants': {
                    'karma': ['*'],
                    'subscription': {
                        'test': ['login_rule', 'create'],
                    },
                },
            },
            'test_with_tvm_client_id': {
                'client': {'client_id': 229},
                'networks': ['23.32.32.43', '23.32.32.44'],
                'grants': {
                    'karma': ['*'],
                    'subscription': {
                        'test': ['login_rule', 'create'],
                    },
                },
            },
            'test_with_other_tvm_client_id': {
                'client': {'client_id': 228},
                'networks': ['23.32.32.45'],
                'grants': {
                    'karma': ['*'],
                    'subscription': {
                        'test': ['login_rule', 'create'],
                    },
                },
            },
            'test6': {
                'client': {},
                'networks': ['192.0.0.1/8'],
                'grants': {
                    'karma': ['*'],
                    'password': ['is_changing_required'],
                    'subscription': {
                        'test6': ['*'],
                    },
                },
            },
            'mail': {'grants': {'karma': ['*']}, 'networks': ['77.88.59.147']},
            'kopalka': {
                'client': {},
                'grants': {'account': ['is_enabled'],
                           'subscription': {'test2': ['update'],
                                            'mail': ['update']}},
                'networks': ['77.88.12.113'],

            },
            'fotki': {
                'grants': {'subscription': {'fotki': ['*']}},
                'networks': ['77.88.59.146'],
            },
            'disk': {
                'grants': {'subscription': {'disk': ['*']}},
                'networks': ['77.88.59.146'],
            },
            (settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX + 'yandex-team'): {
                'grants': {},
                'networks': ['77.88.12.113', '87.250.232.64/27', '95.108.158.0/26'],
            },
            (settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX + 'yndx'): {
                'grants': {},
                'networks': ['77.88.12.113', '178.154.221.128/25'],
            },
            'without_grants': {
                'grants': {},
                'networks': ['111.111.111.111'],
            },
            'admreg_albireo': {
                'client': {},
                'grants': {'admreg': ['*']},
                'networks': ['178.154.246.118'],
            },
            'yacorp': {
                'client': {},
                'grants': {'subscription': {'yacorp': ['*']}},
                'networks': ['178.154.246.118'],
            },
            'overlap1': {
                'networks': ['192.0.0.1'],
                'grants': {
                    'password': ['is_changing_required'],
                },
            },
            'overlap2': {
                'networks': ['192.0.0.1/31'],
                'grants': {
                    'karma': ['*'],
                },
            },
            'mobileproxy_substitute_ip': {
                'networks': ['7.7.7.7'],
                'grants': {},
            },
            'allow_ya_consumer_real_ip': {
                'networks': ['9.9.9.9'],
                'grants': {},
            },
        })

        self.func_mock = mock.Mock()
        self.func_mock.__name__ = 'func_mock'

    def tearDown(self):
        self.grants_config.stop()
        del self.grants_config
        del self.func_mock


class TestGrantsConfigWithLegacyGetter(TestGrantsConfigBase):
    def setUp(self):
        super(TestGrantsConfigWithLegacyGetter, self).setUp()
        self.grants = Grants()

    def tearDown(self):
        super(TestGrantsConfigWithLegacyGetter, self).tearDown()

    def check_grants(self, grants, ip='127.0.0.1', consumer=None):
        self.grants.check_access(
            ip,
            get_grants_config().get_consumers(ip, consumer),
            grants,
            optional_grants=None,
            grants_args=[ip, consumer],
        )

    def test_str(self):
        ok_(str(get_grants_config()))

    def test_grants_entity_star(self):
        self.check_grants(['karma'], consumer='test')

    def test_grants_action_service(self):
        self.check_grants(['subscription.login_rule.test'], consumer='test')

    def test_grants_action_ip(self):
        self.check_grants(['subscription.create.test'])

    def test_grants_ip(self):
        self.check_grants(['subscription.*.test6'], ip='192.168.1.1')

    @raises(UnknownConsumerError)
    def test_grants_ip_range_error(self):
        self.check_grants(['karma'], ip='191.168.1.1')

    @raises(MissingRequiredGrantsError)
    def test_grants_missing(self):
        self.check_grants(['admfake'])

    @raises(MissingRequiredGrantsError)
    def test_grants_missing_star(self):
        self.check_grants(['subscription.*.test'], consumer='test')

    @raises(MissingRequiredGrantsError)
    def test_grants_missing_action(self):
        self.check_grants(['subscription.host_id.test'], consumer='test')

    @raises(MissingRequiredGrantsError)
    def test_grants_wrong_service(self):
        self.check_grants(['password.is_changing_required'], consumer='test')

    def test_grants_only_for_service_skip(self):
        def service_grant(ip, consumer, service='mail'):
            return ['password.is_changing_required'] if service == 'passport' else []

        self.check_grants([service_grant], consumer='test')

    @raises(MissingRequiredGrantsError)
    def test_grants_only_for_service_check(self):
        def service_grant(ip, consumer, service='passport'):
            return ['password.is_changing_required'] if service == 'passport' else []

        self.check_grants([service_grant], consumer='test')

    def test_complex_grants(self):
        self.check_grants(['password.is_changing_required'], ip='192.168.1.1', consumer='test6')

    def test_grants_with_ipv4_mapped(self):
        self.check_grants(['password.is_changing_required'], ip='::ffff:192.168.1.1')

    def test_kopalka_grants_with_service_and_consumer(self):
        self.check_grants(['subscription.update.mail'], ip='77.88.12.113', consumer='mail')

    def test_kopalka_grants_with_service_or_consumer_without_grants(self):
        self.check_grants(['subscription.update.test2'], ip='77.88.12.113', consumer='kopalka')
        self.check_grants(['subscription.update.test2'], ip='77.88.12.113', consumer='test2')

    def test_kopalka_grants_without_consumer(self):
        self.check_grants(['account.is_enabled'], ip='77.88.12.113')

    def test_grants_with_equal_networks_for_different_consumers(self):
        self.check_grants(['subscription.create.fotki'], ip='77.88.59.146', consumer='fotki')
        self.check_grants(['subscription.create.disk'], ip='77.88.59.146', consumer='disk')

    def test_not_required_grants(self):
        self.check_grants([], ip='77.88.59.146', consumer='fotki')

    def test_allow_create_test_yandex_login(self):
        assert_true(check_specialtest_yandex_login_grant('77.88.12.113', 'yandex-team'))
        assert_true(check_specialtest_yandex_login_grant('87.250.232.64', 'yandex-team'))
        assert_true(check_specialtest_yandex_login_grant('77.88.12.113', 'yndx'))
        assert_true(check_specialtest_yandex_login_grant('178.154.221.128', 'yndx'))
        assert_true(check_specialtest_yandex_login_grant('178.154.221.254', 'yndx'))

    def test_not_allow_create_test_yandex_login(self):
        assert_false(check_specialtest_yandex_login_grant('77.88.12.114', 'yandex-team'))
        assert_false(check_specialtest_yandex_login_grant('127.0.0.1', 'yandex-team'))
        assert_false(check_specialtest_yandex_login_grant('77.88.12.114', 'yndx'))
        assert_false(check_specialtest_yandex_login_grant('127.0.0.2', 'yndx'))

    def test_check_substitute_user_ip_grant(self):
        assert_true(check_substitute_user_ip_grant('7.7.7.7'))
        assert_false(check_substitute_user_ip_grant('7.7.7.8'))

    def test_check_substitute_consumer_ip_grant(self):
        assert_true(check_substitute_consumer_ip_grant('9.9.9.9'))
        assert_false(check_substitute_consumer_ip_grant('9.9.9.8'))

    @raises(MissingRequiredGrantsError)
    def test_consumer_without_grants(self):
        self.check_grants(['fakegrant'], ip='111.111.111.111', consumer='without_grants')

    def test_get_all_consumer(self):
        result = [c for c in get_grants_config().config.keys() if not c.lower().startswith(settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX)]
        eq_(get_grants_config().get_all_consumers(), result)

    @raises(UnknownConsumerError)
    def test_unavailable_consumer_in_grants(self):
        # данный тест проверяет, что мы не добавляем ноду в radix-дерево
        # c ip-адресами из спец консумера settings.TEST_YANDEX_LOGIN_CONSUMER_PREFIX
        self.check_grants(['g'], ip='178.154.221.128')

    def test_allow_subscription_grant(self):
        self.check_grants(['subscription.update.mail'], ip='77.88.12.113', consumer='kopalka')

    @raises(MissingRequiredGrantsError)
    def test_missing_subscrption_grant_for_consumer(self):
        self.check_grants(['subscription.create.mail'], ip='77.88.59.146', consumer='fotki')

    # блок тестов, посвящённых поиску consumer-а по ip,
    # когда consumer хранится множеством в radix-tree
    def test_consumer_admreg(self):
        self.check_grants(['admreg'], ip='178.154.246.118')

    def test_consumer_yacorp(self):
        self.check_grants(['subscription.create.yacorp'], ip='178.154.246.118')

    @raises(MissingRequiredGrantsError)
    def test_consumer_yacorp_admreg_without_grants(self):
        self.check_grants(['subscription.create.mail'], ip='178.154.246.118')


class TestGrantsExceptions(TestGrantsConfigBase):
    def test_grants_error(self):
        eq_(
            str(GrantsError('1.2.3.4', 'dev', 123)),
            '<GrantsError: consumer=dev, ip=1.2.3.4, tvm_client_id=123>',
        )

    def test_missing_grants_error(self):
        eq_(
            str(MissingGrantsError('grant', '1.2.3.4', 'dev', 123)),
            '<MissingGrantsError: consumer=dev, ip=1.2.3.4, missing_grants=grant, tvm_client_id=123>',
        )

    def test_ticket_parsing_error(self):
        eq_(
            str(TicketParsingError('debug_info', 'message', 'status', '1.2.3.4', 'dev', None)),
            '<TicketParsingError: consumer=dev, debug_info=debug_info, ip=1.2.3.4, message=message, tvm_client_id=None>'
        )


class TestGrantsConfig(TestGrantsConfigBase):
    def setUp(self):
        super(TestGrantsConfig, self).setUp()
        self._graphite_logger = GraphiteLogger()
        self._graphite_logger_faker = GraphiteLoggerFaker()
        self._graphite_logger_faker.start()
        self.grants = Grants(graphite_logger=self._graphite_logger)

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

    def tearDown(self):
        self._graphite_logger_faker.stop()
        self.fake_tvm_credentials_manager.stop()
        del self._graphite_logger_faker
        del self.fake_tvm_credentials_manager
        super(TestGrantsConfig, self).tearDown()

    def check_grants(self, required_grants, ip, consumer, optional_grants=None, service_ticket=None):
        self.grants.check_access(
            ip, set([consumer]), required_grants, optional_grants=optional_grants, service_ticket=service_ticket,
        )

    def test_check_grant_grant(self):
        check_grant_grant('subscription.create.test', '127.0.0.1', 'test')
        check_grant_grant('subscription.create.test', '127.0.0.1', 'test', TEST_TICKET)

    def test_grants_consumers_cache(self):
        grants = get_grants_config()
        # До первого вызова get_all_consumers() кэш пуст
        eq_(grants._consumer_cache, [])

        # Результат вызова функции равен содержимому кэша
        consumers = grants.get_all_consumers()
        eq_(grants._consumer_cache, consumers)

        # Значения берутся только из кэша
        grants._consumer_cache.append('test_consumer')
        grants.config = {}
        consumers = grants.get_all_consumers()
        eq_(grants._consumer_cache, consumers)

    def test_grants_entity_star(self):
        self.check_grants(['karma'], '127.0.0.1', 'test')

    def test_grants_action_service(self):
        self.check_grants(['subscription.login_rule.test'], '127.0.0.1', 'test')

    def test_grants_action_ip(self):
        self.check_grants(['subscription.create.test'], '127.0.0.1', 'test')

    def test_grants_ip(self):
        self.check_grants(['subscription.*.test6'], '192.168.1.1', 'test6')

    def test_grants_get_tvm_client_id(self):
        eq_(get_grants_config().get_tvm_client_id('test_with_tvm_client_id'), 229)
        ok_(get_grants_config().get_tvm_client_id('test5') is None)

    @raises(UnknownConsumerError)
    def test_grants_ip_range_error(self):
        self.check_grants(['karma'], '191.168.1.1', 'test6')

    def test_grants_ok_ticket(self):
        self.check_grants(['subscription.create.test'], '23.32.32.44', 'test_with_tvm_client_id', service_ticket=TEST_TICKET)

    @raises(InvalidSourceError)
    def test_grants_ticket_with_invalid_source(self):
        self.check_grants(['karma'], '23.32.32.45', 'test_with_other_tvm_client_id', service_ticket=TEST_TICKET)

    @raises(MissingTicketError)
    def test_grants_ticket_with_missing_ticket(self):
        self.check_grants(['karma'], '23.32.32.44', 'test_with_tvm_client_id', service_ticket=None)

    @raises(MissingTicketError)
    def test_grants_ticket_with_empty_ticket(self):
        self.check_grants(['karma'], '23.32.32.44', 'test_with_tvm_client_id', service_ticket='')

    @raises(TicketParsingError)
    def test_grants_ticket_with_invalid_ticket(self):
        self.check_grants(['karma'], '23.32.32.44', 'test_with_tvm_client_id', service_ticket=TEST_INVALID_TICKET)

    @raises(UnknownConsumerError)
    def test_grants_ticket_with_missing_ticket_and_wrong_ip(self):
        self.check_grants(['karma'], '191.168.1.1', 'test_with_tvm_client_id', service_ticket=None)

    @raises(TicketParsingError)
    def test_grants_with_not_required_but_invalid_ticket(self):
        self.check_grants(['subscription.create.test'], '127.0.0.1', 'test', service_ticket=TEST_INVALID_TICKET)

    @raises(MissingRequiredGrantsError)
    def test_grants_missing(self):
        self.check_grants(['admfake'], '127.0.0.1', 'test')

    @raises(MissingRequiredGrantsError)
    def test_grants_missing_star(self):
        self.check_grants(['subscription.*.test'], '127.0.0.1', 'test')

    @raises(MissingRequiredGrantsError)
    def test_grants_missing_action(self):
        self.check_grants(['subscription.host_id.test'], '127.0.0.1', 'test')

    @raises(MissingRequiredGrantsError)
    def test_grants_missing_grant(self):
        self.check_grants(['password.is_changing_required'], '127.0.0.1', 'test')

    def test_grants_with_ipv4_mapped(self):
        self.check_grants(['password.is_changing_required'], '::ffff:192.168.1.1', 'test6')

    def test_allow_subscription_grant(self):
        self.check_grants(['subscription.update.mail'], '77.88.12.113', 'kopalka')
        self.check_grants(['subscription.update.test2'], '77.88.12.113', 'kopalka')

    @raises(MissingRequiredGrantsError)
    def test_missing_subscription_grant(self):
        self.check_grants(['subscription.create.mail'], '77.88.59.146', 'fotki')

    def test_grants_with_equal_networks_for_different_consumers(self):
        self.check_grants(['subscription.create.fotki'], '77.88.59.146', 'fotki')
        self.check_grants(['subscription.create.disk'], '77.88.59.146', 'disk')

    def test_not_required_grants(self):
        self.check_grants([], ip='77.88.59.146', consumer='fotki')

    def test_allow_create_test_yandex_login(self):
        assert_true(check_specialtest_yandex_login_grant('77.88.12.113', 'yandex-team'))
        assert_true(check_specialtest_yandex_login_grant('87.250.232.64', 'yandex-team'))
        assert_true(check_specialtest_yandex_login_grant('77.88.12.113', 'yndx'))
        assert_true(check_specialtest_yandex_login_grant('178.154.221.128', 'yndx'))

    def test_not_allow_create_test_yandex_login(self):
        assert_false(check_specialtest_yandex_login_grant('77.88.12.114', 'yandex-team'))
        assert_false(check_specialtest_yandex_login_grant('127.0.0.1', 'yandex-team'))
        assert_false(check_specialtest_yandex_login_grant('77.88.12.114', 'yndx'))
        assert_false(check_specialtest_yandex_login_grant('127.0.0.2', 'yndx'))

    @raises(MissingRequiredGrantsError)
    def test_consumer_without_grants(self):
        self.check_grants(['fakegrant'], '111.111.111.111', 'without_grants')

    def test_overlapping_consumer_networks(self):
        # Не находим всех потребителей из-за несовпадающих, но пересекающихся сетей - такое поведение
        # сложилось исторически, влияет на легаси-апи и "тестовые логины".
        eq_(get_grants_config().get_consumers('192.0.0.1'), {'overlap1'})

        # Поиск IP идет в независимых деревьях, специфичных для потребителя
        self.check_grants(['password.is_changing_required'], '192.0.0.1', 'overlap1')
        self.check_grants(['karma.whatever'], '192.0.0.0', 'overlap2')
        self.check_grants(['karma.whatever'], '192.0.0.1', 'overlap2')

        with assert_raises(MissingRequiredGrantsError):
            self.check_grants(['password.is_changing_required'], '192.0.0.1', 'overlap2')

        with assert_raises(UnknownConsumerError):
            self.check_grants(['karma.whatever'], '192.0.0.0', 'overlap1')

        with assert_raises(MissingRequiredGrantsError):
            self.check_grants(['karma.whatever'], '192.0.0.1', 'overlap1')

    def test_graphite__no_required_grant(self):
        self.grants_config.set_grants_return_value({
            'leo': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': [],
                },
            },
        })

        try:
            self.check_grants(['tmnt.pizza'], '1.2.3.4', 'leo')
        except MissingRequiredGrantsError:
            pass

        self._graphite_logger_faker.assert_has_written([{
            'status': 'error',
            'ip': '1.2.3.4',
            'tvm_client_id': '-',
            'required_grants': 'tmnt.pizza',
            'consumers': 'leo',
            'missing_grants': 'tmnt.pizza',
            'reason': 'missing_grants',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_graphite__missing_ticket(self):
        try:
            self.check_grants(['karma'], '23.32.32.44', 'test_with_tvm_client_id', service_ticket=None)
        except MissingTicketError:
            pass

        self._graphite_logger_faker.assert_has_written([{
            'status': 'error',
            'ip': '23.32.32.44',
            'tvm_client_id': '-',
            'consumers': 'test_with_tvm_client_id',
            'reason': 'missing_ticket',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_graphite__forbidden_consumer_ip(self):
        self.grants_config.set_grants_return_value({
            'mike': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': ['pizza'],
                },
            },
        })

        try:
            self.check_grants(['tmnt.pizza'], '4.3.2.1', 'mike')
        except UnknownConsumerError:
            pass

        self._graphite_logger_faker.assert_has_written([{
            'status': 'error',
            'ip': '4.3.2.1',
            'tvm_client_id': '-',
            'consumers': 'mike',
            'reason': 'consumer_not_allowed',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_graphite__ok_grants_check(self):
        self.grants_config.set_grants_return_value({
            'mike': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': ['pizza'],
                },
            },
        })

        self.check_grants(['tmnt.pizza'], '1.2.3.4', 'mike')

        self._graphite_logger_faker.assert_has_written([{
            'status': 'ok',
            'ip': '1.2.3.4',
            'tvm_client_id': '-',
            'required_grants': 'tmnt.pizza',
            'consumers': 'mike',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_graphite__ok_grants_check_with_tvm(self):
        self.grants_config.set_grants_return_value({
            'mike': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': ['pizza'],
                },
                'client': {
                    'client_id': TEST_CLIENT_ID_2,
                },
            },
        })

        self.check_grants(['tmnt.pizza'], '1.2.3.4', 'mike', service_ticket=TEST_TICKET)

        self._graphite_logger_faker.assert_has_written([{
            'status': 'ok',
            'ip': '1.2.3.4',
            'tvm_client_id': str(TEST_CLIENT_ID_2),
            'required_grants': 'tmnt.pizza',
            'consumers': 'mike',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_graphite__no_required_grant_with_tvm(self):
        self.grants_config.set_grants_return_value({
            'leo': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': [],
                },
                'client': {
                    'client_id': TEST_CLIENT_ID_2,
                },
            },
        })

        try:
            self.check_grants(['tmnt.pizza'], '1.2.3.4', 'leo', service_ticket=TEST_TICKET)
        except MissingRequiredGrantsError:
            pass

        self._graphite_logger_faker.assert_has_written([{
            'status': 'error',
            'ip': '1.2.3.4',
            'tvm_client_id': str(TEST_CLIENT_ID_2),
            'required_grants': 'tmnt.pizza',
            'consumers': 'leo',
            'missing_grants': 'tmnt.pizza',
            'reason': 'missing_grants',
            'timestamp': self._graphite_logger_faker.get_timestamp_mock(),
            'unixtime': self._graphite_logger_faker.get_unixtime_mock(),
            'tskv_format': 'passport-log',
        }])

    def test_ok_optional_grants(self):
        self.grants_config.set_grants_return_value({
            'mike': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': ['pizza'],
                },
            },
        })

        self.check_grants([], '1.2.3.4', 'mike', optional_grants=['tmnt.pizza'])

    @raises(MissingOptionalGrantsError)
    def test_error__no_optional_grants(self):
        self.grants_config.set_grants_return_value({
            'leo': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': [],
                },
            },
        })

        self.check_grants([], '1.2.3.4', 'leo', optional_grants=['tmnt.pizza'])

    def test_graphite__no_optional_grants(self):
        self.grants_config.set_grants_return_value({
            'leo': {
                'networks': ['1.2.3.4'],
                'grants': {
                    'tmnt': [],
                },
            },
        })

        try:
            self.check_grants([], '1.2.3.4', 'leo', optional_grants=['tmnt.pizza'])
        except MissingOptionalGrantsError:
            pass

        self._graphite_logger_faker.assert_has_written([])


@with_settings(GRANTS_FILES=TEST_GRANTS_FILES)
class TestReadingGrants(TestCase):
    def setUp(self):
        self.load_json = mock.Mock()
        self.load_patch = mock.patch('passport.backend.core.grants.grants_config.load_json', self.load_json)
        self.load_patch.start()
        self.grants_config = GrantsConfig()

    def tearDown(self):
        self.load_patch.stop()
        del self.load_json
        del self.load_patch

    def test_first_load_grants_with_value_error(self):
        self.load_json.side_effect = ValueError(u'Monkey gone to heaven')
        with self.assertRaisesRegexp(
            LoadGrantsError,
            u'^Monkey gone to heaven$',
        ):
            self.grants_config._read_configs()

    def test_first_load_grants_with_io_error(self):
        exception = IOError(2, u'No such file or directory')
        exception.filename = u'mind'
        self.load_json.side_effect = exception
        with self.assertRaisesRegexp(
            LoadGrantsError,
            u'^No such file or directory \(mind\)$',
        ):
            self.grants_config._read_configs()

    def test_get_yenv_type(self):
        yenv = mock.Mock()
        with mock.patch('passport.backend.core.grants.grants_config.yenv', yenv):
            yenv.name = 'localhost'
            yenv.type = 'rc'
            eq_(get_yenv_type(), 'production')

            yenv.name = 'localhost'
            yenv.type = 'production'
            eq_(get_yenv_type(), 'production')

            yenv.name = 'intranet'
            yenv.type = 'production'
            eq_(get_yenv_type(), 'intranet.production')

            yenv.name = 'intranet'
            yenv.type = 'rc'
            eq_(get_yenv_type(), 'intranet.production')

    def test_reading_grants(self):
        with mock.patch('os.path.getmtime') as getmtime:
            self.load_json.side_effect = [
                {
                    'dev': {
                        'grants': {
                            'karma': ['*'],
                        },
                        'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
                    },
                },
                {
                    'old_yasms_grants_dev': {
                        'grants': {
                            'Registrator': ['Yes'],
                        },
                        'networks': ['23.32.32.43'],
                    },
                },
                {
                    'dev-c': {
                        'grants': {
                            'account': ['*'],
                        },
                        'networks': ['2001:DB8::/3'],
                    },
                },
            ]
            getmtime.side_effect = [
                1,
                2,
                3,
            ]

            grants = self.grants_config._read_configs()
            eq_(
                grants,
                {
                    'dev': {
                        'grants': {
                            'karma': ['*'],
                        },
                        'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
                    },
                    'old_yasms_grants_dev': {
                        'grants': {
                            'Registrator': ['Yes'],
                        },
                        'networks': ['23.32.32.43'],
                    },
                    'dev-c': {
                        'grants': {
                            'account': ['*'],
                        },
                        'networks': ['2001:DB8::/3'],
                    },
                },
            )
            eq_(
                self.load_json.call_args_list,
                [
                    (('/usr/lib/yandex/a/consumer_grants.development.json',),),
                    (('/usr/lib/yandex/b/yasms_for_passport.development.json',),),
                    (('/usr/lib/yandex/c/development.json',),),
                ],
            )
            eq_(
                self.grants_config._files_mtimes,
                {
                    '/usr/lib/yandex/a/consumer_grants.development.json': 1,
                    '/usr/lib/yandex/b/yasms_for_passport.development.json': 2,
                    '/usr/lib/yandex/c/development.json': 3,
                },
            )

    def test_single_file_ok(self):
        self.load_json.return_value = {
            'dev': {
                'grants': {
                    'karma': ['*'],
                },
                'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
            },
        }

        with settings_context(GRANTS_FILES=[TEST_GRANTS_FILES[0]]):
            with mock.patch('os.path.getmtime') as getmtime:
                getmtime.return_value = 1
                grants_config = GrantsConfig()
                grants = grants_config._read_configs()

        eq_(
            grants,
            {
                'dev': {
                    'grants': {
                        'karma': ['*'],
                    },
                    'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
                },
            },
        )
        eq_(
            self.load_json.call_args_list,
            [
                (('/usr/lib/yandex/a/consumer_grants.development.json',),),
            ],
        )
        eq_(
            grants_config._files_mtimes,
            {
                '/usr/lib/yandex/a/consumer_grants.development.json': 1,
            },
        )

    @raises(LoadGrantsError)
    def test_error_when_read_different_grant_files_with_identical_consumers(self):
        self.load_json.side_effect = [
            {
                'dev-a': {
                    'grants': {
                        'karma': ['*'],
                    },
                    'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
                },
            },
            {
                'dev-b': {
                    'grants': {
                        'Registrator': ['Yes'],
                    },
                    'networks': ['23.32.32.43'],
                },
            },
            {
                'dev-a': {
                    'grants': {
                        'Registrator': ['Yes'],
                    },
                    'networks': ['23.32.32.43'],
                },
            },
        ]
        self.grants_config._read_configs()


@with_settings
class TestGettingGrants(TestCase):
    def setUp(self):
        self.read_grants_func = mock.Mock()
        self.read_grants = mock.patch.object(
            GrantsConfig,
            '_read_configs',
            self.read_grants_func,
        )
        self.read_grants.start()
        LazyLoader.flush(instance_name='GrantsConfig')

    def tearDown(self):
        self.read_grants.stop()
        del self.read_grants
        del self.read_grants_func

    @raises(LoadGrantsError)
    def test_getting_grants_error(self):
        self.read_grants_func.side_effect = LoadGrantsError
        get_grants_config()

    def test_getting_grants(self):
        grants = {
            'dev': {
                'grants': {
                    'karma': ['*'],
                },
                'networks': ['23.32.32.43', '127.0.0.2/8', '2001:DB8::/3'],
            },
            'test': {
                'grants': {
                    'karma': ['*'],
                    'password': 'is_changing_required',
                    'subscription': {
                        'test6': ['*'],
                    },
                },
                'networks': ['192.0.0.1/8'],
            },
        }
        self.read_grants_func.return_value = grants

        eq_(get_grants_config().is_valid_ip('23.32.32.43', 'dev'), True)
        eq_(get_grants_config().is_valid_ip('192.0.0.2', 'test'), True)
        eq_(get_grants_config().is_valid_ip('192.0.0.2', 'dev'), False)
        eq_(get_grants_config().is_valid_ip('182.0.0.1', 'test'), False)

        eq_(check_grant('karma', get_grants_config().config.get('dev').get('grants')), True)
        eq_(check_grant('person', get_grants_config().config.get('dev').get('grants')), False)

        eq_(check_grant('karma', get_grants_config().config.get('test').get('grants')), True)
        eq_(check_grant('person', get_grants_config().config.get('test').get('grants')), False)
        eq_(check_grant('password.is_changing_required', get_grants_config().config.get('test').get('grants')), True)
        eq_(check_grant('blah', get_grants_config().config.get('test').get('grants')), False)

    def test_empty_grants(self):
        self.read_grants_func.return_value = {'dev': {}}

        eq_(get_grants_config().config.get('dev', {}).get('grants'), None)
        eq_(get_grants_config().config.get('dev', {}).get('networks'), None)


@with_settings
class TestReloadingGrants(TestCase):
    def setUp(self):
        self.read_grants_func = mock.Mock()
        self.read_grants = mock.patch.object(
            GrantsConfig,
            '_read_configs',
            self.read_grants_func,
        )
        self.read_grants.start()

    def tearDown(self):
        self.read_grants.stop()
        del self.read_grants
        del self.read_grants_func

    def test_reload_grants_with_exceptions(self):
        grants = GrantsConfig()
        example_grants = {
            'dev': {'networks': ['127.0.0.1'], 'grants': {'karma': ['*']}},
        }
        self.read_grants_func.return_value = example_grants
        grants.load()

        grants.expires_at -= 3600

        self.read_grants_func.side_effect = LoadGrantsError('Some error')
        grants.load()

    def test_reload_grants(self):
        grants = GrantsConfig()
        example_grants = {
            'dev': {'networks': ['127.0.0.1'], 'grants': {'karma': ['*']}},
        }
        self.read_grants_func.return_value = example_grants
        grants.load()

        grants.expires_at -= 3600

        example_grants = {
            'dev': {'networks': ['127.0.0.2'], 'grants': {'person': ['*']}},
        }
        self.read_grants_func.return_value = example_grants
        grants.load()
        eq_(grants.is_valid_ip('127.0.0.2', 'dev'), True)
        eq_(grants.is_valid_ip('127.0.0.1', 'dev'), False)

        eq_(check_grant('karma', grants.config.get('dev').get('grants')), False)
        eq_(check_grant('person', grants.config.get('dev').get('grants')), True)

    def test_reload_grant_with_consumer_without_networks(self):
        grants = GrantsConfig()
        self.read_grants_func.return_value = {
            'dev': {'networks': ['127.0.0.1'], 'grants': {'karma': ['*']}},
        }
        grants.load()

        grants.expires_at -= 3600

        example_grants = {
            'dev': {'grants': {'karma': ['*']}},
        }
        self.read_grants_func.return_value = example_grants
        grants.load()

        eq_(check_grant('karma', grants.config.get('dev').get('grants')), True)
        eq_(grants.config.get('dev').get('netwoks'), None)


@with_settings(GRANTS_FILES=TEST_GRANTS_FILES)
class TestReloadingCachedGrants(TestCase):
    def setUp(self):
        self.getmtime_patch = mock.patch('os.path.getmtime', return_value=1)
        self.getmtime_patch.start()

    def tearDown(self):
        self.getmtime_patch.stop()

    def test_reload_grants_not_modified(self):
        grants = {
            'dev': {
                'networks': ['127.0.0.2'],
                'grants': {
                    'person': ['*'],
                },
            },
        }
        mock_open = mock.MagicMock(
            side_effect=lambda fn: grants if fn == '/usr/lib/yandex/a/consumer_grants.development.json' else {},
        )
        with mock.patch.object(
            GrantsConfig,
            'read_config_file',
            mock_open,
            create=True,
        ):
            grants_config = GrantsConfig()
            # Проверяем, что первоначальная загрузка без дополнительной
            # информации о файлах выдает список грантов и словарь с временами
            # модификации.
            new_grants = grants_config._read_configs()
            eq_(new_grants, grants)

            # Проверяем, что если файлы с грантами не были модифицированы
            # (т.е. время их модификации совпадает с переданным), то
            # нам не будет возвращен список новых грантов.
            mtimes = grants_config._files_mtimes.copy()
            reloaded_grants = grants_config._read_configs()
            eq_(reloaded_grants, None)
            eq_(grants_config._files_mtimes, mtimes)

            # Имитируем модификацию файлов через уменьшение известных
            # нам временных меток модификации файлов.
            for fn in grants_config._files_mtimes.keys():
                grants_config._files_mtimes[fn] -= 1

            # Если время модификации не совпадает с переданным, то файлы будут
            # перечитаны и возвращен список грантов. Также проверяем, что нам
            # вернется словарь с обновленными временами доступа.
            reloaded_grants = grants_config._read_configs()
            eq_(reloaded_grants, grants)
            eq_(grants_config._files_mtimes, mtimes)

    def test_grants_config_load_grants(self):
        grants_config = GrantsConfig()
        with mock.patch.object(
            GrantsConfig,
            '_read_configs',
            mock.Mock(return_value=None),
        ):
            grants_config.load()
            eq_(grants_config._consumer_cache, [])

    @raises(LoadGrantsError)
    def test_load_grants_not_found(self):
        self.getmtime_patch.stop()
        self.getmtime_patch = mock.patch('os.path.getmtime', side_effect=OSError)
        self.getmtime_patch.start()

        def ioerror_raiser(fn):
            raise IOError('Hello, world!', 'Monkey has gone to heaven')

        with mock.patch(
            OPEN_PATCH_TARGET,
            side_effect=ioerror_raiser,
            create=True,
        ):
            grants_config = GrantsConfig()
            grants_config.load()
