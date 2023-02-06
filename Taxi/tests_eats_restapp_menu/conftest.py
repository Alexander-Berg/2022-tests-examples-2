import json

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_restapp_menu_plugins import *  # noqa: F403 F401


@pytest.fixture()
def mock_place_access_400(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_func(request):
        req_json = request.json
        assert req_json['partner_id'] == 777 and req_json['place_ids'] == [
            109151,
        ]
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )

    return _mock_func


@pytest.fixture()
def mock_place_access_200(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_func(request):
        req_json = request.json
        assert req_json['partner_id'] == 777 and (
            req_json['place_ids'] == [109151]
            or req_json['place_ids'] == [109152]
        )
        return {}

    return _mock_func


@pytest.fixture()
def mock_write_access_403(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_func(request):
        req_json = request.json
        assert (
            req_json['partner_id'] == 777
            and req_json['place_ids'] == [109151]
            and req_json['permissions'] == ['permission.restaurant.menu']
        )
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': (
                    'Some permissions are missing or places are forbidden'
                ),
            },
        )

    return _mock_func


@pytest.fixture()
def mock_write_access_200(mockserver):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_func(request):
        req_json = request.json
        assert (
            req_json['partner_id'] == 777
            and req_json['place_ids'] == [109151]
            and req_json['permissions'] == ['permission.restaurant.menu']
        )
        return {}

    return _mock_func


@pytest.fixture()
def pg_get_revisions(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_revisions
            ORDER BY place_id, revision
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture()
def pg_get_menu_content(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_content
            ORDER BY place_id, menu_hash
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture()
def pg_get_item_nutrients(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_item_nutrients
            ORDER BY place_id, origin_id
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture
def mock_eats_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage(request):
        assert request.json['projection'] == ['address', 'brand']
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {
                        'id': request.json['place_ids'][0],
                        'revision_id': 0,
                        'updated_at': '1970-01-02T00:00:00.000Z',
                        'address': {'city': 'Москва', 'short': 'qwerty'},
                    },
                ],
                'not_found_place_ids': [],
            },
        )


@pytest.fixture
def mock_eats_catalog_storage_404(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_eats_catalog_storage_400(request):
        assert request.json['projection'] == ['address', 'brand']
        return mockserver.make_response(
            status=200,
            json={
                'places': [],
                'not_found_place_ids': request.json['place_ids'],
            },
        )


@pytest.fixture(name='mock_eats_moderation')
def _mock_eats_moderation(mockserver):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _eats_moderation(request):
        assert request.json['scope'] == 'eda'
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})

    return _eats_moderation


@pytest.fixture()
def pg_get_pictures(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.pictures
            ORDER BY avatarnica_identity
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture()
def pg_get_menus(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menus
            ORDER BY place_id, id
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture()
def pg_get_categories_by_parts(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        res = {}

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_to_categories
            ORDER BY hash
        """,
        )
        res['to_categories'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_categories
            ORDER BY hash
        """,
        )
        res['categories'] = cursor.fetchall()

        return res

    return _mock_func


@pytest.fixture()
def pg_get_items_by_parts(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        res = {}

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_to_items
            ORDER BY hash
        """,
        )
        res['to_items'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_items
            ORDER BY hash
        """,
        )
        res['items'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_item_data_bases
            ORDER BY hash
        """,
        )
        res['item_data_bases'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_item_data
            ORDER BY hash
        """,
        )
        res['item_data'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_options_bases
            ORDER BY hash
        """,
        )
        res['options_bases'] = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.menu_options
            ORDER BY hash
        """,
        )
        res['options'] = cursor.fetchall()

        return res

    return _mock_func


@pytest.fixture()
def pg_get_revision_transitions(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                eats_restapp_menu.revision_transitions
            ORDER BY place_id, old_revision
        """,
        )
        return cursor.fetchall()

    return _mock_func


@pytest.fixture()
def pg_get_categories(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                mtc.categories_hash,
                mtc.category_hash,
                mc.json,
                mc.origin_id
            FROM
            (
                SELECT hash AS categories_hash, UNNEST(hashes) AS category_hash
                FROM eats_restapp_menu.menu_to_categories
            ) mtc
            INNER JOIN eats_restapp_menu.menu_categories mc
                ON mc.hash = mtc.category_hash
            ORDER BY mtc.categories_hash, mtc.category_hash
        """,
        )

        rows = cursor.fetchall()
        for row in rows:
            row['json'] = json.loads(row['json'])

        return rows

    return _mock_func


@pytest.fixture()
def pg_get_items(pgsql):
    def _mock_func():
        cursor = pgsql['eats_restapp_menu'].dict_cursor()

        cursor.execute(
            """
            SELECT
                mti.items_hash,
                mti.item_hash,
                mi.data_base_hash,
                mi.data_hash,
                mi.options_base_hash,
                mi.options_hash,
                mi.origin_id,
                midb.json AS data_base_json,
                mid.json AS data_json,
                mob.json AS options_base_json,
                mo.json AS options_json
            FROM
            (
                SELECT hash AS items_hash, UNNEST(hashes) AS item_hash
                FROM eats_restapp_menu.menu_to_items
            ) mti
            INNER JOIN eats_restapp_menu.menu_items mi
                ON mi.hash = mti.item_hash
            INNER JOIN eats_restapp_menu.menu_item_data_bases midb
                ON midb.hash = mi.data_base_hash
            INNER JOIN eats_restapp_menu.menu_item_data mid
                ON mid.hash = mi.data_hash
            INNER JOIN eats_restapp_menu.menu_options_bases mob
                ON mob.hash = mi.options_base_hash
            INNER JOIN eats_restapp_menu.menu_options mo
                ON mo.hash = mi.options_hash
            ORDER BY mti.items_hash, mti.item_hash
        """,
        )

        rows = cursor.fetchall()
        for row in rows:
            row['data_base_json'] = json.loads(row['data_base_json'])
            row['data_json'] = json.loads(row['data_json'])
            row['options_base_json'] = json.loads(row['options_base_json'])
            row['options_json'] = json.loads(row['options_json'])

        return rows

    return _mock_func


@pytest.fixture(
    scope='module',
    params=[
        pytest.param(0, id='empty_reasons'),
        pytest.param(1, id='2_reasons'),
        pytest.param(2, id='1_reason_code'),
        pytest.param(
            2,
            id='1_reason_code_config',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MODERATION_CODES_MAPPING={
                        'some_code2': 'not_changed',
                        'other_code': 'not_changed',
                    },
                ),
            ],
        ),
        pytest.param(
            3,
            id='1_reason_code_changed',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_MODERATION_CODES_MAPPING={
                        'some_code': 'CHANGED',
                        'other_code': 'not_changed',
                    },
                ),
            ],
        ),
    ],
)
def get_parametrized_config(request):
    params = (
        {
            'reasons': [],
            'expected': {'items': [{'id': '1234595', 'codes': []}]},
        },
        {
            'reasons': [
                {
                    'reason_text': 'непонравилось что-то',
                    'reason_title': 'заголовок',
                },
                {'reason_text': 'тут тоже', 'reason_title': 'заголовок2'},
            ],
            'expected': {
                'items': [
                    {
                        'id': '1234595',
                        'codes': [
                            {
                                'code': 'unknown_error',
                                'source': 'moderation',
                                'message': 'непонравилось что-то',
                            },
                            {
                                'code': 'unknown_error',
                                'source': 'moderation',
                                'message': 'тут тоже',
                            },
                        ],
                    },
                ],
            },
        },
        {
            'reasons': [
                {
                    'reason_text': 'непонравилось что-то',
                    'reason_title': 'заголовок',
                    'reason_code': 'some_code',
                },
            ],
            'expected': {
                'items': [
                    {
                        'id': '1234595',
                        'codes': [
                            {
                                'code': 'some_code',
                                'source': 'moderation',
                                'message': 'непонравилось что-то',
                            },
                        ],
                    },
                ],
            },
        },
        {
            'reasons': [
                {
                    'reason_text': 'непонравилось что-то',
                    'reason_title': 'заголовок',
                    'reason_code': 'some_code',
                },
            ],
            'expected': {
                'items': [
                    {
                        'id': '1234595',
                        'codes': [
                            {
                                'code': 'CHANGED',
                                'source': 'moderation',
                                'message': 'непонравилось что-то',
                            },
                        ],
                    },
                ],
            },
        },
    )

    return params[request.param]
