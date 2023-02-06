# import pytest
#
#
# ROUTE = '/v1/lead/activate'
#
# REQUESTS_FILE = 'requests.json'
# HIRING_API_RESPONSES_FILE = 'hiring_api_responses.json'
# EXPECTED_RESPONSES_FILE = 'expected_responses.json'
# # EXPECTED_HIRING_API_FILE = 'expected_hiring_api_calls.json'
#
#
# @pytest.mark.usefixtures('mock_personal_api',
# 'mock_data_markup', 'tvm_client')
# @pytest.mark.parametrize(
#     (
#         'request_name',
#         'hiring_api_response_name',
#         'expected_response_name',
#     ),
#     [
#         ('valid_agent', 'success', 'success'),
#     ],
# )
# @pytest.mark.now('2021-03-03T03:10:00+03:00')
# async def test_v1_leads_create(
#         mock_hiring_api_v1_lead_activate,
#         taxi_hiring_partners_app_web,
#         load_json,
#         request_name,
#         hiring_api_response_name,
#         expected_response_name,
# ):
#     request = load_json(REQUESTS_FILE)[request_name]
#     hiring_api_response = load_json(HIRING_API_RESPONSES_FILE)[
#         hiring_api_response_name
#     ]
#     hiring_api_mock = mock_hiring_api_v1_lead_activate(
#         hiring_api_response['body'], hiring_api_response['status'],
#     )
#
#     response = await taxi_hiring_partners_app_web.post(
#         ROUTE, json=request['data'], headers=request['headers'],
#     )
#
#     expected_response = load_json(EXPECTED_RESPONSES_FILE)[
#         expected_response_name
#     ]
#     assert response.status == expected_response['status']
#     body = await response.json()
#     assert body == expected_response['body']
#
#     # expected_hiring_api = load_json(EXPECTED_HIRING_API_FILE)[
#     #     expected_call_name
#     # ]
#     # assert hiring_api_mock.times_called ==
#     expected_hiring_api['times_called']
#     # if hiring_api_mock.times_called:
#     #     hiring_api_call = hiring_api_mock.next_call()
#     #     request = hiring_api_call['request']
#     #     x_delivery_id = request.headers['X-Delivery-Id']
#     #     query = dict(request.query)
#     #     json = request.json
#     #     assert x_delivery_id == expected_hiring_api['x_delivery_id']
#     #     assert query == expected_hiring_api['query']
#     #     assert json == expected_hiring_api['json']
