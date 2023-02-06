import pytest

TERMINALS = [
    {
        'terminal_id': 'terminal_id',
        'has_menu': False,
        'address': {'short': 'address short', 'comment': 'address comment'},
        'place_name': 'Place 146',
    },
    {
        'terminal_id': 'terminal_id_2',
        'has_menu': False,
        'address': {'short': 'address short', 'comment': 'address comment'},
        'place_name': 'Place 147',
    },
]


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        ({}, 200, {'terminals': TERMINALS, 'has_more': False}),
        (
            {'position': '52.569089,39.60258'},
            200,
            {'terminals': TERMINALS[::-1], 'has_more': False},
        ),
    ],
)
async def test_terminals_get(
        taxi_eats_corp_orders_web,
        eats_user,
        params,
        expected_status,
        expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/user/terminals',
        params=params,
        headers={'X-Eats-User': eats_user},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
