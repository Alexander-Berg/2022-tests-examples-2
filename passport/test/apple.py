# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from base64 import urlsafe_b64encode
import json
import textwrap

from jwt import PyJWS
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.test.consts import (
    AUTHORIZATION_CODE1,
    EMAIL1,
    EXTERNAL_APPLICATION_ID1,
    FIRSTNAME1,
    LASTNAME1,
    SIMPLE_USERID1,
    UNIXTIME1,
    UNIXTIME2,
)
from passport.backend.social.common.useragent import Url
from passport.backend.social.proxylib.AppleProxy import APPLE_TOKEN_ISSUER
from passport.backend.social.proxylib.repo.AppleRepo import AppleRepo
from passport.backend.social.proxylib.test.base import (
    BaseFakeProxy,
    FakeResponse,
)
from passport.backend.utils.common import merge_dicts


# Чтобы сгенерить закрытый ключ нужно выполнить
# openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:512
APPLE_PRIVATE_KEY1 = textwrap.dedent('''\
    -----BEGIN PRIVATE KEY-----
    MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAwxL1e9i74LR+V+iE
    HJskBOoTjU3Zrwjitdb8F2YleCbsOmxh7Dd0RsbU8KImEm4Y8MFSM9cOpczCo+zz
    YZ1qgQIDAQABAkBM8yGa5PfXv9tG2hWjIx+mQJ/N0bPY8+xaRp/SqxyEtETCJUB7
    fsQOlnZJSL50yfArqpjnNYRr6/wr0+lpjeCxAiEA9iUft/1Jr8LwXIKxGgiPHXM5
    Cqg2uzvTosUfd3611JMCIQDK4mFu3gXQvbkIDuMRNlloXNOcupRyS6raojzvN2Zl
    GwIgXK21t60i5Y7cubhrvoWifVA5Fg4oLW9lTFA0fOW0yQkCICr7IqEWMC00xEpM
    vRYcaXyOjdYaQPClzyBaVoZnOi4ZAiEAtJdKoAFUnMXiZGkPVKycP6U4rai32dXD
    t5cQqnHKSHQ=
    -----END PRIVATE KEY-----
''')
APPLE_PRIVATE_KEY2 = textwrap.dedent('''\
    -----BEGIN PRIVATE KEY-----
    MIIBVgIBADANBgkqhkiG9w0BAQEFAASCAUAwggE8AgEAAkEAyBQOSRJaI+Th77Nz
    owoCtUjg463dvKozdrFiAJPZkS6046TEF5unwL80KLmtFU3S1cSyyk51sid1qHdW
    EBCktwIDAQABAkEAxeko1Fkl9xmB8HSnLyBI23/yjOTAUM5fR8pg8cdOUE+MuSZE
    sKCeGEWR+lZ+7EbISeLQq2oh4y/mddKwVRTRiQIhAPdLBQ+EpzTB3sLYCnTRgaX/
    N+yzz5j+CdV0dE6lQ6btAiEAzx93KXK+8BJj0etTBqusJ5dZoufTz6uziLtIhLcM
    AbMCIQDQL6sJ/m5ZvuEPfZuH7xzLp8noDxS1QyD6P7juwLjsnQIhAK0HT0gL+OCb
    rFIoshKHhekJMjO6UaNSgEhAlMNyG5CrAiAW6TghtSZ2Nq/qSENiZIwOAdyYwwY7
    uqIbjdyQH84xVw==
    -----END PRIVATE KEY-----
''')

# Каждый APPLE_JSON_WEB_KEYn соответствует APPLE_PRIVATE_KEYn

# Чтобы сгенерить Json Web Key нужно выполнить
# from jwcrypto.jwk import JWK
# jwk = JWK()
# jwk.import_from_pem(private_key)
# jwk.export_public()
APPLE_JSON_WEB_KEY1 = {
    'e': 'AQAB',
    'kid': 'ApbNwEcP5MUMfH9IIwN_8QVAdKzjxjZKN6Dz8xR4I0E',
    'kty': 'RSA',
    'n': 'wxL1e9i74LR-V-iEHJskBOoTjU3Zrwjitdb8F2YleCbsOmxh7Dd0RsbU8KImEm4Y8MFSM9cOpczCo-zzYZ1qgQ',
}
APPLE_JSON_WEB_KEY2 = {
    'e': 'AQAB',
    'kid': '-rMRuDYsv_TvgNI1CVriQUpDQj67n6jmYnu6KodcY4I',
    'kty': 'RSA',
    'n': 'yBQOSRJaI-Th77NzowoCtUjg463dvKozdrFiAJPZkS6046TEF5unwL80KLmtFU3S1cSyyk51sid1qHdWEBCktw',
}

_DEFAULT_ID_TOKEN = {
    'aud': EXTERNAL_APPLICATION_ID1,
    'email_verified': 'true',
    'email': EMAIL1,
    'exp': UNIXTIME1,
    'iat': UNIXTIME2,
    'iss': APPLE_TOKEN_ISSUER,
    'sub': SIMPLE_USERID1,
}

APPLE_TEAM_ID1 = 'team1'
APPLE_TEAM_ID2 = 'team2'


def build_id_token(
    id_token=dict(),
    exclude_attrs=None,
    private_key=APPLE_PRIVATE_KEY1,
    key_id=None,
    algorithm=None,
):
    if key_id is None:
        key_id = APPLE_JSON_WEB_KEY1['kid']
    if algorithm is None:
        algorithm = 'RS256'
    id_token = build_dict_from_standard(_DEFAULT_ID_TOKEN, id_token, exclude_attrs)
    headers = {'kid': key_id}
    return PyJWS().encode(
        json.dumps(id_token),
        private_key,
        algorithm=algorithm,
        headers=headers,
    )


def build_client_token_v1(
    kwargs=None,
    exclude_attrs=None,
):
    default_kwargs = dict(
        authorization_code=AUTHORIZATION_CODE1,
        id_token=build_id_token(),
        firstname=FIRSTNAME1,
        lastname=LASTNAME1,
        version=1,
    )
    kwargs = build_dict_from_standard(default_kwargs, kwargs, exclude_attrs)
    return urlsafe_b64encode(json.dumps(kwargs))


class FakeProxy(BaseFakeProxy):
    def __init__(self):
        super(FakeProxy, self).__init__(AppleRepo)

    def _request_to_method(self, request):
        if Url(request['url']).paramless == 'https://appleid.apple.com/auth/keys':
            return 'get_public_keys'
        if Url(request['url']).paramless == 'https://appleid.apple.com/auth/revoke':
            return 'revoke_token'


class AppleApi(object):
    @classmethod
    def get_public_keys(cls, keys=None, alg=None):
        if keys is None:
            keys = [APPLE_JSON_WEB_KEY1]
        if alg is None:
            alg = 'RS256'
        common = {
            'alg': alg,
            'use': 'sig',
        }
        keys2 = list()
        for key in keys:
            jwk = merge_dicts(common, key)
            keys2.append(jwk)
        response = {'keys': keys2}
        response = json.dumps(response)
        return FakeResponse(response, 200)

    @classmethod
    def revoke_token(cls):
        return FakeResponse('', 200)
