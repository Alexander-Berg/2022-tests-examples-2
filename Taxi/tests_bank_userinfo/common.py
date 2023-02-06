SESSION_STATUS_NOT_REGISTERED = 'not_registered'
SESSION_STATUS_NOT_AUTHORIZED = 'not_authorized'
SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS = (
    'required_application_in_progress'
)
SESSION_STATUS_PHONE_RECOVERY_REQUIRED = 'phone_recovery_required'
SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED = 'account_recovery_required'
SESSION_STATUS_BANK_PHONE_WITHOUT_BUID = 'bank_phone_without_buid'
SESSION_STATUS_BANNED = 'banned'
SESSION_STATUS_INVALID_TOKEN = 'invalid_token'
SESSION_STATUS_APP_UPDATE_REQUIRED = 'app_update_required'
SESSION_STATUS_BANK_RISK_DENY = 'bank_risk_deny'
SESSION_STATUS_SPEND_ALL_ATTEMPTS_TO_VERIFY_CODE = (
    'spend_all_attempts_to_verify_code'
)
SESSION_STATUS_PIN_TOKEN_CLEAR = 'pin_token_clear'
SESSION_STATUS_PIN_TOKEN_REISSUE = 'pin_token_reissue'
SESSION_STATUS_PIN_TOKEN_RETRY = 'pin_token_retry'
SESSION_STATUS_PIN_TOKEN_REGISTRATION = 'pin_token_registration'
SESSION_STATUS_OK = 'ok'
SESSION_STATUS_NO_PRODUCT = 'no_product'

ACTION_NONE = 'NONE'
ACTION_AUTHORIZATION = 'AUTHORIZATION'
ACTION_PASSPORT_REGISTRATION = 'PASSPORT_REGISTRATION'
ACTION_BANK_REGISTRATION = 'BANK_REGISTRATION'
ACTION_APPLICATION_STATUS_CHECK = 'APPLICATION_STATUS_CHECK'
ACTION_SUPPORT = 'SUPPORT'
ACTION_AM_TOKEN_UPDATE = 'AM_TOKEN_UPDATE'
ACTION_APP_UPDATE = 'APP_UPDATE'
ACTION_PIN_TOKEN_CLEAR = 'PIN_TOKEN_CLEAR'
ACTION_PIN_TOKEN_REISSUE = 'PIN_TOKEN_REISSUE'
ACTION_PIN_TOKEN_RETRY = 'PIN_TOKEN_RETRY'
ACTION_OPEN_PRODUCT = 'OPEN_PRODUCT'

START_SESSION_REQUIRED_JSON = {
    'antifraud_info': {'device_id': 'e17d59f4f273e5fefcc6b8435909ff46'},
}

SUPPORT_URL = 'support_url'

JWT_PUBLIC_KEYS = [
    """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvn1cNgJw9KHL2jbRqag9ZYSpxnoKYV81ek
JtMb4ZCrLRc92kgDDqdU0A2TK1wN56/yE4E8qn+4rJiYmv8VoPIlSjJyAubBFkcXVlBX5AtJQ64+/K
R+Oh27LlarPq/xvSeSUUMInTdBbsFUmz7FGlx2LwpL0m8RywE0dOguBG1X4U/2c3eWivycpvWiCGGG
1BJa2keq2whIFoka+pFXxGsRMGzF5P26YdJ/I5pEr6662vRSQA3gdLHfBgcm2ZVUvnlTSR0Aw66vEu
h+1+KsBfIyS8YcWVjzSueMSpVBp+rZUjV58TjRRLSWnhYsago3f7doCin5bsWgRHpRroQRcW8QIDAQ
AB
-----END PUBLIC KEY-----""",
    """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAorq3zv5ZKNFRhrWb2H/k
rLCkammXGbWJ6Qc5E8rHZW0yqR9jyMWPZefDOGQv5TFxONUH/KRCz+BnkpB1Eehm
X9fv/a5iHcTq2eiqXIHZk1UxKN5arNfriHOgiifzEeMn2eRhjbrtlwFxT/LnLiXg
/EKsiKw6Hw/1FEF19sQ3hGh1CL4ufECEHIx3LzRO73PGTQda//O6HtQ/V8JZGxy9
WaREO1ETl8KfmnigIc7ZLk4hVdCoqZOc7pfDaVcPfLpl7Rb/C2U4c4d5xL208SM4
IAaWQIVExilGM+0pSq+CX/B5rhfoTP6iN/CCvl/j6FsxIkRzRVTEp/rUpq4zxun/
NQIDAQAB
-----END PUBLIC KEY-----""",
]

JWT_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAorq3zv5ZKNFRhrWb2H/krLCkammXGbWJ6Qc5E8rHZW0yqR9j
yMWPZefDOGQv5TFxONUH/KRCz+BnkpB1EehmX9fv/a5iHcTq2eiqXIHZk1UxKN5a
rNfriHOgiifzEeMn2eRhjbrtlwFxT/LnLiXg/EKsiKw6Hw/1FEF19sQ3hGh1CL4u
fECEHIx3LzRO73PGTQda//O6HtQ/V8JZGxy9WaREO1ETl8KfmnigIc7ZLk4hVdCo
qZOc7pfDaVcPfLpl7Rb/C2U4c4d5xL208SM4IAaWQIVExilGM+0pSq+CX/B5rhfo
TP6iN/CCvl/j6FsxIkRzRVTEp/rUpq4zxun/NQIDAQABAoIBAA0JfYFhYj5BatEq
ipZRRL5LFpkJ5ZejMi3PrNR3mfr3wSfIgoOKxF7LLxo8+JNZnzMI6i9k749c8J9O
4HozTsRd9fWye1zcMl6L494ubwJ9QEeAbO5NDCst7E41PiWQN9iekew7bh57eJsJ
oFjTow9CvjTi63MioaViSzOea745SXWsBQfsKV91bSpoUxP0OzdTgWAuDuomeqgS
+7cMKwgH4zEm71nR62Q9hCxzpoTjZZiwZTLKwb5HEfzeV3sqtzSL7HGxy/HAhBp1
+1+5LufPNGnh1JXEV8wJGTEBe2LJxZlg4UKsbl2eJgqoVceYCJ94amksa3Z7imzj
bTJVeR8CgYEAz3MOmsQfut68RvKAyjEcZZxbXlIxi3CqGIK5pW3B+Uf+3Smih8F/
f3tyIqShqs2KSXGr5jW5dAyGYfKdJl4MsbDnFlTT8jNX1uBjIwHT5k9dcV43ObTA
jMNEMNsfOCT3CBQINloSo9GQthEy3HvQt8lyNU5JhiJ2RTXLy//AeXcCgYEAyNBX
gvMXMN6AqMXt1Tpp2TDeRTI1+eowpVSNQj3s77JtWGQmBphmg09fZzubRsdzr+fy
cpQ6rEg/cYIFltdvQJHx4+ehQpEyvUuRmcZTmpwrDAN45wgZlpWlxAqBeRjo5WrX
RrRn3BKJEJSVeFlprJc0THdIpbiXQ2IRxNfHt7MCgYEAwvZHC3y2tVEPcT4He/6b
yYMg+4wTtBC2S0LQZoC4hCb9h6zRavSXdp/1rEk9BuEUzeFexIRJPp9mzDbPKnfJ
RlYTWBFw/3bxXqiTgxr8or6D+z+odztAmwoI1EGbHZDf+V+aODp+uicB8ZpISp6y
kYdpJl/lCYLp1DGyzo4VvhECgYBiribi3awewqg8x47ZAmxzY1VGcacemVuwUv1b
eOzO2UJsdkJNaWSu0DlUlHD4dhi+b1+vuHGgqZwrnjY66sDr3Qwd73xKJunlJZZ2
F4SL7IQm0in+dfeFDSK5VGRNatU/r6H8R7jl52HdePZ+fom0W1VC4jcb4LrMTQvo
TBUDiwKBgCaqW2ya3h4kzAzdkWyCpYirqG//5ckNR15yLpNXGmI4TL2Bjq0g8vvK
VxinJlXDdq6zypVoke6GSGOTBeBL7oDjQmmctG/htXx3R9aSLXjJ6yim/vMC0/hs
kbipoHh7GcC0bxZf35qKAq5Gms73TTlY/1ZEFAU/T5Fuyz+iRrsY
-----END RSA PRIVATE KEY-----"""


def get_headers(
        uid=None,
        buid=None,
        phone_id=None,
        session_uuid=None,
        verification_token=None,
        idempotency_token=None,
        pass_flags='',
        remote_ip='',
        app_name='sdk_example',
):
    headers = {
        'X-YaTaxi-Pass-Flags': pass_flags,
        'X-Remote-IP': remote_ip,
        'X-Request-Application': f'app_name={app_name},X-Platform=fcm',
        'X-Request-Language': 'ru',
    }
    if uid is not None:
        headers['X-Yandex-UID'] = uid
    if buid is not None:
        headers['X-Yandex-BUID'] = buid
    if phone_id is not None:
        headers['X-YaBank-PhoneID'] = phone_id
    if session_uuid is not None:
        headers['X-YaBank-SessionUUID'] = session_uuid
    if verification_token is not None:
        headers['X-YaBank-Verification-Token'] = verification_token
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers


def get_support_headers(token='allow', idempotency_token=None):
    headers = {'X-Bank-Token': token}
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers
