import os.path

import pytest

from sticker.mail import exceptions
from sticker.mail import types
from sticker.mail.smailik import client
from sticker.mail.smailik import path
from test_sticker.mail import smailik as smailik_test


async def _send_email_from_static_file(xml_body_filename):
    with open(
            os.path.join(
                os.path.dirname(__file__), 'static', xml_body_filename,
            ),
            'r',
    ) as body_file:
        client.send_email(
            'to@to.to',
            types.MailRequest(
                id=1,
                recipient='1',
                recipient_type=types.RecipientType.PERSONAL,
                idempotence_token='1',
                body=body_file.read(),
                status='',
            ),
            [],
            None,
            None,
        )


@pytest.mark.parametrize(
    'body, is_valid',
    [(body, False) for body in smailik_test.INVALID_MAIL_REQUEST_BODIES]
    + [  # type: ignore
        (smailik_test.VAILD_MAIL_REQUEST_BODY, True),
    ],
)
def test_validate_email_body(body, is_valid):
    try:
        client.validate_email_body(body)

    except exceptions.InvalidEmailBodyError:
        assert not is_valid


@pytest.mark.parametrize(
    'tmp_xml_dir, smailik_dir, xml_body_filename, expected_error',
    [
        (None, None, 'invalid.xml', exceptions.RetriableError),
        (
            '/usr/non_existent_dir',
            None,
            'valid.xml',
            exceptions.RetriableError,
        ),
        (None, '/usr/non_existent_dir', 'valid.xml', exceptions.FatalError),
    ],
)
async def test_send_email_errors(
        monkeypatch,
        tmp_xml_dir,
        smailik_dir,
        xml_body_filename,
        expected_error,
        tmpdir,
):
    tmp_xml_dir = tmp_xml_dir or tmpdir.mkdir('tmp_xml')
    smailik_dir = smailik_dir or tmpdir.mkdir('smailik')
    monkeypatch.setattr(path, 'TEMPORARY_FILES_DIR', tmp_xml_dir)
    monkeypatch.setattr(path, 'SMAILIK_PREPARER_SPOOL_DIR', smailik_dir)

    with pytest.raises(expected_error):
        await _send_email_from_static_file(xml_body_filename)


@pytest.mark.parametrize(
    'mail_body, attachments, remove_custom, cc_emails, bcc_emails, expected',
    [
        (
            '<mails><mail></mail></mails>',
            [],
            False,
            None,
            None,
            (
                '<mails><mail><to>to@to.to</to>'
                '<messageid>hex</messageid></mail></mails>'
            ),
        ),
        (
            (
                '<mails><mail><parts>'
                '<part type="application/pdf" name="invoice.pdf" '
                'encoding="base64">'
                '<file>/tmp/ride_reportWq4IuT</file>'
                '</part></parts></mail></mails>'
            ),
            [
                types.MailAttachment(
                    id=1,
                    file_name='invoice.pdf',
                    content_type='application/pdf',
                    idempotence_token='1',
                    recipient='1',
                    recipient_type=types.RecipientType.PERSONAL,
                    body=b'',
                ),
            ],
            False,
            None,
            None,
            (
                '<mails><mail><parts>'
                '<part encoding="base64" name="invoice.pdf" '
                'type="application/pdf">'
                '<file>{tmp_dir}/1.invoice.pdf</file></part>'
                '</parts><to>to@to.to</to>'
                '<messageid>hex</messageid></mail></mails>'
            ),
        ),
        (
            '<mails><mail></mail></mails>',
            [
                types.MailAttachment(
                    id=1,
                    file_name='invoice.pdf',
                    content_type='application/pdf',
                    idempotence_token='1',
                    recipient='1',
                    recipient_type=types.RecipientType.PERSONAL,
                    body=b'',
                ),
            ],
            False,
            None,
            None,
            (
                '<mails><mail><to>to@to.to</to><messageid>hex</messageid>'
                '<parts><part encoding="base64" name="invoice.pdf" '
                'type="application/pdf">'
                '<file>{tmp_dir}/1.invoice.pdf</file></part>'
                '</parts></mail></mails>'
            ),
        ),
        (
            '<mails><mail>'
            '<custom>'
            '<header name="cc">c@c.c</header>'
            '<header name="cc">d@d.d</header>'
            '<header name="bcc">e@e.e</header>'
            '</custom>'
            '</mail></mails>',
            [],
            False,
            None,
            None,
            (
                '<mails><mail>'
                '<custom>'
                '<header name="cc">c@c.c</header>'
                '<header name="cc">d@d.d</header>'
                '<header name="bcc">e@e.e</header>'
                '</custom>'
                '<to>to@to.to</to><messageid>hex</messageid>'
                '</mail></mails>'
            ),
        ),
        (
            '<mails><mail>'
            '<custom>'
            '<header name="cc">c@c.c</header>'
            '<header name="cc">d@d.d</header>'
            '<header name="bcc">e@e.e</header>'
            '</custom>'
            '</mail></mails>',
            [],
            True,
            None,
            None,
            (
                '<mails><mail><to>to@to.to</to>'
                '<messageid>hex</messageid></mail></mails>'
            ),
        ),
        (
            '<mails><mail>'
            '<custom>'
            '<header name="cc">c@c.c</header>'
            '<header name="cc">d@d.d</header>'
            '<header name="bcc">e@e.e</header>'
            '</custom>'
            '</mail></mails>',
            [],
            True,
            ['c@c.c', 'e@e.e'],
            ['a@a.a'],
            (
                '<mails><mail>'
                '<to>to@to.to</to>'
                '<messageid>hex</messageid>'
                '<custom>'
                '<header name="cc">c@c.c,e@e.e</header>'
                '<header name="bcc">a@a.a</header>'
                '</custom>'
                '</mail></mails>'
            ),
        ),
    ],
)
async def test_send_email_success(
        monkeypatch,
        tmpdir,
        mail_body,
        attachments,
        expected,
        remove_custom,
        cc_emails,
        bcc_emails,
):
    monkeypatch.setattr(path, 'TEMPORARY_FILES_DIR', tmpdir.mkdir('tmp_xml'))
    monkeypatch.setattr(
        path, 'SMAILIK_PREPARER_SPOOL_DIR', tmpdir.mkdir('smailik'),
    )

    client.send_email(
        'to@to.to',
        types.MailRequest(
            id=1,
            recipient='1',
            recipient_type=types.RecipientType.PERSONAL,
            idempotence_token='1',
            body=mail_body,
            status='',
        ),
        attachments,
        cc_emails,
        bcc_emails,
        need_remove_cc_and_bcc=remove_custom,
    )

    with open(
            os.path.join(path.SMAILIK_PREPARER_SPOOL_DIR, '1.xml'), 'r',
    ) as sent_mail_file:
        assert sent_mail_file.read() == (
            expected.format(tmp_dir=path.TEMPORARY_FILES_DIR)
        )
