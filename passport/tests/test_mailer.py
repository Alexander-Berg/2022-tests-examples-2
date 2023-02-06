# -*- coding: utf-8 -*-
from subprocess import (
    PIPE,
    STDOUT,
)
import unittest

from nose.tools import eq_
from passport.backend.core.mailer import (
    connection,
    HTMLMessage,
    send_message,
)
from passport.backend.core.mailer.faker.mail_utils import assert_messages_equal
from passport.backend.core.mailer.faker.mailer import FakeMailer

from .test_data import (
    TEST_BCC,
    TEST_CC,
    TEST_EMAIL_MAXIMUM_HEADERS,
    TEST_EMAIL_MINIMUM_HEADERS,
    TEST_FROM,
    TEST_FROM_ADDRESS,
    TEST_HTML,
    TEST_RECIPIENT,
    TEST_REPLY_TO,
    TEST_SENDER,
    TEST_SUBJECT,
)


class TestMailer(unittest.TestCase):
    def setUp(self):
        self.mailer = FakeMailer()
        self.mailer.start()

    def tearDown(self):
        self.mailer.stop()
        del self.mailer

    def test_sendmail_connection(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML)
        connection.SendmailConnection().send(message)

        connection.Popen.assert_called_with(
            ['/usr/sbin/sendmail', '-t', '-f', TEST_FROM_ADDRESS],
            stdin=PIPE,
            stderr=STDOUT,
            stdout=PIPE,
        )
        eq_(self.mailer._mock.stdin.write.call_count, 1)

    def test_send_message_minimum(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM)
        code = send_message(message)

        eq_(code, 0)
        eq_(self.mailer.message_count, 1)
        assert_messages_equal(self.mailer.get_message_content(), TEST_EMAIL_MINIMUM_HEADERS)

    def test_send_message_full(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM, sender=TEST_SENDER,
                              cc=TEST_CC, bcc=TEST_BCC, reply_to=TEST_REPLY_TO,
                              extra_headers={'X-OTRS-Pass': 'yauser'})
        code = send_message(message)

        eq_(code, 0)
        eq_(self.mailer.message_count, 1)
        assert_messages_equal(
            self.mailer.get_message_content(),
            TEST_EMAIL_MAXIMUM_HEADERS,
        )

    def test_send_message_error(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM)
        self.mailer.set_side_effect([Exception])
        code = send_message(message)
        eq_(code, None)
