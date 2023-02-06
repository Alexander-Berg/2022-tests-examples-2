import copy

import pytest


URI = '/admin/promo_on_map/'

# The same as in db
DEFAULT_DATA = {
    'name': 'promo_on_map_name',
    'priority': 1,
    'image_tag': 'image_tag',
    'action': {'deeplink': 'deeplink', 'promotion_id': 'promotion_id'},
    'bubble': {
        'id': 'bubble_id',
        'hide_after_tap': True,
        'max_per_session': 1,
        'max_per_user': 10,
        'components': [
            {
                'font_style': 'bold',
                'has_tanker_key': True,
                'type': 'text',
                'value': 'text on bubble',
            },
        ],
    },
    'cache_distance': 1000,
    'attract_to_road': True,
}

DATA_TO_MODIFY = {
    'name': 'promo_on_map_name2',
    'priority': 2,
    'image_tag': 'image_tag2',
    'action': {'deeplink': 'deeplink2', 'promotion_id': 'promotion_id2'},
    'bubble': {
        'id': 'bubble_id2',
        'hide_after_tap': False,
        'max_per_session': 2,
        'max_per_user': 11,
        'components': [
            {
                'font_style': 'bold',
                'has_tanker_key': True,
                'type': 'text',
                'value': 'text on bubble2',
            },
        ],
    },
    'cache_distance': 1001,
    'attract_to_road': False,
}


async def _check_create_edit(
        web_app_client, pgsql, mode, data, id=None,
):  # pylint: disable=C0103, W0622
    method = web_app_client.put if mode == 'edit' else web_app_client.post
    uri = URI + str(id) + '/' if mode == 'edit' else URI + 'create/'
    response = await method(uri, json=data)
    assert response.status == 200
    if mode == 'create':
        resp_data = await response.json()
        id = resp_data['id']

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT name, priority, image_tag, action, bubble, '
            f'cache_distance, attract_to_road, status FROM '
            f'promotions.promo_on_map '
            f'WHERE id = \'{id}\'',
        )
        assert cursor.rowcount == 1
        saved = cursor.fetchone()
        for ind, key in zip(range(len(data)), data.keys()):
            assert saved[ind] == data[key]
        assert saved[-1] == 'created'


@pytest.mark.pgsql('promotions')
async def test_create_ok(web_app_client, pgsql):
    await _check_create_edit(web_app_client, pgsql, 'create', DEFAULT_DATA)


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_create_already_exists(web_app_client, pgsql):
    response = await web_app_client.post(URI + 'create/', json=DEFAULT_DATA)
    data = await response.json()
    assert response.status == 400
    assert data['code'] == 'already_exists'
    assert data['message'] == 'Промо-объект с таким названием уже существует'


@pytest.mark.parametrize(
    ['promo_on_map_id'], [('promo_on_map_id',), ('stopped_promo_on_map_id',)],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_modify_ok(web_app_client, pgsql, promo_on_map_id):
    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(f'SELECT id FROM promotions.promo_on_map')
        before = cursor.rowcount
    await _check_create_edit(
        web_app_client, pgsql, 'edit', DATA_TO_MODIFY, 'promo_on_map_id',
    )
    # should not to change count
    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(f'SELECT id FROM promotions.promo_on_map')
        assert before == cursor.rowcount


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_modify_not_found(web_app_client, pgsql):
    response = await web_app_client.put(
        URI + 'no_such_id_in_db/', json=DATA_TO_MODIFY,
    )
    data = await response.json()
    assert response.status == 404
    assert data['code'] == 'not_found'
    assert data['message'] == 'Промо-объект не найден'


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_modify_published(web_app_client, pgsql):
    response = await web_app_client.put(
        URI + 'published_promo_on_map_id/', json=DATA_TO_MODIFY,
    )
    data = await response.json()
    assert response.status == 409
    assert data['code'] == 'edit_error'
    assert (
        data['message'] == 'Нельзя редактировать опубликованные промо-объекты'
    )


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_modify_unique_name(web_app_client, pgsql):
    data = copy.deepcopy(DATA_TO_MODIFY)
    data['name'] = 'published_promo_on_map_name'
    response = await web_app_client.put(URI + 'promo_on_map_id/', json=data)
    data = await response.json()
    assert response.status == 409
    assert data['code'] == 'edit_error'
    assert data['message'] == 'Нельзя задать имя, уже присутствующее в базе'


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_get_ok(web_app_client, pgsql):
    response = await web_app_client.get(URI + f'?promotion_id=promo_on_map_id')
    data = await response.json()
    assert response.status == 200
    assert data == dict(
        {
            **DEFAULT_DATA,
            **{
                'id': 'promo_on_map_id',
                'created_at': '2019-07-22T19:51:09+03:00',
                'status': 'created',
                'updated_at': '2019-07-22T19:57:09+03:00',
            },
        },
    )


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_get_not_found(web_app_client, pgsql):
    response = await web_app_client.get(
        URI + f'?promotion_id=no_such_id_in_db',
    )
    data = await response.json()
    assert response.status == 404
    assert data['code'] == 'not_found'
    assert data['message'] == 'Промо-объект не найден'
