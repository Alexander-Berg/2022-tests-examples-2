import pytest


@pytest.fixture(name='mock_catalog_storage')
def _mock_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/'
        'v1/places/retrieve-by-ids',
    )
    def _catalog_storage(request):
        request.json['projection'].sort()
        assert request.json == {
            'place_ids': [1],
            'projection': ['address', 'brand', 'name'],
        }
        return mockserver.make_response(
            status=200,
            json={
                'not_found_place_ids': [],
                'places': [
                    {
                        'id': 1,
                        'name': 'Вкусная еда',
                        'address': {
                            'city': 'Санкт-Петербург',
                            'short': 'Улица и дом',
                        },
                        'brand': {
                            'id': 2,
                            'slug': 'brand_slug',
                            'name': 'brand_name',
                            'picture_scale_type': 'aspect_fit',
                        },
                        'revision_id': 123,
                        'updated_at': '2022-03-01T00:00:00Z',
                    },
                ],
            },
        )

    return _catalog_storage


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_promocode_types_happy_path(
        taxi_eats_place_rating, mock_authorizer_allowed, mock_catalog_storage,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/promocode_types',
        headers={'X-YaEda-PartnerId': '1'},
        params={'place_id': '1'},
    )

    assert response.status_code == 200
    assert response.json() == {'available': True}
    assert mock_catalog_storage.times_called == 1


@pytest.mark.experiments3(filename='exp3_eats_place_rating.json')
async def test_promocode_types_403(
        taxi_eats_place_rating, mock_authorizer_403,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/promocode_types',
        headers={'X-YaEda-PartnerId': '1'},
        params={'place_id': '1'},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'For user 1 access to places is denied',
    }
