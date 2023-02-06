import pytest

QUERY = """
INSERT INTO hiring_data_markup.endpoints
    (name, description, markup, section, "limit")
VALUES
    ('endpoint1', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb,
    'section', 20),
    ('endpoint2', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb,
    'section', 20),
    ('endpoint3', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb,
    'section', 20);
"""


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY])
@pytest.mark.parametrize('total_items, offset', [('three', 0), ('zero', 3)])
@pytest.mark.now('2021-12-12T03:00:00+03:00')
async def test_get_endpoint_list(
        web_app_client, load_json, total_items, offset,
):
    expected_result = load_json('expected_result.json')
    response = await web_app_client.get(
        f'/v2/endpoint/list?section=section&limit=3&offset={offset}',
    )
    assert response.status == 200
    assert await response.json() == expected_result[total_items]
