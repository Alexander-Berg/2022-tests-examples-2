import aiohttp.web
import pytest


FLEET_COUNTRY_PROPERTIES = {
    'deu': {},
    'rus': {'vat_values': ['0', '7', '19']},
    'usa': {'vat_values': ['0.12', '7.34', '19.56']},
}


@pytest.mark.config(FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES)
@pytest.mark.parametrize(
    'park_id, response_200',
    [
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf00f',
            ['0', '7', '19'],
            id='correct_request_rus',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf01f', [], id='correct_request_deu',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf02f',
            ['0.12', '7.34', '19.56'],
            id='correct_request_usa',
        ),
        pytest.param(
            '8601e1f8e094424aa70c81b61ffdf03f', [], id='correct_request_ukr',
        ),
    ],
)
async def test_response_200(
        web_app_client,
        headers,
        park_id,
        response_200,
        mock_fleet_parks,
        load_json,
):
    fleet_parks_stub = load_json('fleet_parks_success.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert (
            request.json['query']['park']['ids'][0]
            in fleet_parks_stub['request']
        )
        return aiohttp.web.json_response(
            fleet_parks_stub['response'][
                request.json['query']['park']['ids'][0]
            ],
        )

    response = await web_app_client.get(
        '/api/v1/country-properties/vat-values',
        headers={**headers, 'X-Park-Id': park_id},
    )

    assert response.status == 200

    data = await response.json()
    assert list(data.keys()) == ['vat_values']
    assert data['vat_values'] == response_200
