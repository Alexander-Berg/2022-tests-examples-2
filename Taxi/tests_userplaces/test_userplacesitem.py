import typing

import dateutil.parser
import pytest

URL = 'userplaces/item'
USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
DEFAULT_PLACE_ID = '123456789abcdef0123456789abcdef0'
DEFAULT_PASS_FLAGS = {'is_phonish': True, 'is_portal': False}


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
    }
    return result


def get_request(
        uid: typing.Optional[str] = DEFAULT_UID,
        phone_id: typing.Optional[str] = DEFAULT_PHONE_ID,
        pass_flags: typing.Optional[dict] = None,
        bound_uids: typing.Optional[list] = None,
        language: typing.Optional[str] = 'ru',
        place_id: typing.Optional[str] = DEFAULT_PLACE_ID,
        app_name: typing.Optional[str] = 'yango_android',
):
    request: typing.Dict[str, typing.Any] = {
        'user_identity': {'user_id': USER_ID},
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
    if place_id is not None:
        request['id'] = place_id
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
    place = response
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


async def test_userplacesitem_get_not_allowed(taxi_userplaces):
    response = await taxi_userplaces.get(URL, json=get_request())
    assert response.status_code == 405, response.text


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_userplacesitem_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request())
    assert response.status_code == 500, response.text
    assert response.headers['Retry-After'] == '120'
    assert response.json() == {'code': '500', 'message': 'Service disabled'}


@pytest.mark.parametrize('uid', [None, ''])
async def test_userplacesitem_no_yandex_uid(taxi_userplaces, uid):
    response = await taxi_userplaces.post(URL, json=get_request(uid=uid))
    assert response.status_code == 400, response.text


@pytest.mark.parametrize('phone_id', [None, ''])
async def test_userplacesitem_no_phone_id(taxi_userplaces, phone_id):
    response = await taxi_userplaces.post(
        URL, json=get_request(phone_id=phone_id),
    )
    assert response.status_code == 400, response.text


async def test_userplacesitem_no_lang(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request(language=None))
    assert response.status_code == 400, response.text


async def test_userplacesitem_no_id(taxi_userplaces):
    response = await taxi_userplaces.post(URL, json=get_request(place_id=None))
    assert response.status_code == 400, response.text


async def test_userplacesitem_simple(taxi_userplaces, load_json):
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data == get_sample_response('ru', load_json)


async def test_userplacesitem_with_another_brand(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(app_name='uber_android'),
    )
    assert response.status_code == 400, response.text


@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        # yataxi applications are not in default config
        'iphone': 'yataxi',
    },
)
async def test_userplacesitem_with_brand_in_same_group(
        taxi_userplaces, load_json,
):
    response = await taxi_userplaces.post(
        URL, json=get_request(app_name='iphone'),
    )

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data == get_sample_response('ru', load_json)


async def test_userplacesitem_no_such_id(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(place_id='123456789abcdef0123456789abcdefa'),
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Userplace not found'}


async def test_userplacesitem_bad_user_identity(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=get_request(phone_id='02aaaaaaaaaaaaaaaaaaaa02'),
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Userplace not found'}


async def test_userplacesitem_localize_userplace(
        taxi_userplaces, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_en_response.json'))
    response = await taxi_userplaces.post(URL, json=get_request(language='en'))
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    ru_to_en_sample = get_sample_response('en', load_json)
    assert data == ru_to_en_sample


async def test_userplacesitem_portal_uid(taxi_userplaces, load_json):
    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            pass_flags={'is_portal': True},
            bound_uids=['002', '003'],
            uid='12345',
        ),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data == get_sample_response('ru', load_json)


async def test_userplacesitem_portal_userplace(taxi_userplaces, load_json):
    place_id = '223456789abcdef0123456789abcdef0'
    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            pass_flags={'is_portal': True},
            uid='12345',
            place_id=place_id,
            phone_id=None,
        ),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    smpl = get_sample_response('ru', load_json)
    smpl['id'] = place_id
    assert data == smpl


@pytest.mark.filldb(user_places='no_optional_fields')
async def test_userplacesitem_no_optional_fields_in_result(
        taxi_userplaces, load_json,
):
    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    sample = get_sample_response('ru', load_json)
    sample.pop('porchnumber')
    sample.pop('floor_number')
    sample.pop('doorphone_number')
    sample.pop('quarters_number')
    sample.pop('comment')
    sample.pop('comment_courier')
    sample.pop('type')
    sample.pop('uri')
    assert data == sample


@pytest.mark.filldb(user_places='no_description')
async def test_userplacesitem_without_description(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_ru_response.json'))

    response = await taxi_userplaces.post(URL, json=get_request())
    assert response.status_code == 200

    data = response.json()
    validate_response_json(data)

    sample_response = get_sample_response('ru', load_json)
    assert data == sample_response

    entry = mongodb.user_places.find_one({'_id': DEFAULT_PLACE_ID})

    assert entry
    db_description = entry['locales']['ru']['description']
    excpected_description = sample_response['description']
    assert db_description == excpected_description


async def test_userplacesitem_place_type_only_datasync(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return get_datasync_item()

    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            pass_flags={'is_portal': True},
            place_id='home',
            phone_id='02aaaaaaaaaaaaaaaaaaaa02',
        ),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data == get_sample_response('datasync_home', load_json)


async def test_userplacesitem_place_type_only_mongo(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return mockserver.make_response('empty param', 400)

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}, place_id='home'),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data == get_sample_response('mongo_home', load_json)


async def test_userplacesitem_place_type_both_datasync_later(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        return get_datasync_item()

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}, place_id='home'),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    datasync_addr = get_sample_response('datasync_home', load_json)
    datasync_addr['version'] = 123
    assert data == datasync_addr


async def test_userplacesitem_place_type_both_datasync_later_same_point(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return get_datasync_item(lon=37.619045, lat=55.767843)

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}, place_id='home'),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data == get_sample_response('mongo_home', load_json)


async def test_userplacesitem_place_type_both_datasync_earlier(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return get_datasync_item(modified='2001-02-08T11:22:33.44+00:00')

    response = await taxi_userplaces.post(
        URL, json=get_request(pass_flags={'is_portal': True}, place_id='home'),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data == get_sample_response('mongo_home', load_json)


async def test_userplacesitem_datasync_bad_response(
        taxi_userplaces, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert request.headers['X-Uid'] == DEFAULT_UID
        return mockserver.make_response('empty param', 400)

    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            pass_flags={'is_portal': True},
            place_id='home',
            phone_id='02aaaaaaaaaaaaaaaaaaaa02',
        ),
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Userplace not found'}


@pytest.mark.config(USERPLACES_USE_DATASYNC=False)
async def test_userplacesitem_datasync_disabled(taxi_userplaces, mockserver):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert False

    response = await taxi_userplaces.post(
        URL,
        json=get_request(
            pass_flags={'is_portal': True},
            place_id='home',
            phone_id='02aaaaaaaaaaaaaaaaaaaa02',
        ),
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Userplace not found'}


@pytest.mark.experiments3(filename='exp_userplaces_from_pers_address.json')
async def test_userplacesitem_from_ypa(taxi_userplaces, load_json, mockserver):
    @mockserver.json_handler('/ya-pers-address/address/get')
    def _mock_pers_address(request):
        response = {'status': 'ok'}
        response.update(load_json('ya-pers-address-1.json'))
        return response

    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    assert response.json() == load_json('from-ypa-1-response.json')


@pytest.mark.experiments3(filename='exp_userplaces_from_pers_address.json')
async def test_userplacesitem_from_ypa_fallback(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/ya-pers-address/address/get')
    def _mock_pers_address(request):
        return mockserver.make_response('kaput', status=500)

    response = await taxi_userplaces.post(URL, json=get_request())

    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data == get_sample_response('ru', load_json)
