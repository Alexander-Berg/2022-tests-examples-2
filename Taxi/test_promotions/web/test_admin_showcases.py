import copy
import datetime
import typing

import pytest

from taxi.util import dates

# pylint: disable=import-only-modules
from .test_admin_collections import DEFAULT_COLLECTION

DEFAULT_SHOWCASE_ID = 'default_showcase_id'
PUBLISHED_SHOWCASE_ID = 'published_showcase_id'
NON_EXISTING_SHOWCASE_ID = 'non_existing_showcase_id'
SHOWCASE_WITH_UNTITLED_COLLECTION_ID = 'showcase_with_untitled_collection_id'
NON_EXISTING_COLLECTION_ID = 'non_existing_collection_id'
DEFAULT_SHOWCASE: typing.Dict[str, typing.Any] = {
    'name': 'default_showcase_name',
    'blocks': [
        {
            'title': 'key',
            'personalized_title': 'personalized_key',
            'is_tanker_key': True,
            'collection_id': 'default_collection_id',
        },
    ],
    'screens': ['ANY_SCREEN'],
}
SHOWCASE_WITH_UNTITLED_COLLECTION: typing.Dict[str, typing.Any] = {
    'name': 'showcase_with_untitled_collection_name',
    'blocks': [{'collection_id': 'default_collection_id'}],
    'screens': ['ANY_SCREEN'],
}


@pytest.mark.parametrize(
    'showcase, expected_status, expected_code',
    [
        pytest.param(
            DEFAULT_SHOWCASE,
            200,
            None,
            id='ok',
            marks=pytest.mark.pgsql(
                'promotions', files=['pg_promotions_collections.sql'],
            ),
        ),
        pytest.param(
            SHOWCASE_WITH_UNTITLED_COLLECTION,
            200,
            None,
            id='ok with untitled collection block',
            marks=pytest.mark.pgsql(
                'promotions', files=['pg_promotions_collections.sql'],
            ),
        ),
        pytest.param(
            {
                'name': 'showcase_name',
                'blocks': [
                    {
                        'title': 'non_existent_key',
                        'personalized_title': 'non_existent_key',
                        'is_tanker_key': True,
                        'collection_id': 'collection_id_1',
                    },
                ],
                'screens': ['ANY_SCREEN'],
            },
            404,
            'not_found',
            id='tanker keys not found',
            marks=pytest.mark.pgsql(
                'promotions', files=['pg_promotions_collections.sql'],
            ),
        ),
        pytest.param(
            DEFAULT_SHOWCASE,
            400,
            'already_exists',
            id='already_exists',
            marks=pytest.mark.pgsql(
                'promotions',
                files=[
                    'pg_promotions_collections.sql',
                    'pg_promotions_showcases.sql',
                ],
            ),
        ),
        pytest.param(
            DEFAULT_SHOWCASE, 404, 'not_found', id='collection_not_found',
        ),
    ],
)
@pytest.mark.translations(
    backend_promotions={
        'key': {'ru': 'value'},
        'personalized_key': {'ru': 'personalized_value'},
    },
)
async def test_create(
        web_app_client, pgsql, showcase, expected_status, expected_code,
):
    response = await web_app_client.post(
        '/admin/showcases/create/', json=showcase,
    )
    assert response.status == expected_status
    data = await response.json()

    if expected_status != 200:
        assert data['code'] == expected_code
        return

    assert data['name'] == showcase['name']
    showcase_id = data['id']

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT name, collection_blocks, screens '
            f'FROM promotions.showcases '
            f'WHERE id = \'{showcase_id}\'',
        )
        expected_result = (
            showcase['name'],
            {'blocks': showcase['blocks']},
            ['ANY_SCREEN'],
        )
        assert cursor.fetchone() == expected_result


@pytest.mark.parametrize(
    'showcase_id, showcase, expected_status, expected_code',
    [
        pytest.param(
            DEFAULT_SHOWCASE_ID,
            DEFAULT_SHOWCASE,
            200,
            None,
            id='ok',
            marks=pytest.mark.pgsql(
                'promotions',
                files=[
                    'pg_promotions_showcases.sql',
                    'pg_promotions_collections.sql',
                ],
            ),
        ),
        pytest.param(
            SHOWCASE_WITH_UNTITLED_COLLECTION_ID,
            SHOWCASE_WITH_UNTITLED_COLLECTION,
            200,
            None,
            id='ok with untitled collection',
            marks=pytest.mark.pgsql(
                'promotions',
                files=[
                    'pg_promotions_showcases.sql',
                    'pg_promotions_collections.sql',
                ],
            ),
        ),
        pytest.param(
            DEFAULT_SHOWCASE_ID, None, 404, 'not_found', id='not_found',
        ),
    ],
)
async def test_get(
        web_app_client, showcase_id, showcase, expected_status, expected_code,
):
    response = await web_app_client.get(
        '/admin/showcases/', params={'showcase_id': showcase_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status == 404:
        assert data['code'] == expected_code
        return

    view_showcase = copy.deepcopy(showcase)
    view_showcase['blocks'][0].update({'collection_data': DEFAULT_COLLECTION})
    assert all(data[key] == value for (key, value) in view_showcase.items())


@pytest.mark.parametrize(
    'payload, showcase_id, expected_status, expected_data',
    [
        pytest.param(
            {
                'name': 'new_showcase_name',
                'blocks': [
                    {
                        'title': 'new_key',
                        'personalized_title': 'new_personalized_key',
                        'is_tanker_key': True,
                        'collection_id': 'collection_id_1',
                    },
                ],
                'screens': ['ANY_SCREEN'],
            },
            DEFAULT_SHOWCASE_ID,
            200,
            None,
            id='ok',
        ),
        pytest.param(
            {
                'name': 'new_showcase_name',
                'blocks': [{'collection_id': 'collection_id_1'}],
                'screens': ['ANY_SCREEN'],
            },
            DEFAULT_SHOWCASE_ID,
            200,
            None,
            id='ok with untitled collection block',
        ),
        pytest.param(
            {
                **DEFAULT_SHOWCASE,  # type: ignore
                'name': NON_EXISTING_SHOWCASE_ID,
            },
            NON_EXISTING_SHOWCASE_ID,
            404,
            {
                'code': 'not_found',
                'message': f'Витрина {NON_EXISTING_SHOWCASE_ID} не существует',
            },
            id='showcase_not_found',
        ),
        pytest.param(
            {
                'name': 'new_showcase_name',
                'blocks': [
                    {
                        'title': 'non_existent_key',
                        'personalized_title': 'non_existent_pers_key',
                        'is_tanker_key': True,
                        'collection_id': 'collection_id_1',
                    },
                ],
                'screens': ['ANY_SCREEN'],
            },
            DEFAULT_SHOWCASE_ID,
            404,
            {
                'code': 'not_found',
                'message': (
                    'В кейсете backend_promotions отсутствуют '
                    'танкерные ключи: non_existent_key, non_existent_pers_key'
                ),
            },
            id='tanker keys not found',
        ),
        pytest.param(
            {
                'name': 'new_name',
                'blocks': [
                    {
                        'title': 'key',
                        'is_tanker_key': True,
                        'collection_id': NON_EXISTING_COLLECTION_ID,
                    },
                ],
                'screens': ['ANY_SCREEN'],
            },
            DEFAULT_SHOWCASE_ID,
            404,
            {
                'code': 'not_found',
                'message': (
                    f'Коллекция {NON_EXISTING_COLLECTION_ID} не существует'
                ),
            },
            id='collection_not_found',
        ),
        pytest.param(
            {**DEFAULT_SHOWCASE, 'name': 'showcase_name_1'},  # type: ignore
            DEFAULT_SHOWCASE_ID,
            409,
            {
                'code': 'edit_error',
                'message': 'Нельзя задать имя, уже присутствующее в базе',
            },
            id='conflicting_name',
        ),
    ],
)
@pytest.mark.pgsql(
    'promotions',
    files=['pg_promotions_collections.sql', 'pg_promotions_showcases.sql'],
)
@pytest.mark.translations(
    backend_promotions={
        'key': {'ru': 'value'},
        'new_key': {'ru': 'new_value'},
        'personalized_key': {'ru': 'personalized_value'},
        'new_personalized_key': {'ru': 'new_personalized_value'},
    },
)
async def test_update(
        web_app_client,
        pgsql,
        payload,
        showcase_id,
        expected_status,
        expected_data,
):
    response = await web_app_client.put(
        '/admin/showcases/', json=payload, params={'showcase_id': showcase_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status != 200:
        assert data == expected_data
        return

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT name, collection_blocks FROM promotions.showcases '
            f'WHERE id = \'{showcase_id}\'',
        )
        expected_data = (payload['name'], {'blocks': payload['blocks']})
        assert cursor.fetchone() == expected_data


@pytest.mark.parametrize(
    'showcase_id, expected_status, expected_code',
    [
        pytest.param(DEFAULT_SHOWCASE_ID, 200, None, id='ok'),
        pytest.param(
            NON_EXISTING_SHOWCASE_ID, 404, 'not_found', id='not_found',
        ),
        pytest.param(
            PUBLISHED_SHOWCASE_ID,
            409,
            'already_published',
            id='published_showcase',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_showcases.sql'])
async def test_archive(
        web_app_client, pgsql, showcase_id, expected_status, expected_code,
):
    response = await web_app_client.post(
        '/admin/showcases/archive/', json={'promotion_id': showcase_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status != 200:
        assert data['code'] == expected_code
        return

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT status FROM promotions.showcases '
            f'WHERE id = \'{showcase_id}\'',
        )
        assert cursor.fetchone()[0] == 'archived'


@pytest.mark.parametrize(
    'showcase_id, expected_status, expected_code',
    [
        pytest.param(DEFAULT_SHOWCASE_ID, 200, None, id='ok'),
        pytest.param(
            NON_EXISTING_SHOWCASE_ID, 404, 'not_found', id='not_found',
        ),
        pytest.param(
            PUBLISHED_SHOWCASE_ID,
            409,
            'already_published',
            id='published_showcase',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_showcases.sql'])
async def test_publish(
        web_app_client, pgsql, showcase_id, expected_status, expected_code,
):
    start_date = datetime.datetime(
        2020, 9, 10, 10, 00, tzinfo=datetime.timezone.utc,
    )
    end_date = datetime.datetime(
        2021, 9, 10, 10, 00, tzinfo=datetime.timezone.utc,
    )
    response = await web_app_client.post(
        '/admin/showcases/publish/',
        json={
            'promotion_id': showcase_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'experiment': 'pub_exp',
        },
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status != 200:
        assert data['code'] == expected_code
        return

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT status, starts_at, ends_at, experiment '
            f'FROM promotions.showcases '
            f'WHERE id = \'{showcase_id}\'',
        )
        status, starts_at, ends_at, experiment = cursor.fetchone()
        assert status == 'published'
        assert dates.localize(starts_at) == start_date
        assert dates.localize(ends_at) == end_date
        assert experiment == 'pub_exp'


@pytest.mark.parametrize(
    'showcase_id, expected_status, expected_code',
    [
        pytest.param(PUBLISHED_SHOWCASE_ID, 200, None, id='ok'),
        pytest.param(
            NON_EXISTING_SHOWCASE_ID, 404, 'not_found', id='not_found',
        ),
        pytest.param(
            DEFAULT_SHOWCASE_ID, 409, 'not_published', id='not_published',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_showcases.sql'])
async def test_unpublish(
        web_app_client, pgsql, showcase_id, expected_status, expected_code,
):
    response = await web_app_client.post(
        '/admin/showcases/unpublish/', json={'promotion_id': showcase_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status != 200:
        assert data['code'] == expected_code
        return

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT status FROM promotions.showcases '
            f'WHERE id = \'{showcase_id}\'',
        )
        assert cursor.fetchone()[0] == 'stopped'
