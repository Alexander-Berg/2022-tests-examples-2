import pytest

from taxi import discovery


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2020-10-08T08:08:08+00:00')
@pytest.mark.parametrize(
    'test_data_path',
    [
        'subventions_csv_yt_upload_completed.json',
        'subventions_csv_yt_upload_processing.json',
        'grocery_courier_coupon_yt_upload_processing.json',
        'grocery_courier_coupon_amount_details.json',
        'yt_path_request_yt_upload_processing.json',
        'yt_path_request_yt_upload_complete.json',
        'yt_path_request_yt_upload_complete_with_error.json',
    ],
)
async def test_v1_manual_transactions_check(
        request_headers,
        patched_tvm_ticket_check,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        test_data_path,
        load_py_json_dir,
):
    test_data = load_py_json_dir(
        'test_v1_manual_transactions_check', test_data_path,
    )
    existing_docs = test_data['existing_docs']
    expected_created_docs = test_data.get('expected_created_docs', [])
    actual_created_docs = []
    next_doc_id = 1000

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            nonlocal next_doc_id
            resp = {'doc_id': next_doc_id, 'kind': json['kind']}
            next_doc_id += 1
            actual_created_docs.append(json)
            return response_mock(json=resp)
        if 'select' in url:
            if 'cursor' in json:
                docs = []
            else:
                docs = [
                    doc
                    for doc in existing_docs
                    if doc['external_obj_id'] == json['external_obj_id']
                ]
            return response_mock(json={'docs': docs, 'cursor': 'some_cursor'})
        return None

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    request = test_data['request']
    response = await taxi_billing_orders_client.post(
        '/v1/manual_transactions/check/',
        headers=request_headers,
        json=request,
    )
    assert response.status == test_data['response_status']
    response_json = await response.json()
    if response.status == 400:
        assert response_json['code'] == test_data['response']['code']
    else:
        assert response_json == test_data['response']
    assert actual_created_docs == expected_created_docs
