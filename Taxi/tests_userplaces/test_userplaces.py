import copy
import datetime
import typing

import bson
import pytest

from tests_plugins import json_util

URL = '3.0/userplaces'

USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
JSON = {'id': USER_ID}

FIX_ENTRANCES_EXP = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'fix_entrances',
    'consumers': ['userplaces/userplaces'],
    'clauses': [
        {
            'title': 'always',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
    'default_value': True,
}


def get_headers(
        uid: typing.Optional[str] = DEFAULT_UID,
        phone_id: typing.Optional[str] = DEFAULT_PHONE_ID,
        pass_flags='phonish',
        bound_uids=None,
        language: typing.Optional[str] = 'ru',
        app_name: typing.Optional[str] = 'yango_android',
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


def get_sample_response(name, load_json):
    return load_json('userplaces_sample_responses.json')[name]


def build_log(id_: str):
    type_ = '\"type\":\"userplace\"'
    id_ = '\"userplace_id\":\"' + id_ + '\"'
    return '{' + ','.join([type_, id_]) + '}'


# Check response format
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
                'version',
                'name',
                'comment',
                'comment_courier',
                'porchnumber',
                'floor_number',
                'doorphone_number',
                'quarters_number',
                'address',
                'place_type',
                'uri',
            )
        assert isinstance(place['id'], str)
        assert isinstance(place['version'], int)
        assert isinstance(place['name'], str)
        if 'comment' in place:
            assert isinstance(place['comment'], str)
        if 'comment_courier' in place:
            assert isinstance(place['comment_courier'], str)
        if 'porchnumber' in place:
            assert isinstance(place['porchnumber'], str)
        if 'floor_number' in place:
            assert isinstance(place['floor_number'], str)
        if 'doorphone_number' in place:
            assert isinstance(place['doorphone_number'], str)
        if 'quarters_number' in place:
            assert isinstance(place['quarters_number'], str)
        address = place['address']
        assert isinstance(address, dict)
        for k in address:
            assert k in (
                'oid',
                'full_text',
                'short_text',
                'country',
                'city',
                'street',
                'house',
                'type',
                'object_type',
                'point',
                'exact',
                'description',
                'porchnumber',
                'floor_number',
                'doorphone_number',
                'quarters_number',
                'comment',
                'log',
                'comment_courier',
                'uri',
            )
        assert isinstance(address['log'], str)
        assert address['log'] == build_log(place['id'])
        address.pop('log')
        assert isinstance(address['full_text'], str)
        assert isinstance(address['short_text'], str)
        assert isinstance(address['country'], str)
        assert isinstance(address['city'], str)
        assert isinstance(address['street'], str)
        assert isinstance(address['house'], str)
        assert isinstance(address['type'], str)
        assert address['type'] in ('address', 'organization')
        assert isinstance(address['object_type'], str)
        assert address['object_type'] in ('аэропорт', 'организация', 'другое')
        assert isinstance(address['exact'], bool)
        if 'description' in address:
            assert isinstance(address['description'], str)
        point = address['point']
        assert isinstance(point, list) and len(point) == 2
        lon = point[0]
        lat = point[1]
        assert isinstance(lon, float) and -180.0 <= lon <= 180.0
        assert isinstance(lat, float) and -90.0 <= lat <= 90.0


async def test_get_not_allowed(taxi_userplaces):
    response = await taxi_userplaces.get(URL, json=JSON, headers=get_headers())
    assert response.status_code == 405, response.text


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


async def test_userplaces_no_language(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None, language=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_userplaces_no_app_name(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None, app_name=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.now('2000-09-01T10:00:00')
async def test_userplaces_simple_correct_scenario(taxi_userplaces, load_json):
    """
    Самый простой корректный сценарий с возвратом userplace:
    Пользователь есть, у него ровно одно userplace, для которого не требуется
    локализация
    """
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response('ru', load_json)


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='no_main_locale')
async def test_userplaces_simple_correct_scenario_no_main_local(
        taxi_userplaces, mongodb, load_json,
):
    """
    Самый простой корректный сценарий:
    Пользователь есть, у него ровно одно userplace, для которого не требуется
    локализация. Отличие от предыдущего случая - запрашиваем неглавную локаль
    """
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='uk'),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response('ru', load_json)
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'phone_id': bson.ObjectId(DEFAULT_PHONE_ID)},
    )
    assert entry
    #  Locales must not be changed
    assert entry['locales'] and len(entry['locales']) == 2
    for locale in entry['locales']:
        assert locale in ('ru', 'uk')


@pytest.mark.now('2000-09-01T10:00:00')
async def test_userplaces_localize_userplace(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    """
    Простой корректный сценарий с локализацией:
    Получение userplace, для которого нужно провести локализацию ru -> en
    В locales должна быть только en локаль
    """

    yamaps.add_fmt_geo_object(load_json('yamaps_en_response.json'))

    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='en'),
    )
    # Check response
    #  Result must be one userplace with localized address
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    ru_to_en_sample = get_sample_response('ru_to_en_translation', load_json)
    assert data['places'][0] == ru_to_en_sample
    # Check DB
    #  Database must have two localizations now
    entry = mongodb.user_places.find_one(
        {'phone_id': bson.ObjectId(DEFAULT_PHONE_ID)},
    )
    assert entry
    entry.pop('touched')  # cause can't mock $currentDate
    entry.pop('updated')  # cause can't mock $currentDate
    #  Entry 'ru' locale - origin
    sample_ru = copy.deepcopy(get_sample_response('ru', load_json))
    #  Entry 'en' locale - translated
    sample_address_en = copy.deepcopy(ru_to_en_sample['address'])
    sample_address_en.pop('porchnumber')  # TAXIBACKEND-6051
    sample_address_en.pop('comment')  # TAXIBACKEND-6051
    sample_address_en.pop('comment_courier')
    sample_address_en.pop('floor_number')
    sample_address_en.pop('doorphone_number')
    sample_address_en.pop('quarters_number')
    #  Entry common data
    entry_sample = {
        '_id': '00000004-AAAA-AAAA-AAAA-000000000001',
        'created': datetime.datetime(2000, 7, 8, 11, 22, 33),
        'drafted': None,
        'version': sample_ru['version'],
        'phone_id': bson.ObjectId('02aaaaaaaaaaaaaaaaaaaa01'),
        'format_version': 4,
        'brand_name': 'yango',
        'device_id': '00000003-AAAA-AAAA-AAAA-000000000001',
        'name': sample_ru['name'],
        'comment': sample_ru['comment'],
        'comment_courier': sample_ru['comment_courier'],
        'porchnumber': sample_ru['porchnumber'],
        'floor_number': sample_ru['floor_number'],
        'doorphone_number': sample_ru['doorphone_number'],
        'quarters_number': sample_ru['quarters_number'],
        'locales': {'en': sample_address_en},
    }
    assert entry == entry_sample


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.parametrize(
    'phone_id, place_id',
    [
        ('02aaaaaaaaaaaaaaaaaaaa01', '00000004-AAAA-AAAA-AAAA-000000000002'),
        ('02aaaaaaaaaaaaaaaaaaaa02', '00000004-AAAA-AAAA-AAAA-000000000001'),
    ],
)
@pytest.mark.filldb(user_places='filter_phone_id')
async def test_userplaces_filter_phone_id(phone_id, place_id, taxi_userplaces):
    """
    Фильтрация мест по phone id
    """
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=phone_id),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0]['id'] == place_id


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='filter_drafted')
async def test_userplaces_filter_drafted(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    """
    Фильтрация мест по метке drafted - черновики не должны попадать в выдачу
    Попутно проверяем, что выданные места локализуются, а отфильтрованные - нет
    """

    yamaps.add_fmt_geo_object(load_json('yamaps_en_response.json'))

    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='en'),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    ru_to_en_sample = get_sample_response('ru_to_en_translation', load_json)
    assert data['places'][0] == ru_to_en_sample
    # Check DB changes - fetched entry - locales must be extended
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    assert entry['locales'] and len(entry['locales']) == 1
    assert entry['locales']['en']
    # Check DB changes - filtered entry - locales must NOT be changed
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000002'},
    )
    assert entry
    assert entry['locales'] and len(entry['locales']) == 1
    assert entry['locales']['ru']


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='no_optional_fields')
async def test_userplaces_no_optional_fields_in_result(
        taxi_userplaces, load_json,
):
    """
    Простой запрос, но в возвращаемых местах отсутствуют все необязательные
    в ответе поля
    """
    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    sample = get_sample_response('ru', load_json)
    sample.pop('comment')
    sample.pop('comment_courier')
    sample.pop('porchnumber')
    sample.pop('floor_number')
    sample.pop('doorphone_number')
    sample.pop('quarters_number')
    sample['address']['oid'] = ''
    sample['address']['description'] = 'Россия, Москва'
    sample['address'].pop('porchnumber')
    sample['address'].pop('floor_number')
    sample['address'].pop('doorphone_number')
    sample['address'].pop('quarters_number')
    sample['address'].pop('comment')
    sample['address'].pop('comment_courier')
    assert data['places'][0] == sample


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='complex_data')
async def test_userplaces_complex_data(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    """
    Большой сценарий:
    Тестируем покрытие разных случаев одной большой коллекцией данных -
    данные взяты из реальной монги unstable
    (с небольшими изменениями), туда добавлены через приложение
    """
    yamaps.add_fmt_geo_object(load_json('yamaps_en_response.json'))

    # Find and return place
    def find_place(places, place_id):
        for place in places:
            if place['id'] == place_id:
                return place
        return None

    # Query
    response = await taxi_userplaces.post(
        URL,
        json=JSON,
        headers=get_headers(
            phone_id='59666d67689b21396ab4561a', language='en',
        ),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    places = data['places']
    assert len(places) == 6
    # Check place - Dubai - use fallback, because org -> no change db: ru, uk
    place = find_place(places, '3ea7add859bf48c9b2e2c67ec8256af5')
    assert place
    assert place['name'] == 'Dubai, Burj Khalifa'
    entry = mongodb.user_places.find_one(
        {'_id': '3ea7add859bf48c9b2e2c67ec8256af5'},
    )
    assert len(entry['locales']) == 2
    locales = list(entry['locales'].keys())
    assert 'ru' in locales
    assert 'uk' in locales
    address = place['address']
    address.pop('porchnumber')  # TAXIBACKEND-6051
    assert address == entry['locales']['ru']
    # Check place - Moscow - no need localization
    place = find_place(places, 'f80e704459a94dfcb1565d619521df22')
    assert place
    assert place['name'] == 'Address'
    entry = mongodb.user_places.find_one(
        {'_id': 'f80e704459a94dfcb1565d619521df22'},
    )
    # 3 locales because didn't translate and update db
    assert len(entry['locales']) == 3
    for locale in entry['locales']:
        assert locale in {'ru', 'uk', 'en'}
    address = place['address']
    assert address == entry['locales']['en']
    assert entry['locales']['en']['point'] == entry['locales']['ru']['point']
    assert entry['locales']['en']['point'] == entry['locales']['uk']['point']
    # Check place - Canada - filtered, because drafted
    place = find_place(places, '985b37707e884966bb36ae079fdae7d0')
    assert place is None
    entry = mongodb.user_places.find_one(
        {'_id': '985b37707e884966bb36ae079fdae7d0'},
    )
    assert entry['name'] == 'Канадский Париж'
    # 3 locales because didn't translate and update db
    assert len(entry['locales']) == 3
    for locale in entry['locales']:
        assert locale in {'ru', 'uk', 'en'}
    assert entry['locales']['en']['point'] == entry['locales']['ru']['point']
    assert entry['locales']['en']['point'] == entry['locales']['uk']['point']
    # Check place - Рязань - filtered, because too old and has no id - so,
    # no need localization
    place = find_place(places, 'f7c386913eae46fa9d309a8ddf18d600')
    assert place is None
    entry = mongodb.user_places.find_one(
        {'_id': 'f7c386913eae46fa9d309a8ddf18d600'},
    )
    assert entry['name'] == 'Где-то в Рязани'
    # 2 locales because didn't translate and update db
    assert len(entry['locales']) == 2
    for locale in entry['locales']:
        assert locale in {'ru', 'uk'}
    assert entry['locales']['ru']['point'] == entry['locales']['uk']['point']
    # Check place - Лосиный остров - check response exact data
    place = find_place(places, 'feec01cd4c2243a290c2cf26f7741b42')
    assert place
    assert place == get_sample_response('losinyi_ostrov', load_json)


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='empty_name')
async def test_userplaces_empty_place_name(taxi_userplaces, load_json):
    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    assert data['places'][0] == get_sample_response('empty_name', load_json)


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='fallback')
async def test_userplaces_fallback(
        taxi_userplaces, mockserver, yamaps, mongodb, load_json,
):
    """
    Сценарий на работу фолбека:
    Пытаемся запросить 2 userplace'а, для которых нужно
    провести локализацию ru -> en
    Один переводится в штатном режиме,
    для другого карты не возвращают перевода, фолбечимся
    """

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        lang = request.args.get('lang')
        point = list(map(float, request.args['ll'].split(',')))
        assert lang == 'en'
        assert point == [37.619046, 55.767843]
        variables = {
            'point': point,
            'short_text': request.args.get('text', ''),
            'full_text': request.args.get('text', ''),
            'description': request.args.get('text', ''),
        }
        if variables['description'] == 'first place':
            return []
        return [
            load_json(
                'yamaps_en_response_template.json',
                object_hook=json_util.VarHook(variables),
            ),
        ]

    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='en'),
    )
    # Check response
    #  Result must be one userplace with ru address placed in en locale
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)

    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 2

    #  Entry 'ru' locale - origin
    sample_ru = copy.deepcopy(get_sample_response('place_ru', load_json))
    sample_address_ru = sample_ru['address']
    sample_address_ru.pop('porchnumber')  # TAXIBACKEND-6051
    sample_address_ru.pop('comment')  # TAXIBACKEND-6051

    #  Entry common data
    entry_sample_fallback = {
        '_id': '00000004-AAAA-AAAA-AAAA-000000000001',
        'created': datetime.datetime(2000, 7, 8, 11, 22, 33),
        'drafted': None,
        'version': sample_ru['version'],
        'phone_id': bson.ObjectId('02aaaaaaaaaaaaaaaaaaaa01'),
        'format_version': 4,
        'brand_name': 'yango',
        'name': sample_ru['name'],
        'comment': sample_ru['comment'],
        'porchnumber': sample_ru['porchnumber'],
        'locales': {'ru': sample_address_ru},
    }

    # Check fallbacked place
    entry_fallback = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry_fallback
    entry_fallback.pop('updated')  # cause can't mock $currentDate
    entry_fallback.pop('touched')  # cause can't mock $currentDate
    entry_fallback.pop('device_id')  # cause can't moc $currentDate
    assert entry_fallback == entry_sample_fallback

    entry_sample_translated = copy.deepcopy(entry_sample_fallback)
    entry_sample_translated['_id'] = '00000004-AAAA-AAAA-AAAA-000000000002'
    entry_sample_translated['locales'].pop('ru')

    place_en_sample = get_sample_response('place_en', load_json)
    sample_address_en = place_en_sample['address']
    sample_address_en.pop('porchnumber')  # TAXIBACKEND-6051
    sample_address_en.pop('comment')  # TAXIBACKEND-6051
    entry_sample_translated['locales']['en'] = sample_address_en

    # Check normal translation place
    entry_translated = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000002'},
    )
    assert entry_translated
    entry_translated.pop('updated')
    entry_translated.pop('touched')
    entry_translated.pop('device_id')

    assert entry_translated == entry_sample_translated


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='with_uri')
async def test_userplaces_uri_in_response(taxi_userplaces):
    # Query

    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data['places']) == 1
    assert data['places'][0]['address']['uri'] == 'test_uri'


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='localize_by_uri')
async def test_userplaces_localize_by_uri(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        uri = request.args.get('uri')
        assert uri == 'test_uri'
        return [load_json('yamaps_response_uri.json')]

    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='en'),
    )

    assert response.status_code == 200

    entry = mongodb.user_places.find_one(
        {'device_id': '00000003-AAAA-AAAA-AAAA-000000000001'},
    )

    assert entry
    assert len(entry['locales']) == 1
    assert 'en' in entry['locales']


# Don't response 500 if ru locale not in db
@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='without_ru_locale')
async def test_userplaces_without_ru_locale(
        taxi_userplaces, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response_uri.json'))

    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(language='uk'),
    )

    assert response.status_code == 200


@pytest.mark.now('2000-09-01T10:00:00')
@pytest.mark.filldb(user_places='no_description')
async def test_userplaces_without_description(
        taxi_userplaces, mockserver, yamaps, load_json, mongodb,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_ru_response.json'))

    # Query
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
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
    excpected_description = sample_response['address']['description']
    assert db_description == excpected_description


@pytest.mark.parametrize(
    'expect_fixed_entrance,yamaps_entrances',
    [
        pytest.param(False, None, id='dont_fix_entrances'),
        pytest.param(
            True,
            [{'name': '45', 'point': [37.5, 55.5]}],
            id='fix_bad_entrance',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
        pytest.param(
            False,
            [{'name': '45', 'point': [37.619046, 55.767843]}],
            id='keep_entrance',
            marks=[pytest.mark.experiments3(**FIX_ENTRANCES_EXP)],
        ),
    ],
)
@pytest.mark.filldb(user_places='with_uri')
@pytest.mark.now('2000-09-01T10:00:00')
async def test_userplaces_fix_entrances(
        taxi_userplaces,
        mockserver,
        load_json,
        yamaps,
        expect_fixed_entrance,
        yamaps_entrances,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        objects = load_json('yamaps_object_with_entrance.json')
        objects['arrival_points'] = yamaps_entrances
        return [objects]

    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    validate_response_json(data)
    assert data and 'places' in data and len(data) == 1
    assert len(data['places']) == 1
    expected_place = get_sample_response('with_uri', load_json)
    if expect_fixed_entrance:
        expected_place['address'][
            'full_text'
        ] = 'Russia, Moscow, Test Street, 2'
        expected_place['address']['short_text'] = 'Test Street 2'
        del expected_place['address']['porchnumber']
        del expected_place['porchnumber']
    assert data['places'][0] == expected_place


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


@pytest.mark.config(USERPLACES_ENABLE_SET_URI_FOR_DATASYNC_PLACES=True)
@pytest.mark.filldb(user_places='empty')
async def test_set_uri(taxi_userplaces, mockserver, load_json, yamaps):
    yamaps.add_fmt_geo_object(load_json('yamaps_response_uri.json'))

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses')
    def _mock_datasync(request):
        return {'items': [get_datasync_item()]}

    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(pass_flags='portal'),
    )
    assert response.status_code == 200
    assert response.json()['places'][0] == load_json('uri_response.json')
