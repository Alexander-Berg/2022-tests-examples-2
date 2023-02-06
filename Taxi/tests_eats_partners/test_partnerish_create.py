from lxml import etree
import pytest

VALID_CAPTCHA_KEY = 'уу32452345234'
VALID_CAPTCHA_TYPE = 'std'
VALID_USER_INPUT = '55548'
INVALID_USER_INPUT = '55549'

VALID_EMAIL = 'dev@test.in'
ALREADY_EXISTED_IN_VENDOR_EMAIL = 'dev_vendor@test.in'
ALREADY_EXISTED_IN_PARTNERS_EMAIL = 'partner1@partner.com'
ALREADY_EXISTED_IN_PARTNERS_EMAIL_UPPER = 'PARTNER1@PARTNER.COM'
ALREADY_EXISTED_IN_PARTNERISH_EMAIL = 'email1@test.ya'
ALREADY_EXISTED_IN_PARTNERISH_EMAIL_UPPER = 'EMAIL1@TEST.YA'
INVALID_EMAIL = 'inv_dev@test.in'

INVALID_VENDOR_JSON = {
    'id': 12,
    'name': 'artur',
    'email': 'artyr@net.net',
    'restaurants': [1],
    'isFastFood': False,
    'timezone': 'asfgsdg',
    'roles': [],
}


@pytest.fixture(autouse=True)
def _captcha_fixture(mockserver):
    @mockserver.handler('/captcha/check')
    def _mock_check(request):
        assert request.args['key'] == VALID_CAPTCHA_KEY
        assert request.args['type'] == VALID_CAPTCHA_TYPE

        root = etree.Element('image_check')

        if request.args['rep'] == VALID_USER_INPUT:
            root.text = 'ok'
        else:
            root.text = 'failed'

        return mockserver.make_response(
            response=etree.tostring(root, xml_declaration=True),
            status=200,
            content_type='application/xml',
        )


@pytest.fixture(autouse=True)
def mock_eats_vendor(mockserver):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users/search')
    def _mock(request):
        assert request.args['limit'] == '1'
        assert request.args['offset'] == '0'
        if request.json['email'] in [
                VALID_EMAIL,
                ALREADY_EXISTED_IN_PARTNERS_EMAIL,
                ALREADY_EXISTED_IN_PARTNERISH_EMAIL,
        ]:
            return {'isSuccess': True, 'payload': [], 'meta': {'count': 0}}

        if request.json['email'] == ALREADY_EXISTED_IN_VENDOR_EMAIL:
            return {
                'isSuccess': True,
                'payload': [INVALID_VENDOR_JSON],
                'meta': {'count': 1},
            }

        return {'isSuccess': False, 'payload': [], 'meta': {'count': 0}}


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }


@pytest.mark.config(
    EATS_PARTNERISH_SETTINGS={
        'registartion_url': 'test.ru',
        'sender_email': 'no-reply@yango.yandex.com',
        'registration_text': (
            'Пожалуйста завершите регистрацию заполнив информацию по ссылке,'
        ),
        'check_email_in_vendor': True,
        'enable_paths': True,
    },
)
@pytest.mark.parametrize(
    'email, captcha_user_input, consent_to_data_processing, status_code',
    [
        (VALID_EMAIL, VALID_USER_INPUT, True, 200),
        (VALID_EMAIL, VALID_USER_INPUT, False, 400),
        (VALID_EMAIL, INVALID_USER_INPUT, True, 400),
        (ALREADY_EXISTED_IN_VENDOR_EMAIL, INVALID_USER_INPUT, True, 400),
        (ALREADY_EXISTED_IN_PARTNERS_EMAIL, INVALID_USER_INPUT, True, 400),
        (
            ALREADY_EXISTED_IN_PARTNERS_EMAIL_UPPER,
            INVALID_USER_INPUT,
            True,
            400,
        ),
        (ALREADY_EXISTED_IN_PARTNERISH_EMAIL, INVALID_USER_INPUT, True, 400),
        (
            ALREADY_EXISTED_IN_PARTNERISH_EMAIL_UPPER,
            INVALID_USER_INPUT,
            True,
            400,
        ),
        (INVALID_EMAIL, INVALID_USER_INPUT, True, 400),
    ],
)
async def test_partnerish_create(
        taxi_eats_partners,
        email,
        captcha_user_input,
        consent_to_data_processing,
        status_code,
        mock_sender_partnerish_register,
        mock_communications_sender,
):

    request_json = {
        'partnerish_reg_info': {
            'email': email,
            'name': 'Dev',
            'rest_name': 'dev rest',
            'city': 'testing',
            'address': 'test street 8',
            'phone_number': '+78889995544',
            'consent_to_data_processing': consent_to_data_processing,
        },
        'captcha_info': {
            'captcha_key': VALID_CAPTCHA_KEY,
            'captcha_type': VALID_CAPTCHA_TYPE,
            'user_input': captcha_user_input,
        },
    }

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/login/partnerish/create',
        json=request_json,
    )

    assert response.status_code == status_code


@pytest.mark.config(
    EATS_PARTNERISH_SETTINGS={
        'registartion_url': 'test.ru',
        'sender_email': 'no-reply@yango.yandex.com',
        'registration_text': (
            'Пожалуйста завершите регистрацию заполнив информацию по ссылке,'
        ),
        'check_email_in_vendor': True,
        'enable_paths': False,
    },
)
async def test_partnerish_create_off_path(taxi_eats_partners):
    request_json = {
        'partnerish_reg_info': {
            'email': 'test@test.com',
            'name': 'Dev',
            'rest_name': 'dev rest',
            'city': 'testing',
            'address': 'test street 8',
            'phone_number': '+78889995544',
            'consent_to_data_processing': True,
        },
        'captcha_info': {
            'captcha_key': VALID_CAPTCHA_KEY,
            'captcha_type': VALID_CAPTCHA_TYPE,
            'user_input': VALID_USER_INPUT,
        },
    }

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/login/partnerish/create',
        json=request_json,
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Path not support'}
