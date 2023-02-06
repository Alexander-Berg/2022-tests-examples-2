import pytest

from tests_grocery_discounts import common


PRIORITY_CHECK_URL = '/v3/admin/priority/check/'
PRIORITY_URL = '/v3/admin/priority/'


async def add_bin_set(client):
    body = {
        'name': 'prioritized_entity',
        'bins': [123321, 221122],
        'time': {'start': '2020-02-01T18:00:00', 'end': '2020-09-01T18:00:00'},
    }
    await client.post(
        common.BIN_SET_URL,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
        json=body,
    )


@pytest.mark.parametrize(
    'prioritized_entity_type',
    (
        pytest.param('bin_set', id='bin_set'),
        pytest.param('class', id='class'),
        pytest.param('tag', id='tag'),
        pytest.param('experiment', id='experiment'),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_priority(client, prioritized_entity_type: str):
    body = {
        'prioritized_entity_type': prioritized_entity_type,
        'priority_groups': [
            {'name': 'default', 'entities_names': ['prioritized_entity']},
        ],
    }
    current: dict = {
        'prioritized_entity_type': prioritized_entity_type,
        'priority_groups': [{'entities_names': [], 'name': 'default'}],
    }
    if prioritized_entity_type == 'bin_set':
        await add_bin_set(client)
        current['priority_groups'][0]['entities_names'] = [
            'prioritized_entity',
        ]
    expected_check_response = {
        'change_doc_id': prioritized_entity_type + '-priority',
        'data': body,
        'diff': {'current': current, 'new': body},
    }

    response = await client.post(
        PRIORITY_CHECK_URL, body, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status == 200
    assert response.json() == expected_check_response

    response = await client.get(
        PRIORITY_URL,
        params={'prioritized_entity_type': prioritized_entity_type},
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == current

    response = await client.post(
        PRIORITY_URL, body, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status == 200
    assert response.json() == body

    response = await client.get(
        PRIORITY_URL,
        params={'prioritized_entity_type': prioritized_entity_type},
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == body
