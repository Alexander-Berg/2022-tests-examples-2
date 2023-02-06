# -*- coding: utf-8 -*-
import six


TEST_SUBJECT = u'тема'
TEST_RECIPIENT = (u'Василий', 'noreply@vasiliy.ru')
TEST_RECIPIENT_ENCODED = '=?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>'
TEST_FROM_ADDRESS = 'noreply@passport.yandex.ru'
TEST_FROM = (u'Яндекс', 'noreply@passport.yandex.ru')
TEST_FROM_ENCODED = '=?utf-8?b?0K/QvdC00LXQutGB?= <noreply@passport.yandex.ru>'
TEST_SENDER = 'sender@passport.yandex.ru'
TEST_REPLY_TO = 'reply@yandex.ru'
TEST_HTML = u'тестовое тело'
TEST_CC = [('CC1', 'cc1@cc.ru'), ('CC2', 'cc2@cc.ru')]
TEST_CC_ENCODED = '=?utf-8?q?CC1?= <cc1@cc.ru>, =?utf-8?q?CC2?= <cc2@cc.ru>'
TEST_BCC = [('BCC1', 'bcc1@bcc.ru'), ('BCC2', 'bcc2@bcc.ru')]
TEST_BCC_ENCODED = '=?utf-8?q?BCC1?= <bcc1@bcc.ru>, =?utf-8?q?BCC2?= <bcc2@bcc.ru>'

TEST_EMAIL_MINIMUM_HEADERS = '''Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: =?utf-8?b?0YLQtdC80LA=?=
From: =?utf-8?b?0K/QvdC00LXQutGB?= <noreply@passport.yandex.ru>
To: =?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>
Date: Wed, 04 Jun 2014 17:47:52 +0400

'''

TEST_EMAIL_MAXIMUM_HEADERS = '''Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Subject: =?utf-8?b?0YLQtdC80LA=?=
From: =?utf-8?b?0K/QvdC00LXQutGB?= <noreply@passport.yandex.ru>
Sender: sender@passport.yandex.ru
To: =?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>
Date: Wed, 04 Jun 2014 17:47:52 +0400
Cc: =?utf-8?q?CC1?= <cc1@cc.ru>, =?utf-8?q?CC2?= <cc2@cc.ru>
Bcc: =?utf-8?q?BCC1?= <bcc1@bcc.ru>, =?utf-8?q?BCC2?= <bcc2@bcc.ru>
Reply-To: reply@yandex.ru
X-OTRS-Pass: yauser

'''

TEST_MULTIPART_EMAIL_TEMPLATE = '''Content-Type: multipart/alternative;
 boundary="%(boundary_0)s"
MIME-Version: 1.0
Subject: =?utf-8?b?0YLQtdC80LA=?=
From: =?utf-8?b?0K/QvdC00LXQutGB?= <noreply@passport.yandex.ru>
To: =?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>
Date: Wed, 04 Jun 2014 22:13:45 +0400

--%(boundary_0)s
Content-Type: multipart/mixed; boundary="%(boundary_1)s"
MIME-Version: 1.0

--%(boundary_1)s
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64

0YLQtdGB0YLQvtCy0L7QtSDRgtC10LvQvg==

--%(boundary_1)s--

--%(boundary_0)s--
'''

TEST_EMAIL_WITH_ATTACHMENTS = '''Content-Type: multipart/mixed; boundary="%(boundary_0)s"
MIME-Version: 1.0
Subject: =?utf-8?b?0YLQtdC80LA=?=
From: =?utf-8?b?0K/QvdC00LXQutGB?= <noreply@passport.yandex.ru>
To: =?utf-8?b?0JLQsNGB0LjQu9C40Lk=?= <noreply@vasiliy.ru>
Date: Wed, 04 Jun 2014 22:30:36 +0400

--%(boundary_0)s
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64


--%(boundary_0)s
Content-Type: image/jpeg
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment;
 filename*={possible_quote}UTF8''%%D1%%84%%D0%%B0%%D0%%B9%%D0%%BB%%201.jpg{possible_quote}

aW1hZ2U={possible_newline}
--%(boundary_0)s
Content-Type: application/json
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment;filename="simplejson"
X-OTRS-123: 321

eyJqc29uIjp0cnVlfQ=={possible_newline}
--%(boundary_0)s--
'''.format(
    possible_newline='' if six.PY2 else '\n',
    possible_quote='"' if six.PY2 else '',
)
