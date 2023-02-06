import base64
import hashlib
import hmac
import json

import pytest

SECDIST_SALT = b'abcdefg12312jasd'


@pytest.fixture(name='mock_personal_phones_factory')
def _mock_personal_phones_factory(mockserver):
    def impl(phone=None, personal_id=None):
        @mockserver.json_handler('/personal/v1/phones/store')
        def mock_impl(request):
            data = request.json

            assert 'value' in data
            assert data['validate']

            if phone is not None:
                assert data['value'] == phone

            pers_id = (
                'personal_phone_id' if personal_id is None else personal_id
            )

            return {'id': pers_id, 'value': data['value']}

        return mock_impl

    return impl


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_phones_present(
        taxi_user_api, mongodb, mock_personal_phones_factory,
):
    phone = '+79991234567'
    type_ = 'yandex'
    personal_id = '557f191e810c19729de860ea'

    mock_personal = mock_personal_phones_factory(
        phone=phone, personal_id=personal_id,
    )

    count_before_request = mongodb.user_phones.find().count()

    response = await _get_user_phone(
        taxi_user_api, phone=phone, phone_type=type_,
    )

    assert response.status_code == 200
    assert mongodb.user_phones.find().count() == count_before_request

    response = response.json()

    assert response == {
        'id': '539e99e1e7e5b1f5397adc5d',
        'phone': phone,
        'type': type_,
        'phone_hash': '123',
        'phone_salt': '132',
        'personal_phone_id': personal_id,
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'stat': {
            'total': 0,
            'fake': 0,
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0,
        },
        'is_loyal': False,
        'is_yandex_staff': False,
        'is_taxi_staff': False,
    }

    assert mock_personal.times_called == 0


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_phones_creation(
        taxi_user_api, mongodb, mock_personal_phones_factory,
):
    mock_personal_phones = mock_personal_phones_factory('+79997654321')

    phone = '+79997654321'
    type_ = 'yandex'
    phone_doc_query = _phone_doc_query(phone, type_)

    assert mongodb.user_phones.find_one(phone_doc_query) is None
    count_before_request = mongodb.user_phones.find().count()

    response = await _get_user_phone(
        taxi_user_api, phone=phone, phone_type=type_,
    )

    assert response.status_code == 200
    assert mongodb.user_phones.find().count() == (count_before_request + 1)

    response = response.json()
    response.pop('id')
    response.pop('updated')
    response.pop('phone_hash')
    response.pop('phone_salt')

    reference_response = {
        'phone': '+79997654321',
        'type': 'yandex',
        'personal_phone_id': 'personal_phone_id',
        'created': '2019-02-01T14:00:00+0000',
        'is_new_number': True,
        'stat': {
            'total': 0,
            'fake': 0,
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0,
        },
        'is_loyal': False,
        'is_yandex_staff': False,
        'is_taxi_staff': False,
    }

    assert response == reference_response

    phone_doc = mongodb.user_phones.find_one(phone_doc_query)
    _validate_hash_in_doc(phone_doc)
    assert mock_personal_phones.times_called == 1


@pytest.mark.parametrize(
    'phone, preexists, reference_response',
    [
        (
            '+71112223344',
            False,
            {
                'phone': '+71112223344',
                'type': 'yandex',
                'created': '2019-02-01T14:00:00+0000',
                'personal_phone_id': 'personal_id',
                'is_new_number': True,
                'stat': {
                    'total': 0,
                    'fake': 0,
                    'big_first_discounts': 0,
                    'complete': 0,
                    'complete_card': 0,
                    'complete_apple': 0,
                    'complete_google': 0,
                },
                'is_loyal': False,
                'is_yandex_staff': False,
                'is_taxi_staff': False,
            },
        ),
        (
            '+79991234567',
            True,
            {
                'id': '539e99e1e7e5b1f5397adc5d',
                'phone': '+79991234567',
                'type': 'yandex',
                'phone_hash': '123',
                'phone_salt': '132',
                'personal_phone_id': '557f191e810c19729de860ea',
                'created': '2019-02-01T13:00:00+0000',
                'updated': '2019-02-01T13:00:00+0000',
                'stat': {
                    'total': 0,
                    'fake': 0,
                    'big_first_discounts': 0,
                    'complete': 0,
                    'complete_card': 0,
                    'complete_apple': 0,
                    'complete_google': 0,
                },
                'is_loyal': False,
                'is_yandex_staff': False,
                'is_taxi_staff': False,
            },
        ),
    ],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_user_phones_creation_by_personal_id(
        taxi_user_api,
        mockserver,
        mongodb,
        phone,
        preexists,
        reference_response,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def mock_impl(request):
        data = request.json
        assert data == {'id': 'personal_id', 'primary_replica': False}
        return {'id': 'personal_id', 'value': phone}

    before = mongodb.user_phones.find_one({'phone': phone, 'type': 'yandex'})

    if preexists:
        assert before is not None

    response = await _get_user_phone(
        taxi_user_api, personal_id='personal_id', phone_type='yandex',
    )
    assert response.status_code == 200
    assert mock_impl.times_called == 1
    response = response.json()

    if not preexists:
        response.pop('id')
        response.pop('updated')
        response.pop('phone_hash')
        response.pop('phone_salt')

    assert response == reference_response

    after = mongodb.user_phones.find_one({'phone': phone, 'type': 'yandex'})

    if not preexists:
        assert after is not None


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_creation_by_personal_id_personal_unavailable(
        taxi_user_api, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def mock_personal(request):
        return mockserver.make_response(status=500)

    response = await _get_user_phone(
        taxi_user_api, personal_id='personal_id', phone_type='yandex',
    )
    assert mock_personal.times_called == 1
    assert response.status_code == 500


@pytest.mark.config(USER_API_PERSONAL_PHONE_ID_REQUIRED=True)
async def test_creation_by_personal_id_personal_not_found(
        taxi_user_api, mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def mock_personal(request):
        return mockserver.make_response(
            status=404,
            response=json.dumps(
                {'code': '404', 'message': 'Doc not found in mongo'},
            ),
        )

    response = await _get_user_phone(
        taxi_user_api, personal_id='personal_id', phone_type='yandex',
    )
    assert mock_personal.times_called == 1
    assert response.status_code == 400


async def test_user_phones_personal_unavailable(taxi_user_api, mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones(request):
        return mockserver.make_response(status=500)

    response = await _get_user_phone(
        taxi_user_api, phone='+79997654321', phone_type='yandex',
    )
    assert response.status_code == 200
    assert 'personal_phone_id' not in response.json()


async def test_user_phones_personal_bad_response(taxi_user_api, mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones(request):
        return {'id': 1, 'foo': 'bar'}

    response = await _get_user_phone(
        taxi_user_api, phone='+79997654321', phone_type='yandex',
    )
    assert response.status_code == 200
    assert 'personal_phone_id' not in response.json()


@pytest.mark.parametrize(
    ['type_', 'is_valid'],
    [
        ('yandex', True),
        ('uber', True),
        ('partner', True),
        ('foobarbaz', False),
    ],
)
async def test_user_phones_types(taxi_user_api, mockserver, type_, is_valid):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones(request):
        return mockserver.make_response(status=500)

    response = await _get_user_phone(
        taxi_user_api, phone='+79991112233', phone_type=type_,
    )

    target_status = 200 if is_valid else 400
    assert response.status_code == target_status


@pytest.mark.parametrize(
    ['phone', 'strictness', 'code'],
    [('nan', None, 400), ('nan', True, 400), ('nan', False, 200)],
)
async def test_user_phones_bad_number(
        taxi_user_api, mockserver, phone, strictness, code,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones(request):
        return mockserver.make_response(status=500)

    response = await _get_user_phone(
        taxi_user_api, phone=phone, phone_type='yandex', strictness=strictness,
    )
    assert response.status_code == code

    if code == 400:
        assert response.json() == {
            'code': '400',
            'message': 'Invalid phone number',
        }


@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_user_phones_dummy_type(taxi_user_api, mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_personal_phones(request):
        return mockserver.make_response(status=500)

    phone = '+79991234568'
    type_ = 'yandex'
    response = await _get_user_phone(
        taxi_user_api, phone=phone, phone_type=type_,
    )

    assert response.status_code == 200
    response = response.json()

    assert response == {
        'id': '539e99e1e7e5b1f5398adc5a',
        'phone': phone,
        'type': type_,
        'phone_hash': '123',
        'phone_salt': '132',
        'personal_phone_id': '507f191e810c19729de860ea',
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'stat': {
            'total': 0,
            'fake': 0,
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0,
        },
        'is_loyal': False,
        'is_yandex_staff': False,
        'is_taxi_staff': False,
    }


@pytest.mark.parametrize(
    'req, message',
    [
        (
            {'phone': 123, 'type': 'yandex'},
            (
                'Field \'phone\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone': '+71112223344', 'type': 123},
            (
                'Field \'type\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'personal_phone_id': 123, 'type': 'yandex'},
            (
                'Field \'personal_phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {
                'phone': '+71112223344',
                'personal_phone_id': '12345',
                'type': 'yandex',
            },
            (
                'Exactly one of phone, personal_phone_id should be specified. '
                'Got both.'
            ),
        ),
        (
            {'type': 'yandex'},
            (
                'Exactly one of phone, personal_phone_id should be specified. '
                'Got none.'
            ),
        ),
    ],
    ids=[
        'phone is int',
        'personal_phone_id is int',
        'type is int',
        'both identifiers',
        'no identifiers',
    ],
)
async def test_user_phones_bad_request(taxi_user_api, req, message):
    response = await taxi_user_api.post('user_phones', json=req)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


def _make_phone_hash(service_salt, phone_salt, phone):
    return hmac.new(
        phone_salt + service_salt, phone.encode(), hashlib.sha256,
    ).hexdigest()


def _is_hash_valid(phone_hash, salt, phone):
    return _make_phone_hash(SECDIST_SALT, salt, phone) == phone_hash


async def _get_user_phone(
        api,
        phone=None,
        personal_id=None,
        phone_type='yandex',
        strictness=True,
):
    request = {'type': phone_type}

    if phone:
        request['phone'] = phone
    elif personal_id:
        request['personal_phone_id'] = personal_id
    else:
        raise ValueError

    if strictness is not None:
        request['validate_phone'] = strictness

    return await api.post('user_phones', json=request)


def _validate_hash_in_doc(phone_doc):
    assert _is_hash_valid(
        phone_doc['phone_hash'],
        base64.b64decode(phone_doc['phone_salt']),
        phone_doc['phone'],
    )


def _phone_doc_query(phone, type_):
    return {'phone': phone, 'type': type_}
