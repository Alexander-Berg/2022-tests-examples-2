from tests_eats_catalog_storage.helpers import helpers


def get_place_db_value(pgsql, place_id, column_name):
    cursor = pgsql['eats_catalog_storage'].cursor()
    cursor.execute(
        f'SELECT {column_name} FROM storage.places WHERE id={place_id}',
    )
    row = cursor.fetchone()
    return row[0] if row is not None else None


async def update_allowed_couriers_type(
        taxi_eats_catalog_storage,
        pgsql,
        place_id,
        couriers_type,
        is_allowed,
        status_code=200,
):
    response = await taxi_eats_catalog_storage.put(
        '/internal/eats-catalog-storage/v1/place/allowed_couriers_type',
        json={
            'place_id': place_id,
            'couriers_type': couriers_type,
            'is_allowed': is_allowed,
        },
    )
    assert response.status_code == status_code
    if status_code == 200:
        return get_place_db_value(pgsql, place_id, 'allowed_couriers_types')


async def test_place_allowed_couriers_type_simple_update(
        taxi_eats_catalog_storage, pgsql,
):
    assert (
        await update_allowed_couriers_type(
            taxi_eats_catalog_storage,
            pgsql,
            place_id=10,
            couriers_type='pedestrian',
            is_allowed=True,
        )
        == '{pedestrian}'
    )


async def test_place_allowed_couriers_type_multiple_updates(
        taxi_eats_catalog_storage, pgsql,
):
    place_id = 10

    async def update_place_couriers(couriers_type, is_allowed):
        return await update_allowed_couriers_type(
            taxi_eats_catalog_storage,
            pgsql,
            place_id,
            couriers_type,
            is_allowed,
        )

    assert (
        await update_place_couriers(
            couriers_type='yandex_rover', is_allowed=True,
        )
        == '{yandex_rover}'
    )

    assert (
        await update_place_couriers(
            couriers_type='pedestrian', is_allowed=True,
        )
        == '{pedestrian,yandex_rover}'
    )

    assert (
        await update_place_couriers(
            couriers_type='yandex_taxi', is_allowed=True,
        )
        == '{pedestrian,yandex_taxi,yandex_rover}'
    )

    assert (
        await update_place_couriers(couriers_type='bicycle', is_allowed=False)
        == '{pedestrian,yandex_taxi,yandex_rover}'
    )

    assert (
        await update_place_couriers(
            couriers_type='yandex_taxi', is_allowed=False,
        )
        == '{pedestrian,yandex_rover}'
    )

    assert (
        await update_place_couriers(
            couriers_type='yandex_rover', is_allowed=False,
        )
        == '{pedestrian}'
    )

    assert (
        await update_place_couriers(
            couriers_type='pedestrian', is_allowed=False,
        )
        == '{}'
    )

    assert (
        await update_place_couriers(
            couriers_type='pedestrian', is_allowed=False,
        )
        == '{}'
    )


async def test_place_allowed_couriers_type_update_and_upsert(
        taxi_eats_catalog_storage, pgsql, load_json,
):
    place_id = 10
    assert (
        await update_allowed_couriers_type(
            taxi_eats_catalog_storage,
            pgsql,
            place_id,
            couriers_type='pedestrian',
            is_allowed=True,
        )
        == '{pedestrian}'
    )

    upsert_data = load_json('place_request.json')
    upsert_data['revision'] = get_place_db_value(pgsql, place_id, 'revision')
    del upsert_data['allowed_couriers_types']
    await helpers.place_upsert(
        taxi_eats_catalog_storage, place_id, upsert_data, 200,
    )

    assert (
        get_place_db_value(pgsql, place_id, 'allowed_couriers_types')
        == '{pedestrian}'
    )


async def test_place_allowed_couriers_type_update_revision_change(
        taxi_eats_catalog_storage, pgsql,
):
    place_id = 10
    prev_db_revision = get_place_db_value(pgsql, place_id, 'revision_id')
    await update_allowed_couriers_type(
        taxi_eats_catalog_storage,
        pgsql,
        place_id=10,
        couriers_type='pedestrian',
        is_allowed=True,
    )
    assert (
        get_place_db_value(pgsql, place_id, 'revision_id')
        == prev_db_revision + 1
    )


async def test_place_allowed_couriers_type_update_not_found(
        taxi_eats_catalog_storage,
):
    await update_allowed_couriers_type(
        taxi_eats_catalog_storage,
        pgsql=None,
        place_id=123,
        couriers_type='pedestrian',
        is_allowed=False,
        status_code=404,
    )
