import pytest

QUERY = """
INSERT INTO hiring_data_markup.sections
    (name, description, markup)
VALUES
    ('section', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb);
"""


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY])
@pytest.mark.parametrize(
    'status_code, section', [(200, 'section'), (404, 'not_section')],
)
@pytest.mark.now('2021-12-12T03:00:00+03:00')
async def test_get_section(web_app_client, load_json, status_code, section):
    expected_result = load_json('expected_result.json')
    response = await web_app_client.get(f'/v2/section?section={section}')
    assert response.status == status_code
    assert await response.json() == expected_result[section]
