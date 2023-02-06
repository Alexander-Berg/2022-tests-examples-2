import pytest


@pytest.mark.pgsql('overlord_catalog', files=['pg_overlord_catalog.sql'])
async def test_sync_success(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/depots/sync_all',
        json={
            'sources': [
                'nomenclatures',
                'stocks',
                'eats_id_mappings',
                'promos',
            ],
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'source', ['nomenclatures', 'stocks', 'eats_id_mappings', 'promos'],
)
@pytest.mark.pgsql('overlord_catalog', files=['pg_overlord_catalog.sql'])
async def test_sync_single(taxi_overlord_catalog, source):
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/depots/sync_all', json={'sources': [source]},
    )
    assert response.status_code == 200


@pytest.mark.pgsql('overlord_catalog', files=['pg_overlord_catalog.sql'])
async def test_sync_bad_request(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/depots/sync_all', json={'sources': []},
    )
    assert response.status_code == 400
