# -*- coding: utf-8 -*-

import json
from unittest import TestCase

import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.blackbox.parsers import parse_blackbox_userinfo_response
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.mailer.faker import FakeMailer
from passport.backend.core.mailer.faker.mail_utils import (
    create_native_email,
    create_validated_external_email,
)
from passport.backend.core.mailer.utils import (
    create_user_message,
    get_tld_by_country,
    login_shadower,
    MailInfo,
    make_email_context,
    send_mail_for_account,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils import with_settings


TEST_LOGIN1 = 'test_login1'
TEST_TEMPLATE1 = 'test_template1'
TEST_TEMPLATE_NAME1 = 'test_template_name1'
TEST_UID1 = 1
TEST_MAIL_NOISE_IMAGE_URL = 'test_mail_noise_image_url'
TEST_MAIL_SHADOW_IMAGE_URL = 'test_mail_shadow_image_url'
TEST_FIRSTNAME = 'test_firstname'
TEST_DISPLAY_LOGIN = 'TestDisplayLogin'
TEST_DISPLAY_NAME = 'Test Display Name'
TEST_LANGUAGE = 'lang'


@with_settings(
    MAIL_DEFAULT_FROM_ADDRESS='test@yandex.%s',
    MAIL_DEFAULT_REPLY_TO=('', 'noreply-test@yandex.%s'),
)
class TestCreateUserMessage(TestCase):
    def setUp(self):
        self.mailer = FakeMailer()
        self.mailer.start()

    def tearDown(self):
        self.mailer.stop()
        del self.mailer

    def test_create_user_message(self):
        """Составим email-сообщение"""
        msg = create_user_message(
            MailInfo(subject='test-subject', tld='ru', from_=u'отправитель'),
            ['test@ya.ru'],
            'hello, tester',
        )

        eq_(msg.subject, 'test-subject')
        eq_(msg.body, b'')
        eq_(msg.html_body, b'hello, tester')
        eq_(msg.recipients, ['test@ya.ru'])

        # Проверим что @with_settings отработал
        eq_(msg.from_address, 'test@yandex.ru')
        eq_(msg.reply_to, ('', 'noreply-test@yandex.ru'))


@with_settings(
    MAIL_NOISE_IMAGE_URL=TEST_MAIL_NOISE_IMAGE_URL,
    MAIL_SHADOW_IMAGE_URL=TEST_MAIL_SHADOW_IMAGE_URL,
    MAX_NOTIFICATION_EMAIL_COUNT=5,
)
class TestSendMailForAccount(TestCase):
    def setUp(self):
        self._mailer_faker = FakeMailer()
        self._mailer_faker.start()

        self._template = mock.Mock()
        self._template.render = mock.Mock(return_value=TEST_TEMPLATE1)

        template_loader = mock.Mock()
        template_loader.get_template.return_value = self._template

        create_template_loader = mock.Mock()
        create_template_loader.return_value = template_loader

        LazyLoader.register('TemplateLoader', create_template_loader)

    def tearDown(self):
        self._mailer_faker.stop()
        del self._mailer_faker
        del self._template
        # Тип является моком и оседает в инстансе lazy loader-а
        LazyLoader.drop('TemplateLoader')

    def test_ok(self):
        account = self._build_account(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            emails=[
                create_native_email(login='login1', domain='yandex.ru'),
                create_validated_external_email(login='login2', domain='mail.ru'),
            ],
        )
        context = {'login': TEST_LOGIN1, 'MASKED_LOGIN': TEST_LOGIN1}

        send_mail_for_account(
            template_name=TEST_TEMPLATE_NAME1,
            mail_info=MailInfo(subject='subject', from_='from', tld='ru'),
            context=context,
            account=account,
            context_shadower=login_shadower,
        )

        sent_messages = self._mailer_faker.messages
        eq_(len(sent_messages), 2)

        eq_(sent_messages[0].recipients, [('', 'login1@yandex.ru')])
        eq_(sent_messages[0].subject, 'subject')
        eq_(sent_messages[0].body, TEST_TEMPLATE1)

        eq_(sent_messages[1].recipients, [('', 'login2@mail.ru')])
        eq_(sent_messages[1].subject, 'subject')
        eq_(sent_messages[1].body, TEST_TEMPLATE1)

        self._template.render.assert_has_calls([
            mock.call(
                MAIL_NOISE_IMAGE_URL=TEST_MAIL_NOISE_IMAGE_URL,
                MAIL_SHADOW_IMAGE_URL=TEST_MAIL_SHADOW_IMAGE_URL,
                login=TEST_LOGIN1,
                MASKED_LOGIN=TEST_LOGIN1,
            ),
            mock.call(
                MAIL_NOISE_IMAGE_URL=TEST_MAIL_NOISE_IMAGE_URL,
                MAIL_SHADOW_IMAGE_URL=TEST_MAIL_SHADOW_IMAGE_URL,
                login='test***',
                MASKED_LOGIN='test***',
            ),
        ])

    def test_too_many_emails(self):
        account = self._build_account(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            emails=[
                create_native_email(login='login', domain='yandex.ru'),
            ] + [
                create_validated_external_email(login='login%s' % i, domain='mail.ru')
                for i in range(10)
            ],
        )
        context = {'login': TEST_LOGIN1, 'MASKED_LOGIN': TEST_LOGIN1}

        send_mail_for_account(
            template_name=TEST_TEMPLATE_NAME1,
            mail_info=MailInfo(subject='subject', from_='from', tld='ru'),
            context=context,
            account=account,
            context_shadower=login_shadower,
        )

        sent_messages = self._mailer_faker.messages
        eq_(len(sent_messages), 6)

        eq_(sent_messages[-1].recipients, [('', 'login@yandex.ru')])
        eq_(sent_messages[-1].subject, 'subject')
        eq_(sent_messages[-1].body, TEST_TEMPLATE1)

    def _build_account(self, **kwargs):
        user_info = blackbox_userinfo_response(**kwargs)
        user_info = parse_blackbox_userinfo_response(json.loads(user_info))
        account = Account().parse(user_info)
        return account


class TestTldDetect(TestCase):
    def test_get_tld_by_country(self):
        eq_(get_tld_by_country(''), 'com')
        eq_(get_tld_by_country(None), 'com')

        eq_(get_tld_by_country('gb'), 'com')
        eq_(get_tld_by_country('us'), 'com')

        eq_(get_tld_by_country('tr'), 'com.tr')

        eq_(get_tld_by_country('ru'), 'ru')
        eq_(get_tld_by_country('RU'), 'ru')

        for country in ['AM', 'AZ', 'BY', 'GE', 'KG',
                        'KZ', 'MD', 'TM', 'TJ', 'UA', 'UZ']:
            eq_(get_tld_by_country(country), 'ru')


@with_settings()
class TestMakeEmailContext(TestCase):
    def _build_account(self, firstname=TEST_FIRSTNAME, **kwargs):
        user_info = blackbox_userinfo_response(
            uid=TEST_UID1,
            login=TEST_LOGIN1,
            firstname=firstname,
            **kwargs
        )
        user_info = parse_blackbox_userinfo_response(json.loads(user_info))
        account = Account().parse(user_info)
        return account

    def check_ok(self, result, login=TEST_LOGIN1, firstname=TEST_FIRSTNAME):
        eq_(
            result,
            {
                'language': TEST_LANGUAGE,
                'logo_url_key': 'logo_url',
                'signature_key': 'signature.secure',
                'feedback_key': 'feedback',
                'feedback_url_key': 'feedback_url',
                'login': login,
                'MASKED_LOGIN': login,
                'FIRST_NAME': firstname,
            }
        )

    def test_ok(self):
        account = self._build_account()
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result)

    def test_social(self):
        account = self._build_account(
            aliases={
                'social': TEST_LOGIN1,
            }
        )
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result, login=TEST_FIRSTNAME)

    def test_neophonish(self):
        account = self._build_account(
            aliases={
                'neophonish': TEST_LOGIN1,
            }
        )
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result, login=TEST_FIRSTNAME)

    def test_with_display_login(self):
        account = self._build_account(display_login=TEST_DISPLAY_LOGIN)
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result, login=TEST_DISPLAY_LOGIN)

    def test_wo_firstname(self):
        account = self._build_account(firstname=None)
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result, firstname=TEST_LOGIN1)

    def test_wo_firstname_w_display_name(self):
        account = self._build_account(firstname=None, display_name={'name': TEST_DISPLAY_NAME})
        result = make_email_context(TEST_LANGUAGE, account)
        self.check_ok(result, firstname=TEST_DISPLAY_NAME)

    def test_w_context(self):
        account = self._build_account()
        result = make_email_context(TEST_LANGUAGE, account, context={'login': 'some_other_value'})
        eq_(result['login'], 'some_other_value')
