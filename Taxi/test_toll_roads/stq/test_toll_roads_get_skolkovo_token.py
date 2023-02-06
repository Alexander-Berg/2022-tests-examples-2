import json

import pytest

from toll_roads.stq import toll_roads_get_skolkovo_token


@pytest.mark.pgsql('toll_roads', files=['init_skolkovo_token.sql'])
@pytest.mark.config(SKOLKOVO_URL='$mockserver/skolkovo-api')
async def test_get_skolkovo_token(
        stq3_context, simple_secdist, mockserver, pgsql,
):
    async def _check_token(expected):
        with pgsql['toll_roads'].cursor() as cursor:
            cursor.execute('SELECT token FROM toll_roads.skolkovo_token;')
            tokens = cursor.fetchall()
            assert len(tokens) == 1
            token = tokens[0]
            assert token[0] == expected

    @mockserver.json_handler('/skolkovo-api/api/Account/Logon')
    async def skolkovo_api(request):
        return {'key': 'skolkovo_key', 'success': True}

    await _check_token('some_token')
    await toll_roads_get_skolkovo_token.task(stq3_context)
    assert skolkovo_api.times_called == 1
    await _check_token('skolkovo_key')


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
            'subErrorCode': 2,
        },
        '',
    ],
)
async def test_get_skolkovo_token_reschedule(
        stq3_context, simple_secdist, mockserver, skolkovo_api_resp,
):
    @mockserver.json_handler('/skolkovo-api/api/Account/Logon')
    async def skolkovo_api(request):
        return mockserver.make_response(json.dumps(skolkovo_api_resp), 500)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def stq_agent_reschedule(request):
        return {}

    await toll_roads_get_skolkovo_token.task(stq3_context)
    assert skolkovo_api.times_called == 3
    assert stq_agent_reschedule.times_called == 1
