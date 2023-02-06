import copy
import typing

import bson
import dateutil.parser
import pytest

from testsuite.utils import ordered_object

URL = 'userplaces/list'
USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
DEFAULT_PASS_FLAGS = {'is_phonish': True, 'is_portal': False}
DEFAULT_PLACE_ID = '00000004-AAAA-AAAA-AAAA-000000000001'


def get_request(
        uid: typing.Optional[str] = DEFAULT_UID,
        phone_id: typing.Optional[str] = DEFAULT_PHONE_ID,
        pass_flags: typing.Optional[dict] = None,
        bound_uids: typing.Optional[list] = None,
        language: typing.Optional[str] = 'ru',
        app_name: typing.Optional[str] = 'yango_android',
        user_id: typing.Optional[str] = None,
):
    request: typing.Dict[str, typing.Any] = {
        'user_identity': {
            'user_id': user_id if user_id is not None else USER_ID,
        },
    }
    if uid is not None:
        request['user_identity']['yandex_uid'] = uid
    if phone_id is not None:
        request['user_identity']['phone_id'] = phone_id
    if bound_uids is not None:
        request['user_identity']['bound_yandex_uids'] = bound_uids
    if pass_flags is None:
        pass_flags = DEFAULT_PASS_FLAGS
    request['user_identity']['flags'] = pass_flags
    if language is not None:
        request['lang'] = language
    if app_name is not None:
        request['app_name'] = app_name
    return request


def get_sample_response(name, load_json):
    return load_json('sample_responses.json')[name]


def check_string_datetime(iso_string):
    isinstance(iso_string, str)
    assert dateutil.parser.parse(iso_string)


def validate_response_json(response):
    assert response
    assert len(response) == 1
    places = response['places']
    assert isinstance(places, list)
    for place in places:
        assert isinstance(place, dict)
        for k in place:
            assert k in (
                'id',
                'source',
                'version',
                'created',
                'updated',
                'name',
                'place_type',
                'full_text',
                'short_text',
                'description',
                'porchnumber',
                'floor_number',
                'doorphone_number',
                'quarters_number',
                'comment',
                'comment_courier',
                'point',
                'uri',
                'type',
            )
        assert isinstance(place['id'], str)
        assert isinstance(place['version'], int)
        check_string_datetime(place['created'])
        check_string_datetime(place['updated'])
        assert isinstance(place['name'], str)
        if 'place_type' in place:
            assert isinstance(place['place_type'], str)
            assert place['place_type'] in ('home', 'work', 'other')

        assert isinstance(place['full_text'], str)
        assert isinstance(place['short_text'], str)
        assert isinstance(place['description'], str)
        if 'porchnumber' in place:
            assert isinstance(place['porchnumber'], str)
        if 'floor_number' in place:
            assert isinstance(place['floor_number'], str)
        if 'doorphone_number' in place:
            assert isinstance(place['doorphone_number'], str)
        if 'quarters_number' in place:
            assert isinstance(place['quarters_number'], str)
        if 'comment' in place:
            assert isinstance(place['comment'], str)
        if 'comment_courier' in place:
            assert isinstance(place['comment_courier'], str)
        if 'uri' in place:
            assert isinstance(place['uri'], str)

        point = place['point']
        assert isinstance(point, list) and len(point) == 2
        lon = point[0]
        lat = point[1]
        assert isinstance(lon, float) and -180.0 <= lon <= 180.0
        assert isinstance(lat, float) and -90.0 <= lat <= 90.0


def get_datasync_item(
        lon: typing.Optional[float] = 37.0,
        lat: typing.Optional[float] = 55.76,
        modified: typing.Optional[str] = '2001-09-08T11:22:33.44+00:00',
):
    result = {
        'address_id': 'home',
        'title': 'datasync',
        'longitude': lon,
        'latitude': lat,
        'created': '2000-02-07T11:22:33.44+00:00',
        'modified': modified,
        'address_line': 'Россия, Москва, Петровский бульвар, 23',
        'address_line_short': 'Петровский бульвар, 23',
        'entrance_number': '45',
    }
    return result


async def test_userplaceslist_get_not_allowed(taxi_userplaces):
    response = await taxi_userplaces.get(URL, json=get_request())
    assert response.status_code == 405, response.text


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_userplaceslist_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request())
    assert response.status_code == 500, response.text
    assert response.headers['Retry-After'] == '120'
    assert response.json() == {'code': '500', 'message': 'Service disabled'}


@pytest.mark.parametrize('uid', [None, ''])
async def test_userplaceslist_no_yandex_uid(taxi_userplaces, uid):
    response = await taxi_userplaces.post(URL, json=get_request(uid=uid))
    assert response.status_code == 400, response.text


@pytest.mark.nofilldb
@pytest.mark.parametrize('phone_id', [None, ''])
async def test_userplaceslist_no_phone_id(taxi_userplaces, phone_id):
    response = await taxi_userplaces.post(
        URL, json=get_request(phone_id=phone_id),
    )
    if phone_id is not None:
        assert response.status_code == 400, response.text
    else:
        assert response.status_code == 200, response.text


async def test_userplaceslist_no_lang(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request(language=None))
    assert response.status_code == 400, response.text


@pytest.mark.parametrize(
    'user_id, status_code', [(USER_ID, 200), ('', 200), (USER_ID[:31], 400)],
)
async def test_empty_user_id(taxi_userplaces, user_id, status_code):
    response = await taxi_userplaces.post(
        URL, json=get_request(user_id=user_id),
    )
    assert response.status_code == status_code, response.text


@pytest.mark.now('2001-09-01T10:00:00')
async def test_userplaceslist_simple(taxi_userplaces, load_json):
    """
    Самый простой корректный сценарий с возвратом userplace:
    Пользователь есть, у него ровно одно userplace, для которого не требуется
    локализация
    """
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response('ru', load_json)


@pytest.mark.now('2001-09-01T10:00:00')
async def test_userplaceslist_localize_userplace(
        taxi_userplaces, mockserver, yamaps, load_json,
):
    """
    Простой корректный сценарий с локализацией:
    Получение userplace, для которого нужно провести локализацию ru -> en
    """

    yamaps.add_fmt_geo_object(load_json('yamaps_en_response.json'))

    response = await taxi_userplaces.post(URL, json=get_request(language='en'))

    #  Result must be one userplace with localized address
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    ru_to_en_sample = get_sample_response('ru_to_en_translation', load_json)
    assert data['places'][0] == ru_to_en_sample


@pytest.mark.now('2001-09-01T10:00:00')
@pytest.mark.filldb(user_places='no_optional_fields')
async def test_userplaceslist_no_optional_fields_in_result(
        taxi_userplaces, load_json,
):
    """
    Простой запрос, но в возвращаемых местах отсутствуют все необязательные
    в ответе поля
    """
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    sample = get_sample_response('no_optional_fields', load_json)
    assert data['places'][0] == sample


@pytest.mark.now('2001-09-01T10:00:00')
@pytest.mark.filldb(user_places='with_types')
async def test_userplaceslist_place_type_sort(
        taxi_userplaces, load_json, mongodb,
):
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 4
    assert data['places'] == get_sample_response(
        'with_place_type_sort', load_json,
    )
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000004'},
    )
    assert entry
    assert entry['removed']
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000005'},
    )
    assert entry
    assert entry['removed']


@pytest.mark.now('2001-09-01T10:00:00')
@pytest.mark.filldb(user_places='portal_auth')
@pytest.mark.parametrize(
    'scenario',
    ['portal_uid', 'portal_uid_no_phone_id', 'phonish_uid', 'no_phone_id'],
)
async def test_userplaceslist_portal_auth(
        scenario, taxi_userplaces, load_json, mockserver, mongodb,
):
    """
    Работа с портальными аккаунтами
    """
    pass_flags = {}
    bound_uids = None
    phone_id = '02aaaaaaaaaaaaaaaaaaaa03'

    if scenario == 'phonish_uid':
        pass_flags = {'is_phonish': True}
    elif scenario == 'portal_uid':
        pass_flags = {'is_portal': True}
    elif scenario == 'portal_uid_no_phone_id':
        pass_flags = {'is_portal': True}
        phone_id = None
    elif scenario == 'no_phone_id':
        pass_flags = {'is_phonish': True}
        phone_id = None

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        return {'items': []}

    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            phone_id=phone_id,
            pass_flags=pass_flags,
            bound_uids=bound_uids,
            uid='12345',
        ),
    )

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data and 'places' in data and len(data) == 1
    data_places = copy.deepcopy(data['places'])
    for place in data_places:
        place.pop('id')

    response_name = 'portal_auth_' + scenario
    sample_resp = get_sample_response(response_name, load_json)
    for place in sample_resp:
        place.pop('id')

    ordered_object.assert_eq(data_places, sample_resp, [''])
    # check that all returned places have correct phone_id and format
    for place in data['places']:
        entry = mongodb.user_places.find_one({'_id': place['id']})
        assert entry
        assert entry['format_version'] == 4
        if 'brand_name' in entry:
            assert entry['brand_name'] == 'yango'
        if 'phone_id' in entry:
            assert entry['phone_id'] == bson.ObjectId(
                '02aaaaaaaaaaaaaaaaaaaa03',
            )


@pytest.mark.now('2001-09-01T10:00:00')
@pytest.mark.filldb(user_places='no_description')
async def test_userplaceslist_without_description(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_ru_response.json'))

    response = await taxi_userplaces.post(URL, json=get_request())
    assert response.status_code == 200

    data = response.json()

    validate_response_json(data)

    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1

    sample_response = get_sample_response('ru', load_json)
    assert data['places'][0] == sample_response

    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )

    assert entry
    db_description = entry['locales']['ru']['description']
    excpected_description = sample_response['description']
    assert db_description == excpected_description


@pytest.mark.now('2000-07-09T00:00:00.0')
async def test_userplaceslist_create_touched(taxi_userplaces, mongodb):
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert 'touched' in entry


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2001-09-01T10:00:00')
async def test_userplaceslist_update_touched(taxi_userplaces, mongodb):
    old_entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    touched = old_entry['touched']
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    assert entry['touched'] != touched


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2001-08-09T00:00:00')
async def test_userplaceslist_not_update_touched_every_time(
        taxi_userplaces, mongodb,
):
    old_entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    touched = old_entry['touched']
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    assert entry['touched'] == touched


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_remove_phone_id_outdated(
        taxi_userplaces, mongodb,
):
    response = await taxi_userplaces.post(URL, json=get_request(uid='333'))

    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert not data['places']
    entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    assert entry
    assert entry['removed']


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_not_remove_if_yandex_uid_match(
        taxi_userplaces, mongodb,
):
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})
    assert entry


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_new_format_phone_id_mismatch(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(phone_id='02aaaaaaaaaaaaaaaaaaaa03'),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert not data['places']


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_new_format_brand_mismatch(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(app_name='uber_android'),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert not data['places']


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_no_items(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return {'items': []}

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_mongo', load_json,
    )


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_no_mongo(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return {'items': [get_datasync_item()]}

    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            phone_id='02aaaaaaaaaaaaaaaaaaaa03',
            pass_flags={'is_portal': True},
        ),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_address', load_json,
    )


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_datasync_later_updated(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return {'items': [get_datasync_item()]}

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    datasync_addr = get_sample_response('datasync_address', load_json)
    datasync_addr['version'] = 123
    assert data['places'][0] == datasync_addr


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_datasync_later_updated_same_point(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return {'items': [get_datasync_item(lon=37.619045, lat=55.767843)]}

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_mongo', load_json,
    )


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_datasync_earlier_updated(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return {
            'items': [
                get_datasync_item(modified='2001-02-08T11:22:33.44+00:00'),
            ],
        }

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1

    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_mongo', load_json,
    )


@pytest.mark.config(USERPLACES_USE_DATASYNC=False)
@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_disabled(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert False

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_mongo', load_json,
    )


@pytest.mark.filldb(user_places='with_touched')
@pytest.mark.now('2003-09-01T10:00:00')
async def test_userplaceslist_datasync_bad_response(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return mockserver.make_response('empty param', 400)

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}),
    )
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response(
        'datasync_mongo', load_json,
    )


@pytest.mark.filldb(user_places='drive_test')
@pytest.mark.now('2001-08-08T11:22:33.0')
async def test_userplaceslist_drive_phone_id(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        return {'items': []}

    req = get_request(
        pass_flags={'is_portal': True},
        uid='400000001',
        phone_id='dddddddddddddddddddddddd',
    )

    response = await taxi_userplaces.post(URL, json=req)
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1

    req = get_request(
        pass_flags={'is_portal': True},
        uid='400000000',
        phone_id='dddddddddddddddddddddddd',
    )

    response = await taxi_userplaces.post(URL, json=req)
    assert response.status_code == 200
    data = response.json()
    assert data and 'places' in data and len(data) == 1
    assert not data['places']


@pytest.mark.now('2001-09-01T10:00:00')
@pytest.mark.filldb(user_places='with_types')
@pytest.mark.experiments3(filename='exp_userplaces_from_pers_address.json')
async def test_userplaceslist_from_ypa(
        taxi_userplaces, load_json, mongodb, mockserver,
):
    @mockserver.json_handler('/ya-pers-address/address/list')
    def _mock_pers_address(request):
        return {
            'status': 'ok',
            'addresses': [load_json('ya-pers-address-1.json')],
            'more': False,
        }

    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    assert response.json() == load_json('from-ypa-1-response.json')
