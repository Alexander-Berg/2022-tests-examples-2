from lxml import etree
import pytest

from sticker.mail.smailik import xml
from test_sticker.mail import smailik as smailik_test


def _xml_element_from_str(xml_str):
    return etree.fromstring(bytes(xml_str, encoding='utf-8'))


@pytest.mark.parametrize(
    'xml_body, should_fail',
    [(body, True) for body in smailik_test.INVALID_MAIL_REQUEST_BODIES]
    + [  # type: ignore
        (smailik_test.VAILD_MAIL_REQUEST_BODY, False),
    ],
)
def test_parse_mail_template(xml_body, should_fail):
    if not should_fail:
        parsed_xml = xml.parse_mail_template(xml_body)
        # pylint: disable=protected-access
        assert isinstance(parsed_xml, etree._Element)

    else:
        with pytest.raises(xml.InvalidTemplateError):
            xml.parse_mail_template(xml_body)


@pytest.mark.parametrize(
    'xml_body_str, email, expected_str',
    [
        (
            '<mails><mail><from>a@a.a</from></mail></mails>',
            'b@b.b',
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
        ),
        (
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            'c@c.c',
            '<mails><mail><from>a@a.a</from><to>c@c.c</to></mail></mails>',
        ),
        (
            (
                '<mails><mail><from>a@a.a</from><to>y@y.y</to></mail>'
                '<mail><from>x@x.x</from></mail></mails>'
            ),
            'z@z.z',
            (
                '<mails><mail><from>a@a.a</from><to>z@z.z</to></mail>'
                '<mail><from>x@x.x</from><to>z@z.z</to></mail></mails>'
            ),
        ),
    ],
)
def test_insert_email(xml_body_str, email, expected_str):
    email_inserted = xml.insert_email(xml_body_str, email)

    expected = _xml_element_from_str(expected_str)

    expected[:] = sorted(expected, key=lambda x: x.find('from').text)
    email_inserted[:] = sorted(
        email_inserted, key=lambda x: x.find('from').text,
    )

    # Relies on the simplicity of test XML's: there shouldn't be any
    # attributes or tags with depth more than 2
    assert etree.tostring(expected) == etree.tostring(email_inserted)


@pytest.mark.parametrize(
    (
        'xml_body_str, email, cc_emails, bcc_emails, '
        'expected_after_remove, expected_after_update'
    ),
    [
        (
            '<mails><mail><from>a@a.a</from></mail></mails>',
            'b@b.b',
            [],
            [],
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
        ),
        (
            (
                '<mails><mail><from>a@a.a</from><custom>'
                '<header name="cc">a@a.a</header>'
                '</custom></mail></mails>'
            ),
            'b@b.b',
            [],
            [],
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
        ),
        (
            (
                '<mails><mail><from>a@a.a</from><custom>'
                '<header name="cc">a@a.a</header>'
                '</custom></mail></mails>'
            ),
            'b@b.b',
            ['c@c.c'],
            [],
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            (
                '<mails><mail><from>a@a.a</from><to>b@b.b</to><custom>'
                '<header name="cc">c@c.c</header>'
                '</custom></mail></mails>'
            ),
        ),
        (
            (
                '<mails><mail><from>a@a.a</from><custom>'
                '<header name="cc">a@a.a</header>'
                '</custom></mail></mails>'
            ),
            'b@b.b',
            ['c@c.c', 'd@d.d'],
            [],
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            (
                '<mails><mail><from>a@a.a</from><to>b@b.b</to><custom>'
                '<header name="cc">c@c.c,d@d.d</header>'
                '</custom></mail></mails>'
            ),
        ),
        (
            (
                '<mails><mail><from>a@a.a</from><custom>'
                '<header name="cc">a@a.a</header>'
                '</custom></mail></mails>'
            ),
            'b@b.b',
            ['c@c.c', 'd@d.d'],
            ['e@e.e'],
            '<mails><mail><from>a@a.a</from><to>b@b.b</to></mail></mails>',
            (
                '<mails><mail><from>a@a.a</from><to>b@b.b</to>'
                '<custom>'
                '<header name="cc">c@c.c,d@d.d</header>'
                '<header name="bcc">e@e.e</header>'
                '</custom></mail></mails>'
            ),
        ),
    ],
)
def test_remove_and_add_cc_emails(
        xml_body_str,
        email,
        cc_emails,
        bcc_emails,
        expected_after_remove,
        expected_after_update,
):
    email_inserted = xml.insert_email(xml_body_str, email)
    cc_removed_inserted = xml.remove_cc_and_bcc(email_inserted)

    check = etree.tostring(cc_removed_inserted)
    assert expected_after_remove == check.decode('utf-8')

    new_cc_inserted = xml.insert_cc_and_bcc_emails(
        cc_removed_inserted, cc_emails, bcc_emails,
    )

    check = etree.tostring(new_cc_inserted)
    assert expected_after_update == check.decode('utf-8')
