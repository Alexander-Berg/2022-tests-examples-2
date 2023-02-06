import pytest

QUERY = """
INSERT INTO hiring_data_markup.endpoints
    (name, description, markup, section, "limit")
VALUES
    ('endpoint', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb,
    'section', 20);
"""


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY])
@pytest.mark.parametrize(
    'status_code, endpoint', [(200, 'endpoint'), (404, 'not_endpoint')],
)
@pytest.mark.now('2021-12-12T03:00:00+03:00')
async def test_get_endpoint(web_app_client, load_json, status_code, endpoint):
    expected_result = load_json('expected_result.json')
    response = await web_app_client.get(
        f'/v2/endpoint?section=section&endpoint={endpoint}',
    )
    assert response.status == status_code
    assert await response.json() == expected_result[endpoint]
