import datetime

import bson
import pytest

URL = '3.0/userplacenew'

USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
JSON = {'id': USER_ID}


def get_headers(
        uid=DEFAULT_UID,
        phone_id=DEFAULT_PHONE_ID,
        pass_flags='',
        bound_uids=None,
        language='ru',
        app_name='yango_android',
):
    headers = {'X-YaTaxi-UserId': USER_ID, 'X-YaTaxi-Pass-Flags': pass_flags}
    if language is not None:
        headers['X-Request-Language'] = language
    if phone_id is not None:
        headers['X-YaTaxi-PhoneId'] = phone_id
    if uid is not None:
        headers['X-Yandex-UID'] = uid
    if bound_uids is not None:
        headers['X-YaTaxi-Bound-Uids'] = bound_uids
    if app_name is not None:
        headers['X-Request-Application'] = 'app_name=' + app_name
    return headers


REQUESTS = {
    'simple': {'id': '01aaaaaaaaaaaaaaaaaaaaaaaaaaaa01'},
    'with_place_type': {
        'id': '01aaaaaaaaaaaaaaaaaaaaaaaaaaaa03',
        'place_type': 'home',
    },
    'with_different_place_type': {
        'id': '01aaaaaaaaaaaaaaaaaaaaaaaaaaaa04',
        'place_type': 'home',
    },
    'first_userplace_with_place_type': {
        'id': '01aaaaaaaaaaaaaaaaaaaaaaaaaaaa05',
        'place_type': 'work',
    },
}


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Userplaces: forbidden',
    }


@pytest.mark.config(USERPLACES_DISABLE_UPDATES=True)
async def test_userplacesnew_disable_updates(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Userplaces: update disabled',
    }


async def test_unauthorized(taxi_userplaces):
    """
    no header X-Yandex-UID
    """
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(uid=None),
    )
    assert response.status_code == 401, response.text
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_no_phone_id(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_userplacenew_no_app_name(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None, app_name=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.parametrize(
    'req_id,app_name,phone_id,expected_code,expected_id,expected_vers',
    [
        ('simple', 'yango_android', '02aaaaaaaaaaaaaaaaaaaa01', 200, None, 0),
        (
            'with_place_type',
            'yango_android',
            '02aaaaaaaaaaaaaaaaaaaa01',
            200,
            'home',
            123,
        ),
        (
            'with_place_type',
            'uber_android',
            '02aaaaaaaaaaaaaaaaaaaa01',
            200,
            'home',
            0,
        ),
        (
            'with_different_place_type',
            'yango_android',
            '02aaaaaaaaaaaaaaaaaaaa02',
            200,
            'home',
            0,
        ),
        (
            'first_userplace_with_place_type',
            'yango_android',
            '02aaaaaaaaaaaaaaaaaaaa01',
            200,
            'work',
            0,
        ),
    ],
    ids=[
        'simple new userplace',
        'userplace with place_type',
        'first userplace with place_type',
        'userplace with different place_type',
        'first userplace with place_type',
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
async def test_base(
        taxi_userplaces,
        req_id,
        app_name,
        phone_id,
        expected_code,
        expected_id,
        expected_vers,
):
    response = await taxi_userplaces.post(
        URL,
        json=REQUESTS[req_id],
        headers=get_headers(phone_id=phone_id, app_name=app_name),
    )

    assert response.status_code == expected_code

    data = response.json()
    if expected_id is None:
        expected_id = data['place']['id']

    assert data == {'place': {'id': expected_id, 'version': expected_vers}}


@pytest.mark.parametrize(
    'req_id, place_type, ypa_fail, expect_fail',
    [
        pytest.param(
            'simple',
            None,
            False,
            False,
            marks=pytest.mark.config(
                USERPLACES_WRITE_YA_PERS_ADDRESS={
                    'enabled': True,
                    'fail_otherwise': True,
                },
            ),
        ),
        pytest.param(
            'with_place_type',
            'home',
            False,
            False,
            marks=pytest.mark.config(
                USERPLACES_WRITE_YA_PERS_ADDRESS={
                    'enabled': True,
                    'fail_otherwise': True,
                },
            ),
        ),
        pytest.param(
            'with_place_type',
            'home',
            True,
            True,
            marks=pytest.mark.config(
                USERPLACES_WRITE_YA_PERS_ADDRESS={
                    'enabled': True,
                    'fail_otherwise': True,
                },
            ),
        ),
        pytest.param(
            'with_place_type',
            'home',
            True,
            False,
            marks=pytest.mark.config(
                USERPLACES_WRITE_YA_PERS_ADDRESS={
                    'enabled': True,
                    'fail_otherwise': False,
                },
            ),
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
async def test_ypa_create(
        taxi_userplaces, req_id, mockserver, place_type, ypa_fail, expect_fail,
):
    @mockserver.json_handler('/ya-pers-address/address/create')
    def _mock_ypa_create(request):
        assert request.query['draft'] == 'true'
        assert request.json['draft'] is True
        assert request.query['is_portal_uid'] == 'false'
        assert request.json['is_portal_uid'] is False
        assert request.query['user_id'] == DEFAULT_UID
        assert request.json['user_id'] == DEFAULT_UID
        assert request.query['user_type'] == 'uid'
        assert request.json['user_type'] == 'uid'
        assert request.json['id'] == request.query['id']
        assert request.query.get('place_type') == place_type
        assert request.json.get('place_type') == place_type
        if place_type:
            assert request.query['id'] == place_type
        if ypa_fail:
            return mockserver.make_response(status=500)
        return {'status': 'ok', 'id': 'some_id', 'version': 0}

    response = await taxi_userplaces.post(
        URL,
        json=REQUESTS[req_id],
        headers=get_headers(
            phone_id='02aaaaaaaaaaaaaaaaaaaa01', app_name='yataxi',
        ),
    )

    assert _mock_ypa_create.has_calls
    expected_code = 500 if expect_fail else 200
    assert response.status_code == expected_code


@pytest.mark.parametrize('scenario', ['portal_uid', 'phonish_uid'])
@pytest.mark.now('2016-12-15T11:30:00+0300')
async def test_portal_auth(taxi_userplaces, mongodb, scenario):

    pass_flags = ''
    uid = '50000000001'

    if scenario == 'portal_uid':
        pass_flags = 'portal'
    elif scenario == 'phonish_uid':
        pass_flags = 'phonish'

    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(pass_flags=pass_flags, uid=uid),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    userplace_id = data['place']['id']
    assert data == {'place': {'id': userplace_id, 'version': 0}}

    # Check mongo
    sample = {
        '_id': userplace_id,
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'drafted': datetime.datetime(2016, 12, 15, 8, 30),
        'updated': datetime.datetime(2016, 12, 15, 8, 30),
        'touched': datetime.datetime(2016, 12, 15, 8, 30),
        'version': 0,
        'format_version': 4,
        'yandex_uid': uid,
    }
    if scenario == 'phonish_uid':
        sample['phone_id'] = bson.ObjectId(DEFAULT_PHONE_ID)
        sample['brand_name'] = 'yango'

    doc = mongodb.user_places.find_one({'_id': userplace_id})
    assert doc == sample


@pytest.mark.now('2016-12-15T11:30:00+0300')
async def test_portal_auth_place_type(taxi_userplaces, mongodb):
    uid = '50000000001'
    phone_id = '02aaaaaaaaaaaaaaaaaaaa02'
    # Query
    response = await taxi_userplaces.post(
        URL,
        json=REQUESTS['with_place_type'],
        headers=get_headers(pass_flags='portal', uid=uid, phone_id=phone_id),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    userplace_id = data['place']['id']
    assert data == {'place': {'id': userplace_id, 'version': 0}}

    # Check mongo
    sample = {
        'created': datetime.datetime(2016, 12, 15, 8, 30),
        'drafted': datetime.datetime(2016, 12, 15, 8, 30),
        'updated': datetime.datetime(2016, 12, 15, 8, 30),
        'touched': datetime.datetime(2016, 12, 15, 8, 30),
        'version': 0,
        'place_type': 'home',
        'format_version': 4,
        'yandex_uid': uid,
        'phone_id': bson.ObjectId(phone_id),
        'brand_name': 'yango',
        'removed': None,
    }
    doc = mongodb.user_places.find_one(
        {'phone_id': bson.ObjectId(phone_id), 'place_type': 'home'},
    )
    doc.pop('_id')
    assert doc == sample
