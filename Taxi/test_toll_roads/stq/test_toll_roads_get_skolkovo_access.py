import json

import pytest

from toll_roads.stq import toll_roads_get_skolkovo_access


ORDER_CREATED = '2020-01-02T10:00:00'


@pytest.mark.pgsql('toll_roads', files=['init_skolkovo_token.sql'])
@pytest.mark.config(SKOLKOVO_URL='$mockserver/skolkovo-api')
async def test_get_skolkovo_access(stq3_context, simple_secdist, mockserver):
    @mockserver.json_handler('/skolkovo-api/api/RequestStandard/create')
    async def skolkovo_api(request):
        return {'id': 2970016, 'success': True}

    await toll_roads_get_skolkovo_access.task(
        stq3_context, 'car_number', ORDER_CREATED,
    )
    assert skolkovo_api.times_called == 1


@pytest.mark.pgsql('toll_roads', files=['init_skolkovo_token.sql'])
@pytest.mark.config(
    SKOLKOVO_API_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 3000},
    },
    TOLL_ROADS_SLEEP_AFTER_SKOLKOVO_API_FAILED_SEC=0,
    SKOLKOVO_URL='$mockserver/skolkovo-api',
)
@pytest.mark.parametrize(
    'skolkovo_api_resp',
    [
        {
            'success': False,
            'errorText': 'errorText',
            'errorType': 'errorType',
            'errorCode': 1,
            'subErrorCode': 3,
        },
        '',
    ],
)
async def test_get_skolkovo_access_reschedule(
        stq3_context, simple_secdist, mockserver, skolkovo_api_resp,
):
    @mockserver.json_handler('/skolkovo-api/api/RequestStandard/create')
    async def skolkovo_api(request):
        return mockserver.make_response(json.dumps(skolkovo_api_resp), 500)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def stq_agent_reschedule(request):
        return {}

    await toll_roads_get_skolkovo_access.task(
        stq3_context, 'car_number', ORDER_CREATED,
    )
    assert skolkovo_api.times_called == 3
    assert stq_agent_reschedule.times_called == 1


@pytest.mark.pgsql('toll_roads', files=['init_skolkovo_token.sql'])
@pytest.mark.config(
    SKOLKOVO_API_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 3000},
    },
    TOLL_ROADS_SLEEP_AFTER_SKOLKOVO_API_FAILED_SEC=0,
    SKOLKOVO_URL='$mockserver/skolkovo-api',
)
async def test_get_skolkovo_access_invalid_token(
        stq3_context, simple_secdist, mockserver,
):
    @mockserver.json_handler('/skolkovo-api/api/RequestStandard/create')
    async def skolkovo_api(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'success': False,
                    'errorText': (
                        'Параметр запроса key не указан, '
                        'пуст или имеет неверный формат'
                    ),
                    'errorType': 'ApiException',
                    'errorCode': 1,
                    'subErrorCode': 2,
                },
            ),
            500,
        )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def stq_agent_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/toll_roads_get_skolkovo_token',
    )
    def stq_agent_add(request):
        return {}

    await toll_roads_get_skolkovo_access.task(
        stq3_context, 'car_number', ORDER_CREATED,
    )
    assert skolkovo_api.times_called == 3
    assert stq_agent_reschedule.times_called == 1
    assert stq_agent_add.times_called == 1
