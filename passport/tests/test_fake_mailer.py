# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.mailer import (
    get_mailer,
    HTMLMessage,
)
from passport.backend.core.mailer.faker import FakeMailer
from passport.backend.core.mailer.faker.mail_utils import assert_messages_equal


TEST_SUBJECT = u'тема'
TEST_RECIPIENT = (u'Василий', 'noreply@vasiliy.ru')
TEST_FROM = 'noreply@passport.yandex.ru'
TEST_SENDER_NAME = u'Яндекс.Паспорт'
TEST_HTML = u'тестовое тело'
TEST_EMAIL = '''Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: =?utf-8?b?0YLQtdC80LA=?=
From: noreply@passport.yandex.ru
To: =?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>
Date: Wed, 04 Jun 2014 17:47:52 +0400

0YLQtdGB0YLQvtCy0L7QtSDRgtC10LvQvg==
'''


class TestFakeMailer(unittest.TestCase):
    def setUp(self):
        self.mailer = FakeMailer()
        self.mailer.start()
        self.message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML)

    def tearDown(self):
        self.mailer.stop()
        del self.mailer

    def test_set_return_code(self):
        self.mailer.set_sendmail_return_code(10)
        code = get_mailer().send(self.message)
        eq_(code, 10)

    def test_message_caught(self):
        code = get_mailer().send(self.message)

        eq_(code, 0)
        eq_(self.mailer.message_count, 1)
        assert_messages_equal(
            self.mailer.get_message_content(),
            TEST_EMAIL,
        )

    def test_multiple_messages_caught(self):
        get_mailer().send(self.message)
        get_mailer().send(self.message)

        eq_(self.mailer.message_count, 2)
        for i in range(2):
            assert_messages_equal(
                self.mailer.get_message_content(i),
                TEST_EMAIL,
            )

    def test_messages_empty_when_did_not_send_mail(self):
        """
        Почта не высылалась.
        """
        eq_(self.mailer.messages, [])

    def test_has_message_when_sent_mail_once(self):
        """
        Перехвачено одно сообщение.
        """
        get_mailer().send(
            HTMLMessage(
                TEST_SUBJECT,
                [TEST_RECIPIENT],
                TEST_FROM,
                html=TEST_HTML,
            ),
        )

        messages = self.mailer.messages
        eq_(len(messages), 1)
        eq_(messages[0].subject, TEST_SUBJECT)
        eq_(messages[0].body, TEST_HTML)
        eq_(messages[0].recipients, [TEST_RECIPIENT])

    def test_has_messages_when_sent_mail_many_times(self):
        """
        Перехватываются несколько сообщений.
        """
        mailer = get_mailer()
        mailer.send(
            HTMLMessage(u'Alice', [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML),
        )
        mailer.send(
            HTMLMessage(u'Bob', [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML),
        )

        messages = self.mailer.messages
        eq_(len(messages), 2)
        eq_(messages[0].subject, u'Alice')
        eq_(messages[1].subject, u'Bob')

    def test_has_sender_recorded(self):
        mailer = get_mailer()
        mailer.send(
            HTMLMessage(u'Alice', [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML),
        )
        mailer.send(
            HTMLMessage(
                u'Bob',
                [TEST_RECIPIENT],
                u'%s <%s>' % (TEST_SENDER_NAME, TEST_FROM),
                html=TEST_HTML,
            ),
        )

        messages = self.mailer.messages
        eq_(messages[0].sender, ('', TEST_FROM))
        eq_(messages[1].sender, (TEST_SENDER_NAME, TEST_FROM))

    def test_ok_message_when_many_recipients(self):
        get_mailer().send(
            HTMLMessage(
                TEST_SUBJECT,
                [
                    (u'Иван', u'john@john'),
                    (u'Марья', u'alice@alice'),
                ],
                TEST_FROM,
                html=TEST_HTML,
            ),
        )

        messages = self.mailer.messages
        eq_(
            messages[0].recipients,
            [
                (u'Иван', u'john@john'),
                (u'Марья', u'alice@alice'),
            ],
        )
