import pytest

URL = '3.0/userplacesremove'

USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'
EMPTY_REQUEST = {'id': USER_ID, 'places': []}


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


@pytest.mark.config(USERPLACES_SERVICE_ENABLED=False)
async def test_userplacesremove_service_disabled(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=EMPTY_REQUEST, headers=get_headers(),
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Userplaces: forbidden',
    }


@pytest.mark.config(USERPLACES_DISABLE_REMOVES=True)
async def test_userplacesremove_disable_removes(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=EMPTY_REQUEST, headers=get_headers(),
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Userplaces: remove disabled',
    }


async def test_unauthorized(taxi_userplaces):
    """
    no header X-Yandex-UID
    """
    response = await taxi_userplaces.post(
        URL, json=EMPTY_REQUEST, headers=get_headers(uid=None),
    )
    assert response.status_code == 401, response.text
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_no_phone_id(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL, json=EMPTY_REQUEST, headers=get_headers(phone_id=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_userplacesremove_no_app_name(taxi_userplaces):
    response = await taxi_userplaces.post(
        URL,
        json=EMPTY_REQUEST,
        headers=get_headers(phone_id=None, app_name=None),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


async def test_simple(taxi_userplaces, mongodb):
    # Query

    request = {
        'id': USER_ID,
        'places': [
            {'id': 'home', 'version': 123},
            {'id': '00000004-AAAA-AAAA-AAAA-000000000003', 'version': 123},
        ],
    }
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert doc is None

    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000003'},
    )
    assert doc is None


@pytest.mark.parametrize(
    'place_id, ypa_fail, expect_fail',
    [
        pytest.param(
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
            '00000004-AAAA-AAAA-AAAA-000000000003',
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
            '00000004-AAAA-AAAA-AAAA-000000000003',
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
            '00000004-AAAA-AAAA-AAAA-000000000003',
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
async def test_ypa_delete(
        taxi_userplaces, place_id, mockserver, ypa_fail, expect_fail,
):
    @mockserver.json_handler('/ya-pers-address/address/delete')
    def _mock_ypa_delete(request):
        assert request.query['user_id'] == DEFAULT_UID
        assert request.query['user_type'] == 'uid'
        assert request.query['id'] == place_id
        if ypa_fail:
            return mockserver.make_response(status=500)
        return {'status': 'ok'}

    request = {'id': USER_ID, 'places': [{'id': place_id, 'version': 123}]}
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(),
    )

    assert _mock_ypa_delete.has_calls
    expected_code = 500 if expect_fail else 200
    assert response.status_code == expected_code


async def test_version_conflict(taxi_userplaces):
    request = {
        'id': USER_ID,
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000003', 'version': 457},
        ],
    }
    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(),
    )

    # Check response
    assert response.status_code == 409


async def test_userplacesremove_another_brand(taxi_userplaces, mongodb):
    request = {
        'id': USER_ID,
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000003', 'version': 123},
        ],
    }
    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(app_name='uber_iphone'),
    )

    # Check response
    assert response.status_code == 200
    assert response.json() == {}
    doc = mongodb.user_places.find_one({'_id': request['places'][0]['id']})
    assert doc


@pytest.mark.parametrize('scenario', ['portal_uid', 'phonish_uid'])
async def test_userplacesremove_portal_auth(
        taxi_userplaces, mongodb, scenario,
):
    request = {
        'id': USER_ID,
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000003', 'version': 123},
        ],
    }
    pass_flags = ''
    uid = '50000000001'

    if scenario == 'portal_uid':
        pass_flags = 'portal'
    elif scenario == 'phonish_uid':
        pass_flags = 'phonish'

    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(pass_flags=pass_flags, uid=uid),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    doc = mongodb.user_places.find_one({'_id': request['places'][0]['id']})
    assert doc is None


async def test_userplacesremove_home_another_brand(taxi_userplaces, mongodb):
    request = {'id': USER_ID, 'places': [{'id': 'home', 'version': 123}]}

    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(app_name='uber_android'),
    )

    # Check response
    assert response.status_code == 200
    assert response.json() == {}
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert doc
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000005'},
    )
    assert doc is None


async def test_userplacesremove_datasync(taxi_userplaces, mongodb, mockserver):
    request = {'id': USER_ID, 'places': [{'id': 'home', 'version': 123}]}
    datasync_called = False

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        nonlocal datasync_called
        datasync_called = True
        assert request.method == 'DELETE'

    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(pass_flags='portal'),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    assert datasync_called
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert doc is None


@pytest.mark.config(USERPLACES_USE_DATASYNC=False)
async def test_userplacesremove_datasync_disabled(
        taxi_userplaces, mongodb, mockserver,
):
    request = {'id': USER_ID, 'places': [{'id': 'home', 'version': 123}]}

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert False

    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(pass_flags='portal'),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert doc is None


async def test_userplacesremove_datasync_place_type_conflict(
        taxi_userplaces, mongodb, mockserver,
):
    request = {'id': USER_ID, 'places': [{'id': 'home', 'version': 456}]}

    @mockserver.json_handler('/datasync/v2/personality/profile/addresses/home')
    def _mock_datasync(request):
        assert False

    # Query
    response = await taxi_userplaces.post(
        URL, json=request, headers=get_headers(pass_flags='portal'),
    )

    # Check response
    assert response.status_code == 409
    doc = mongodb.user_places.find_one(
        {'_id': '00000004-AAAA-AAAA-AAAA-000000000001'},
    )
    assert doc


async def test_userplacesremove_portal_userplace(taxi_userplaces, mongodb):
    request = {
        'id': USER_ID,
        'places': [
            {'id': '00000004-AAAA-AAAA-AAAA-000000000007', 'version': 123},
        ],
    }
    # Query
    response = await taxi_userplaces.post(
        URL,
        json=request,
        headers=get_headers(pass_flags='portal', uid=DEFAULT_UID),
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data == {}

    doc = mongodb.user_places.find_one({'_id': request['places'][0]['id']})
    assert doc is None
