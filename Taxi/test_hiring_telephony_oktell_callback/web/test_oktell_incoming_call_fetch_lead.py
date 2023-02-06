import pytest

ROUTE = '/v1/tasks/oktell/incoming-call/fetch-lead'


@pytest.fixture(name='hiring_candidates_py3')
def hiring_candidates_(mockserver):
    def builder(data, status):
        @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
        def candidates(request):  # pylint: disable=W0612
            response = mockserver.make_response(json=data, status=status)
            return response

    return builder


@pytest.fixture(name='hiring_api')
def hiring_api_(mockserver):
    def builder(data, status):
        @mockserver.json_handler('/hiring-api/v1/leads/create-sync')
        def api(request):  # pylint: disable=W0612
            response = mockserver.make_response(json=data, status=status)
            return response

    return builder


@pytest.mark.usefixtures('personal')
@pytest.mark.parametrize(
    'request_name, candidates_response_name, api_response_name',
    [
        ('default', 'empty', 'default'),
        ('default', 'default', 'not_accessed'),
        ('hiring_api_400', 'empty', '400'),
        ('hiring_api_409', 'empty', '409'),
        ('hiring_api_429', 'empty', '429'),
    ],
)
async def test_simple_request(
        load_json,
        taxi_hiring_telephony_oktell_callback_web,
        hiring_candidates_py3,
        hiring_api,
        request_name,
        candidates_response_name,
        api_response_name,
):
    async def make_request(body, status=200):
        resp = await taxi_hiring_telephony_oktell_callback_web.post(
            ROUTE, json=body,
        )
        assert resp.status == status
        return resp

    request_data = load_json('requests.json')[request_name]
    candidates_data = load_json('candidates_responses.json')[
        candidates_response_name
    ]
    api_data = load_json('api_responses.json')[api_response_name]

    hiring_candidates_py3(**candidates_data)
    hiring_api(**api_data)

    response = await make_request(**request_data['request'])
    body = await response.json()
    assert body
    if request_data['request']['status'] != 200:
        assert 'code' in body
        return
    assert body == request_data['response']
