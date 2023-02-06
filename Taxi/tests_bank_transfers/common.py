import jwt

TEST_YANDEX_UID = 'a5ba5b82-1534-42bc-8e3c-b9c1a1000d2a'
TEST_BANK_UID = 'a41a2ef0-2140-4037-85b5-ebaa12e34224'
TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID = (
    'a41a2ef0-2140-4037-85b5-ebaa12e34225'
)
TEST_ABSENT_IN_USERINFO_BUID = 'a41a2ef0-2140-4037-85b5-ebaa12e34226'

TEST_YANDEX_BANK_FPS_ON_BUID = 'a41a2ef0-2140-4037-85b5-ebaa12e34227'
TEST_SESSION_UUID = 'f7c31972-25d4-4977-905f-42ecf4a357f5'
TEST_NOT_COMMON_SESSION_UUID = 'f7c31972-25d4-4977-905f-42ecf4a357f6'
TEST_PHONE_ID = 'db901ba3-12f1-4e20-b993-38bdb6b8620b'
TEST_LOCALE = 'ru'
TEST_AGREEMENT_ID = '8bc0840e-8c97-453d-986f-d117bef16774'
TEST_USER_TICKET = 'user_ticket'

AGREEMENT_BALANCE = 1000
MAX_TXN_SUM = 1370
MAX_MONTHLY_TURNOVER = 10000.01
CREDIT_LIMITS = 500, 152.45, 327.5
DEBIT_LIMITS = [MAX_TXN_SUM, MAX_MONTHLY_TURNOVER, 1500]
DEBIT_MAX_LIMIT = 2000
DEBIT_MIN_LIMIT = 10
THRESHOLD_LIMIT = 15000
DEFAULT_CURRENCY = 'RUB'
DEFAULT_OFFER_AMOUNT = 100.05
DEFAULT_FEE = 0

RECEIVER_PHONE_00 = '+79000000000'
RECEIVER_PHONE_01 = '+79000000001'
RECEIVER_PHONE_1 = '+79123456789'
RECEIVER_PHONE_1_F = '+7 912 345-67-89'
RECEIVER_NAME_1 = 'Иван Иванович А'
SHORT_RECEIVER_NAME_1 = 'Иван А'
RECEIVER_PHONE_2 = '+79123456780'
RECEIVER_NAME_2 = 'Иван Иванович Б'
SHORT_RECEIVER_NAME_2 = 'Иван Б'
RECEIVER_PHONE_3 = '+79123456781'
RECEIVER_NAME_3 = 'Иван Иванович В'
SHORT_RECEIVER_NAME_3 = 'Иван В'
RECEIVER_PHONE_YANDEX = '+79123456782'
RECEIVER_PHONE_SBER = '+79123456783'

PREFERRED = 'Получатель предпочитает этот банк'
PREFERRED_EN = 'Receiver prefers this bank'

TINKOFF = '100000000004'
ROSDORBANK = '110000000084'
YANDEX_BANK = '100000000150'

CHECK_REQUEST_ID = '6e387a2f-2884-44dd-b2b7-d3a829079d73'
BANKS_WITH_M2M = [{'bank_id': '100000000190', 'title': 'РОСКОСМОСБАНК'}]

DEFAULT_IDEMPOTENCY_TOKEN = '7ed58d18-63aa-4838-9ec7-8dfbf9e9d6bb'
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

GOOD_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    JWT_PRIVATE_KEY,
    algorithm='PS512',
)

GOOD_OLD_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2000-06-13T14:00:00Z',
    },
    JWT_PRIVATE_KEY,
    algorithm='PS512',
)


def get_receiver_name(phone=RECEIVER_PHONE_1):
    if phone == RECEIVER_PHONE_2:
        return RECEIVER_NAME_2
    if phone == RECEIVER_PHONE_3:
        return RECEIVER_NAME_3
    return RECEIVER_NAME_1


def get_receiver_short_name(phone=RECEIVER_PHONE_1):
    if phone == RECEIVER_PHONE_2:
        return SHORT_RECEIVER_NAME_2
    if phone == RECEIVER_PHONE_3:
        return SHORT_RECEIVER_NAME_3
    return SHORT_RECEIVER_NAME_1


def get_yandex_bank_description(description=None):
    yandex_bank_description = {
        'bank_id': '100000000150',
        'title': 'Яндекс Банк',
        'image': (
            'https://avatars.mdst.yandex.net/get-fintech/1401668/ya-bank.png'
        ),
    }
    if description:
        yandex_bank_description['description'] = description
    return yandex_bank_description


def build_headers(
        buid=TEST_BANK_UID,
        session_uuid=TEST_SESSION_UUID,
        yuid=TEST_YANDEX_UID,
        phone_id=TEST_PHONE_ID,
        language=TEST_LOCALE,
        user_ticket=TEST_USER_TICKET,
        idempotency_token=None,
        verification_token=None,
):
    headers = {
        'X-Yandex-BUID': buid,
        'X-YaBank-SessionUUID': session_uuid,
        'X-Yandex-UID': yuid,
        'X-YaBank-PhoneID': phone_id,
        'X-Request-Language': language,
        'X-Ya-User-Ticket': user_ticket,
    }
    if idempotency_token:
        headers['X-Idempotency-Token'] = idempotency_token
    if verification_token:
        headers['X-YaBank-Verification-Token'] = verification_token
    return headers


def get_fps_params(boolean_value=True, locale='ru'):
    if locale == 'en':
        title = 'Receiving transfers by phone number'
        description = (
            'You will be able to transfer money'
            ' through the Faster Payments System'
        )
    else:
        title = 'Получение переводов по номеру телефона'
        description = (
            'Вам смогут переводить деньги через Систему быстрых платежей'
        )
    return {
        'key': 'faster_payments_system',
        'title': title,
        'description': description,
        'enabled': True,
        'property': {'type': 'SWITCH', 'boolean_value': boolean_value},
    }


def get_fps_priority_bank_params(
        boolean_value=True, locale='ru', enabled=False,
):
    if locale == 'en':
        title = 'Priority Bank'
        if boolean_value:
            description = (
                'Yandex has been selected as a priority for incoming'
                ' transfers through the Faster Payments System'
            )
        else:
            description = (
                'When making transfers through the Fast Payment System,'
                ' people will see that you prefer Yandex Bank'
            )
    else:
        title = 'Приоритетный банк'
        if boolean_value:
            description = (
                'Яндекс выбран приоритетным для входящих'
                ' переводов через Систему быстрых платежей'
            )
        else:
            description = (
                'При переводах через Систему быстрых платежей люди увидят,'
                ' что вы предпочитаете банк Яндекса'
            )
    return {
        'key': 'fps_priority_bank',
        'title': title,
        'description': description,
        'enabled': enabled,
        'property': {'type': 'SWITCH', 'boolean_value': boolean_value},
    }


def get_settings(boolean_value_fps=True, boolean_value_pb=False, locale='ru'):
    settings = []
    settings.append(get_fps_params(boolean_value_fps, locale))
    settings.append(
        get_fps_priority_bank_params(
            boolean_value_pb, locale, enabled=boolean_value_fps,
        ),
    )
    return {'settings': settings}


def get_default_response_header(locale='ru'):
    title = (
        'Система быстрых платежей'
        if locale == 'ru'
        else 'Faster payments system'
    )
    return {
        'title': title,
        'image': 'https://avatars.mdst.yandex.net/get-fintech/1401668/sbp.svg',
    }


def build_simplified_confirm_params(
        agreement_id=TEST_AGREEMENT_ID,
        bank_id=TINKOFF,
        amount=str(DEFAULT_OFFER_AMOUNT),
        currency='RUB',
):
    return {
        'agreement_id': agreement_id,
        'bank_id': bank_id,
        'money': {'amount': amount, 'currency': currency},
    }
