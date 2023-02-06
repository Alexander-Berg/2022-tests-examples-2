import typing

import dateutil.parser
import pytest

from testsuite.utils import ordered_object

URL = 'v1/takeout'
URL_STATUS = 'v1/takeout/status/'
URL_DELETE = 'v1/takeout/delete/'
USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
DEFAULT_USER = {
    'id': USER_ID,
    'phone_id': DEFAULT_PHONE_ID,
    'yandex_uid': DEFAULT_UID,
}


def get_request(
        uid: typing.Optional[str] = DEFAULT_UID,
        users: typing.Optional[list] = None,
):
    request: typing.Dict[str, typing.Any] = {}
    if uid is not None:
        request['yandex_uid'] = uid
    if users is not None:
        request['users'] = users
    return request


def get_sample_response(name, load_json):
    return load_json('sample_responses.json')[name]


def check_string_datetime(iso_string):
    isinstance(iso_string, str)
    assert dateutil.parser.parse(iso_string)


async def test_takeout_get_not_allowed(taxi_userplaces):
    response = await taxi_userplaces.get(URL, json=get_request(users=[]))
    assert response.status_code == 405, response.text


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_takeout_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request(users=[]))
    assert response.status_code == 500, response.text
    assert response.headers['Retry-After'] == '120'
    assert response.json() == {'code': '500', 'message': 'Service disabled'}


async def test_takeout_no_yandex_uid(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(uid=None, users=[]),
    )
    assert response.status_code == 400, response.text


async def test_takeout_no_users(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request())
    assert response.status_code == 400, response.text


async def test_takeout_no_data(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(uid='600000000', users=[]),
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'no_data'


async def test_takeout_single(taxi_userplaces, load_json):
    response = await taxi_userplaces.post(
        URL, json=get_request(users=[DEFAULT_USER]),
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'ok'
    places = response_data['data']['places']
    assert len(places) == 1
    assert places[0] == get_sample_response('single', load_json)


@pytest.mark.now('2019-07-01T10:00:00')
async def test_takeout_multiple(taxi_userplaces, load_json):
    users = [
        DEFAULT_USER,
        {
            'id': USER_ID,
            'yandex_uid': '500000000',
            'phone_id': '02aaaaaaaaaaaaaaaaaaaa03',
        },
    ]
    response = await taxi_userplaces.post(URL, json=get_request(users=users))
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'ok'
    places = response_data['data']['places']
    assert len(places) == 4
    ordered_object.assert_eq(
        places, get_sample_response('multiple', load_json), [''],
    )


@pytest.mark.now('2019-09-01T10:00:00')
async def test_takeout_multiple_phone_id_timeout(taxi_userplaces, load_json):
    users = [
        DEFAULT_USER,
        {
            'id': USER_ID,
            'yandex_uid': '500000000',
            'phone_id': '02aaaaaaaaaaaaaaaaaaaa03',
        },
    ]
    response = await taxi_userplaces.post(URL, json=get_request(users=users))
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'ok'
    places = response_data['data']['places']
    assert len(places) == 2
    ordered_object.assert_eq(
        places, get_sample_response('phone_id_timeout', load_json), [''],
    )


@pytest.mark.now('2019-07-01T10:00:00')
async def test_takeout_status(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL_STATUS,
        json={
            'yandex_uids': [
                {'uid': '400000000', 'is_portal': False},
                {'uid': '500000000', 'is_portal': True},
            ],
            'phone_ids': [
                '02aaaaaaaaaaaaaaaaaaaa03',
                '02aaaaaaaaaaaaaaaaaaaa01',
            ],
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {'data_state': 'ready_to_delete'}


@pytest.mark.now('2019-07-01T10:00:00')
async def test_takeout_status_empty(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL_STATUS,
        json={
            'yandex_uids': [{'uid': '8888', 'is_portal': True}],
            'phone_ids': ['bbbbbbbbbbbbbbbbbbbbbbbb'],
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {'data_state': 'empty'}


@pytest.mark.now('2019-07-01T10:00:00')
async def test_takeout_delete(taxi_userplaces, mockserver, mongodb):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        return {
            'items': [
                {
                    'address_id': 'home',
                    'title': 'datasync',
                    'longitude': 37.619046,
                    'latitude': 55.767843,
                    'created': '2000-02-07T11:22:33.44+00:00',
                    'modified': '2001-07-08T11:22:33.00+00:00',
                    'address_line': 'Россия, Москва, Петровский бульвар, 23',
                    'address_line_short': 'Петровский бульвар, 23',
                    'entrance_number': '45',
                },
            ],
        }

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync_delete(request):
        return {}

    response = await taxi_userplaces.post(
        URL_DELETE,
        json={
            'request_id': '1',
            'yandex_uids': [{'uid': '400000000', 'is_portal': True}],
            'phone_ids': ['02aaaaaaaaaaaaaaaaaaaa03'],
        },
    )
    assert response.status_code == 200

    db_result = sorted(
        [doc['_id'] for doc in mongodb.user_places.find({}, {'_id': 1})],
    )
    assert db_result == [
        '00000004-AAAA-AAAA-AAAA-000000000009',
        '00000004-AAAA-AAAA-AAAA-00000000008',
    ]
    assert _mock_datasync.has_calls
    assert _mock_datasync_delete.has_calls
