import pytest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_CITY_COMPANIES_MAP={
        'city1': ['aaa', 'bbb'],
        'city2': ['ccc'],
    },
)
async def test_get_companies_list(web_app_client):
    response = await web_app_client.get('/v2/suggests/companies_list/')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'companies': [
            {'name_id': 'aaa', 'name_ru': 'aaa'},
            {'name_id': 'bbb', 'name_ru': 'bbb'},
            {'name_id': 'ccc', 'name_ru': 'ccc'},
        ],
    }

    # case with specified city
    response = await web_app_client.get(
        '/v2/suggests/companies_list/', params={'city': 'city2'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'companies': [{'name_id': 'ccc', 'name_ru': 'ccc'}]}
