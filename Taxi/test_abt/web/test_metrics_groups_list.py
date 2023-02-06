import pytest

from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'post', '/v1/metrics_groups/list', taxi_abt_web,
    )


async def prepare_state(abt):
    return [
        await abt.state.add_metrics_group(
            title=lhs,
            description=rhs,
            scopes=[f'scope_{lhs}'],
            owners=[f'owner_{lhs}'],
        )
        for lhs, rhs in [('one', 'first'), ('two', 'second')]
    ]


@pytest.mark.parametrize(
    'body,expected_titles',
    [
        pytest.param(
            {}, ['one', 'two'], id='Fetch all due to no params specified',
        ),
        pytest.param({'query': 'one'}, ['one'], id='Fetch by query'),
        pytest.param({'scopes': ['scope_one']}, ['one'], id='Fetch by scope'),
        pytest.param({'owners': ['owner_two']}, ['two'], id='Fetch by owner'),
        pytest.param(
            {'query': 'one', 'owners': ['owner_two']},
            [],
            id='Fetch by query and owner -> no results',
        ),
        pytest.param(
            {'query': 'one', 'owners': ['owner_one']},
            ['one'],
            id='Fetch by query and owner -> one result',
        ),
        pytest.param(
            {'owners': ['owner_one'], 'scopes': ['scope_one']},
            ['one'],
            id='Fetch by scope and owner -> one result',
        ),
        pytest.param(
            {'owners': ['owner_one', 'owner_two'], 'scopes': ['scope_one']},
            ['one'],
            id='Fetch by 2 owners and 1 scope -> one result',
        ),
    ],
)
async def test_metrics_groups_list(abt, invoke_handler, body, expected_titles):
    added_metrics_groups = await prepare_state(abt)
    title_to_id_map = {
        group['title']: group['id'] for group in added_metrics_groups
    }
    expected_ids = [title_to_id_map[title] for title in expected_titles]

    got = await invoke_handler(body=body)

    assert [group['id'] for group in got['metrics_groups']] == expected_ids
