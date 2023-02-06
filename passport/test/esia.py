# -*- coding: utf-8 -*-

import json
import re

import jwt
from passport.backend.social.common import crypto
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    SIMPLE_USERID1,
)
from passport.backend.social.common.useragent import Url
from passport.backend.social.proxylib.EsiaProxy import (
    EsiaPermissions,
    get_esia_yandex_private_key,
    verify_esia_signature,
)
from passport.backend.social.proxylib.repo.EsiaRepo import EsiaRepo
import pytz

from .base import (
    BaseFakeProxy,
    FakeResponse,
)


# Validity
#     Not Before: Sep 17 16:27:35 2021 GMT
#     Not After : Sep 15 16:27:35 2031 GMT
# Subject Public Key Info:
#     Public Key Algorithm: GOST R 34.10-2012 with 256 bit modulus
#         Public key:
#            X:2321EBF57B4B82BEADBF945020D16B4976A17CF84D353BCD089BD9D3FFC100CE
#            Y:D5419E316B7BC44A8E06905BB5EB449314F1685EB1911E0CC4B98C7048866C22
#         Parameter set: id-GostR3410-2001-CryptoPro-XchA-ParamSet
#
# Выписать можно так
# openssl req -newkey gost2012_256 -pkeyopt paramset:XA -x509 -out my.crt -keyout my.key -days 3650 -nodes
ESIA_YANDEX_CERTIFICATE = b'''
-----BEGIN CERTIFICATE-----
MIIB6TCCAZSgAwIBAgIUIQsNApdEfjFjg5yVWB2ywtHMxzIwDAYIKoUDBwEBAwIF
ADBFMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwY
SW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMB4XDTIxMDkxNzE2MjczNVoXDTMxMDkx
NTE2MjczNVowRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAf
BgNVBAoMGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDBmMB8GCCqFAwcBAQEBMBMG
ByqFAwICJAAGCCqFAwcBAQICA0MABEDOAMH/09mbCM07NU34fKF2SWvRIFCUv62+
gkt79eshIyJshkhwjLnEDB6RsV5o8RSTROu1W5AGjkrEe2sxnkHVo1MwUTAdBgNV
HQ4EFgQUT1VG+jYEwiDNf1aQNPcrcC8HG/QwHwYDVR0jBBgwFoAUT1VG+jYEwiDN
f1aQNPcrcC8HG/QwDwYDVR0TAQH/BAUwAwEB/zAMBggqhQMHAQEDAgUAA0EA1A09
vFQ3olb9aS2gbPxYniJAWdi9bal/BhJwqjyF5lrC5GwKnEB8hnKAE3wMqk04TKet
qw5Ws2+E05YipS0Z3A==
-----END CERTIFICATE-----
'''

ESIA_YANDEX_PRIVATE_KEY = b'''
-----BEGIN PRIVATE KEY-----
MEYCAQAwHwYIKoUDBwEBAQEwEwYHKoUDAgIkAAYIKoUDBwEBAgIEIHMxmp022Nkp
JBD4MCTlAhwbkhc5Z5srn1RlK3kFi2EI
-----END PRIVATE KEY-----
'''


GET_PROFILE_URL_PATH_RE = re.compile('/rs/prns/[^/]+')


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(EsiaRepo)

    def _request_to_method(self, request):
        url = Url(request['url'])
        if url.path == '/aas/oauth2/te':
            return 'refresh_token'
        if GET_PROFILE_URL_PATH_RE.match(url.path):
            return 'get_profile'


class EsiaApi(object):
    default_id_token = {
        'amr': 'PWD',
        'aud': 'YANDEXID',
        'auth_time': 1629721100,
        'iat': 1629721141,
        'iss': 'http://esia-portal1.test.gosuslugi.ru/',
        'nbf': 1629721141,
        'sub': int(SIMPLE_USERID1),
        'urn:esia:amd': 'PWD',
        'urn:esia:sbj': {
            'urn:esia:sbj:is_tru': True,
            'urn:esia:sbj:nam': 'OID.1000299654',
            'urn:esia:sbj:oid': 1000299654,
            'urn:esia:sbj:typ': 'P',
        },
        'urn:esia:sid': '63e07a8e-5667-4dfe-a54a-3e392455b6b6',
    }

    @staticmethod
    def refresh_token(
        access_token=APPLICATION_TOKEN1,
        expires_in=APPLICATION_TOKEN_TTL1,
        refresh_token=APPLICATION_TOKEN2,
    ):
        response = {
            'access_token': access_token,
            'expires_in': expires_in,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
        }
        return FakeResponse(json.dumps(response), 200)

    @staticmethod
    def build_id_token(
        id_token=dict(),
        headers=dict(),
        private_key=None,
        algorithm=None,
        id_token_ttl=APPLICATION_TOKEN_TTL1,
    ):
        id_token = build_dict_from_standard(EsiaApi.default_id_token, id_token)
        id_token.setdefault('exp', now.f() + id_token_ttl)

        headers = build_dict_from_standard(
            dict(
                sbt='id',
                ver=0,
            ),
            headers,
        )

        if private_key is None:
            private_key = get_esia_yandex_private_key()

        if algorithm is None:
            algorithm = 'GOST3410_2012_256'

        return jwt.encode(
            id_token,
            private_key,
            algorithm=algorithm,
            headers=headers,
        )

    @staticmethod
    def esia_datetime_format(timestamp):
        return pytz.timezone('Europe/Moscow').localize(timestamp).strftime('%Y.%m.%d %H:%M:%S %z')

    @staticmethod
    def assert_ok_esia_signature(params, signature):
        try:
            verify_esia_signature(params, signature)
        except crypto.Pkcs7VerifyError as e:
            assert False, str(e)

    @staticmethod
    def assert_ok_esia_permissions(params, permissions):
        assert EsiaPermissions.from_params(params).to_list() == permissions.to_list()
