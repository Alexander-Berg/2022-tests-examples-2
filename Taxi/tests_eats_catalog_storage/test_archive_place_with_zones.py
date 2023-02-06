import psycopg2
import pytest


async def archive_place(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/place/archive'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


async def archive_delivery_zone(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/delivery_zone/archive'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_archive_place(taxi_eats_catalog_storage, pgsql):
    place_id = 20
    data = {
        'id': place_id,
        'source': 'eats_core',
        'revision': 100,
        'archived': True,
    }
    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        f"""SELECT revision_id FROM storage.places
            WHERE id = '{place_id}';""",
    )
    db_revision_id = cursor.fetchone()['revision_id']

    response = await archive_place(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    cursor.execute(
        f"""SELECT archived, revision_id FROM storage.places
            WHERE id = '{place_id}';""",
    )
    place = cursor.fetchone()
    assert place['archived']
    assert place['revision_id'] == db_revision_id + 1

    # try to archive not existing place
    data['id'] = 321
    response = await archive_place(taxi_eats_catalog_storage, data)
    assert response.status_code == 404
    assert response.json()['code'] == 'place_not_exists'

    # try to archive place with wrong revision
    data['id'] = place_id
    data['revision'] = 321
    response = await archive_place(taxi_eats_catalog_storage, data)
    assert response.status_code == 409
    assert response.json()['code'] == 'race_condition'


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_archive_delivery_zone(taxi_eats_catalog_storage, pgsql):
    zone_external_id = 'id-100'
    data = {
        'external_id': zone_external_id,
        'source': 'eats_core',
        'revision': 200,
        'archived': True,
    }
    cursor = pgsql['eats_catalog_storage'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        f"""
        SELECT revision_id FROM storage.delivery_zones
        WHERE source='eats_core' AND external_id='{zone_external_id}';
        """,
    )
    db_revision_id = cursor.fetchone()['revision_id']

    response = await archive_delivery_zone(taxi_eats_catalog_storage, data)
    assert response.status_code == 200
    cursor.execute(
        f"""
        SELECT archived, revision_id FROM storage.delivery_zones
        WHERE source='eats_core' AND external_id='{zone_external_id}';
        """,
    )
    zone = cursor.fetchone()
    assert zone['archived']
    assert zone['revision_id'] == db_revision_id + 1

    # try to archive not existing place
    data['external_id'] = 'id-321'
    response = await archive_delivery_zone(taxi_eats_catalog_storage, data)
    assert response.status_code == 404
    assert response.json()['code'] == 'delivery_zone_not_exists'

    # try to archive place with wrong revision
    data['external_id'] = zone_external_id
    data['revision'] = 321
    response = await archive_delivery_zone(taxi_eats_catalog_storage, data)
    assert response.status_code == 409
    assert response.json()['code'] == 'race_condition'
