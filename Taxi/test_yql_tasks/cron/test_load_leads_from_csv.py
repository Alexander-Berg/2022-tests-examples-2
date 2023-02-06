import logging

import aiohttp
from aiohttp import web

from yql_tasks.internal import load_csv_leads_from_csv

logger = logging.getLogger(__name__)

TOKEN = 'token_park_rejected_lead'


async def test_load_csv(mockserver, cron_context, load, load_json):
    @mockserver.handler('/smthing_data')
    def data_handler(request):  # pylint: disable=unused-variable
        return aiohttp.web.Response(text=load('load.csv'))

    logger.error('Smth test %s', dir(cron_context))
    expected_result = load_json('load_csv_result.json')
    url = mockserver.url('smthing_data')
    data = await load_csv_leads_from_csv.load_csv(cron_context, url)
    assert len(data) == 13
    for lead in data:
        assert {
            k: v for k, v in lead.serialize().items() if k != 'lead_id'
        } in expected_result


async def test_send_leads_to_hiring_api(
        cron_context, mock_hiring_api, load_json,
):
    requests = load_json('expected_request.json')

    @mock_hiring_api('/v1/tickets/create')
    def handler(request):  # pylint: disable=unused-variable
        expected_request = requests[request.headers['X-Delivery-Id']]
        assert expected_request['body'] == request.json
        assert expected_request['endpoint'] == request.args['endpoint']
        return web.json_response(load_json('success_response.json'))

    data = load_json('leads_for_infranaim.json')
    res = await load_csv_leads_from_csv.send_leads_to_hiring_api(
        cron_context, data,
    )
    assert res == {'created': len(data), 'duplicate': 0, 'error': 0}
