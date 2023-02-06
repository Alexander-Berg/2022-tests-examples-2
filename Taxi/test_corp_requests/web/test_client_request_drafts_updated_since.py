# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.parametrize(
    ['query', 'expected_draft_ids'],
    [
        pytest.param(
            {'updated_since': '2020-04-21 11:00:00'}, ['draft', 'small'],
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_drafts_updates_since(
        taxi_corp_requests_web,
        mock_personal,
        query,
        expected_draft_ids,
        load_json,
):
    response = await taxi_corp_requests_web.get(
        '/v1/client-request-drafts/list/updated-since', params=query,
    )

    assert response.status == 200
    response_json = await response.json()

    expected_drafts = load_json('expected_request_drafts.json')

    expected_drafts = [expected_drafts[req] for req in expected_draft_ids]
    assert response_json['client_request_drafts'] == expected_drafts
