# -*- coding: utf-8 -*-
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_SMTP_HOST = 'outbound-relay.yandex.net'

logger = logging.getLogger(__name__)


def send_email(from_, to, subject, content):
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = from_
    message['To'] = ', '.join(to) if isinstance(to, (list, tuple)) else to
    message.attach(MIMEText(content, 'html'))

    smtp = smtplib.SMTP(_SMTP_HOST)
    logger.debug(u'Sending email to {}'.format(str(to)))
    smtp.sendmail(from_, to, message.as_string())
    smtp.quit()
