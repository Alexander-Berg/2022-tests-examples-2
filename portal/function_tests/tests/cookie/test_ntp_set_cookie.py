# -*- coding: utf-8 -*-

import logging
import allure
import pytest
import re

from common import env
from common.client import MordaClient
from common.morda import Morda
import common.utils

logger = logging.getLogger(__name__)

@allure.feature("function_tests_stable")
def test_ntp_secure_yandexuid_cookie():
    client = MordaClient()
    url    = Morda.get_origin(no_prefix=True, domain="ru", env=client.env)

    response = client.request(
        url="{}{}".format(url, "/portal/ntp/informers"),
        allow_redirects = False,
        allow_retry = False,
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 YaBrowser/22.3.3.855 Yowser/2.5 Safari/537.36"}
    ).send()

    headers = response.headers
    assert "set-cookie" in headers

    set_cookie = common.utils.parse_set_cookie(headers["set-cookie"])
    yandexuid = None
    for item in set_cookie:
        if item.startswith("yandexuid="):
            yandexuid = item
            break
    assert yandexuid, "Can not find header set-cookie: yandexuid="

    assert re.search("; Secure(?:;|$)", yandexuid, re.I), "cookie yandexuid has not prop Secure. {}".format(yandexuid)
    assert re.search("; SameSite=None(?:;|$)", yandexuid, re.I), "cookie yandexuid has not prop SameSite=None. {}".format(yandexuid)

# этот тест работает только в проде. потому что ручка /portal/ntp/informers на проде идет в апхост, а на деве в fsgi
# в проде балансер довешивает на куки пропертю Secure, поэтому надо делать json_dump_responses=MORDA_LEGACY_BACKEND:http_response:
# и смотреть на куки, которые выставил перл
@allure.feature("function_tests_stable")
def test_apphost_ntp_secure_yandexuid_cookie():
    client = MordaClient()
    url    = Morda.get_origin(no_prefix=True, domain="ru", env=client.env)

    response = client.request(
        url="{}{}".format(url, "/portal/ntp/informers?json_dump_responses=MORDA_LEGACY_BACKEND:http_response:"),
        allow_redirects = False,
        allow_retry = False,
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 YaBrowser/22.3.3.855 Yowser/2.5 Safari/537.36"}
    ).send()

    set_cookie = None
    json_data = response.json()
    # check data in path MORDA_LEGACY_BACKEND.response[0].decoded_protobuf
    if "MORDA_LEGACY_BACKEND" in json_data:
        if "response" in json_data["MORDA_LEGACY_BACKEND"] and len(json_data["MORDA_LEGACY_BACKEND"]["response"]):
            dpb = json_data["MORDA_LEGACY_BACKEND"]["response"][0]["decoded_protobuf"]
            for i in range(len(dpb)):
                # "  1: 'Set-Cookie'",
                # "  2: 'yandexuid=8242271241652809567; Expires=Fri, 14-May-2032 17:46:07 GMT; Domain=.yandex.ru; Path=/'",
                if dpb[i] == "  1: 'Set-Cookie'" and dpb[i+1].startswith("  2: 'yandexuid="):
                    # берем строку внутри одинарных кавычек
                    start = 6
                    end = len(dpb[i+1]) - 1
                    set_cookie = common.utils.parse_set_cookie(dpb[i+1][start:end])
    
                    yandexuid = None
                    for item in set_cookie:
                        if item.startswith("yandexuid="):
                            yandexuid = item
                            break
                    assert yandexuid, "Can not find header set-cookie: yandexuid="

                    assert re.search("; Secure(?:;|$)", yandexuid, re.I), "cookie yandexuid has not prop Secure. {}".format(yandexuid)
                    assert re.search("; SameSite=None(?:;|$)", yandexuid, re.I), "cookie yandexuid has not prop SameSite=None. {}".format(yandexuid)
