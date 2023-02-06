import aiohttp
import aiohttp.web
import pytest


@pytest.mark.now('2020-11-12T12:39:00+00:00')
@pytest.mark.config(
    OPTEUM_PARK_LEADS_OPTEUM_PARK_LEADS_QOS={
        'attempts': 2,
        'batch_size': 10,
        'timeout': 1000,
    },
)
async def test_success(
        web_app_client, mock_parks, headers, mock_hiring_api, load_json, patch,
):
    stub = load_json('success.json')

    @mock_hiring_api('/v1/tickets/bulk/create')
    async def _bulk_create(request):
        assert request.json == stub['hiring_api_request']
        return aiohttp.web.json_response(stub['hiring_api_response'])

    with aiohttp.MultipartWriter('form-data') as data:
        part = data.append(
            b'some \x00 data',
            {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # noqa: E501
            },
        )
        part.set_content_disposition(
            'form-data', name='attachment', filename='test.xlsx',
        )

    @patch('taxi_fleet.api.park_leads_upload._rows')
    def _rows(*args, **kwargs):
        return [
            {
                0: 'Driver 1',
                1: '+79111111111',
                2: 'Авто не подходит по классификатору',
                3: None,
            },
            {
                0: 'Driver 2',
                1: '+79111111112',
                2: 'Страна выдачи ВУ не соответствует требованиям',
                3: None,
            },
            {
                0: 'Driver 3',
                1: '+79111111113',
                2: 'Недостаточный стаж',
                3: None,
            },
            {0: 'Driver 4', 1: '+791111111', 2: 'Недостаточный стаж', 3: None},
            {0: None, 1: '+79111111115', 2: None, 3: None},
        ]

    response = await web_app_client.post(
        '/api/v1/park-leads/upload',
        headers={
            **headers,
            'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
            'X-Idempotency-Token': '1',
        },
        data=data,
    )

    assert response.status == 200
