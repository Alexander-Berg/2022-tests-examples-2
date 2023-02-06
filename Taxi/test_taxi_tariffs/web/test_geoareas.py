import pytest


@pytest.mark.parametrize(
    'country, geoareas',
    [
        (
            None,
            [
                {'name': 'pavlodar_activation', 'country': 'kaz'},
                {'name': 'vladivostok', 'country': 'rus'},
            ],
        ),
        ('rus', [{'name': 'vladivostok', 'country': 'rus'}]),
        ('kaz', [{'name': 'pavlodar_activation', 'country': 'kaz'}]),
    ],
)
async def test_get_list_country(web_app_client, country, geoareas):
    params = {}
    if country:
        params['country'] = country
    response = await web_app_client.get('/v1/geoareas', params=params)
    data = await response.json()
    assert response.status == 200, data
    assert data == {'geoareas': geoareas}
