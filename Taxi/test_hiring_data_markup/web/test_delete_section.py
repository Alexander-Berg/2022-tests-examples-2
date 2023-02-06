import pytest

REQUESTS_FILE = 'requests.json'
ROUTE = '/v2/section/delete'
QUERY_ADD_ENDPOINT = """
INSERT INTO hiring_data_markup.endpoints
    ("name", "description", "markup", "section", "limit")
VALUES
    ('online', 'description', \'{\"data\" : 1}\'::jsonb,
    'salesforce_all_leads', 20);
INSERT INTO hiring_data_markup.sections
    ("name", "description", "markup")
VALUES
    ('salesforce_all_leads', 'description', \'{\"data\" : 1}\'::jsonb);
"""


async def check_table_is_empty(table_name: str, web_context):
    query = f'SELECT * FROM hiring_data_markup.{table_name}'
    async with web_context.postgresql() as connection:
        rows = list(await connection.fetch(query))
        assert not rows


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY_ADD_ENDPOINT])
@pytest.mark.parametrize('request_name', ['simple'])
async def test_delete_endpoint(
        web_context,
        taxi_hiring_data_markup_web,
        load_json,
        pgsql,
        request_name,
):
    request = load_json(REQUESTS_FILE)[request_name]
    response = await taxi_hiring_data_markup_web.post(ROUTE, **request)

    assert response.status == 200
    await check_table_is_empty('sections', web_context)
    await check_table_is_empty('endpoints', web_context)


@pytest.mark.pgsql('hiring_data_markup', queries=[QUERY_ADD_ENDPOINT])
@pytest.mark.parametrize('request_name', ['not_exist'])
async def test_delete_endpoint_not_found(
        web_context,
        taxi_hiring_data_markup_web,
        load_json,
        pgsql,
        request_name,
):
    request = load_json(REQUESTS_FILE)[request_name]
    response = await taxi_hiring_data_markup_web.post(ROUTE, **request)
    assert response.status == 404
