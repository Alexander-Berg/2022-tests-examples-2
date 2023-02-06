import pytest

from eats_corp_orders.internal import types

DEFAULT_TERMINAL = {
    'id': 'terminal_id',
    'place_id': '146',
    'token': '6j3/BEioT3vgvNa9ca2U7e+DuO1dqEs9x8hShzbet/I=',
    'dek': 'pbrXGGxr9JdNTEsQeCjss+gc/8S9hyYndVkxdNw0B5e3B0CV4WXAyCZZBcIP7aqxLRCql1nNVjeTXDBBNCYQYQ==',  # noqa: E501
    'slug': None,
    'idempotency_key': None,
    'enabled': True,
}


async def check_terminal(context: types.Context, updated: dict):
    terminal = await context.queries.terminal_tokens.get_by_id('terminal_id')
    assert terminal
    result = terminal.serialize()
    del result['created_at']
    del result['updated_at']
    expected = dict(DEFAULT_TERMINAL)
    expected.update(updated)
    return result == expected


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
@pytest.mark.parametrize(
    ('params', 'r_json', 'expected_status'),
    [
        ({'terminal_id': 'not_found'}, {}, 404),
        ({'terminal_id': 'terminal_id'}, {'slug': 'new_slug'}, 200),
        ({'terminal_id': 'terminal_id'}, {'slug': 'new_slug'}, 200),
        ({'terminal_id': 'terminal_id'}, {'enabled': False}, 200),
        (
            {'terminal_id': 'terminal_id'},
            {'slug': 'new_slug', 'enabled': False},
            200,
        ),
    ],
)
async def test_admin_terminal_modify(
        taxi_eats_corp_orders_web,
        params,
        r_json,
        expected_status,
        web_context,
):
    response = await taxi_eats_corp_orders_web.patch(
        '/v1/admin/terminal', params=params, json=r_json,
    )
    assert response.status == expected_status
    assert await check_terminal(web_context, r_json)
