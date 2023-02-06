# pylint: disable=redefined-outer-name

import pytest


@pytest.mark.parametrize(
    ['query', 'expected_request_ids'],
    [
        pytest.param(
            {'updated_since': '2018-04-20 00:00:00'},
            ['rejected', '95b3c932435f4f008a635faccb6454f6'],
        ),
        pytest.param({}, None),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_bulk_retrieve(
        mock_personal,
        mock_mds,
        taxi_corp_requests_web,
        load_json,
        query,
        expected_request_ids,
):
    response = await taxi_corp_requests_web.get(
        '/v1/client-requests/list/updated-since', params=query,
    )

    assert response.status == 200

    response_json = await response.json()

    expected_requests = load_json('expected_requests.json')

    if expected_request_ids is not None:
        expected_requests = [
            expected_requests[req] for req in expected_request_ids
        ]

    assert (
        len(expected_request_ids) if expected_request_ids is not None else 7
    ) == len(response_json['client_requests'])

    if expected_request_ids is not None:
        assert response_json['client_requests'] == expected_requests
