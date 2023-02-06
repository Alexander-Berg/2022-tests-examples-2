import pytest


@pytest.mark.config(
    HIRING_SELFREG_FORMS_USE_REGION_SETTINGS=True,
    HIRING_SELFREG_FORMS_REGION_SETTINGS=[
        {
            'country': 'RU',
            'citizenships': ['RU'],
            'regions': ['Москва', 'Волгоград'],
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
@pytest.mark.parametrize(
    'params,expected_data',
    [
        (
            None,
            {
                'regions': [
                    {
                        'id': 1,
                        'name': 'Москва',
                        'training_type': 'offline',
                        'oktmo': '45000000',
                    },
                    {
                        'id': 5,
                        'name': 'Волгоград',
                        'training_type': 'online',
                        'oktmo': '18000000',
                    },
                    {
                        'id': 128,
                        'name': 'Нур-Султан',
                        'training_type': 'offline',
                        'oktmo': '0',
                    },
                ],
            },
        ),
        (
            {'country': 'KZ'},
            {
                'regions': [
                    {
                        'id': 128,
                        'name': 'Нур-Султан',
                        'training_type': 'offline',
                        'oktmo': '0',
                    },
                ],
            },
        ),
    ],
)
async def test_eda_suggest_regions(
        make_request, eda_core, params, expected_data,
):
    response = await make_request(
        '/v1/eda/suggests/regions', method='get', params=params,
    )
    assert response == expected_data
