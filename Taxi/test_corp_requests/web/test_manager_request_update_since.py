# pylint: disable=redefined-outer-name

import pytest


@pytest.mark.parametrize(
    ['query', 'expected'],
    [
        pytest.param({'updated_since': '2018-04-20 00:00:00'}, []),
        pytest.param(
            {},
            [
                'request_accepted',
                'request_pending',
                'request_accepting',
                'bad_request',
            ],
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_bulk_retrieve(
        mock_personal,
        mock_mds,
        taxi_corp_requests_web,
        load_json,
        query,
        expected,
):
    response = await taxi_corp_requests_web.get(
        '/v1/manager-request/list/updated-since', params=query,
    )

    assert response.status == 200
    response_json = await response.json()

    for i, value in enumerate(expected):
        assert response_json['manager_requests'][i]['id'] == value
