import email

import pytest

from sber_int_api.email_api import mail


@pytest.mark.config(SBER_SENDERS_EMAILS=['1@m.ru', '2@m.ru'])
def test_get_latest_email(patch, load_binary, cron_context):
    @patch('imaplib.IMAP4.open')
    @patch('imaplib.IMAP4._connect')
    @patch('imaplib.IMAP4.select')
    @patch('imaplib.IMAP4.logout')
    def _init(*args, **kwargs):
        pass

    @patch('imaplib.IMAP4.login')
    def _login(user, password):
        assert user == 'login@yandex-team.ru'
        assert password == '123'

    @patch('imaplib.IMAP4.search')
    def _search(*args):
        return 'OK', [b'1 2 3']

    @patch('imaplib.IMAP4.fetch')
    def _fetch(num, *args):
        return (
            'OK',
            [
                [
                    (b'1 (RFC822 {7738}', load_binary('email1.txt')),
                    b' FLAGS (\\Seen))',
                ],
                [
                    (b'2 (RFC822 {7745}', load_binary('email2.txt')),
                    b' FLAGS (\\Seen))',
                ],
                [
                    (b'3 (RFC822 {7745}', load_binary('email3.txt')),
                    b' FLAGS (\\Seen))',
                ],
            ][int(num) - 1],
        )

    @patch('imaplib.IMAP4.store')
    def _store(*args):
        return 'OK', None

    messages = mail.get_latest_email(cron_context)
    messages = {
        address: (message['Date'], message['Subject'])
        for address, message in messages.items()
    }

    assert messages == {
        '1@m.ru': ('Tue, 14 Jul 2020 04:11:49 +0300', 'tema'),
        '2@m.ru': ('Tue, 14 Jul 2020 17:37:55 +0300', 'tema2'),
    }


def test_get_xml_file(load_binary):
    data = load_binary('email1.txt')
    message = email.message_from_bytes(data)
    incoming_xml = mail.get_xml_file(message)
    expected_xml = load_binary('request.xml')
    assert incoming_xml.decode() == expected_xml.decode()
