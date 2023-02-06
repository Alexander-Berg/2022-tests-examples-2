import pytest

TRANSLATIONS = {
    'list_v1.title': {'en': 'Title'},
    'list_v1.subtitle': {'en': 'Subtitle'},
    'category.tire': {'en': 'Tires and so'},
    'category.washing': {'en': 'Washing and so'},
    'category.washing.slider': {'en': 'WASH-WASH-WASH'},
}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
async def test_ok(taxi_contractor_merch, mockserver):
    response = await taxi_contractor_merch.get(
        '/admin/contractor-merch/v1/categories',
        headers={'Accept-Language': 'en'},
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'categories': [
            {
                'background_color': 'yellow',
                'category_id': 'tire',
                'category_image': '<url>',
                'name': 'Tires and so',
                'place_id': 1,
                'text_color': 'white',
            },
            {
                'background_color': 'blue',
                'category_id': 'washing',
                'category_image': '<url>',
                'name': 'Washing and so',
                'place_id': 2,
                'slider': {
                    'image': '<url>',
                    'slider_place_id': 1,
                    'text': 'WASH-WASH-WASH',
                },
                'text_color': 'white',
            },
        ],
    }
