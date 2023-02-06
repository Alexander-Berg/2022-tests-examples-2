import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_taximeter_versions.sql'],
)
async def test_get_taximeter_versions(web_app_client):
    response = await web_app_client.get('/api/v1/taximeter_versions')
    assert response.status == 200, await response.text()

    data = await response.json()
    versions = sorted(data['taximeter_versions'])
    assert versions == [
        '11.11 (3014662)',
        '12.00 (15167)',
        '9.97 (8246)',
        '9.99 (8371)',
    ]
