from typing import Optional

import pytest

from taxi import discovery
from taxi.clients import stq_agent

from taxi_billing_calculators import config as calculators_config
from . import common


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_TLOG_SERVICE_IDS={'card': 124, 'uber': 125},
    BILLING_GET_MVP_OEBS_ID=True,
)
@pytest.mark.parametrize(
    'test_data_path, doc_id',
    [
        ('skip_by_version.json', 1008),
        ('skip_by_version_two_v1.json', 1008),
        ('handle_v1.json', 1006),
        ('handle_v2.json', 1008),
        ('handle_with_send_to_tlog.json', 1006),
        ('handle_with_send_to_taximeter_and_income.json', 1006),
    ],
)
# pylint: disable=invalid-name
async def test_process_payout_docs(
        test_data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    test_data = load_json(test_data_path)
    entries_sent_to_tlog = []

    @patch_aiohttp_session(
        discovery.find_service('driver-work-modes').url, 'GET',
    )
    def _patch_driver_work_modes_request(
            method, url, headers, params, **kwargs,
    ):
        assert 'park-commission-rate' in url
        return response_mock(json={'park_commission_rate': '0.1'})

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v1/journal/append' in url or 'v2/journal/append' in url:
            nonlocal entries_sent_to_tlog
            entries_sent_to_tlog = json['entries']
            return response_mock(
                json={
                    'entries': common.make_tlog_response_entries(
                        entries_sent_to_tlog,
                    ),
                },
            )
        raise NotImplementedError

    results = await common.test_process_doc(
        data_path=test_data_path,
        doc_id=doc_id,
        load_json=load_json,
        patch_aiohttp_session=patch_aiohttp_session,
        response_mock=response_mock,
        mockserver=mockserver,
        taxi_billing_calculators_stq_main_ctx=(
            taxi_billing_calculators_stq_main_ctx
        ),
        patch=patch,
        asserts=False,
    )
    for expected, actual in results:
        assert expected == actual

    assert entries_sent_to_tlog == test_data['expected_tlog_entries']


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_TAXIMETER_REQUEST_DOC=False,
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_TLOG_SERVICE_IDS={'card': 124, 'uber': 125},
    BILLING_GET_MVP_OEBS_ID=True,
)
@pytest.mark.parametrize(
    'test_data_path, doc_id',
    [('handle_with_send_to_taximeter_and_income_stq.json', 1006)],
)
# pylint: disable=invalid-name
async def test_process_payout_docs_with_taximeter_request_stq(
        test_data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    test_data = load_json(test_data_path)
    entries_sent_to_tlog = []

    @patch_aiohttp_session(
        discovery.find_service('driver-work-modes').url, 'GET',
    )
    def _patch_driver_work_modes_request(
            method, url, headers, params, **kwargs,
    ):
        assert 'park-commission-rate' in url
        return response_mock(json={'park_commission_rate': '0.1'})

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v1/journal/append' in url or 'v2/journal/append' in url:
            nonlocal entries_sent_to_tlog
            entries_sent_to_tlog = json['entries']
            return response_mock(
                json={
                    'entries': common.make_tlog_response_entries(
                        entries_sent_to_tlog,
                    ),
                },
            )
        raise NotImplementedError

    results = await common.test_process_doc(
        data_path=test_data_path,
        doc_id=doc_id,
        load_json=load_json,
        patch_aiohttp_session=patch_aiohttp_session,
        response_mock=response_mock,
        mockserver=mockserver,
        taxi_billing_calculators_stq_main_ctx=(
            taxi_billing_calculators_stq_main_ctx
        ),
        patch=patch,
        asserts=False,
    )
    for expected, actual in results:
        assert expected == actual

    assert entries_sent_to_tlog == test_data['expected_tlog_entries']

    @patch('taxi_billing_calculators.stq.helper.put_to_stq_queue')
    async def _put_stq(
            config: calculators_config.config,
            stq_client: stq_agent.StqAgentClient,
            queue: str,
            task_id: str,
            kwargs: Optional[dict] = None,
            eta=None,
            log_extra=None,
    ):
        del eta
        del log_extra
        assert queue == 'billing_calculators_taximeter_process_doc'
        assert task_id == 'taximeter_request/based_on_doc_id/1006'
        assert kwargs == {
            'doc_id': None,
            'kind': 'taximeter_request',
            'event_at': '2019-11-20T15:13:02.832000+00:00',
            'external_event_ref': '1006/taximeter_request_created',
            'data': {
                'based_on_doc_id': 1006,
                'driver': {
                    'db_id': '7ad36bc7560449998acbe2c57a75c293',
                    'driver_uuid': '769ce26febec46b0a16eee7a560d7eda',
                },
                'kind': 'commission',
                'payments': [
                    {
                        'agreement': 'taxi/yandex_ride/mode/driver_fix',
                        'amount': '-2000.0',
                        'currency': 'RUB',
                        'entry_id': 20011,
                        'sub_account': 'commission/park',
                    },
                ],
                'transaction_id': 'doc/1006',
            },
        }
