import pytest

from tests_driver_profile_view import utils as c


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_driver_banners(
        taxi_driver_profile_view, driver_authorizer, load_json, parks,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params={'park_id': 'db_id1'},
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'session1',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.parametrize(
    'params,headers,expected_code',
    [
        (c.AUTH_PARAMS, c.HEADERS, 401),
        (c.AUTH_PARAMS, {}, 400),
        ({'db': 'db_id1'}, c.HEADERS, 400),
        ({'session': 'session1'}, c.HEADERS, 400),
    ],
)
async def test_driver_banners_bad_response(
        taxi_driver_profile_view,
        params,
        headers,
        expected_code,
        parks,
        driver_authorizer,
):
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners', params=params, headers=headers,
    )
    assert response.status_code == expected_code


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor'),
        ('id_2', 'small_title', 'TITLE', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('tag', ARRAY['selfemployed'])]::banners.filter_t[],
        TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2)
        """,
    ],
)
@pytest.mark.driver_tags_match(
    dbid='db_id_selfemployed', uuid='uuid_selfemployed', tags=['selfemployed'],
)
async def test_driver_banners_tag_filter(
        taxi_driver_profile_view,
        driver_authorizer,
        mockserver,
        driver_tags_mocks,
        parks,
        taxi_config,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    driver_authorizer.set_session(
        'db_id_selfemployed', 'session2', 'uuid_selfemployed',
    )
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 1

    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params={'db': 'db_id_selfemployed', 'session': 'session2'},
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 2

    headers_v2 = c.HEADERS_V2.copy()
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers_v2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 1

    headers_v2['X-YaTaxi-Driver-Profile-Id'] = 'uuid_selfemployed'
    headers_v2['X-YaTaxi-Park-Id'] = 'db_id_selfemployed'
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers_v2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 2


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor'),
        ('id_2', 'small_title', 'TITLE', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        array[ROW('exclude_tag',
        ARRAY['test_tag', 'selfemployed'])]::banners.filter_t[],
        TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2)
        """,
    ],
)
@pytest.mark.driver_tags_match(
    dbid='db_id_selfemployed', uuid='uuid_selfemployed', tags=['selfemployed'],
)
async def test_driver_banners_exclude_tag_filter(
        taxi_driver_profile_view, driver_authorizer, parks,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    driver_authorizer.set_session(
        'db_id_selfemployed', 'session2', 'uuid_selfemployed',
    )
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 2

    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params={'db': 'db_id_selfemployed', 'session': 'session2'},
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 1

    headers_v2 = c.HEADERS_V2.copy()
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers_v2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 2

    headers_v2['X-YaTaxi-Driver-Profile-Id'] = 'uuid_selfemployed'
    headers_v2['X-YaTaxi-Park-Id'] = 'db_id_selfemployed'
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers_v2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == 1


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor'),
        ('id_2', 'small_title', 'TITLE', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('city', ARRAY['Минск','Киев'])]::banners.filter_t[],
        TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2)
        """,
    ],
)
@pytest.mark.parametrize(
    'city,expected_banners', [('Москва', 1), ('Минск', 2), ('Киев', 2)],
)
async def test_driver_banners_city_filter(
        taxi_driver_profile_view,
        driver_authorizer,
        parks,
        city,
        expected_banners,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    parks.set_park_info(c.AUTH_PARAMS['db'], 'rus', city)
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == expected_banners

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == expected_banners


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'bogginat'),
        ('id_2', 'small_title', 'TITLE', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('country', ARRAY['lva','srb'])]::banners.filter_t[],
        TRUE, 'bogginat')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2)
        """,
    ],
)
@pytest.mark.parametrize(
    'country,expected_banners', [('rus', 1), ('lva', 2), ('srb', 2)],
)
async def test_driver_banners_country_filter(
        taxi_driver_profile_view,
        driver_authorizer,
        parks,
        country,
        expected_banners,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    parks.set_park_info(c.AUTH_PARAMS['db'], country, 'some_city')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == expected_banners

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['items'][0]['banners']) == expected_banners


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], FALSE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_driver_banner_disabled(
        taxi_driver_profile_view, driver_authorizer, parks,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    expected_response = {
        'items': [
            {
                'type': 'banner_gallery',
                'horizontal_divider_type': 'none',
                'banners': [],
            },
        ],
    }
    assert response.json() == expected_response

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor'),
        ('id_2', 'small_title', 'TITLE', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[],
        TRUE, 'laidegor'),
        ('id_3', 'small_title_hint', 'TITLE', 'SUBTITLE',
        'blue', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[],
        TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2), ('id_3', 3)
        """,
    ],
)
async def test_driver_banners_order(
        taxi_driver_profile_view, driver_authorizer, parks,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    banners = response['items'][0]['banners']
    assert [banner['id'] for banner in banners] == ['id_1', 'id_2', 'id_3']
    types = [banner['type'] for banner in banners]
    assert types == ['big_title_hint', 'small_title', 'small_title_hint']
    subtitles = [banner.get('subtitle') for banner in banners]
    assert subtitles[1] is None and subtitles[0] and subtitles[2]

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    response = response.json()
    banners = response['items'][0]['banners']
    assert [banner['id'] for banner in banners] == ['id_1', 'id_2', 'id_3']
    types = [banner['type'] for banner in banners]
    assert types == ['big_title_hint', 'small_title', 'small_title_hint']
    subtitles = [banner.get('subtitle') for banner in banners]
    assert subtitles[1] is None and subtitles[0] and subtitles[2]


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'BAD_TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[]::banners.filter_t[], TRUE, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_driver_banners_no_translations(
        taxi_driver_profile_view, parks, driver_authorizer,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    assert not response['items'][0]['banners']

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    response = response.json()
    assert not response['items'][0]['banners']


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'banner_title_driver',
        'SUBTITLE', 'red', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('tag', ARRAY['selfreg_v2_driver_unreg'])]
        ::banners.filter_t[],
        TRUE, 'bogginat'),
        ('id_2', 'small_title', 'banner_title_profi', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('tag', ARRAY['selfreg_v2_profi_unreg'])]
        ::banners.filter_t[],
        TRUE, 'bogginat'),
        ('id_3', 'small_title', 'banner_title_courier', NULL,
        'green', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('tag', ARRAY['selfreg_v2_courier_unreg'])]
        ::banners.filter_t[],
        TRUE, 'bogginat')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1), ('id_2', 2), ('id_3', 3)
        """,
    ],
)
@pytest.mark.parametrize(
    'selfreg_type,selfreg_tags,status_code,expected_title',
    [
        (None, None, 401, None),
        ('driver', None, 200, 'Баннер для водителя'),
        ('profi', None, 200, 'Баннер для профи'),
        ('courier', None, 200, 'Баннер для курьера'),
        ('profi', ['selfreg_v2_driver_unreg'], 200, 'Баннер для водителя'),
        ('profi', ['selfreg_v2_profi_unreg'], 200, 'Баннер для профи'),
        ('profi', ['selfreg_v2_courier_unreg'], 200, 'Баннер для курьера'),
    ],
)
async def test_driver_banners_v2_selfreg(
        taxi_driver_profile_view,
        mockserver,
        taxi_config,
        selfreg,
        selfreg_type,
        selfreg_tags,
        status_code,
        expected_title,
):
    if selfreg_type is None:
        selfreg.set_error_code(500)
    elif selfreg_type != 'profi':
        selfreg.set_selfreg(selfreg_type=selfreg_type, mock_tags=selfreg_tags)
    else:
        selfreg.set_selfreg(mock_tags=selfreg_tags)

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners',
        headers=c.UNAUTH_HEADERS_V2,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == status_code
    if status_code != 200:
        return
    response_json = response.json()
    assert response_json['items'][0]['banners'][0]['title'] == expected_title


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, screen)
        VALUES ('id_1', 'small_title_hint', 'support_1',
        'SUBTITLE', 'yellow_warn', 'taximeter:/click_url',
        'deeplink',ARRAY[]::banners.filter_t[], TRUE,
        'bogginat','support'),
        ('id_2', 'small_title_hint', 'support_2',
        'SUBTITLE', 'yellow_warn', 'taximeter:/click_url',
        'deeplink', ARRAY[]::banners.filter_t[], TRUE,
        'bogginat','support')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 2), ('id_2', 1)
        """,
    ],
)
async def test_driver_banners_support(
        taxi_driver_profile_view, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners/support', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_support.json')


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, screen)
        VALUES ('id_3', 'small_title_hint', 'support_2',
        'SUBTITLE', 'yellow_warn', NULL,
        NULL, ARRAY[]::banners.filter_t[], TRUE,
        'bogginat','support')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_3', 3)
        """,
    ],
)
async def test_driver_banners_support_no_url(
        taxi_driver_profile_view, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners/support', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response_support.json')
    del expected_response['items'][0]['payload']
    del expected_response['items'][0]['right_icon']
    assert response.json() == expected_response


async def test_driver_banners_no_banners_for_support(
        taxi_driver_profile_view, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners/support', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, screen)
        VALUES ('id_1', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink',ARRAY[ROW('app',
        ARRAY['pro'])]::banners.filter_t[], TRUE,
        'bogginat', 'profile'),
        ('id_2', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('app',
        ARRAY['uber'])]::banners.filter_t[], TRUE,
        'bogginat', 'profile'),
        ('id_3', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('app', ARRAY['uber', 'pro'])]
        ::banners.filter_t[], TRUE, 'bogginat','profile'),
        ('id_4', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[]::banners.filter_t[],
        TRUE, 'bogginat','profile'),
        ('id_5', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('app',
        ARRAY['not_exist'])]::banners.filter_t[],
        TRUE, 'bogginat','profile'),
        ('id_6', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('app',
        ARRAY['yango'])]::banners.filter_t[],
        TRUE, 'bogginat','profile')

        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 2), ('id_2', 1), ('id_3', 3),
        ('id_4', 4), ('id_5', 5), ('id_6', 6)
        """,
    ],
)
@pytest.mark.parametrize(
    'app_type,expected_response',
    [
        ('uberdriver', 'expected_uber_response.json'),
        ('taximeter', 'expected_pro_response.json'),
        ('yango', 'expected_yango_response.json'),
    ],
)
async def test_driver_banners_app_filter(
        taxi_driver_profile_view,
        load_json,
        driver_authorizer,
        parks,
        app_type,
        expected_response,
):
    headers = c.HEADERS_V2.copy()
    if app_type == 'uberdriver':
        headers['User-Agent'] = 'Taximeter-Uber 8.80 (562)'
        headers['X-Request-Version-Type'] = 'uber'
    if app_type == 'yango':
        headers[
            'X-Request-Application'
        ] = 'app_brand=yango,app_name=yango_android'
        headers['X-Request-Version-Type'] = 'yango'
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)

    if app_type == 'yango':
        return
    headers = c.HEADERS.copy()
    if app_type == 'uberdriver':
        headers['User-Agent'] = 'Taximeter-Uber 8.80 (562)'
    driver_authorizer.set_client_session(
        app_type, 'db_id1', 'session1', 'uuid1',
    )
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, screen)
        VALUES ('id_1', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink',ARRAY[ROW('platform',
        ARRAY['android'])]::banners.filter_t[], TRUE,
        'bogginat', 'profile'),
        ('id_2', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['ios'])]::banners.filter_t[], TRUE,
        'bogginat', 'profile'),
        ('id_3', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['ios', 'android'])]
        ::banners.filter_t[], TRUE, 'bogginat','profile'),
        ('id_4', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[]::banners.filter_t[],
        TRUE, 'bogginat','profile'),
        ('id_5', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['not_exist'])]::banners.filter_t[],
        TRUE, 'bogginat','profile')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 2), ('id_2', 1), ('id_3', 3),
        ('id_4', 4), ('id_5', 5)
        """,
    ],
)
@pytest.mark.parametrize(
    'platform_type,expected_response',
    [
        ('ios', 'expected_ios_response.json'),
        ('android', 'expected_android_response.json'),
    ],
)
async def test_driver_banners_platform_filter(
        taxi_driver_profile_view,
        load_json,
        driver_authorizer,
        parks,
        platform_type,
        expected_response,
):
    headers = c.HEADERS_V2.copy()
    if platform_type == 'ios':
        headers['X-Request-Platform'] = 'ios'
        headers['User-Agent'] = 'Taximeter 8.80 (562) ios'
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)

    headers = c.HEADERS.copy()
    if platform_type == 'ios':
        headers['X-Request-Platform'] = 'ios'
        headers['User-Agent'] = 'Taximeter 8.80 (562) ios'
    driver_authorizer.set_client_session(
        'taximeter', 'db_id1', 'session1', 'uuid1',
    )
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id1_with_auth', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', '{}',
        'navigate_url',
        ARRAY[]::banners.filter_t[], TRUE, 'bogginat')
        """.format(
            c.V1_BANNERS_REDIRECT_URL,
        ),
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id1_with_auth', 1)
        """,
    ],
)
async def test_driver_banners_v2_with_auth(
        taxi_driver_profile_view, driver_authorizer, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    expected_response['items'][0]['banners'][0]['payload'][
        'type'
    ] = 'navigate_url'
    expected_response['items'][0]['banners'][0]['payload'][
        'url'
    ] = c.V2_BANNERS_REDIRECT_URL
    expected_response['items'][0]['banners'][0]['id'] = 'id1_with_auth'
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', '{}',
        'navigate_url',
        ARRAY[]::banners.filter_t[], TRUE, 'bogginat')
        """.format(
            c.V1_BANNERS_REDIRECT_URL,
        ),
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_driver_banners_v2_with_auth_wrong_id(
        taxi_driver_profile_view, driver_authorizer, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    expected_response['items'][0]['banners'][0]['payload'][
        'type'
    ] = 'navigate_url'
    expected_response['items'][0]['banners'][0]['payload'][
        'url'
    ] = c.V1_BANNERS_REDIRECT_URL
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id1_with_auth', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', '{}',
        'navigate_url',
        ARRAY[]::banners.filter_t[], TRUE, 'bogginat')
        """.format(
            c.V1_COVID_BANNERS_URL,
        ),
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id1_with_auth', 1)
        """,
    ],
)
async def test_driver_banners_v2_covid_banner(
        taxi_driver_profile_view, driver_authorizer, load_json, parks,
):
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    expected_response['items'][0]['banners'][0]['payload'][
        'type'
    ] = 'navigate_url'
    expected_response['items'][0]['banners'][0]['payload'][
        'url'
    ] = c.V2_COVID_BANNERS_URL
    expected_response['items'][0]['banners'][0]['id'] = 'id1_with_auth'
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author)
        VALUES ('id_1', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'red', NULL, NULL,
        ARRAY[]::banners.filter_t[], TRUE, 'bogginat')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_driver_banners_no_url(
        taxi_driver_profile_view, parks, driver_authorizer,
):
    driver_authorizer.set_session('db_id1', 'session1', 'uuid1')
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=c.HEADERS,
    )
    expected_banner = {
        'background_color': '#F5523A',
        'id': 'id_1',
        'subtitle': 'subtilte_translated',
        'tint_color': '#FFBA8F',
        'title': 'tilte_translated',
        'type': 'big_title_hint',
    }
    assert response.status_code == 200
    response = response.json()
    assert response['items'][0]['banners'][0] == expected_banner

    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=c.HEADERS_V2,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['items'][0]['banners'][0] == expected_banner


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, screen) VALUES
        ('id_3', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['android:9.78'])]
        ::banners.filter_t[], TRUE, 'bogginat','profile'),
        ('id_4', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['android:9.77'])]::banners.filter_t[],
        TRUE, 'bogginat','profile'),
        ('id_5', 'small_title_hint', 'TITLE',
        'SUBTITLE', 'red', 'taximeter:/click_url',
        'deeplink', ARRAY[ROW('platform',
        ARRAY['android:9.56'])]::banners.filter_t[],
        TRUE, 'bogginat','profile')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_3', 3), ('id_4', 4), ('id_5', 5)
        """,
    ],
)
async def test_driver_banners_version_filter(
        taxi_driver_profile_view, load_json, driver_authorizer, parks,
):
    headers = c.HEADERS_V2.copy()
    response = await taxi_driver_profile_view.post(
        'driver/v1/profile-view/v2/banners', headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    banners = response_json['items'][0]['banners']
    assert len(banners) == 2

    headers = c.HEADERS.copy()
    driver_authorizer.set_client_session(
        'taximeter', 'db_id1', 'session1', 'uuid1',
    )
    response = await taxi_driver_profile_view.post(
        'driver/profile-view/v1/banners',
        params=c.AUTH_PARAMS,
        headers=headers,
    )
    banners = response_json['items'][0]['banners']
    assert len(banners) == 2
