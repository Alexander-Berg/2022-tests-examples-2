import pytest

# Check handlers:
# /v1/dictionaries/hierarchy_countries
# /v1/dictionaries/hierarchy_zones
# /v1/dictionaries/hierarchy_agglomerations


@pytest.mark.pgsql('crm_admin', files=['init_geo_hierarchy.sql'])
async def test_get_countries(web_app_client):
    link = '/v1/dictionaries/hierarchy_countries'
    response = await web_app_client.get(link)

    assert response.status == 200
    response_data = await response.json()

    response_data.sort(key=lambda row: row['label'])

    assert response_data == [
        {'label': 'Азербайджан', 'value': 'br_azerbaijan'},
        {'label': 'Белоруссия', 'value': 'br_belarus'},
        {'label': 'Россия', 'value': 'br_russia'},
    ]


@pytest.mark.pgsql('crm_admin', files=['init_geo_hierarchy.sql'])
async def test_get_zones_without_filter(web_app_client):
    response = await web_app_client.get('/v1/dictionaries/hierarchy_zones')

    assert response.status == 200
    response_data = await response.json()
    response_data.sort(key=lambda row: row['label'])

    assert len(response_data) == 6
    assert response_data == [
        {'label': 'Баку', 'value': 'br_baku', 'country': 'br_azerbaijan'},
        {
            'label': 'Благовещенск',
            'value': 'br_blagoveshchensk',
            'country': 'br_russia',
        },
        {'label': 'Бобруйск', 'value': 'br_bobruisk', 'country': 'br_belarus'},
        {'label': 'Брест', 'value': 'br_brest', 'country': 'br_belarus'},
        {
            'label': 'Брянская область',
            'value': 'br_brjanskaja_obl',
            'country': 'br_belarus',
        },
        {
            'label': 'Череповец',
            'value': 'br_cherepovets',
            'country': 'br_russia',
        },
    ]


@pytest.mark.pgsql('crm_admin', files=['init_geo_hierarchy.sql'])
async def test_get_zones_filtered(web_app_client):
    response = await web_app_client.get(
        '/v1/dictionaries/hierarchy_zones?countries=br_azerbaijan,br_russia',
    )

    assert response.status == 200
    response_data = await response.json()
    response_data.sort(key=lambda row: row['label'])

    assert len(response_data) == 3
    assert response_data == [
        {'label': 'Баку', 'value': 'br_baku', 'country': 'br_azerbaijan'},
        {
            'label': 'Благовещенск',
            'value': 'br_blagoveshchensk',
            'country': 'br_russia',
        },
        {
            'label': 'Череповец',
            'value': 'br_cherepovets',
            'country': 'br_russia',
        },
    ]


@pytest.mark.pgsql('crm_admin', files=['init_geo_hierarchy.sql'])
async def test_get_agglomeration_without_filter(web_app_client):
    response = await web_app_client.get(
        '/v1/dictionaries/hierarchy_agglomerations',
    )

    assert response.status == 200
    response_data = await response.json()
    # response_data.sort(key=lambda row: row['label'])

    assert len(response_data) == 5
    assert response_data == [
        {'label': 'Баку', 'value': 'br_baku', 'country': 'br_azerbaijan'},
        {
            'label': 'Благовещенск',
            'value': 'br_blagoveshchensk',
            'country': 'br_russia',
        },
        {'label': 'Бобруйск', 'value': 'br_bobruisk', 'country': 'br_belarus'},
        {'label': 'Брест', 'value': 'br_brest', 'country': 'br_belarus'},
        {
            'label': 'Череповец',
            'value': 'br_cherepovets',
            'country': 'br_russia',
        },
    ]


@pytest.mark.pgsql('crm_admin', files=['init_geo_hierarchy.sql'])
async def test_get_agglomeration_filtered(web_app_client):
    response = await web_app_client.get(
        '/v1/dictionaries/hierarchy_agglomerations?countries='
        'br_azerbaijan,br_belarus',
    )

    assert response.status == 200
    response_data = await response.json()
    response_data.sort(key=lambda row: row['label'])

    assert len(response_data) == 3
    assert response_data == [
        {'label': 'Баку', 'value': 'br_baku', 'country': 'br_azerbaijan'},
        {'label': 'Бобруйск', 'value': 'br_bobruisk', 'country': 'br_belarus'},
        {'label': 'Брест', 'value': 'br_brest', 'country': 'br_belarus'},
    ]
