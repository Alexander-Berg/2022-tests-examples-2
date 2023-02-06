from aiohttp import web
import pytest

from taxi import discovery

from taxi_billing_orders import config as orders_config

ENTRIES_TEMPLATES = [
    {
        'agreement_id': 'taxi/%',
        'entity_external_id': 'taximeter_driver_id/%/%',
        'sub_account': '%',
        'mappers': ['park_entry_mapper'],
        'actions': ['send_to_taximeter'],
        'applied_at': {
            'begin': '2020-09-20T12:00:00.00000+00:00',
            'end': '2099-01-01T00:00:00.00000+00:00',
        },
    },
]
ENTRIES_MAPPERS_AND_ACTIONS = {
    'actions': [{'name': 'send_to_taximeter', 'vars': {}}],
    'mappers': [
        {
            'name': 'park_entry_mapper',
            'vars': {
                'alias_id': 'context.alias_id',
                'driver_uuid': 'context.driver.driver_uuid',
            },
        },
    ],
}


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_ARBITRARY_ENTRIES_TEMPLATES=ENTRIES_TEMPLATES,
    BILLING_ARBITRARY_ENTRIES_MAPPERS_AND_ACTIONS=ENTRIES_MAPPERS_AND_ACTIONS,
    TVM_ENABLED=True,
)
@pytest.mark.parametrize('test_data_path', ['arbitrary_entries.json'])
async def test_arbitrary_entries_size_validation(
        test_data_path,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        response_mock,
        patch_aiohttp_session,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        doc = json.copy()
        doc['doc_id'] = 111111
        doc['created'] = doc['event_at']
        return response_mock(status=200, json=doc)

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    # Test positive result with default config
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    assert response.status == data['response_status']

    # Test negative result with low limit for details

    monkeypatch.setattr(
        orders_config.Config, 'BILLING_ARBITRARY_ENTRIES_DETAILS_MAX_SIZE', 10,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    assert response.status == web.HTTPBadRequest.status_code

    # Test negative result with low limit for full event
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ARBITRARY_ENTRIES_DETAILS_MAX_SIZE',
        10000,
    )
    monkeypatch.setattr(
        orders_config.Config, 'BILLING_ARBITRARY_ENTRIES_CONTEXT_MAX_SIZE', 10,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    assert response.status == web.HTTPBadRequest.status_code
