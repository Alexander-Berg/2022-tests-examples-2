import typing

import pytest


def get_place_revision(cursor, place_id: int) -> typing.Optional[int]:
    cursor.execute(
        f'SELECT revision_id FROM storage.places WHERE id={place_id}',
    )

    entry = cursor.fetchone()

    if entry is None:
        return None
    return entry[0]


@pytest.mark.parametrize(
    'place_id,data,response_code,rating',
    [
        pytest.param(
            10,
            {'rating': 5, 'show': True},
            200,
            {'rating': 5, 'show': True, 'count': 0},
            id='rating update',
        ),
        pytest.param(
            10,
            {'rating': 5, 'show': True, 'count': 100},
            200,
            {'rating': 5, 'show': True, 'count': 100},
            id='rating update with count',
        ),
        pytest.param(
            404, {'rating': 5, 'show': True}, 404, None, id='unknown place',
        ),
    ],
)
async def test_place_rating_update(
        taxi_eats_catalog_storage,
        place_id,
        data,
        response_code,
        rating,
        pgsql,
):
    cursor = pgsql['eats_catalog_storage'].cursor()
    revision = get_place_revision(cursor, place_id)

    response = await taxi_eats_catalog_storage.put(
        '/internal/eats-catalog-storage/v1/place/rating',
        json={'place_id': place_id, 'rating': data},
    )
    assert response.status_code == response_code

    cursor.execute(
        f'SELECT new_rating FROM storage.places WHERE id={place_id}',
    )
    entry = cursor.fetchone()
    if rating is None:
        assert entry is None
    else:
        assert entry is not None and entry[0] == rating

    new_revision = get_place_revision(cursor, place_id)

    assert (revision is None) or (revision + 1 == new_revision)
