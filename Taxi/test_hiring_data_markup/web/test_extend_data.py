import pytest

QUERY = """
INSERT INTO hiring_data_markup.endpoints
    (name, description, markup, section, "limit")
VALUES
    ('endpoint', 'description',
    \'[{\"name\" : "test1", "value": 1}, '
    '{\"name\" : "test_endpoint", "value": 1}]\'::jsonb,
    'section', 20);
INSERT INTO hiring_data_markup.sections
    (name, description, markup)
VALUES
    ('section', 'description',
    \'[{\"name\" : "test1", "value": 33}, '
    '{\"name\" : "test_section", "value": 1}]\'::jsonb);
"""


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY])
@pytest.mark.parametrize(
    'status_code, endpoint', [(200, 'endpoint'), (404, 'not_endpoint')],
)
@pytest.mark.now('2021-12-12T03:00:00+03:00')
async def test_get_endpoint(web_app_client, load_json, status_code, endpoint):
    request_data = load_json('request_data.json')
    expected_result = load_json('expected_result.json')
    response = await web_app_client.post(
        f'/v2/extend-data?section=section&endpoint={endpoint}',
        json=request_data,
    )
    assert response.status == status_code
    assert await response.json() == expected_result[endpoint]
