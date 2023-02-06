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
            {'region': 'Москва'},
            {
                'citizenships': [{'id': 'RU', 'name': 'Российская Федерация'}],
                'vehicle_types': [
                    {'id': 'car'},
                    {'id': 'bicycle'},
                    {'id': 'pedestrian'},
                ],
            },
        ),
    ],
)
async def test_eda_suggest_citizenships_and_vehicle_types(
        make_request, eda_core, params, expected_data,
):
    response = await make_request(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
        method='get',
        params=params,
    )
    assert response == expected_data
