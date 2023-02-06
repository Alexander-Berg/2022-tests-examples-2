import pytest

QUERY = """
INSERT INTO hiring_data_markup.sections
    (name, description, markup)
VALUES
    ('section1', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb),
    ('section2', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb),
    ('section3', 'description', \'[{\"name\" : "test1", "value": 1}]\'::jsonb);
"""


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY])
@pytest.mark.now('2021-12-12T03:00:00+03:00')
async def test_get_section_list(web_app_client, load_json):
    expected_result = load_json('expected_result.json')
    response = await web_app_client.get(f'/v2/section/list')
    assert response.status == 200
    assert await response.json() == expected_result['three']
