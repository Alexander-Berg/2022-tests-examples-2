import pytest


def fetch_banners_from_db(pgsql):
    cursor = pgsql['driver_profile_view'].cursor()
    cursor.execute(
        """
        SELECT
          banner.id,
          banner.type,
          banner.title_key,
          banner.subtitle_key,
          banner.color,
          banner.click_url,
          banner.click_url_type,
          banner.is_external,
          banner.filters,
          banner.is_enabled,
          banner.author,
          banner.screen,
          pos.position
        FROM banners.value AS banner
        INNER JOIN banners.position as pos
        ON banner.id = pos.id
    """,
    )
    result = [row for row in cursor]
    cursor.close()
    return result


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
        ARRAY[ROW('tag', ARRAY['selfemployed'])]::banners.filter_t[],
        True, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_service_banners_get(taxi_driver_profile_view, load_json):
    response = await taxi_driver_profile_view.get(
        'service/profile-view/v1/banners?id=id_1',
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_get_response.json')


async def test_service_banners_put(taxi_driver_profile_view, pgsql):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'big_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': 'red',
                'payload': {
                    'click_url_type': 'deeplink',
                    'click_url': 'taximeter:/click_url',
                },
                'filters': [{'type': 'tag', 'value': ['selfemployed']}],
                'is_enabled': True,
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'laidegor'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    banners = fetch_banners_from_db(pgsql)
    assert banners[0] == (
        'id_1',
        'big_title_hint',
        'TITLE',
        'SUBTITLE',
        'red',
        'taximeter:/click_url',
        'deeplink',
        None,
        '{"(tag,{selfemployed})"}',
        True,
        'laidegor',
        'profile',
        1,
    )


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
        ARRAY[]::banners.filter_t[],
        True, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_service_banners_put_change_position(
        taxi_driver_profile_view, pgsql,
):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'small_title',
                'title_key': 'TITLE2',
                'color': 'green',
                'payload': {
                    'click_url_type': 'navigate_url',
                    'click_url': 'taxi.yandex.ru',
                    'is_external': True,
                },
                'filters': [],
                'is_enabled': False,
                'position': 4,
            },
        },
        headers={'X-Yandex-Login': 'someoneelse'},
    )
    assert response.status_code == 200
    banners = fetch_banners_from_db(pgsql)
    assert banners[0] == (
        'id_1',
        'small_title',
        'TITLE2',
        None,
        'green',
        'taxi.yandex.ru',
        'navigate_url',
        True,
        '{}',
        False,
        'someoneelse',
        'profile',
        4,
    )


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
        ARRAY[]::banners.filter_t[],
        True, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_service_banners_put_override_banner(
        taxi_driver_profile_view, pgsql,
):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_3',
                'type': 'big_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': 'red',
                'payload': {
                    'click_url_type': 'deeplink',
                    'click_url': 'taximeter:/click_url',
                },
                'filters': [],
                'is_enabled': True,
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'laidegor'},
    )
    assert response.status_code == 406


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
async def test_service_banners_list(
        taxi_driver_profile_view, pgsql, load_json,
):
    response = await taxi_driver_profile_view.get(
        'service/profile-view/v1/banners/list',
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_list_response.json')


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
        ARRAY[ROW('tag', ARRAY['selfemployed'])]::banners.filter_t[],
        True, 'laidegor')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_remove_banner(taxi_driver_profile_view, pgsql):
    response = await taxi_driver_profile_view.delete(
        'service/profile-view/v1/banners?id=id_1',
    )
    assert response.status_code == 200
    assert response.json() == {}
    banners = fetch_banners_from_db(pgsql)
    assert not banners


async def test_remove_banner_not_found(taxi_driver_profile_view, pgsql):
    response = await taxi_driver_profile_view.delete(
        'service/profile-view/v1/banners?id=id_1',
    )
    assert response.status_code == 404


@pytest.mark.parametrize('color,code', [('yellow_warn', 200), ('red', 400)])
async def test_service_banners_put_support(
        taxi_driver_profile_view, pgsql, color, code,
):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'small_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': color,
                'payload': {
                    'click_url_type': 'deeplink',
                    'click_url': 'taximeter:/click_url',
                },
                'filters': [{'type': 'tag', 'value': ['selfemployed']}],
                'is_enabled': True,
                'screen': 'support',
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'bogginat'},
    )
    assert response.status_code == code
    if code == 200:
        assert response.json() == {}
    else:
        assert response.json() == {
            'code': '400',
            'message': 'incorrect color: red',
        }
    if code == 200:
        banners = fetch_banners_from_db(pgsql)
        assert banners[0] == (
            'id_1',
            'small_title_hint',
            'TITLE',
            'SUBTITLE',
            'yellow_warn',
            'taximeter:/click_url',
            'deeplink',
            None,
            '{"(tag,{selfemployed})"}',
            True,
            'bogginat',
            'support',
            1,
        )


@pytest.mark.parametrize(
    'filters,filter_result',
    [
        ([{'type': 'app', 'value': ['not_exist']}], None),
        ([{'type': 'app', 'value': ['yango']}], '{"(app,{yango})"}'),
        ([{'type': 'app', 'value': ['uber']}], '{"(app,{uber})"}'),
        ([{'type': 'app', 'value': ['uber:1.85']}], '{"(app,{uber:1.85})"}'),
        ([{'type': 'app', 'value': ['pro']}], '{"(app,{pro})"}'),
        ([{'type': 'app', 'value': ['pro:53.14']}], '{"(app,{pro:53.14})"}'),
        (
            [{'type': 'app', 'value': ['pro', 'uber']}],
            '{"(app,\\"{pro,uber}\\")"}',
        ),
        (
            [{'type': 'app', 'value': ['pro', 'yango']}],
            '{"(app,\\"{pro,yango}\\")"}',
        ),
    ],
)
async def test_service_banners_put_app_filter(
        taxi_driver_profile_view, pgsql, filters, filter_result,
):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'big_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': 'red',
                'payload': {
                    'click_url_type': 'deeplink',
                    'click_url': 'taximeter:/click_url',
                },
                'filters': filters,
                'is_enabled': True,
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'bogginat'},
    )
    if filter_result is None:
        assert response.status_code == 400
        return
    assert response.status_code == 200
    assert response.json() == {}
    banners = fetch_banners_from_db(pgsql)
    assert banners[0] == (
        'id_1',
        'big_title_hint',
        'TITLE',
        'SUBTITLE',
        'red',
        'taximeter:/click_url',
        'deeplink',
        None,
        filter_result,
        True,
        'bogginat',
        'profile',
        1,
    )


@pytest.mark.parametrize(
    'filters,filter_result',
    [
        ([{'type': 'platform', 'value': ['not_exist']}], None),
        ([{'type': 'platform', 'value': ['ios']}], '{"(platform,{ios})"}'),
        (
            [{'type': 'platform', 'value': ['ios:1.89']}],
            '{"(platform,{ios:1.89})"}',
        ),
        (
            [{'type': 'platform', 'value': ['android']}],
            '{"(platform,{android})"}',
        ),
        (
            [{'type': 'platform', 'value': ['ios:1.34', 'android:54.12']}],
            '{"(platform,\\"{ios:1.34,android:54.12}\\")"}',
        ),
    ],
)
async def test_service_banners_put_platform_filter(
        taxi_driver_profile_view, pgsql, filters, filter_result,
):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'big_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': 'red',
                'payload': {
                    'click_url_type': 'deeplink',
                    'click_url': 'taximeter:/click_url',
                },
                'filters': filters,
                'is_enabled': True,
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'bogginat'},
    )
    if filter_result is None:
        assert response.status_code == 400
        return
    assert response.status_code == 200
    assert response.json() == {}
    banners = fetch_banners_from_db(pgsql)
    assert banners[0] == (
        'id_1',
        'big_title_hint',
        'TITLE',
        'SUBTITLE',
        'red',
        'taximeter:/click_url',
        'deeplink',
        None,
        filter_result,
        True,
        'bogginat',
        'profile',
        1,
    )


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
        ARRAY[ROW('tag', ARRAY['selfemployed'])]::banners.filter_t[],
        True, 'bogginat')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_1', 1)
        """,
    ],
)
async def test_service_banners_get_no_url(taxi_driver_profile_view, load_json):
    response = await taxi_driver_profile_view.get(
        'service/profile-view/v1/banners?id=id_1',
    )
    assert response.status_code == 200
    expected_response = load_json('expected_get_response.json')
    del expected_response['banner']['payload']
    expected_response['author'] = 'bogginat'
    expected_response['banner']['position'] = 1.0
    assert response.json() == expected_response


async def test_service_banners_put_no_url(taxi_driver_profile_view, pgsql):
    response = await taxi_driver_profile_view.put(
        'service/profile-view/v1/banners?id=id_1',
        json={
            'banner': {
                'id': 'id_1',
                'type': 'big_title_hint',
                'title_key': 'TITLE',
                'subtitle_key': 'SUBTITLE',
                'color': 'red',
                'filters': [{'type': 'tag', 'value': ['selfemployed']}],
                'is_enabled': True,
                'position': 1,
            },
        },
        headers={'X-Yandex-Login': 'bogginat'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    banners = fetch_banners_from_db(pgsql)
    assert banners[0] == (
        'id_1',
        'big_title_hint',
        'TITLE',
        'SUBTITLE',
        'red',
        None,
        None,
        None,
        '{"(tag,{selfemployed})"}',
        True,
        'bogginat',
        'profile',
        1,
    )


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO banners.value
        (id, type, title_key, subtitle_key, color,
        click_url, click_url_type, filters,
        is_enabled, author, permit)
        VALUES ('id_7', 'big_title_hint', 'TITLE',
        'SUBTITLE', 'blue', 'taximeter:/click_url', 'deeplink',
        ARRAY[ROW('tag', ARRAY['selfemployed'])]::banners.filter_t[],
        True, 'sheen7', 'support')
        """,
        """
        INSERT INTO banners.position (id, position)
        VALUES ('id_7', 1)
        """,
    ],
)
async def test_service_banners_get_permit(taxi_driver_profile_view, load_json):
    response = await taxi_driver_profile_view.get(
        'service/profile-view/v1/banners?id=id_7',
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_get_permit_response.json')
