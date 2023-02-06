import copy
import datetime
import json

import bson
import pytest

URL = '/3.0/userplacesupdate'
USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
JSON = {'id': USER_ID, 'places': []}

DATASYNC_REQUEST = {
    'address_id': 'home',
    'title': 'Дом',
    'longitude': 37.12,
    'latitude': 55.12,
    'address_line': 'Россия, Москва, Петровский бульвар, 21с',
    'address_line_short': 'Петровский бульвар, 21с',
    'entrance_number': '18',
}


def build_log(id_: str):
    type_ = '\"type\":\"userplace\"'
    id_ = '\"userplace_id\":\"' + id_ + '\"'
    return '{' + ','.join([type_, id_]) + '}'


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


def load_sample_request(name, load_json):
    return load_json('sample_requests.json')[name]


def load_sample_entry(name, load_json):
    json_sample = load_json('sample_entries.json')[name]
    if 'created' in json_sample:
        json_sample['created'] = json_sample['created'].replace(tzinfo=None)
    if 'updated' in json_sample:
        json_sample['updated'] = json_sample['updated'].replace(tzinfo=None)
    if 'drafted' in json_sample:
        json_sample['drafted'] = json_sample['drafted'].replace(tzinfo=None)
    return json_sample


# Check response format
def validate_response_json(response):
    assert response
    assert len(response) == 1
    places = response['places']
    assert isinstance(places, list)
    for place in places:
        assert isinstance(place, dict)
        for k in place:
            assert k in ('id', 'version', 'address')
        assert isinstance(place['id'], str)
        assert isinstance(place['version'], int)


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
async def test_userplacesupdate_disable_updates(taxi_userplaces):
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


async def test_userplacesupdate_no_language(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None, language=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_userplacesupdate_no_app_name(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=JSON, headers=get_headers(phone_id=None, app_name=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_userplacesupdate_simple_correct_scenario(
        taxi_userplaces, load_json, now, mongodb,
):
    """
    Самый простой корректный сценарий:
     * добавление одного userplace в пустую базу пользователя
     * userplace был drafted
    """
    # Query
    smpl = load_sample_request('simple', load_json)
    response = await taxi_userplaces.post(
        URL, load_sample_request('simple', load_json), headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    addr = smpl['places'][0]['address']
    addr.pop('short_text_from')
    addr.pop('short_text_to')
    addr.pop('accepts_exact5')
    addr['log'] = build_log('00000004-AAAA-AAAA-AAAA-000000000001')
    assert data['places'][0]['address'] == addr
    data['places'][0].pop('address')
    assert data == {
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000001', 'version': 1},
        ],
    }
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    #  Timestep must be just updated
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    #  Check other fields
    entry.pop('updated')
    assert entry == load_sample_entry('ru', load_json)


@pytest.mark.parametrize(
    'req_id, headers, ypa_fail, expect_fail',
    [
        pytest.param(
            'simple',
            get_headers(),
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
            'userplace-place-type',
            get_headers(
                phone_id='01aaaaaaaaaaaaaaaaaaaa11', app_name='yataxi',
            ),
            False,
            False,
            marks=[
                pytest.mark.config(
                    USERPLACES_WRITE_YA_PERS_ADDRESS={
                        'enabled': True,
                        'fail_otherwise': True,
                    },
                ),
                pytest.mark.filldb(user_places='with_place_type'),
            ],
        ),
        pytest.param(
            'userplace-place-type',
            get_headers(
                phone_id='01aaaaaaaaaaaaaaaaaaaa11', app_name='yataxi',
            ),
            True,
            True,
            marks=[
                pytest.mark.config(
                    USERPLACES_WRITE_YA_PERS_ADDRESS={
                        'enabled': True,
                        'fail_otherwise': True,
                    },
                ),
                pytest.mark.filldb(user_places='with_place_type'),
            ],
        ),
        pytest.param(
            'userplace-place-type',
            get_headers(
                phone_id='01aaaaaaaaaaaaaaaaaaaa11', app_name='yataxi',
            ),
            True,
            False,
            marks=[
                pytest.mark.config(
                    USERPLACES_WRITE_YA_PERS_ADDRESS={
                        'enabled': True,
                        'fail_otherwise': False,
                    },
                ),
                pytest.mark.filldb(user_places='with_place_type'),
            ],
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
async def test_ypa_update(
        taxi_userplaces,
        req_id,
        mockserver,
        headers,
        ypa_fail,
        expect_fail,
        load_json,
):
    @mockserver.json_handler('/ya-pers-address/address/update')
    def _mock_ypa_update(request):
        assert request.query['user_id'] == DEFAULT_UID
        assert request.query['user_type'] == 'uid'
        assert request.query['return_updated'] == 'true'
        assert request.json == load_json('expected_ypa_requests.json')[req_id]
        if ypa_fail:
            return mockserver.make_response(status=500)
        return {'status': 'ok'}

    response = await taxi_userplaces.post(
        URL, json=load_sample_request(req_id, load_json), headers=headers,
    )

    assert _mock_ypa_update.has_calls
    expected_code = 500 if expect_fail else 200
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'phone_id, status_code',
    [
        ('02aaaaaaaaaaaaaaaaaaaa01', 200),  # ok
        (
            '03aaaaaaaaaaaaaaaaaaaa02',
            409,
        ),  # place with such phone_id is not found
        (None, 400),  # no phone id
    ],
)
async def test_userplacesupdate_phone_id_variants(
        taxi_userplaces, load_json, phone_id, status_code,
):
    """
    Различные user id на входе
    """
    request = load_sample_request('simple', load_json)
    response = await taxi_userplaces.post(
        URL, request, headers=get_headers(phone_id=phone_id),
    )
    assert response.status_code == status_code
    if status_code == 200:
        validate_response_json(response.json())


@pytest.mark.parametrize(
    'request_sample_name, status_code',
    [
        ('simple', 200),  # ok
        ('places-variants-no', 400),  # no places at all
        (
            'places-variants-invalid-scalar_value',
            400,
        ),  # places has invalid type
        ('places-variants-no-id', 400),  # place has no id
        ('places-variants-none-id', 400),  # place id is None
        ('places-variants-invalid-id-type', 400),  # place id is integer
        ('places-variants-no-name', 400),  # place has no name
        ('places-variants-empty-name', 200),  # place name is empty
        ('places-variants-invalid-name-type', 400),  # place name is integer
        ('places-variants-no-version', 400),  # place has no version
        (
            'places-variants-invalid-version-type',
            400,
        ),  # place version is string
        # place version is negative
        ('places-variants-invalid-version-value', 400),
        ('places-variants-no-address', 400),  # place has no address
        (
            'places-variants-invalid-address-type',
            400,
        ),  # place address is invalid
        ('places-variants-no-full-text', 400),  # place has no full text - ok
        (
            'places-variants-invalid-full-text',
            400,
        ),  # place has invalid full text
        ('places-variants-no-point', 400),  # place has no point
        ('places-variants-invalid-point', 400),  # place has invalid point
    ],
)
async def test_userplacesupdate_places_variants(
        taxi_userplaces, load_json, request_sample_name, status_code,
):
    """
    Различные places на входе
    """
    request = load_sample_request(request_sample_name, load_json)
    response = await taxi_userplaces.post(URL, request, headers=get_headers())
    assert response.status_code == status_code
    if status_code == 200:
        validate_response_json(response.json())


async def test_userplacesupdate_not_ru_locales(
        taxi_userplaces, load_json, mongodb,
):
    response = await taxi_userplaces.post(
        URL,
        load_sample_request('simple', load_json),
        headers=get_headers(language='en'),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000001', 'version': 1},
        ],
    }
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    entry.pop('updated')
    assert entry == load_sample_entry('en', load_json)


@pytest.mark.parametrize(
    'porchnumber, comment',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_userplacesupdate_simple_correct_scenario_with_optionals(
        taxi_userplaces, load_json, mongodb, porchnumber, comment,
):
    """
    Простой корректный сценарий, но с необязательными полями:
     porchnumber, comment
    Должны попасть в базу только если были во входных данных
    """
    # Query
    request = load_sample_request(
        'simple-with-optionals-porchnumber-and-comment', load_json,
    )
    if not porchnumber:
        request['places'][0]['address'].pop('porchnumber')
    if not comment:
        request['places'][0]['address'].pop('comment')
    response = await taxi_userplaces.post(URL, request, headers=get_headers())
    # Check response
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000001', 'version': 1},
        ],
    }
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    entry.pop('updated')
    sample_entry = load_sample_entry(
        'ru-with-optionals-porchnumber-and-comment', load_json,
    )
    if not porchnumber:
        sample_entry.pop('porchnumber')
    if not comment:
        sample_entry.pop('comment')
    assert entry == sample_entry


@pytest.mark.parametrize(
    'request_name, app_name, status_code',
    [
        ('conflict-no', 'yango_iphone', 200),  # no conflict
        ('conflict-no', 'uber_iphone', 409),  # another brand
        (
            'conflict-incorrect-place-id',
            'yango_iphone',
            409,
        ),  # place id is wrong
        # version is ok, not drafted
        ('conflict-not-drafted-correct-version', 'yango_iphone', 200),
        # verison is wrong, not draft.
        ('conflict-not-drafted-wrong-version', 'yango_iphone', 409),
        # one of 3 places will race error
        ('conflict-one-of-three-places', 'yango_iphone', 409),
    ],
)
async def test_userplacesupdate_conflict_error(
        taxi_userplaces, load_json, request_name, app_name, status_code,
):
    """
    Простые сценарии для ответа Conflict Error (409)
    """
    # Query
    response = await taxi_userplaces.post(
        URL,
        load_sample_request(request_name, load_json),
        headers=get_headers(
            phone_id='02aaaaaaaaaaaaaaaaaaaa04', app_name=app_name,
        ),
    )
    # Check response
    assert response.status_code == status_code
    if response.status_code == 200:
        validate_response_json(response.json())


@pytest.mark.filldb(user_places='update_some_places')
async def test_userplacesupdate_update_some_places(
        taxi_userplaces, load_json, now, mongodb,
):
    """
    Корректный сценарий обновления сразу нескольких мест
    Заодно проверяем:
    1) Поле updated выставляется на текущее время
    2) Поля получают правильные значения: name, device_id, locales, comment,
       porchnumber, place_type
    3) Поле drafted снимается
    4) Поле version увеличивается на единицу
    5) Число локалей не завсисит от того, сколько их было до обновления,
       а определяется текущей локалью
    """
    # Query
    response = await taxi_userplaces.post(
        URL,
        load_sample_request('some-places', load_json),
        headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    data = response.json()
    for place in data['places']:
        place.pop('address')
    assert data == {
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000001', 'version': 1},
            {'id': '00000004-AAAA-AAAA-AAAA-000000000003', 'version': 5},
            {'id': 'home', 'version': 174},
        ],
    }
    # Check DB changes
    #  Place 1: from draft to not drafted place
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('ru', load_json)
    #  Place 2: no changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000002'},
    )
    assert entry
    assert entry == load_sample_entry('some-places-not-changed', load_json)
    #  Place 3: version up, fields changed
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000003'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    assert entry
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('some-places-changed-1', load_json)
    #  Place 4: from draft to not drafted place
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000004'},
    )
    assert entry
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('some-places-changed-2', load_json)


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_update_place_type(
        taxi_userplaces, load_json, now, mongodb,
):
    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        load_sample_request('userplace-place-type', load_json),
        headers=get_headers(phone_id='01aaaaaaaaaaaaaaaaaaaa11'),
    )
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {'places': [{'id': 'home', 'version': 5}]}
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000011'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('userplace-place-type', load_json)


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_update_place_type_without_place_type(
        taxi_userplaces, load_json, now, mongodb,
):
    sample_req = load_sample_request('userplace-place-type', load_json)
    sample_req['places'][0].pop('place_type')
    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        sample_req,
        headers=get_headers(phone_id='01aaaaaaaaaaaaaaaaaaaa11'),
    )
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {'places': [{'id': 'home', 'version': 5}]}
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000011'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('userplace-place-type', load_json)


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_create_place_type(
        taxi_userplaces, load_json, now, mongodb,
):
    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        load_sample_request('new-userplace-place-type', load_json),
        headers=get_headers(phone_id='01aaaaaaaaaaaaaaaaaaaa11'),
    )
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {'places': [{'id': 'work', 'version': 1}]}
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000012'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('new-userplace-place-type', load_json)


@pytest.mark.filldb(user_places='portal_auth')
@pytest.mark.parametrize(
    'scenario, userplaces_numbers, status_code',
    [
        ('portal_uid_no_bindings', [1], 200),
        ('portal_uid_no_bindings', [1, 3, 4], 409),
        ('phonish_uid', [1], 200),
        ('phonish_uid', [1, 3, 4], 409),
    ],
)
@pytest.mark.now('2018-02-01T10:00:00')
async def test_userplacesupdate_portal_auth(
        taxi_userplaces,
        load_json,
        mongodb,
        scenario,
        userplaces_numbers,
        status_code,
):
    """
    Тест работы с портальным логином
    """
    # pylint: disable=invalid-name
    ID_FORMAT = '00000004-AAAA-AAAA-AAAA-00000000000%d'

    pass_flags = ''
    bound_uids = None

    if scenario == 'portal_uid_no_bindings':
        pass_flags = 'portal'
    elif scenario == 'phonish_uid':
        pass_flags = 'phonish'

    # Build query
    userplaces_ids = [
        ID_FORMAT % userplace_number for userplace_number in userplaces_numbers
    ]
    sample_request = load_sample_request('portal-auth', load_json)
    query = copy.deepcopy(sample_request)
    query['places'] = []
    for userplace in sample_request['places']:
        if userplace['id'] in userplaces_ids:
            query['places'].append(userplace)

    # Do call
    response = await taxi_userplaces.post(
        URL,
        query,
        headers=get_headers(
            pass_flags=pass_flags, bound_uids=bound_uids, uid='12345',
        ),
    )

    # Check response
    places_sample = [{'id': ID_FORMAT % i, 'version': 7} for i in (1, 3, 4)]

    places = [
        place for place in places_sample if place['id'] in userplaces_ids
    ]

    assert response.status_code == status_code
    if status_code == 200:
        data = response.json()
        for place in data['places']:
            place.pop('address')
        assert data == {'places': places}

    # Check DB changes
    now = datetime.datetime.utcnow()
    #  Place 1: from draft to not drafted place
    if 1 in userplaces_numbers:
        entry = mongodb.user_places.find_one({'_id': ID_FORMAT % 1})
        assert entry
        assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
        entry.pop('updated')  # already checked
        assert entry == load_sample_entry('portal-auth-0', load_json)

        #  Place 2: no changes
    if 2 in userplaces_numbers:
        entry = mongodb.user_places.find_one({'_id': ID_FORMAT % 2})
        assert entry
        assert entry == load_sample_entry('portal-auth-1', load_json)

        #  Place 3: version up, fields changed
    if 3 in userplaces_numbers and status_code == 200:
        entry = mongodb.user_places.find_one({'_id': ID_FORMAT % 3})
        assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
        assert entry
        entry.pop('updated')  # already checked
        assert entry == load_sample_entry('portal-auth-2', load_json)

        #  Place 4: from draft to not drafted place
    if 4 in userplaces_numbers and status_code == 200:
        entry = mongodb.user_places.find_one({'_id': ID_FORMAT % 4})
        assert entry
        assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
        entry.pop('updated')  # already checked
        assert entry == load_sample_entry('portal-auth-3', load_json)


async def test_userplacesupdate_uri_in_db(taxi_userplaces, load_json, mongodb):
    response = await taxi_userplaces.post(
        URL, load_sample_request('with-uri', load_json), headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    entry.pop('updated')
    assert entry == load_sample_entry('with-uri', load_json)


async def test_userplacesupdate_uri_not_in_db(
        taxi_userplaces, load_json, mongodb,
):
    """
        Test case: make userplaces with uri
        and update it - new address but without uri,
        Exptected: uri isn't in doc
    """

    response = await taxi_userplaces.post(
        URL, load_sample_request('with-uri', load_json), headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    entry.pop('updated')
    assert entry == load_sample_entry('with-uri', load_json)

    response = await taxi_userplaces.post(
        URL,
        load_sample_request('without-uri', load_json),
        headers=get_headers(),
    )
    # Check response
    assert response.status_code == 200
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert entry
    entry.pop('updated')
    assert entry == load_sample_entry('without-uri', load_json)


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_datasync(
        taxi_userplaces, load_json, now, mongodb, mockserver,
):
    datasync_called = False

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        nonlocal datasync_called
        datasync_called = True
        assert request.method == 'PUT'
        assert json.loads(request.get_data()) == DATASYNC_REQUEST

    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        load_sample_request('userplace-place-type', load_json),
        headers=get_headers(
            phone_id='01aaaaaaaaaaaaaaaaaaaa11', pass_flags='portal',
        ),
    )
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {'places': [{'id': 'home', 'version': 5}]}
    assert datasync_called
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000011'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('userplace-place-type', load_json)


@pytest.mark.config(USERPLACES_USE_DATASYNC=False)
@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_datasync_disabled(
        taxi_userplaces, load_json, now, mongodb, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert False

    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        load_sample_request('userplace-place-type', load_json),
        headers=get_headers(
            phone_id='01aaaaaaaaaaaaaaaaaaaa11', pass_flags='portal',
        ),
    )
    assert response.status_code == 200
    data = response.json()
    data['places'][0].pop('address')
    assert data == {'places': [{'id': 'home', 'version': 5}]}
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000011'},
    )
    assert abs(now - entry['updated']) < datetime.timedelta(minutes=10)
    entry.pop('updated')  # already checked
    assert entry == load_sample_entry('userplace-place-type', load_json)


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_place_type_conflict(
        taxi_userplaces, load_json, mockserver,
):
    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert False

    smpl = load_sample_request('userplace-place-type', load_json)
    smpl['places'][0]['version'] = 3
    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        smpl,
        headers=get_headers(
            phone_id='01aaaaaaaaaaaaaaaaaaaa11', pass_flags='portal',
        ),
    )
    assert response.status_code == 409


@pytest.mark.filldb(user_places='with_place_type')
async def test_userplacesupdate_datasync_create_new(
        taxi_userplaces, load_json, mongodb, mockserver,
):
    datasync_called = False

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        nonlocal datasync_called
        datasync_called = True
        assert request.method == 'PUT'
        assert json.loads(request.get_data()) == DATASYNC_REQUEST

    smpl = load_sample_request('userplace-place-type', load_json)
    smpl['places'][0]['version'] = 0

    response = await taxi_userplaces.post(
        '3.0/userplacesupdate',
        smpl,
        headers=get_headers(
            phone_id='01aaaaaaaaaaaaaaaaaaaa12', pass_flags='portal',
        ),
    )
    assert response.status_code == 200
    data = response.json()
    assert data['places'][0]['version'] == 1
    assert datasync_called
    # Check DB changes
    entry = mongodb.user_places.find_one(
        {'phone_id': bson.ObjectId('01aaaaaaaaaaaaaaaaaaaa12')},
    )
    entry.pop('updated')
    entry.pop('created')
    entry.pop('touched')
    entry.pop('_id')
    assert entry == load_sample_entry(
        'userplace-place-type-new-datasync', load_json,
    )
