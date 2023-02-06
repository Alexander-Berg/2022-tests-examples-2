# -*- coding: utf-8 -*-
from email.utils import parseaddr
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.mailer import (
    Attachment,
    HTMLMessage,
    HtmlWithMixedAttachmentMessage,
    MessageBase,
    MultipartMixin,
)
from passport.backend.core.mailer.faker.mail_utils import (
    assert_messages_equal,
    get_multipart_boundaries,
    mail_date_to_timestamp,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
import six

from .test_data import (
    TEST_BCC,
    TEST_BCC_ENCODED,
    TEST_CC,
    TEST_CC_ENCODED,
    TEST_EMAIL_MAXIMUM_HEADERS,
    TEST_EMAIL_MINIMUM_HEADERS,
    TEST_EMAIL_WITH_ATTACHMENTS,
    TEST_FROM,
    TEST_FROM_ENCODED,
    TEST_HTML,
    TEST_MULTIPART_EMAIL_TEMPLATE,
    TEST_RECIPIENT,
    TEST_RECIPIENT_ENCODED,
    TEST_REPLY_TO,
    TEST_SENDER,
    TEST_SUBJECT,
)


class TestMessage(unittest.TestCase):
    @raises(NotImplementedError)
    def test_message_base_populate_raises(self):
        MessageBase(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM)

    def test_from_address(self):
        addresses = [
            TEST_FROM,
            (None, TEST_FROM[1]),
            (None, u'кириллическое@что.то'),
        ]
        for addr in addresses:
            message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], addr)
            eq_(parseaddr(message._mime_msg['From'])[1], message.from_address)

    def test_headers_minimum(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM)
        mime_msg = message._mime_msg

        eq_(
            mime_msg.keys(),
            [
                'Content-Type',
                'MIME-Version',
                'Content-Transfer-Encoding',
                'Subject',
                'From',
                'To',
                'Date',
            ],
        )

        eq_(mime_msg['Content-Type'], 'text/html; charset="utf-8"')
        eq_(mime_msg['MIME-Version'], '1.0')
        eq_(mime_msg['Content-Transfer-Encoding'], 'base64')

        eq_(mime_msg['Subject'], TEST_SUBJECT)
        eq_(mime_msg['From'], TEST_FROM_ENCODED)
        eq_(mime_msg['To'], TEST_RECIPIENT_ENCODED)
        eq_(mail_date_to_timestamp(mime_msg['Date']), TimeNow())

        assert_messages_equal(
            mime_msg.as_string(),
            TEST_EMAIL_MINIMUM_HEADERS,
        )

    def test_headers_full(self):
        message = HTMLMessage(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM, sender=TEST_SENDER,
                              cc=TEST_CC, bcc=TEST_BCC, reply_to=TEST_REPLY_TO,
                              extra_headers={'X-OTRS-Pass': 'yauser'})
        mime_msg = message._mime_msg

        eq_(
            mime_msg.keys(),
            [
                'Content-Type',
                'MIME-Version',
                'Content-Transfer-Encoding',
                'Subject',
                'From',
                'Sender',
                'To',
                'Date',
                'Cc',
                'Bcc',
                'Reply-To',
                'X-OTRS-Pass',
            ],
        )

        eq_(mime_msg['Content-Type'], 'text/html; charset="utf-8"')
        eq_(mime_msg['MIME-Version'], '1.0')
        eq_(mime_msg['Content-Transfer-Encoding'], 'base64')

        eq_(mime_msg['Subject'], TEST_SUBJECT)
        eq_(mime_msg['From'], TEST_FROM_ENCODED)
        eq_(mime_msg['Sender'], TEST_SENDER)
        eq_(mime_msg['To'], TEST_RECIPIENT_ENCODED)
        eq_(mail_date_to_timestamp(mime_msg['Date']), TimeNow())
        eq_(mime_msg['CC'], TEST_CC_ENCODED)
        eq_(mime_msg['BCC'], TEST_BCC_ENCODED)
        eq_(mime_msg['Reply-To'], TEST_REPLY_TO)
        eq_(mime_msg['X-OTRS-Pass'], 'yauser')

        assert_messages_equal(
            mime_msg.as_string(),
            TEST_EMAIL_MAXIMUM_HEADERS,
        )

    def test_address_parsing(self):
        message = HTMLMessage(
            TEST_SUBJECT,
            [
                'vasiliy@yandex.ru',
                u'василий_at_yandex_ru',
                ('', 'vasiliy'),
                (u'василий', u'василий@почта.рф'),
                u'bad@.рф',
                u'unicode-error@]ъ.рф',
            ],
            TEST_FROM,
        )
        mime_msg = message._mime_msg

        eq_(
            mime_msg.keys(),
            [
                'Content-Type',
                'MIME-Version',
                'Content-Transfer-Encoding',
                'Subject',
                'From',
                'To',
                'Date',
            ],
        )

        eq_(mime_msg['Content-Type'], 'text/html; charset="utf-8"')
        eq_(mime_msg['MIME-Version'], '1.0')
        eq_(mime_msg['Content-Transfer-Encoding'], 'base64')

        eq_(mime_msg['Subject'], TEST_SUBJECT)
        eq_(mime_msg['From'], TEST_FROM_ENCODED)
        eq_(
            {to.strip() for to in mime_msg['To'].split(',')},
            {
                'unicode-error@' if six.PY2 else '',
                '=?utf-8?b?0LLQsNGB0LjQu9C40Lk=?= <=?utf-8?b?0LLQsNGB0LjQu9C40Lk=?=@xn--80a1acny.xn--p1ai>',
                '=?utf-8?b?YmFkQC7RgNGE?=',
                'vasiliy',
                'vasiliy@yandex.ru',
                '=?utf-8?b?0LLQsNGB0LjQu9C40LlfYXRfeWFuZGV4X3J1?=',
            },
        )
        eq_(mail_date_to_timestamp(mime_msg['Date']), TimeNow())

    def test_multipart_mixin(self):
        cls = type('TestMultipart', (HTMLMessage, MultipartMixin('mixed'), MultipartMixin('alternative')), {})
        message = cls(TEST_SUBJECT, [TEST_RECIPIENT], TEST_FROM, html=TEST_HTML)

        message_text = message.as_string()
        boundaries = get_multipart_boundaries(message_text)
        assert_messages_equal(
            message_text,
            TEST_MULTIPART_EMAIL_TEMPLATE,
            boundaries,
        )

        root_msg = message._mime_msg
        eq_(root_msg['Content-Type'], 'multipart/alternative; boundary="%s"' % boundaries['boundary_0'])
        eq_(len(root_msg.get_payload()), 1)

        nested_msg_1 = root_msg.get_payload()[0]
        eq_(nested_msg_1['Content-Type'], 'multipart/mixed; boundary="%s"' % boundaries['boundary_1'])
        eq_(len(nested_msg_1.get_payload()), 1)

        nested_msg_2 = nested_msg_1.get_payload()[0]
        eq_(nested_msg_2['Content-Type'], 'text/html; charset="utf-8"')

    def test_multipart_with_attachment(self):
        attachments = [
            Attachment(filename=u'файл 1.jpg', content_type='image/jpeg', data='image'),
            Attachment(
                filename=u'simplejson',
                content_type='application/json',
                data='{"json":true}',
                headers={'X-OTRS-123': '321'},
            ),
        ]
        message = HtmlWithMixedAttachmentMessage(
            TEST_SUBJECT,
            [TEST_RECIPIENT],
            TEST_FROM,
            attachments=attachments,
        )

        message_text = str(message)
        boundaries = get_multipart_boundaries(message_text)
        assert_messages_equal(
            message_text,
            TEST_EMAIL_WITH_ATTACHMENTS,
            boundaries,
        )

        root_msg = message._mime_msg
        eq_(root_msg['Content-Type'], 'multipart/mixed; boundary="%s"' % boundaries['boundary_0'])
        eq_(len(root_msg.get_payload()), 3)  # HTML и два аттача

        html_msg, attach_1, attach_2 = root_msg.get_payload()
        eq_(html_msg['Content-Type'], 'text/html; charset="utf-8"')
        eq_(attach_1['Content-Type'], 'image/jpeg')
        eq_(attach_2['Content-Type'], 'application/json')

    def test_new_lines_in_subject(self):
        message = HTMLMessage(
            '\r\n\rfoo\r\n\n\rbar\r\n\r\n\n\r\r',
            [TEST_RECIPIENT],
            TEST_FROM,
        )
        eq_(message._mime_msg['Subject'], 'foo bar')
