#!/usr/bin/env python
from lxml import etree
import base64
import Crypto.Hash.SHA256
import MySQLdb
import os
import requests
import time


def update_rfc_totp_check_time(mysql):
    t = get_timestamp()
    if t % 30 > 20:
        time.sleep(31 - t % 30)
        t = get_timestamp()

    cur = mysql.cursor()

    # here t is in [0..20] range
    # fmt: off
    cur.execute("UPDATE attributes SET value='%d' "
                "WHERE type=156 AND uid IN (4006854609);" % t)
    # fmt: on
    cur.fetchall()
    mysql.commit()
    time.sleep(4)  # ensure db replicaton works
    # time now is [4..24]


def clean_attrs_in_db():
    mysql = MySQLdb.connect(
        host="cnt-dbm-test.passport.yandex.net",
        user=os.environ["BB_PASSPORTDB_USER_RW"],
        passwd=os.environ["BB_PASSPORTDB_PASSWD_RW"],
        db="passportdbshard1",
    )
    cur = mysql.cursor()
    cur.execute(
        "UPDATE attributes SET value='123' "
        "WHERE type=106 AND uid IN (71001, 4001517393, 4001595411, 4001595721, 4001784375);"
    )
    cur.fetchall()
    mysql.commit()

    update_rfc_totp_check_time(mysql)


def clean_local_rfc_totp_check_time(mysql_port):

    mysql = MySQLdb.connect(
        host='127.0.0.1',
        user='root',
        passwd='',
        port=mysql_port,
        db="passportdbshard1",
    )

    update_rfc_totp_check_time(mysql)


def get_timestamp():
    return int(time.time())


def _get_str_from_resp(resp, val):
    try:
        tree = etree.fromstring(resp.encode('utf-8'))
        return tree.xpath('/doc/' + val)[0].text
    except:
        return ''


def get_status_from_resp(resp):
    return _get_str_from_resp(resp, 'status')


def get_secret_from_resp(resp):
    return _get_str_from_resp(resp, 'secret_value')


def get_error_from_resp(resp):
    return _get_str_from_resp(resp, 'error')


def get_junk_from_resp(resp):
    return _get_str_from_resp(resp, 'junk_secret_value')


def get_time_from_resp(resp):
    return _get_str_from_resp(resp, 'time')


def get_secret_key(pin, secret):
    s = Crypto.Hash.SHA256.new()
    s.update((pin + secret).encode('ascii'))
    return s.digest()


def do_request(host, method, request_part):
    request = 'http://%s/blackbox?method=%s&%s' % (host, method, request_part)
    response = requests.get(request)
    return request, response.text


def encode_base64(s):
    if isinstance(s, str):
        s = s.encode('ascii')

    return base64.urlsafe_b64encode(s).decode('ascii')
