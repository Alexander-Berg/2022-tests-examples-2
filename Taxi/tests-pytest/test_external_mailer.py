#! -*- coding: utf-8 -*-

import shutil
import StringIO
import tempfile

import pytest

from taxi.conf import settings
from taxi.internal import email_sender
from taxi.external import mailer


class FakeNamedTemporaryFile(StringIO.StringIO):
    """Fake named temporary file object.

    We don't want our tests to touch the filesystem.
    This object is in-memory buffer that can be used
    to mock tempfile.NamedTemporaryFile() return value.

    :attr name: "Filename" of the fake object
    """
    name = 'NamedTemporaryFile.mock'


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'sender,to,reply_to,subject,body,html_body,headers,attach,xml', [
        # Case 1: Invalid email
        (
            None,    # sender
            None,    # to
            None,    # reply-to
            'Test',  # subject
            'Test',  # body
            None,    # html_body
            None,    # headers
            None,    # attach
            None     # expected xml
        ),

        # Case 2: Basic email
        (
            'sample@ya.ru',   # sender
            'another@ya.ru',  # to
            None,             # reply-to
            u'Тестовое',      # subject
            u'Тест',          # body
            None,             # html_body
            [],               # headers
            None,             # attach
            'basic.xml'       # expected xml
        ),

        # Case 4: HTML mail
        (
            'sample@ya.ru',   # sender
            'another@ya.ru',  # to
            None,             # reply-to
            u'Тестовое',      # subject
            u'Тест',          # body
            u'<p>Тест</p>',   # html_body
            None,             # headers
            None,             # attach
            'html_mail.xml'   # expected_xml
        ),

        # Case 5: "Advanced" email
        (
            'sample@ya.ru',   # sender
            'another@ya.ru',  # to
            'me.too@ya.ru',   # reply-to
            u'Тестовое',      # subject
            u'Тест',          # body
            u'<p>Тест</p>',   # html_body
            [                 # headers
                ('CC', 'and.mee.too@mail.ru')
            ],
            [                 # attach
                {'blob': 'Test attachment'},
                {'file': 'test.txt'},
            ],
            'adv_mail.xml'    # expected_xml
        ),
    ])
def test_render_smailik(sender, to, reply_to, subject, body,
                        html_body, headers, attach, xml,
                        load, mock, monkeypatch):

    real_xml = {
        'buffer': None
    }

    @mock
    def _NamedTemporaryFile(*args, **kwargs):
        real_xml['buffer'] = FakeNamedTemporaryFile()
        return real_xml['buffer']

    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', _NamedTemporaryFile)

    email_message = email_sender.EmailMessage(sender, to, subject, body)

    if reply_to is not None:
        email_message.reply_to = reply_to

    if html_body is not None:
        email_message.html_body = html_body

    if headers is not None:
        for name, value in headers:
            email_message.add_header(name, value)

    if attach is not None:
        for item in attach:
            if 'blob' in item:
                email_message.attach_blob(
                    item['blob'],
                    attachment_name='blob.bin'
                )
            elif 'file' in item:
                email_message.attach_file(
                    item['file'],
                    content_type='text/plain'
                )

    if xml is None:
        with pytest.raises(email_sender.MalformedEmailError):
            email_message.validate()
    else:
        expected_xml = load(xml).replace('ID_HERE', email_message.message_id)
        tmp_name = mailer._render_for_smailik(email_message)
        assert tmp_name == FakeNamedTemporaryFile.name
        assert expected_xml.strip() == real_xml['buffer'].getvalue().strip()


def test_send_email(mock, monkeypatch):
    @mock
    def _NamedTemporaryFile(*args, **kwargs):
        return FakeNamedTemporaryFile()

    @mock
    def _shutil_move(src, dst):
        pass

    monkeypatch.setattr(tempfile, 'NamedTemporaryFile', _NamedTemporaryFile)
    monkeypatch.setattr(shutil, 'move', _shutil_move)

    email_message = email_sender.EmailMessage(
        sender='me@ya.ru',
        to='another.me@ya.ru',
        subject='Few lines of nonsense here',
        body='Hi There!'
    )

    msgid = email_message.message_id
    mailer.send_email(email_message)

    calls = _shutil_move.calls
    assert len(calls) == 1
    assert calls[0]['src'] == FakeNamedTemporaryFile.name
    assert calls[0]['dst'] == '%s/%s.xml' % (settings.SMAILIK_DIR, msgid)
