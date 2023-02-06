# -*- coding: utf-8 -*-

import logging
import time
import json
import re
import smtplib
from collections import defaultdict
from copy import deepcopy

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email.header import Header
from urlparse import urljoin
import requests

from sandbox import common
from sandbox import sdk2

from sandbox.sandboxsdk.environments import PipEnvironment

BLACKLIST = ["meta", "id", "form_id", "_publishUrl", "_landingTitle", "_customerEmail"]
# form - form_id
# sk - security key of report_portal
# meta - landing metainfo
# _publishUrl - page url the form was sent from
# _landingTitle - page title
# _customerEmail - customer email for ecom
# we shouldn't send em to user actually


def is_ecom(row):
    return '_orderItems' in row['data']


def split_goods(row):
    def create_good(item):
        data = row['data'].copy()

        data.pop('_orderItems')
        data.update({
            'product': item['name'],
            'quantity': item['amount'],
            'price': '%s%s' % (item['price'], item['currency']),
            'total_price': '%s%s' % (item['total'], item['currency']),
        })

        good_row = row.copy()
        good_row['data'] = data

        return good_row

    items = json.loads(row['data']['_orderItems'])

    return map(create_good, items)


def to_csv(rows_in):
    if not rows_in:
        return

    def key_to_header(key):
        # приводим приватные ключи к виду пользовательских
        if key[0] == '_':
            key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key[1:])).lower()

        header = key.replace("_", " ")

        return header[0].upper() + header[1:]

    rows = deepcopy(rows_in)

    # enrich data with landing name and landing id
    for row in rows:
        row["data"] = row.get("data", {})

        if row.get("landing_name"):
            row["data"]["landing_name"] = row["landing_name"]

        if row.get("landing_id"):
            row["data"]["landing_id"] = row["landing_id"]

    filtered_rows = [{k: v for k, v in row["data"].iteritems()
                      if k not in BLACKLIST} for row in rows]

    keys = sorted(reduce(lambda keys, dct: keys.union(set(dct.keys())), filtered_rows, set()))

    # create csv
    return "\n".join([
        ";".join([key_to_header(key) for key in keys]),  # header
        "\n".join([";".join(csv_escape(unicode(row.get(key, ""))) for key in keys) for row in filtered_rows if row])
    ]).strip()


def csv_escape(value):
    if '"' in value:
        value = value.replace('"', '""')

    if " " in value \
            or ',' in value \
            or '"' in value \
            or ';' in value:
        value = '"' + value + '"'

    return value


def to_plain(rows_in):
    if not rows_in:
        return

    rows = []
    landing_name = rows_in[0]["landing_name"]

    for row_in in rows_in:
        assert landing_name == row_in["landing_name"]

        row = row_in.get("data", {}).copy()

        fields_meta = row.pop("meta", {}).get("fields", {})

        for key in BLACKLIST:
            row.pop(key, None)

        if row:
            row_list = row.items()

            if fields_meta:
                row_list.sort(key=lambda (k, v): fields_meta.get(k, {}).get("order", float("inf")))
                row_list = [(
                    fields_meta.get(k, {}).get("display_name", k),
                    v,
                ) for k, v in row_list]

            rows.append(row_list)

    body = u"<br><br>".join(
        u"<br>".join(
            u"<b>%s</b>: %s" % (key.strip(), unicode(value).strip()) for key, value in row
        ) for row in rows
    )

    return u"<h4>На турбо-странице %s вам оставили заявки:</h4>%s" % (landing_name, body)


def to_ecom_html(orders, for_seller):
    def to_html(goods):
        def get_field(field):
            return unicode(data.get(field, ''))

        def format_field(field):
            value = get_field(field)

            if field == 'phone':
                return '<a href="tel:{p}">{p}</a>'.format(p=value)

            return value

        def format_entry(field):
            name = fields_meta.get(field, {}).get("display_name", field)
            value = format_field(field)

            if field == '_receiptUrl':
                return u'<a href="%s">%s</a>' % (value, name)

            return '%s: %s' % (name, value)

        def make_link(url, name):
            return u'<a href="{url}">{name}</a>'.format(url=url, name=name)

        data = goods[0]['data']
        fields_meta = data.get('meta', {}).get('fields', {})

        order_id = get_field('_orderId')

        personal_info_keys = [k for k in fields_meta if not k.startswith("_")]
        personal_info_keys.sort(key=lambda k: fields_meta.get(k, {}).get("order", float("inf")))

        delivery_info_keys = ['_deliveryType', '_deliveryAddr', '_deliveryComment']
        payment_info_keys = ['_paymentType', '_orderTotal', '_paymentId', '_receiptUrl']

        publish_url = get_field('_publishUrl')
        landing_title = get_field('_landingTitle')
        landing_name = unicode(goods[0]['landing_name'])

        greeting = u'На Турбо-странице %s вам оставили заявку:' % make_link(publish_url, landing_name) \
            if for_seller else u'Ваш заказ на %s принят.' % make_link(publish_url, u'странице')

        footer = ''.join([
            u'Вы получили это письмо, потому что кто-то оставил заявку на %s.<br>' % make_link(publish_url, u'странице'),
            u'Это письмо отправлено автоматически, пожалуйста не отвечайте на него.<br><br>',
            u'С вопросами по вашему заказу обращайтесь по контактам, указанным на странице: %s.' % make_link(publish_url, landing_title)
        ]) if not for_seller else ''

        order_table = ''.join(
            u'<tr><td>{good}</td><td>{price}</td><td>{count}</td><td>{total}</td></tr>'.format(
                good=g['data']['product'],
                count=g['data']['quantity'],
                price=g['data']['price'],
                total=g['data']['total_price'],
            ) for g in goods
        )

        order_info = u'<b>Номер заказа:</b> %s<br><br>' % order_id if order_id else ''

        personal_info = '<br/>'.join([
            format_entry(k) for k in personal_info_keys if get_field(k) != ''
        ])

        delivery_info = '<br/>'.join([
            format_entry(k) for k in delivery_info_keys if get_field(k) != ''
        ])

        payment_info = '<br/>'.join([
            format_entry(k) for k in payment_info_keys if get_field(k) != ''
        ])

        return u'''\
<html><body>
Здравствуйте.<br><br>
{greeting}<br><br>
<table border="1" cellspacing="0" cellpadding="2">
<tr><td><b>Товар</b></td><td><b>Цена</b></td><td><b>Количество</b></td><td><b>Стоимость</b></td></tr>
{order_table}
</table><br>
{order_info}
<b>Информация об оплате:</b><br>
{payment_info}<br><br>
<b>Информация о доставке:</b><br>
{delivery_info}<br><br>
<b>Данные получателя:</b><br>
{personal_info}<br><br>
{footer}
</body></html>
'''.format(
            greeting=greeting,
            footer=footer,
            order_table=order_table,
            personal_info=personal_info,
            delivery_info=delivery_info,
            payment_info=payment_info,
            order_info=order_info
        )

    return map(to_html, orders)


class CanvasLandingFormNotifierTest(sdk2.Task):
    """
    fetch landing-form-data from YT and notify subscribers about new records
    """
    class Requirements(sdk2.Requirements):
        environments = [PipEnvironment("requests")]
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        bcc_emails = sdk2.parameters.List(
            "email addresses to send bcc-copy to",
            default=["landing-notifications@yandex-team.ru"]
        )

        blanding_uri = sdk2.parameters.String(
            "landing-form-backend api uri",
            default="https://yandex.ru/turbofeedback/",
            required=True,
        )

        ignore_user_email = sdk2.parameters.Bool(
            "send email only to bcc_emails",
            default=False,
            required=True,
        )

        fails_count_max = sdk2.parameters.Integer(
            "Submissions treat as failed if error counter is greater than this",
            default=3,
            required=True,
        )

    def sendmail(self, csv, plain, emails, header):
        if not csv and not plain:
            raise RuntimeError("nothing to send")

        FROM = "devnull@yandex.ru"
        TO = list(emails)
        BCC = list(self.Parameters.bcc_emails)

        msg = MIMEMultipart()
        msg['Subject'] = Header(header, "utf-8")
        msg['From'] = FROM
        msg['To'] = COMMASPACE.join(TO)
        if BCC:
            msg['RCPT TO'] = COMMASPACE.join(BCC)

        msg.attach(MIMEText(plain, _subtype='html', _charset='utf-8'))

        if csv:
            part = MIMEText(csv, _subtype='csv', _charset='utf-8-sig')
            part.add_header("Content-Disposition", "attachment", filename='{}.csv'.format(time.strftime("%Y%m%dT%H%M%S")))
            msg.attach(part)

        logging.info("email to send:")
        logging.info(msg.as_string())
        addresses = BCC
        if not self.Parameters.ignore_user_email:
            addresses += TO

        try:
            if not getattr(self, "_smtp_client", None):
                self._smtp_client = smtplib.SMTP(host='yabacks.yandex.ru', port=25)

            self._smtp_client.sendmail(from_addr=FROM, to_addrs=list(set(addresses)), msg=msg.as_string())
        except Exception:
            try:
                self._smtp_client.quit()  # hmm, maybe there is no need to reconnect... maybe not.
            except Exception:
                pass
            finally:
                self._smtp_client = None
            raise

    def on_execute(self):
        def _process_result(ids, success, error_msg=""):
            response = requests.patch(urljoin(blanding_uri, "submissions"),
                                      json=dict(ids=ids, succeed=success, fail_msg=error_msg),
                                      headers=dict(Authorization=blanding_token))
            if response.status_code != 200:
                logging.error(
                    (u"Can't set processed status to submissions. Emails might be sent twice. Success: {success}." +
                     u"Error message: {error_msg}" +
                     u"Http code: {code}. Response text: {text}. Submission ids: [{ids}]")
                    .format(code=response.status_code,
                            error_msg=error_msg,
                            success=success,
                            text=response.text,
                            ids=ids))
                return
            logging.info("State {state} was set on submissions".format(state=("success" if success else "failure")),
                         extra=dict(ids=ids))

        def _send(text, csv, emails, ids, header):
            # noinspection PyBroadException
            try:
                self.sendmail(csv=csv, plain=text, emails=emails, header=header)
            except Exception as e:
                logging.exception("Error while sending emails")
                _process_result(ids=ids, success=False,
                                error_msg="Error while sending emails: {}".format(e))
                # Remember to set failure state on task
                return True
            else:
                _process_result(ids=ids, success=True)
                return False

        blanding_uri = self.Parameters.blanding_uri
        blanding_token = sdk2.Vault.data("BLANDING_API_TOKEN")

        fails_count_max = self.Parameters.fails_count_max
        response = requests.get(urljoin(blanding_uri, "submissions/new"),
                                params=dict(limit=1000, fails_count_max=fails_count_max),
                                headers=dict(Authorization=blanding_token))
        if response.status_code != 200:
            logging.error(u"Can't get submissions from blanding. Http code: {code}. Response text: {text}"
                          .format(code=response.status_code,
                                  text=response.text))
            response.raise_for_status()

        rows = response.json()["items"]

        grouped_submissions = defaultdict(list)
        for row in rows:
            emails = frozenset([email.encode("utf8") for email in row["data"]["meta"]["emails"]])
            letter_type = 'ecom' if is_ecom(row) else 'default'
            grouped_submissions[emails, letter_type, row["landing_name"]].append(row)

        was_error = False
        for ((emails, letter_type, landing_name), rows) in grouped_submissions.iteritems():

            ids = [row["id"] for row in rows]

            if letter_type == 'ecom':
                orders = []

                for row in rows:
                    try:
                        good = split_goods(row)
                        orders.append(good)
                    except Exception as e:
                        logging.exception("Error while parsing order items")
                        _process_result(ids=[row["id"]], success=False,
                                        error_msg="Error while parsing order items: {}".format(e))
                        was_error = True

                header = u'На турбо-странице "%s" вам оставили заявку' % landing_name
                was_error = any(
                    _send(html, csv, emails, ids, header) for html, csv in zip(
                        to_ecom_html(orders, True), map(to_csv, orders)
                    )
                ) or was_error

                header = u'Ваш заказ'
                was_error = any(
                    _send(html, None, [email.encode("utf8")], ids, header) for html, email in zip(
                        to_ecom_html(orders, False),
                        [order[0]['data'].get('_customerEmail') for order in orders]
                    ) if email is not None
                ) or was_error
            else:
                was_error = _send(to_plain(rows), to_csv(rows), emails, ids, u"Новые заявки от Яндекса") or was_error

        try:
            self._smtp_client.quit()
        except Exception:
            pass

        if was_error:
            raise common.errors.TaskFailure("There was errors on sending emails. " +
                                            "Error counter was increased and error message was set for broken submissions. " +
                                            "The number of attempts to send email is limited [default=3]. " +
                                            "This error has no effect on good submissions.")
