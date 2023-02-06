import pytest


@pytest.mark.config(
    HIRING_SELFREG_FORMS_USE_REGION_SETTINGS=True,
    HIRING_SELFREG_FORMS_REGION_SETTINGS=[
        {
            'country': 'RU',
            'citizenships': ['RU'],
            'regions': ['Москва'],
            'vehicle_types': ['car', 'bicycle', 'pedestrian'],
        },
        {
            'country': 'KZ',
            'citizenships': ['KZ'],
            'regions': ['Нур-Султан'],
            'vehicle_types': ['car', 'bicycle', 'pedestrian'],
        },
    ],
)
async def test_eda_suggest_countries(make_request, eda_core):
    response = await make_request('/v1/eda/suggests/countries', method='get')
    assert response == {
        'countries': [
            {'code': 'KZ', 'id': 5, 'name': 'Казахстан'},
            {'code': 'RU', 'id': 35, 'name': 'Российская Федерация'},
        ],
    }
