import pytest

from taxi import discovery


@pytest.mark.now('2019-10-07T15:00:00')
@pytest.mark.config(BILLING_EYE_SAVE_ALIAS_ID_TAG=True)
@pytest.mark.parametrize(
    'location, request_data_path',
    [
        ('/v1/antifraud', 'antifraud_action.json'),
        ('/v1/rebill_order', 'rebill_order.json'),
        ('/v1/rebill_order', 'rebill_old_order.json'),
    ],
)
async def test_insert_doc(
        location,
        request_data_path,
        load_json,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
):
    created_docs = []

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'create' in url
        assert json.get('tags', []) == data['expected_doc_tags']
        del json['event_at']
        created_docs.append(json)
        return response_mock(json={'doc_id': 1042, 'kind': json['kind']})

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(
            method, url, headers, json, **kwargs,
    ):
        assert 'process_doc' in url
        assert json['doc']['id'] == 1042
        return response_mock(json=json)

    data = load_json(request_data_path)
    response = await taxi_billing_orders_client.post(
        location, headers=request_headers, json=data['request'],
    )
    assert response.status == data['expected_response']['status_code']
    content = await response.json()
    assert created_docs == data['expected_created_docs']
    assert content == data['expected_response']['content']
