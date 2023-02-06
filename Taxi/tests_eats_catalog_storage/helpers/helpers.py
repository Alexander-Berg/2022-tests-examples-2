async def put(eats_catalog_storage, path, json, expected_status_code):
    response = await eats_catalog_storage.put(path, json)

    assert response.status_code == expected_status_code
    return response.json()


async def place_upsert(
        taxi_eats_catalog_storage, place_id, data, expected_status_code,
):
    response = await put(
        taxi_eats_catalog_storage,
        f'/internal/eats-catalog-storage/v1/place/{place_id}',
        data,
        expected_status_code,
    )

    return response


async def place_enabled(
        taxi_eats_catalog_storage,
        place_id,
        status,
        revision,
        expected_status_code,
):
    response = await put(
        taxi_eats_catalog_storage,
        f'/internal/eats-catalog-storage/v1/place/{place_id}/enabled',
        {'enabled': status, 'source': 'eats_core', 'revision': revision},
        expected_status_code,
    )

    return response


def get_delivery_zone_id(pgsql, external_id, source='eats_core'):
    assert source in ['eats_core', 'yandex_rover']
    cursor = pgsql['eats_catalog_storage'].cursor()
    cursor.execute(
        f"""SELECT id FROM storage.delivery_zones
            WHERE source='{source}' AND external_id='{external_id}'""",
    )

    zone = cursor.fetchone()
    assert (
        zone is not None
    ), f'Zone with source="{source}" and external_id="{external_id}" not found'
    return zone[0]


async def delivery_zone_upsert(
        taxi_eats_catalog_storage, external_id, data, expected_status_code,
):
    response = await put(
        taxi_eats_catalog_storage,
        f'/internal/eats-catalog-storage/v1/delivery_zone/{external_id}',
        data,
        expected_status_code,
    )

    return response


async def delivery_zone_enabled(
        taxi_eats_catalog_storage,
        external_id,
        status,
        revision,
        expected_status_code,
):
    response = await put(
        taxi_eats_catalog_storage,
        '/internal/eats-catalog-storage/v1/delivery_zone/'
        + f'{external_id}/enabled',
        {'enabled': status, 'source': 'eats_core', 'revision': revision},
        expected_status_code,
    )

    return response


async def delivery_zone_polygon_update(
        taxi_eats_catalog_storage, external_id, data, expected_status_code,
):
    response = await put(
        taxi_eats_catalog_storage,
        '/internal/eats-catalog-storage/v1/delivery_zone/'
        + f'{external_id}/polygon',
        data,
        expected_status_code,
    )

    return response


def place_exists(pgsql, place_id):
    cursor = pgsql['eats_catalog_storage'].cursor()
    cursor.execute(
        f"""SELECT COUNT(*) FROM storage.places WHERE id='{place_id}'""",
    )
    [count_places] = cursor.fetchone()
    return count_places != 0
