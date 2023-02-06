import pytest

from taxi import discovery

from taxi_billing_calculators.stq.main import task as stq_main_task
from taxi_billing_calculators.stq.taximeter import task as stq_taximeter_task
from . import common


@pytest.mark.config(BILLING_CALCULATORS_SEND_PAYMENTS_TO_TAXIMETER=True)
@pytest.mark.parametrize(
    ['data_path', 'doc_id', 'expected_docs_calls', 'expected_taximeter_calls'],
    [
        ('taximeter_request.json', 1004, 2, 1),
        ('taximeter_request.json', 1005, 3, 1),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_taximeter_request(
        data_path,
        doc_id,
        expected_docs_calls,
        expected_taximeter_calls,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_taximeter_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            new_doc = json.copy()
            new_doc['doc_id'] = 2005
            return response_mock(json=new_doc)
        if 'is_ready_for_processing' in url:
            json_data = load_json(data_path)
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'ready': True, 'doc': one_doc})
            assert False, 'Doc not found'
        elif 'finish_processing' in url:
            return response_mock(json={})
        raise NotImplementedError

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'POST')
    def _patch_taximeter_request(method, url, headers, json, **kwargs):
        assert 'process_events' in url
        json_data = load_json(data_path)
        json_data_by_doc_id = {
            data['doc_id']: data for data in json_data['taximeter_response']
        }
        assert json == json_data_by_doc_id[doc_id]['request']
        return response_mock(json=json_data_by_doc_id[doc_id]['response'])

    await stq_taximeter_task.process_doc(
        taxi_billing_calculators_stq_taximeter_ctx,
        task_info=common.create_task_info(),
        doc_id=doc_id,
    )

    assert len(_patch_billing_docs_request.calls) == expected_docs_calls
    assert len(_patch_taximeter_request.calls) == expected_taximeter_calls


@pytest.mark.config(BILLING_CALCULATORS_SEND_PAYMENTS_TO_TAXIMETER=True)
@pytest.mark.parametrize(
    ['data_path', 'expected_docs_calls', 'expected_taximeter_calls'],
    [
        ('taximeter_request_1004.json', 0, 1),
        ('taximeter_request_1005.json', 1, 1),
        ('taximeter_request_billing_park_commission.json', 0, 1),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_taximeter_request_without_doc(
        data_path,
        expected_docs_calls,
        expected_taximeter_calls,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_taximeter_ctx,
):
    json_data = load_json(data_path)
    taximeter_response = json_data['taximeter_response']
    stq_task_kwargs = json_data['stq_task_kwargs']

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            new_doc = json.copy()
            new_doc['doc_id'] = 2005
            return response_mock(json=new_doc)
        raise NotImplementedError

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'POST')
    def _patch_taximeter_request(method, url, headers, json, **kwargs):
        assert 'process_events' in url
        return response_mock(json=taximeter_response)

    await stq_taximeter_task.process_doc(
        taxi_billing_calculators_stq_taximeter_ctx,
        task_info=common.create_task_info(),
        doc_id=None,
        **stq_task_kwargs,
    )

    assert len(_patch_billing_docs_request.calls) == expected_docs_calls
    assert len(_patch_taximeter_request.calls) == expected_taximeter_calls


@pytest.mark.config(BILLING_CALCULATORS_SEND_PAYMENTS_TO_TAXIMETER=True)
@pytest.mark.parametrize(
    ['request_json', 'response_json', 'expected_doc_json'],
    [
        (
            'taximeter_request.json',
            'not_empty_response.json',
            'not_empty_response_expected_doc.json',
        ),
        (
            'taximeter_request.json',
            'empty_response.json',
            'empty_response_expected_doc.json',
        ),
        (
            'taximeter_request.json',
            'error_response.json',
            'error_response_expected_doc.json',
        ),
    ],
)
# pylint: disable=invalid-name
async def test_handle_taximeter_response(
        request_json,
        response_json,
        expected_doc_json,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_taximeter_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            new_doc = json.copy()
            new_doc['doc_id'] = 2006
            return response_mock(json=new_doc)
        if 'is_ready_for_processing' in url:

            doc = load_json(request_json)
            return response_mock(json={'ready': True, 'doc': doc})
        if 'finish_processing' in url:
            assert json == load_json(expected_doc_json)
            return response_mock(json={})
        raise NotImplementedError

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'POST')
    def _patch_taximeter_request(method, url, headers, json, **kwargs):
        assert 'process_events' in url
        return response_mock(json=load_json(response_json))

    await stq_taximeter_task.process_doc(
        taxi_billing_calculators_stq_taximeter_ctx,
        task_info=common.create_task_info(),
        doc_id=1001,
    )


@pytest.mark.config(BILLING_CALCULATORS_SEND_PAYMENTS_TO_TAXIMETER=True)
@pytest.mark.parametrize(
    ['request_json', 'response_json', 'expected_exception'],
    [
        ('taximeter_request.json', 'error_response.json', ValueError),
        ('taximeter_request.json', 'wrong_amount_response.json', ValueError),
    ],
)
# pylint: disable=invalid-name
async def test_handle_error_taximeter_response(
        request_json,
        response_json,
        expected_exception,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_taximeter_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert 'is_ready_for_processing' in url
        doc = load_json(request_json)
        return response_mock(json={'ready': True, 'doc': doc})

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'POST')
    def _patch_taximeter_request(method, url, headers, json, **kwargs):
        assert 'process_events' in url
        return response_mock(json=load_json(response_json))

    with pytest.raises(expected_exception):
        await stq_taximeter_task.process_doc(
            taxi_billing_calculators_stq_taximeter_ctx,
            task_info=common.create_task_info(),
            doc_id=1001,
        )


@pytest.mark.config(
    BILLING_CALCULATORS_SEND_PAYMENTS_TO_TAXIMETER=True,
    BILLING_CALCULATORS_USE_BUFFER_PROXY=True,
)
@pytest.mark.parametrize(
    ['data_path', 'doc_id', 'expected_docs_calls', 'expected_taximeter_calls'],
    [
        ('taximeter_request.json', 1004, 2, 2),
        ('taximeter_request.json', 1005, 3, 2),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_buffer_proxy(
        data_path,
        doc_id,
        expected_docs_calls,
        expected_taximeter_calls,
        load_json,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_taximeter_ctx,
):
    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            new_doc = json.copy()
            new_doc['doc_id'] = 2005
            return response_mock(json=new_doc)
        if 'is_ready_for_processing' in url:
            json_data = load_json(data_path)
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'ready': True, 'doc': one_doc})
            assert False, 'Doc not found'
        elif 'finish_processing' in url:
            return response_mock(json={})
        raise NotImplementedError

    @patch_aiohttp_session(
        discovery.find_service('billing_buffer_proxy').url, 'POST',
    )
    def _patch_taximeter_request(method, url, headers, json, **kwargs):
        if 'push' in url:
            return response_mock(json={})
        if 'poll' in url:
            response = {}
            json_data = load_json(data_path)
            for one_doc_res in json_data['taximeter_response']:
                if one_doc_res['doc_id'] == doc_id:
                    response = one_doc_res['response']
                    break
            return response_mock(
                json={
                    'status': 'sent',
                    'response': {
                        'http_status': 200,
                        'text': None,
                        'json': response,
                    },
                },
            )
        raise NotImplementedError

    await stq_taximeter_task.process_doc(
        taxi_billing_calculators_stq_taximeter_ctx,
        task_info=common.create_task_info(),
        doc_id=doc_id,
    )

    assert len(_patch_billing_docs_request.calls) == expected_docs_calls
    assert len(_patch_taximeter_request.calls) == expected_taximeter_calls


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('taximeter_open_account.json', 1001),
        ('taximeter_open_account_already_exists.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_process_taximeter_open_account(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
):
    await _test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
    )


# pylint: disable=invalid-name
async def _test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
):

    account_idx = 1
    docs_created = []
    entities_created = []
    accounts_created = []

    json_data = load_json(data_path)
    expected_docs = json_data['expected_docs']
    expected_accounts = json_data['expected_accounts']
    expected_entities = json_data['expected_entities']
    accounts = json_data.get('accounts', [])

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'create' in url:
            docs_created.append(json)
            new_doc = json.copy()
            new_doc['doc_id'] = 2001
            return response_mock(json=new_doc)
        if 'is_ready_for_processing' in url:
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'ready': True, 'doc': one_doc})
            assert False, 'Doc not found'
        elif 'finish_processing' in url:
            return response_mock(json={})
        return None

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _patch_billing_accounts_entities_search(request):
        return mockserver.make_response(json=[])

    @mockserver.json_handler('/billing-accounts/v1/entities/create')
    def _patch_billing_accounts_entities_create(request):
        new_entity = request.json.copy()
        new_entity['created'] = '2018-10-10T09:56:13.758202Z'
        entities_created.append(request.json)
        return mockserver.make_response(json=new_entity)

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _patch_billing_accounts_v1_accounts_search(request):
        return mockserver.make_response(json=accounts)

    @mockserver.json_handler('/billing-accounts/v1/accounts/create')
    def _patch_billing_accounts_v1_accounts_create(request):
        nonlocal account_idx

        new_acc = request.json.copy()
        new_acc['account_id'] = account_idx
        new_acc['opened'] = '2018-10-10T09:56:13.758202Z'
        account_idx += 1
        accounts_created.append(new_acc)
        return mockserver.make_response(json=new_acc)

    await stq_main_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=common.create_task_info(),
        doc_id=doc_id,
    )

    assert expected_entities == entities_created
    assert expected_accounts == accounts_created
    assert expected_docs == docs_created
