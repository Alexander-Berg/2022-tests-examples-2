import pytest

from taxi import discovery


@pytest.mark.parametrize(
    'data_path',
    [
        'new_request.json',
        'new_request_file_id_and_yt_path.json',
        'complete_document_exists.json',
        'new_document_exists.json',
        'complete_documents_with_errors_exist.json',
        'arbitrary_revenues_request.json',
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    MANUAL_TRANSACTIONS_CREATE_SETTINGS={
        '__default__': {
            'docs_select_max_requests': 10,
            'docs_select_limit': 10,
        },
    },
)
@pytest.mark.now('2020-10-08T08:08:08+00:00')
async def test_v1_manual_transactions_create(
        request_headers,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        response_mock,
        patch_aiohttp_session,
        load_py_json_dir,
        patch,
        data_path,
):
    test_data = load_py_json_dir(
        'test_v1_manual_transactions_create', data_path,
    )
    request_data = test_data['request_data']
    existing_docs = test_data['existing_docs']
    expected_response = test_data['expected_response']
    mds_file = test_data['mds_file']
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

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        content = '\n'.join(mds_file)
        return bytearray(content.encode('utf-8'))

    response = await taxi_billing_orders_client.post(
        '/v1/manual_transactions/create/',
        headers={
            **request_headers,
            'X-YaTaxi-Draft-Approvals': 'login-1,login-2',
            'X-YaTaxi-Draft-Tickets': 'ticket-1,ticket-2',
            'X-YaTaxi-Draft-Author': 'login-3',
            'X-YaTaxi-Draft-Id': 'draft-id-1',
        },
        json=request_data,
    )
    actual_json = await response.json()
    assert response.status == 200
    assert actual_json == expected_response
    if expected_created_docs:
        assert actual_created_docs == expected_created_docs


@pytest.mark.parametrize(
    'data_path',
    ['validate_total_amount.json', 'validate_num_transactions.json'],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    MANUAL_TRANSACTIONS_CREATE_SETTINGS={
        '__default__': {
            'docs_select_max_requests': 10,
            'docs_select_limit': 10,
        },
    },
)
@pytest.mark.now('2020-10-08T08:08:08+00:00')
async def test_v1_manual_transactions_create_invalid(
        request_headers,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        response_mock,
        patch_aiohttp_session,
        load_py_json_dir,
        patch,
        data_path,
):
    test_data = load_py_json_dir(
        'test_v1_manual_transactions_create', data_path,
    )
    request_data = test_data['request_data']
    existing_docs = test_data['existing_docs']
    mds_file = test_data['mds_file']

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
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

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        content = '\n'.join(mds_file)
        return bytearray(content.encode('utf-8'))

    response = await taxi_billing_orders_client.post(
        '/v1/manual_transactions/create/',
        headers=request_headers,
        json=request_data,
    )
    json = await response.json()
    assert response.status == 400
    assert json['code'] == 'validation_error'
