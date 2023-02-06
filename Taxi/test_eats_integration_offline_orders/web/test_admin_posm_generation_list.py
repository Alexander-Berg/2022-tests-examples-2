import pytest

DEFAULT_DATE_TO = '2022-05-17 23:00:00+0300'


@pytest.mark.parametrize(
    ('params', 'expected_ids', 'has_more'),
    (
        pytest.param(
            {'date_to': DEFAULT_DATE_TO}, [4, 3, 2, 1], False, id='OK',
        ),
        pytest.param(
            {'date_to': '2022-05-17 21:30:00+0300'},
            [2, 1],
            False,
            id='date_to',
        ),
        pytest.param(
            {
                'date_to': DEFAULT_DATE_TO,
                'date_from': '2022-05-17 21:30:00+0300',
            },
            [4, 3],
            False,
            id='date_from',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 1}, [4], True, id='limit',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 1, 'offset': 1},
            [3],
            True,
            id='offset',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'place_id': 'place_id__2'},
            [4],
            False,
            id='place_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'place_id': 'place_id__1'},
            [3, 2, 1],
            False,
            id='place_id-few',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'template_id': 1},
            [2, 1],
            False,
            id='template_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'author': 'username'},
            [3, 1],
            False,
            id='author',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
        'posm_generations.sql',
        'posm_generations_templates.sql',
    ],
)
async def test_admin_posm_generation_list(
        taxi_eats_integration_offline_orders_web,
        params,
        expected_ids,
        has_more,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/generation/list', params=params,
    )
    body = await response.json()
    generation_ids = [
        generation['generation_id'] for generation in body['generations']
    ]
    assert generation_ids == expected_ids
    assert body['has_more'] is has_more
