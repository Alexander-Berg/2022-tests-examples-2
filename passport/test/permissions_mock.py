# -*- coding: utf-8 -*-

from collections import (
    Iterable,
    namedtuple,
)

import mock
import paramiko.agent
from passport.backend.vault.api.models import ExternalRecord
from passport.backend.vault.api.test.fake_blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.vault.api.views.base_view import BaseView
from passport.backend.vault.api.views.secrets.views import BaseSecretView
from six import (
    string_types,
    StringIO,
)


TEST_OAUTH_TOKEN_1 = 'OAuth token-ololoken'
TEST_OAUTH_TOKEN_2 = 'token-ololoken'
TEST_STRANGE_KEY_1 = 'strange-key ororo ppodolsky@213.180.218.205-red.dhcp.yndx.net'
TEST_ECDSA_PRIVATE_KEY_1 = u'''
-----BEGIN EC PRIVATE KEY-----
MIGkAgEBBDA1qfk/2g4GoVXGs6EPLjLOvDNdtdysMtlEGvGybykCeMga6rYkqoKV
SpZfXiPtro+gBwYFK4EEACKhZANiAATDbvbLyBs62OBSJz3aC4XutFnygTJnzGZJ
ZSBIha08rrjSlJ19IDO+8jUCWqgS8XT84ZJlvnogqe7r5h0cJh/1E10pBafXrKQp
yHngndFk5+eTUmaz3HL/HBq/1n5Qa8I=
-----END EC PRIVATE KEY-----
'''
TEST_ECDSA_PUBLIC_KEY_1 = (
    'ecdsa-sha2-nistp384 AAAAE2VjZHNhLXNoYTItbmlzdHAzODQAAAAIbm'
    'lzdHAzODQAAABhBMNu9svIGzrY4FInPdoLhe60WfKBMmfMZkllIEiFrTyu'
    'uNKUnX0gM77yNQJaqBLxdPzhkmW+eiCp7uvmHRwmH/UTXSkFp9espCnIee'
    'Cd0WTn55NSZrPccv8cGr/WflBrwg== ppodolsky@213.180.218.205-red.dhcp.yndx.net'
)
TEST_RSA_PRIVATE_KEY_1 = u'''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA63Qr2tsZPe9kQJdQE9im/dQ2TU/fc5mt+TD7IdHI6F3NzIlh
m8wX4ferxzma5WUk2sTJpzlNcnHBh7cBAyJMJo0knktKvfZD7uHcxPBrhlHUV58D
HPwpXM9znJaElNQoZXPQ3y/dmvY9ym0khGNCDjGjI5z9C8ATw8+D7Y6DS3ZC5oOQ
Q5r4f/K2sKbVakUutqunkMR14Non5O1abtqjoYCyCAXP08rdj3ooY6I/maOty/yU
I2Xg6NHpP5Q/YvskZPNxB1M3VMh0WZPIX0urb1Qzam/zScM6Ew31nsh55gPQ8r8j
6wkPBk/j0xhdtl53tLTDj317C8BHEGTPmdPhdQIDAQABAoIBAFyMLTC5LhLKJf29
fBxQ7FKZNz7sRkiJ/3gTaKLCctXjCSF8XoF+l2SalUqZueiw+OuErj6sp2R0kj1m
EV/J+2Sr1djif15rjgg3fy9p0NnbEDvgpLif5SI16JuEDljxi29VNqSDi/d9Eoye
mdvvp+csW5OEAXK87QfqaVDW04S1FlKpQqXv3If0MSmt8J26IUUMWeTXfIKGBIGx
N4gfbFlrLxoediyDUFv0CE5bSQpTeEe6q+e1iMdrWXZHA8gWtdU2MEw+v7wcKju7
oP//Jp/Eg8pXmoWC80lje+Tb3pL9WHRMR2yt89Q81nXvIBRVHWSqvWZLfDEWjUoT
IGNYgAECgYEA+CSdesEmh4xKMrQTo95zTomm6vXZ+gJe9gvS24F6lx3DN9x9LMrl
cK1WOSGVus2feVDxjVz4F8Mdu8hPE9BZWhKzSg2AqBXG5t1htKaSQ2D8Jrks3byc
hjIpo5Zzqen/FUpFiA1IxlrSMK8z0o0wXsGRXVoc6+0fskMRluE3owECgYEA8uiz
Tus3ClCrcjL2ycIX2TAQMhlP6pjPt1YvO+SPjBvVj74ArwKZxPrm1XmqVqEekvpg
sdeWU9S6h3J+yhxi2DIDCgM2nUotYBcCaFs6Ir11RXgQyjYKeJsFV1sYrImTFsCY
0QtVG87xWZeYAHkby2qhT8dBr+iyZ/TBJl8AYnUCgYBWhF2r6SBH7nAIUaTvY6YM
Yg4iqemAM8dsPh8cjX5ypdvk5Cl4rp1kter0LHOKGBtcLw6pXRrbHhqF2IdJv0EI
GLEORrru3/jjkZh5ZgJlH7GKxtGP1i001NSTxuc4/O8FO0oW75rKHexfMRb+eF+/
Cfpm8/5Ve+2rN5swYgIGAQKBgCT9grC16P/NIQ6W7DX1NKSCSTUX3a+f7aHBohfA
yotPgcoN6RS9lKUGgDhp+qKOjpVbQ3ZRmjbR4kXWDbDBedvqYcQYkSyKqzZCyr8R
hVzc9QrLKeNhL18GXF3dJXjAyoFgeuT6kM9XSDGYgDEyQCVN65q2gS5EhUaHYxJw
zSIxAoGBAIUHxgTXBStKvvO31Cu2MHLl3VwnNu+7FTQHSArMTndv6BPOJZha8+Bc
U2eCXNWVYzd7dGObEac3iX/tGi7BFKgj3DUgCHpibE2GsByb9GCwRK7ELGMb54HU
S6YpUSO7mgyX1eqSBfcFx0+KOtvk1CvqnxcF+ImyvqkLuDTI120h
-----END RSA PRIVATE KEY-----
'''

TEST_RSA_PRIVATE_KEY_1_MD5_HASH = '03:94:5c:75:d7:4a:21:f2:51:39:42:34:85:30:35:d2'
TEST_RSA_PRIVATE_KEY_1_SHA256_HASH = 'tXVlNyIDl1au2i6zMvihflDdQgtBaRLT9QaA918iovQ'
TEST_RSA_PRIVATE_KEY_1_SHA1_HASH = 'I/OuiCggEdfndLoOQCm3cWmiS6o'

TEST_RSA_PUBLIC_KEY_1 = (
    u"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDrdCva2xk972RAl1AT2Kb91DZNT99zma35MPsh0cjoXc3MiWGbzBfh96vHOZrlZSTaxMmnOU1yc"
    u"cGHtwEDIkwmjSSeS0q99kPu4dzE8GuGUdRXnwMc/Clcz3OcloSU1Chlc9DfL92a9j3KbSSEY0IOMaMjnP0LwBPDz4PtjoNLdkLmg5BDmvh/8rawpt"
    u"VqRS62q6eQxHXg2ifk7Vpu2qOhgLIIBc/Tyt2Peihjoj+Zo63L/JQjZeDo0ek/lD9i+yRk83EHUzdUyHRZk8hfS6tvVDNqb/NJwzoTDfWeyHnmA9D"
    u"yvyPrCQ8GT+PTGF22Xne0tMOPfXsLwEcQZM+Z0+F1 ppodolsky@example.com"
)

TEST_RSA_LOGIN_1 = 'ppodolsky'

TEST_RSA_PRIVATE_KEY_2 = u'''
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA14/fwjniiYTkr95Lk+AMrdUW2bpn70vIaU3E7fZVR+PQTF4y
DbKDwo3PoTLfP2a29tOIzu36PJAtxvxjEaswJ06WwwqOFmht0yCHsET8/NBNuANZ
Tr/KuBUN69VsrUsXjws/QJkK3QVkzcvPSwP0n2oBX49Sp10R8FrkfJ5UWHj4WtTJ
nKle4Dj0/b9Vd4jgivK0Z5TosoELe1YL7qzzxrb+RP9em7z9r2d0WLY/P2M3CAqm
LXg1SPXitg6oZYrERV4hheoJMfC9x3mXN1HJj3LTiUOWGciUW0Jnpwmm+l3p/1+s
Zgt1q2lOzbsD+iYIHjlzny+AnDxmHvoCke0FzwIDAQABAoIBAEODbkN4ubj0hGOI
rgccjxwKt2Nt/It4IsbIcrtNAZzIfz7L6cVceeP/Yl5Mfptu4jMgQaL96ff5+Dxw
Y97uzOAivxlLPwFJp8wOTjEpCktsOks90UTW0Pkirv+EEsubzz8f+KmUxVBAFjhW
cxA9puoe21tAmlSM08eB0DovpJ8ogLB+HLqxXTWRO58hWxsDEi5HAaEeN5iYix2R
NwWNFohOY6jwWuXL8pRYIPB4MW41iOxcCg7u/xvWp55Q2oHOlvQ/6t+46M6BBRTT
/W0d1eL2KtdwkGlR+Wn//QsLOV5Sj1Gcja0ulEy/V3o7qfjto+Y0l2q1ECtVIfIi
MXPKzmECgYEA+67Lp8BS40hTAbzY7gdPFcMMCTl1Kz6EKorGSNnVMETueSUitXOY
6Cf2QgVA0oRKDy4FtwqcxumL5eaqwII9jB3pj0zI6tjzG7c9H2in4e/IDQ3fm2SU
6Fe639Pp6JcqiYTQnhgdwmW0Bl2e5nN88bioCHpAJZ2VQjMP7cfphccCgYEA20J2
eK49fXo7/fmSsGt79B8D+qALhspqvEutg0pFfb8IwEzJLnr+ien8qtKoqTClrQdh
Xwwx4uzsk3WpMJ3E5Bt/Dv9WPhvOK3tOrIZpA1OWWUHaKm1VXLE4xPl1pUZKoQ56
aUDhL1O7KrwmVv1S5U8WX+c+F7dFnk5Kq2BF37kCgYEApzoAFUkDigKvLJNm69kt
Yf9ECwkDYiVauc2VbChYr4bNkO7svfW93ltXE4zcAkRl1Oo2X+WMP9pD2xDF2b1v
2Z6yZkWVpf1aosrAsRLfoY6ptIrITT6qdip8f2YVoDZ4zADUgIbzlwvubuBbyTFp
Dk8sTt2zq4ql9uNorQxMjFcCgYAG9lBOurGnJ1d6VA9tXKxd7xIwRh63k/vZqMmE
rroQKR29BXMp76vfczebsP68CJhqKx7TZs66tu04LXdG3OuglqLtNfxmEnn0dYDl
B4uUGHZgtS+ZQ0l/nP0BfC5ZJic+f/gxGWdNGmqKC9lnz7lvIJjESNJ27FHgmfnT
AUaWuQKBgCh2NvqkzXBL9pMMd0qa6pLoq/YWvVIfpcgxbZuU7BidzgpqREJ9eiQq
f3hbs4SF60F9lzTvXY0Xj5X2S95EQAIyIaf22CZibjEj6lv3I9kPckPsHNNawrA6
mlgCHNG1Hu6Qv2XedaeWrna4GXzQeZSn/3daXrVtReFquuwFH/4V
-----END RSA PRIVATE KEY-----
'''

TEST_RSA_PRIVATE_KEY_2_MD5_HASH = 'f3:6d:f3:e7:aa:6c:98:36:c4:77:c0:31:43:1b:57:4f'
TEST_RSA_PRIVATE_KEY_2_SHA256_HASH = '2nyNOLPUH+Am0oHUzwKGevq//3i9a8R4utwDaduk8p8'
TEST_RSA_PRIVATE_KEY_2_SHA1_HASH = 'vGNudtUXNiFpe+5WobWNRDZvzes'

TEST_RSA_PUBLIC_KEY_2 = (
    u"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXj9/COeKJhOSv3kuT4Ayt1RbZumfvS8hpTcTt9lVH49BMXjINsoPCjc+hMt8/Zrb204jO7fo8k"
    u"C3G/GMRqzAnTpbDCo4WaG3TIIewRPz80E24A1lOv8q4FQ3r1WytSxePCz9AmQrdBWTNy89LA/SfagFfj1KnXRHwWuR8nlRYePha1MmcqV7gOPT9v1"
    u"V3iOCK8rRnlOiygQt7VgvurPPGtv5E/16bvP2vZ3RYtj8/YzcICqYteDVI9eK2DqhlisRFXiGF6gkx8L3HeZc3UcmPctOJQ5YZyJRbQmenCab6Xen"
    u"/X6xmC3WraU7NuwP6JggeOXOfL4CcPGYe+gKR7QXP alice@example.com"
)

TEST_RSA_LOGIN_2 = 'alice'

TEST_RSA_PRIVATE_KEYS = [
    TEST_RSA_PRIVATE_KEY_1,
    TEST_RSA_PRIVATE_KEY_2,
]

VALID_USER_TICKET_1 = (
    '3:user:CA0Q__________9_GhkKAghkEGQaCXZhdWx0OnVzZSDShdjMBCgB:HuxD6wnoAMnOebE2B8VM0iCx-jzdUbTS65qkJsCoB-uuGjo8m8kSKY'
    'w0jDqiJ72E4iBeodWEWDVSQ_7jExn1NeNagd7ukAgRWNq6tYZjMFDKeDYbCjQRsaC6Fvmnft1fbYq3xJBrtqX4S44t4nF59Mi360udUt2689cWFhQ1a'
    'mw'
)

VALID_USER_TICKET_SIGNLESS_1 = (
    '3:user:CA0Q__________9_GhkKAghkEGQaCXZhdWx0OnVzZSDShdjMBCgB:'
)

# Service ticket: src == 1, dst == 2

VALID_SERVICE_TICKET_1 = (
    '3:serv:CBAQ__________9_IgQIARAC:KhMboSUz4BwIJ5Hzvs5K4q0ydkB52HokUjcbdHJ9CHusib3MKGr8dJp-nX5P6vdgeH-ou3zGUGPATU6m'
    'GDQG-gjPB5P2ux9xy4PgmpGZ19eEDkw621c5zuW8WLB9VpTfdbEoWnTREn4rCaHhwDDU8fQHV4RjrEGJACyB--pvpqQ'
)

VALID_SERVICE_TICKET_SINGLESS_1 = (
    '3:serv:CBAQ__________9_IgQIARAC:'
)


class FakeUserTicket(object):
    def __init__(self, default_uid=None, scopes=None):
        self.default_uid = default_uid
        self.uids = []
        if default_uid:
            self.uids.append(default_uid)
        self.scopes = scopes if scopes is not None else []

    def has_scope(self, scope):
        return scope in self.scopes


FakeServiceTicket = namedtuple('FakeServiceTicket', 'src')


class FakeUserContext(object):
    def __init__(self, uid=None, scopes=None):
        self.uid = uid
        self.mock = mock.patch(
            'passport.backend.vault.api.tvm.get_user_context',
            return_value=self,
        )
        self.scopes = scopes

    def check(self, user_ticket):
        return FakeUserTicket(self.uid, self.scopes)

    def start(self):
        if self.uid is not None:
            return self.mock.start()

    def stop(self):
        if self.uid is not None:
            return self.mock.stop()


class FakeServiceContext(object):
    def __init__(self, tvm_client_id=None):
        self.tvm_client_id = tvm_client_id
        self.mock = mock.patch(
            'passport.backend.vault.api.tvm.get_service_context',
            return_value=self,
        )

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def check(self, service_ticket):
        return FakeServiceTicket(self.tvm_client_id)

    def start(self):
        if self.tvm_client_id:
            return self.mock.start()

    def stop(self):
        if self.tvm_client_id:
            return self.mock.stop()


class PermissionsMock(object):
    def __init__(self, uid=None, scopes=None, ssh_agent_key=None,
                 fixture=None, abc_groups=None, abc_roles=None, staff_groups=None,
                 rsa=None, oauth=None, supervisor=False,
                 service_ticket=VALID_SERVICE_TICKET_1, tvm_client_id=1):
        """
        Mock all permission points
        :param rsa: dict of two {'uid': 123, 'keys': ['456']}
        :param oauth: dict of three {'uid': 123, 'login': 'vovan', 'scope': '456'}
        """
        self.patches = []

        self.fixture = fixture
        self.db_entities = []

        if uid is not None:
            self.mocked_uid = uid
            self.patches.extend([
                mock.patch.object(
                    BaseView,
                    'user_ticket',
                    mock.PropertyMock(side_effect=lambda: VALID_USER_TICKET_1),
                ),
                FakeUserContext(uid, scopes=scopes or ['vault:use']),
            ])

        if service_ticket is not None:
            self.patches.extend([
                mock.patch.object(
                    BaseView,
                    'service_ticket',
                    mock.PropertyMock(side_effect=lambda: service_ticket),
                ),
                FakeServiceContext(tvm_client_id),
            ])

        if ssh_agent_key is not None:
            if isinstance(ssh_agent_key, string_types):
                return_value = [paramiko.RSAKey.from_private_key(StringIO(ssh_agent_key))]
            elif isinstance(ssh_agent_key, Iterable):
                return_value = [
                    paramiko.RSAKey.from_private_key(StringIO(key))
                    for key in ssh_agent_key
                ]
            else:
                raise ValueError('ssh_agent_key must be either string or iterable')

            self.paramiko_mock = mock.patch.object(
                paramiko.agent.Agent,
                'get_keys',
                return_value=return_value,
            )
            self.patches.append(self.paramiko_mock)

        if rsa:
            self.mock_rsa = mock.patch.object(
                BaseView,
                '_acquire_credentials',
                return_value=(rsa['uid'], rsa['keys']),
            )
            self.patches.append(self.mock_rsa)

        if oauth:
            self.fake_blackbox = FakeBlackbox()
            self.fake_blackbox.set_response_value(
                'oauth',
                blackbox_oauth_response(
                    uid=oauth['uid'],
                    login=oauth.get('login'),
                    scope=oauth.get('scope', ''),
                ),
            )
            self.patches.append(self.fake_blackbox)

        if abc_groups:
            self.db_entities.extend(map(
                lambda x: ExternalRecord(
                    external_type='abc',
                    uid=self.mocked_uid,
                    external_id=x[0],
                    external_scope_id=x[1],
                ),
                abc_groups,
            ))

        if abc_roles:
            self.db_entities.extend(map(
                lambda x: ExternalRecord(
                    external_type='abc',
                    uid=self.mocked_uid,
                    external_id=x[0],
                    external_role_id=x[1],
                ),
                abc_roles,
            ))

        if staff_groups:
            self.db_entities.extend(map(
                lambda x: ExternalRecord(
                    external_type='staff',
                    uid=self.mocked_uid,
                    external_id=x,
                ),
                staff_groups,
            ))

        if supervisor:
            self.supervisor_mock = mock.patch.object(
                BaseSecretView,
                'check_if_supervisor',
                return_value=supervisor,
            )
            self.patches.append(self.supervisor_mock)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if self.fixture:
            with self.fixture.app.app_context():
                for e in self.db_entities:
                    self.fixture.db.session.add(e)
                self.fixture.db.session.commit()
        elif self.db_entities:
            raise Exception('PermissionMock requires a fixture option')

        for patch in self.patches:
            patch.start()

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()

        if self.fixture:
            with self.fixture.app.app_context():
                for e in self.db_entities:
                    self.fixture.db.session.delete(e)
                self.fixture.db.session.commit()
