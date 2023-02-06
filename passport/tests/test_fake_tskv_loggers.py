# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    AccessLoggerFaker,
    AccountModificationInfosecLoggerFaker,
    AccountModificationLoggerFaker,
    AvatarsLoggerFaker,
    BASE_STATBOX_TEMPLATES,
    GraphiteLoggerFaker,
    PharmaLoggerFaker,
    PhoneLoggerFaker,
    StatboxLoggerFaker,
    YasmsPrivateLoggerFaker,
)
from passport.backend.core.logging_utils.loggers import (
    AccessLogger,
    AccountModificationInfosecLogger,
    AccountModificationLogger,
    AvatarsLogger,
    GraphiteLogger,
    PharmaLogger,
    PhoneLogger,
    StatboxLogger,
    YasmsPrivateLogger,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts
from six import iteritems


class TestStatboxFakerTemplates(TestCase):
    def setUp(self):
        super(TestStatboxFakerTemplates, self).setUp()
        self.faker = StatboxLoggerFaker()
        self.faker.start()

    def tearDown(self):
        super(TestStatboxFakerTemplates, self).tearDown()
        self.faker.stop()
        del self.faker

    def test_faker_base_templates(self):
        """
        Проверяем, что сформированные записи получаются сложением
        базовой записи и шаблона.
        """
        base = self.faker.entry('base')
        eq_(base['unixtime'], TimeNow())
        eq_(self.faker.base_entry, {})

        for tag, template in iteritems(BASE_STATBOX_TEMPLATES):
            entry = self.faker.entry(tag)
            expected = merge_dicts(base, template)

            for name, value in iteritems(expected):
                if callable(value):
                    expected[name] = value()

            eq_(entry, expected)

    def test_faker_bind_base(self):
        """
        Проверяем, что внесение изменений в базовый шаблон не влияет
        и на все сформированные записи.
        """
        self.faker.bind_base(hello='world')

        for tag, template in iteritems(BASE_STATBOX_TEMPLATES):
            entry = self.faker.entry(tag)
            ok_('hello' not in entry)

    def test_faker_adds_base_template(self):
        """
        Проверим, что записи из шаблона base добавляются в каждую запись.
        """
        entry = self.faker.entry(None, key='value')
        eq_(
            entry,
            dict(
                BASE_STATBOX_TEMPLATES['base'],
                key='value',
                unixtime=TimeNow(),
                timestamp=DatetimeNow(convert_to_datetime=True),
                timezone='+0300',
            ),
        )

    def test_faker_callable_entries(self):
        """
        Если в entry callable объект, то должны получить значение при вызове entry.
        """
        ok_(callable(BASE_STATBOX_TEMPLATES['base']['unixtime']))

        entry = self.faker.entry(None, key='value')
        eq_(entry['unixtime'], TimeNow())

    def test_faker_bind_entry(self):
        """
        Проверяем, что запись на основе собственноручно зарегистрированного
        шаблона все равно строится на основе базовой.
        """
        self.faker.bind_entry('custom', hello='world')

        base = self.faker.entry('base')
        entry = self.faker.entry('custom')
        eq_(entry, merge_dicts(base, dict(hello='world')))

    def test_faker_entry_inheritance(self):
        """
        Проверяем, что созданная от унаследованного шаблона запись содержит
        как поля самого шаблона + дополнительные аргументы, так и поля
        его родителя.
        """
        self.faker.bind_entry('ancestor', hello='world')
        self.faker.bind_entry(
            'custom',
            _inherit_from='ancestor',
            foo='bar',
        )
        result = self.faker.entry('custom', a=42)
        eq_(result['hello'], 'world')
        eq_(result['foo'], 'bar')
        eq_(result['a'], 42)

        # Проверяем, что внесение изменений в родительский шаблон
        # не отражается на унаследованном шаблоне
        self.faker.bind_entry('ancestor', hello='another world')
        result = self.faker.entry('custom')
        eq_(result['hello'], 'world')

    def test_inherit_list_of_entries(self):
        """
        Проверяем, что унаследовались от списка шаблонов по порядку.
        """
        self.faker.bind_entry(
            'ancestor1',
            hello='smarty',
            sleep='engineer',
        )
        self.faker.bind_entry(
            'ancestor2',
            sleep='whoever',
            bye='smarty',
        )
        self.faker.bind_entry(
            'descendant',
            _inherit_from=['ancestor1', 'ancestor2'],
            miss='engineer',
        )
        result = self.faker.entry('descendant', moar_data='dodge')
        eq_(result['hello'], 'smarty')
        eq_(result['sleep'], 'whoever')
        eq_(result['bye'], 'smarty')
        eq_(result['miss'], 'engineer')
        eq_(result['moar_data'], 'dodge')

        # Проверяем, что внесение изменений в родительский шаблон
        # не отражается на унаследованном шаблоне
        self.faker.bind_entry('ancestor1', hello='stupid')
        result = self.faker.entry('descendant')
        eq_(result['hello'], 'smarty')

    def test_inherit_empty_list(self):
        """
        Проверяем, что пустой список шаблонов, от которого наследуемся, ничего не сломает.
        """
        self.faker.bind_entry('ancestor1', hello='smarty')
        self.faker.bind_entry('ancestor1', _inherit_from=[])
        result = self.faker.entry('ancestor1', bye='smarty')
        eq_(result['hello'], 'smarty')
        eq_(result['bye'], 'smarty')

        self.faker.bind_entry('ancestor2', _inherit_from=[])
        result = self.faker.entry('ancestor2', bye='beauty')
        eq_(
            result,
            dict(
                self.faker.entry('base'),
                bye='beauty',
            ),
        )

    def test_faker_exclude_fields(self):
        """
        Проверяем, что указанные для исключения поля не попадут в
        созданную запись.
        """
        self.faker.bind_entry('custom', a=42, b=65535)
        result = self.faker.entry('custom', _exclude=['a'])
        ok_('a' not in result)

    def test_faker_bind_exclude_fields(self):
        """
        Проверяем, что указанные для исключения поля не попадут в
        созданную запись.
        """
        self.faker.bind_entry('custom', a=42, b=65535, _exclude=['a'])
        result = self.faker.entry('custom')
        ok_('a' not in result)

    @raises(AssertionError)
    def test_assert_equal_empty_error(self):
        logger = StatboxLogger()
        logger.log(hello='world')
        self.faker.assert_equals([])

    def test_assert_equals(self):
        logger = StatboxLogger()
        logger.log(hello='world')

        self.faker.assert_equals(
            [
                {
                    'hello': 'world',
                    'tskv_format': 'passport-log',
                    'py': '1',
                    'unixtime': TimeNow(),
                    'timestamp': DatetimeNow(convert_to_datetime=True),
                    'timezone': '+0300',
                },
            ]
        )

    def test_assert_equals_last(self):
        logger = StatboxLogger()
        logger.log(first='first')
        logger.log(hello='world')

        self.faker.assert_equals(
            [
                {
                    'hello': 'world',
                    'tskv_format': 'passport-log',
                    'py': '1',
                    'unixtime': TimeNow(),
                    'timestamp': DatetimeNow(convert_to_datetime=True),
                    'timezone': '+0300',
                },
            ],
            offset=-1,
        )

    def test_assert_contains(self):
        logger = StatboxLogger()
        logger.log(light='dark')
        logger.log(hello='world')
        logger.log(up='down')

        self.faker.assert_contains(
            [
                self.faker.entry('base', hello='world'),
                self.faker.entry('base', up='down'),
            ]
        )

    def test_assert_contains_single_argument(self):
        logger = StatboxLogger()
        logger.log(light='dark')
        logger.log(hello='world')
        logger.log(up='down')

        self.faker.assert_contains(
            self.faker.entry('base', hello='world'),
        )

    def test_assert_equals_single_argument(self):
        logger = StatboxLogger()
        logger.log(hello='world')

        self.faker.assert_equals(
            self.faker.entry('base', hello='world'),
        )

    @raises(AssertionError)
    def test_assert_contains_not(self):
        logger = StatboxLogger()
        logger.log(light='dark')
        logger.log(hello='world')
        logger.log(up='down')

        self.faker.assert_contains(
            [
                self.faker.entry('base', hello='smaller world'),
            ]
        )

    @raises(AssertionError)
    def test_assert_expected_too_many(self):
        logger = StatboxLogger()
        logger.log(hello='world')

        self.faker.assert_contains(
            [
                self.faker.entry('base', hello='smaller world'),
                self.faker.entry('base', hello='world'),
            ]
        )


class BaseLoggerFakerTestCase(object):
    FAKER_CLS = None
    LOGGER_CLS = None
    LOG_CONTEXT = dict(foo='bar')

    def setUp(self):
        self.faker = self.FAKER_CLS()
        self.logger = self.LOGGER_CLS()
        self.log_context = dict(self.LOG_CONTEXT)

    def tearDown(self):
        del self.faker
        del self.logger
        del self.log_context

    def test_logger_iface_is_mocked(self):
        ok_(not isinstance(self.logger._write_to_log, mock.Mock))
        self.faker.start()
        try:
            ok_(isinstance(self.logger._write_to_log, mock.Mock))
        finally:
            self.faker.stop()

    def test_logger_calls_log(self):
        self.faker.start()
        try:
            ok_(not self.logger._write_to_log.called)
            self.logger.log(**self.log_context)
            ok_(self.logger._write_to_log.called)
        finally:
            self.faker.stop()


class StatboxLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = StatboxLoggerFaker
    LOGGER_CLS = StatboxLogger


class PharmaLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = PharmaLoggerFaker
    LOGGER_CLS = PharmaLogger


class GraphiteLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = GraphiteLoggerFaker
    LOGGER_CLS = GraphiteLogger


class PhoneLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = PhoneLoggerFaker
    LOGGER_CLS = PhoneLogger


class AccessLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = AccessLoggerFaker
    LOGGER_CLS = AccessLogger


class AvatarsLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = AvatarsLoggerFaker
    LOGGER_CLS = AvatarsLogger


class YasmsPrivateLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = YasmsPrivateLoggerFaker
    LOGGER_CLS = YasmsPrivateLogger
    LOG_CONTEXT = dict(foo='bar', global_smsid='global-sms-id')


class AccountModificationLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = AccountModificationLoggerFaker
    LOGGER_CLS = AccountModificationLogger


class AccountModificationInfosecLoggerFakerTestCase(BaseLoggerFakerTestCase, TestCase):
    FAKER_CLS = AccountModificationInfosecLoggerFaker
    LOGGER_CLS = AccountModificationInfosecLogger
