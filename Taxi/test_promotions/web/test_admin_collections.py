import pytest

DEFAULT_COLLECTION_ID = 'default_collection_id'
DEFAULT_COLLECTION = {
    'name': 'default_collection_name',
    'cells': [
        {
            'one_of': [
                {'type': 'scenario', 'scenario': 'afisha-event'},
                {'type': 'tag', 'tag': 'scooter'},
                {'type': 'promotion_id', 'promotion_id': 'id1'},
            ],
            'size': {'width': 4, 'height': 4},
        },
    ],
}

BAD_PROMO_COLLECTION = {
    'name': 'bad_promo_collection_name',
    'cells': [
        {
            'one_of': [
                {
                    'type': 'promotion_id',
                    'promotion_id': 'non_existent_promo_id',
                },
            ],
            'size': {'width': 4, 'height': 4},
        },
    ],
}

# ID of the collection that is in the published showcase
PUBLISHED_COLLECTION_ID = 'collection_id_1'
PUBLISHED_COLLECTION = {
    'name': 'collection_name_1',
    'cells': DEFAULT_COLLECTION['cells'],
}

NON_EXISTENT_COLLECTION_ID = 'non_existent_collection_id'


@pytest.mark.parametrize(
    'expected_status, expected_code, expected_message, collection',
    [
        pytest.param(
            200,
            None,
            None,
            DEFAULT_COLLECTION,
            id='ok',
            marks=pytest.mark.pgsql(
                'promotions', files=['pg_promotions_all.sql'],
            ),
        ),
        pytest.param(
            400,
            'bad_promotion_matcher',
            'No such promotion_id="non_existent_promo_id" '
            '(used in collection_name="bad_promo_collection_name")',
            BAD_PROMO_COLLECTION,
            id='ok',
            marks=pytest.mark.pgsql(
                'promotions', files=['pg_promotions_all.sql'],
            ),
        ),
        pytest.param(
            400,
            'already_exists',
            None,
            DEFAULT_COLLECTION,
            id='already_exists',
            marks=pytest.mark.pgsql(
                'promotions',
                files=[
                    'pg_promotions_collections.sql',
                    'pg_promotions_all.sql',
                ],
            ),
        ),
    ],
)
async def test_create(
        web_app_client,
        pgsql,
        expected_status,
        expected_code,
        expected_message,
        collection,
):
    response = await web_app_client.post(
        '/admin/collections/create/', json=collection,
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status == 400:
        assert data['code'] == expected_code
        if expected_code == 'bad_promotion_matcher':
            assert data['message'] == expected_message
        return

    assert data['name'] == collection['name']
    collection_id = data['id']

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT name, cells FROM promotions.collections '
            f'WHERE id = \'{collection_id}\'',
        )
        expected_result = (collection['name'], {'cells': collection['cells']})
        assert cursor.fetchone() == expected_result


@pytest.mark.parametrize(
    'collection_id, expected_status, expected_code, expected_data',
    [
        pytest.param(
            DEFAULT_COLLECTION_ID,
            200,
            None,
            {
                **DEFAULT_COLLECTION,  # type: ignore
                'containing_showcases': [
                    {
                        'id': 'default_showcase_id',
                        'name': 'default_showcase_name',
                        'status': 'created',
                    },
                    {
                        'id': 'showcase_id_1',
                        'name': 'showcase_name_1',
                        'status': 'created',
                    },
                    {
                        'id': 'showcase_with_untitled_collection_id',
                        'name': 'showcase_with_untitled_collection_name',
                        'status': 'created',
                    },
                ],
                'can_be_modified': True,
            },
            id='ok',
        ),
        pytest.param(
            PUBLISHED_COLLECTION_ID,
            200,
            None,
            {
                **PUBLISHED_COLLECTION,  # type: ignore
                'containing_showcases': [
                    {
                        'id': 'published_showcase_id',
                        'name': 'published_showcase_name',
                        'status': 'published',
                    },
                ],
                'can_be_modified': False,
            },
            id='ok with containing_showcases',
        ),
        pytest.param(
            NON_EXISTENT_COLLECTION_ID, 404, 'not_found', None, id='not_found',
        ),
    ],
)
@pytest.mark.pgsql(
    'promotions',
    files=['pg_promotions_collections.sql', 'pg_promotions_showcases.sql'],
)
async def test_get(
        web_app_client,
        collection_id,
        expected_status,
        expected_code,
        expected_data,
):
    response = await web_app_client.get(
        '/admin/collections/', params={'collection_id': collection_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status == 404:
        assert data['code'] == expected_code
        return
    assert data == expected_data


@pytest.mark.parametrize(
    'name, collection_id, collection, expected_status, expected_code',
    [
        pytest.param(
            'collection_name_new',
            DEFAULT_COLLECTION_ID,
            DEFAULT_COLLECTION,
            200,
            None,
            id='ok',
        ),
        pytest.param(
            'collection_name_new',
            DEFAULT_COLLECTION_ID,
            BAD_PROMO_COLLECTION,
            400,
            'bad_promotion_matcher',
            id='bad_promotion_matcher',
        ),
        pytest.param(
            'new_name',
            'non_existing_id',
            DEFAULT_COLLECTION,
            404,
            'not_found',
            id='not_found',
        ),
        pytest.param(
            'collection_name_1',
            DEFAULT_COLLECTION_ID,
            DEFAULT_COLLECTION,
            409,
            'edit_error',
            id='conflicting_name',
        ),
        pytest.param(
            'collection_name_new',
            'collection_id_1',  # published showcase includes this collection
            DEFAULT_COLLECTION,
            409,
            'already_published',
            id='editing collection from published showcase',
        ),
    ],
)
@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_collections.sql',
        'pg_promotions_showcases.sql',
        'pg_promotions_all.sql',
    ],
)
async def test_update(
        web_app_client,
        pgsql,
        name,
        collection_id,
        collection,
        expected_status,
        expected_code,
):
    response = await web_app_client.put(
        '/admin/collections/',
        json={**collection, 'name': name},
        params={'collection_id': collection_id},
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status != 200:
        assert data['code'] == expected_code
        return

    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT name FROM promotions.collections '
            f'WHERE id = \'{collection_id}\'',
        )
        assert cursor.fetchone()[0] == name
