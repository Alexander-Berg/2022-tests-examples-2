import mock
import pytest
from dmp_suite.mail_utils import _to_list, _add_domain_if_needed, _format_message, send_mail


@pytest.mark.parametrize(
    "iterable, expected",
    [
        (None, []),
        ("", []),
        ("some_string", ["some_string"]),
        (["some_string", "some_string2"], ["some_string", "some_string2"]),
        (("some_string", "some_string2"), ["some_string", "some_string2"]),
    ],
)
def test_to_list(iterable, expected):
    assert _to_list(iterable) == expected


@pytest.mark.parametrize(
    "send_to, domain, expected",
    [
        ([], None, []),
        (["some_string"], None, ["some_string"]),
        (["some_string"], "@some_domain", ["some_string@some_domain"]),
        (["some_string@other_domain"], "@some_domain", ["some_string@other_domain"]),
        (["some_string", "some_string2@some_domain"], "@some_domain",
         ["some_string@some_domain", "some_string2@some_domain"]),
    ],
)
def test_add_domain_if_needed(send_to, domain, expected):
    assert _add_domain_if_needed(send_to, domain) == expected


@pytest.mark.parametrize(
    "send_from, send_to, subject, text, is_html, expected",
    [
        ("some_sender", ["some_receiver", "some_receiver2"], "some_subject", "some_text", False,
         [('Content-Type', 'multipart/mixed'),
          ('MIME-Version', '1.0'),
          ('From', 'some_sender'),
          ('To', 'some_receiver, some_receiver2'),
          ('Subject', 'some_subject')]
         ),
    ],
)
def test_format_message(send_from, send_to, subject, text, is_html, expected):

    # looks dangerous to compare dates in this context -> remove it
    def remove_date(headers):
        return [element for element in headers if element[0] != 'Date']

    actual = _format_message(send_from, send_to, subject, text, is_html)
    headers = remove_date(actual._headers)
    assert headers == expected


@mock.patch('smtplib.SMTP.connect')
@mock.patch('smtplib.SMTP.sendmail')
@mock.patch('smtplib.SMTP.close')
def test_send_mail(smtp_connect, smtp_sendmail, smtp_close):
    send_mail(
        send_from="some_sender",
        send_to="some_receiver",
        subject="some_subject",
        text="some_text",
    )
    smtp_connect.assert_called_once()
    smtp_sendmail.assert_called_once()
    smtp_close.assert_called_once()
