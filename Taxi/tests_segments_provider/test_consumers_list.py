import pytest


@pytest.mark.pgsql('segments_provider', files=['fill_consumers.sql'])
async def test_consumer_list(taxi_segments_provider):
    response = await taxi_segments_provider.get(
        '/admin/v1/consumers-list', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'consumers': [
            # Properly localized
            {'name': 'tags', 'title': 'Теги водителей'},
            # Localization missing
            {'name': 'grocery-tags', 'title': 'grocery-tags'},
        ],
    }
