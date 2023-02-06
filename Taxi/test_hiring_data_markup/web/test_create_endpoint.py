import pytest

REQUESTS_FILE = 'requests.json'
EXPECTED_FILE = 'expected.json'
ROUTE = '/v2/endpoint/create'
OK = 201


@pytest.mark.parametrize('request_name', ['simple'])
async def test_create_endpoint(
        web_context,
        taxi_hiring_data_markup_web,
        load_json,
        pgsql,
        request_name,
):
    request = load_json(REQUESTS_FILE)[request_name]
    expected = load_json(EXPECTED_FILE)[request_name]
    response = await taxi_hiring_data_markup_web.post(ROUTE, **request)

    assert response.status == OK

    query = 'SELECT * FROM hiring_data_markup.endpoints '
    async with web_context.postgresql() as connection:
        rows = list(await connection.fetch(query))
        assert dict(rows[-1]) == expected


@pytest.mark.parametrize('request_name', ['simple'])
async def test_create_endpoint_duplicate(
        web_context,
        taxi_hiring_data_markup_web,
        load_json,
        pgsql,
        request_name,
):
    request = load_json(REQUESTS_FILE)[request_name]

    response = await taxi_hiring_data_markup_web.post(ROUTE, **request)
    assert response.status == OK
    response = await taxi_hiring_data_markup_web.post(ROUTE, **request)
    assert response.status == 400
