import pytest


@pytest.mark.parametrize('user_header', ['user_id', 'partner_user_id'])
async def test_add_non_existing(
        user_header,
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search,
        mock_catalog_storage_places,
        pgsql,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = user_header + '=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT COUNT(*) FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s;""",
        (eater_id,),
    )
    reactions = list(cursor)
    assert len(reactions) == 1
    assert reactions[0][0] == 1


async def test_add_existing(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search,
        mock_catalog_storage_places,
        pgsql,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'

    db_id = '9fc54b04-2dd9-4fba-bd0b-6770abb77571'
    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """INSERT INTO eats_user_reactions.favourite_reactions
           (id, eater_id, subject_namespace, subject_id)
           VALUES (%s, %s, %s, %s);""",
        (db_id, eater_id, 'catalog_brand', '222'),
    )

    headers['X-Eats-User'] = 'user_id=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor.execute(
        """SELECT * FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s;""",
        (eater_id,),
    )
    reactions = list(cursor)
    assert len(reactions) == 1
    assert reactions[0][0] == db_id


async def test_add_catalog_search_500(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search_500,
        mock_catalog_storage_places,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = 'user_id=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 500


async def test_add_catalog_search_empty(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_search_empty,
        mock_catalog_storage_places,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = 'user_id=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_brand',
        'message': 'Invalid request parameter',
    }


async def test_add_catalog_places_500(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search,
        mock_catalog_storage_places_500,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = 'user_id=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 500


async def test_add_catalog_places_empty(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search,
        mock_catalog_places_empty,
):
    request_json = {'catalog_brand_slug': 'brand_slug'}
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = 'user_id=' + eater_id
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        headers=headers,
        json=request_json,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_brand',
        'message': 'Invalid request parameter',
    }


async def test_ios_add_request(
        taxi_eats_user_reactions,
        mockserver,
        mock_catalog_storage_search,
        mock_catalog_storage_places,
        pgsql,
):
    headers = {}
    eater_id = 'eater1'
    headers['X-Eats-User'] = 'user_id=' + eater_id
    headers['Content-Type'] = 'application/json'
    response = await taxi_eats_user_reactions.post(
        '/eats/v1/eats-user-reactions/v1/favourites/catalog-brand/add',
        params={'catalog_brand_slug': 'brand_slug'},
        headers=headers,
        json=None,
    )
    assert response.status_code == 204
    assert response.content == b''

    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT COUNT(*) FROM eats_user_reactions.favourite_reactions
        WHERE eater_id = %s;""",
        (eater_id,),
    )
    reactions = list(cursor)
    assert len(reactions) == 1
    assert reactions[0][0] == 1
