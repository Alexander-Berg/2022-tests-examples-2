import pytest

from taxi import discovery

from taxi_billing_calculators.stq.payment_requests import task as stq_task
from . import common

SELECTOR_DATE = '2019-04-01T00:00:00+00:00'


@pytest.mark.config(
    BILLING_PERIODIC_PAYMENTS_PARTNER_BALANCE_SELECTOR=SELECTOR_DATE,
    BILLING_SEND_PROCESSING_BILLING_TRANSFERS_ENABLED=True,
)
@pytest.mark.now('2021-07-30T01:25:00.000000+00:00')
@pytest.mark.parametrize(
    'test_data_path, doc_id',
    [
        ('transfer_order_payment.json', 1010),
        ('transfer_order_cancel.json', 1010),
        ('transfer_order_payment_long_trn.json', 1010),
        ('periodic_payment.json', 1010),
        ('periodic_payment_confirm.json', 1010),
        ('periodic_payment_confirm_zero.json', 1010),
        ('periodic_payment_cancel.json', 1010),
        ('periodic_payment_cancel_confirm.json', 1010),
        ('periodic_payment_cancel_confirm_duplicate.json', 1010),
        ('periodic_payment_cancel_confirm_zero.json', 1010),
        ('periodic_payment_reject.json', 1010),
        ('remittance_order_lightbox_rent_payment.json', 1010),
        ('remittance_order_store_payment.json', 1010),
        ('remittance_order_confirm_lightbox_rent_payment.json', 1010),
        ('remittance_order_confirm_old_lightbox_rent_payment.json', 1010),
        ('remittance_order_signalq_rent_payment.json', 1010),
        ('remittance_order_confirm_signalq_rent_payment.json', 1010),
        ('remittance_order_cancel.json', 1010),
        ('remittance_order_cancel_not_exist.json', 1010),
        ('remittance_order_confirm_v2_lightbox_rent_payment.json', 1010),
        ('remittance_order_confirm_v2_signalq_rent_payment.json', 1010),
    ],
)
# pylint: disable=invalid-name
async def test_queue_processing(
        test_data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_payment_requests_ctx,
        patch,
):
    """
    Test payment order handler and all data for billing docs and billing tlog.
    """
    test_data = load_json(test_data_path)
    entries_sent_to_tlog = []
    events_sent_to_processor_billing = []

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v2/journal/append' in url:
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

    @mockserver.json_handler('/processor_billing/v1/process')
    def _patch_billing_processing_billing_request(request):
        nonlocal events_sent_to_processor_billing
        json = request.json
        events_sent_to_processor_billing.append(json)

        error_billing_processing = test_data.get(
            'error_billing_processing', False,
        )
        if error_billing_processing:
            return mockserver.make_response(
                json={
                    'data': {
                        'error': 'CALCULATOR_ERROR',
                        'result': {
                            'message': 'TRANSFER_NOT_FOUND_ERROR',
                            'params': {
                                'object_id': 'test_01',
                                'object_type': 'transfer_event',
                            },
                        },
                    },
                },
                status=400,
            )

        event = {}
        if json['endpoint'] == 'transfer-cancel':
            event = {
                'tariffer_payload': {
                    'cancelled_event': {
                        'remains': 1800.0,
                        'payload': {'external_ref': 124567890},
                    },
                },
                'transaction_id': 'test_01',
            }
        return mockserver.make_response(
            json={'data': {'result': {'event': event, 'message': ''}}},
        )

    results = await common.test_process_doc(
        data_path=test_data_path,
        doc_id=doc_id,
        load_json=load_json,
        patch_aiohttp_session=patch_aiohttp_session,
        response_mock=response_mock,
        mockserver=mockserver,
        taxi_billing_calculators_stq_main_ctx=(
            taxi_billing_calculators_stq_payment_requests_ctx
        ),
        patch=patch,
        asserts=False,
        stq_queue_task=stq_task,
    )
    for expected, actual in results:
        assert actual == expected

    assert entries_sent_to_tlog == test_data['expected_tlog_entries']
    assert events_sent_to_processor_billing == test_data.get(
        'expected_processor_billing_events', [],
    )


@pytest.mark.parametrize(
    'test_data_path, doc_id', [('payment_order.json', 1010)],
)
# pylint: disable=invalid-name
async def test_payment_order_processing(
        test_data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_payment_requests_ctx,
        patch,
):
    """
    Test payment order handler and all data for billing docs and billing tlog.
    """
    test_data = load_json(test_data_path)
    entries_sent_to_tlog = []

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v2/journal/append' in url:
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
            taxi_billing_calculators_stq_payment_requests_ctx
        ),
        patch=patch,
        asserts=False,
    )
    for expected, actual in results:
        assert actual == expected

    assert entries_sent_to_tlog == test_data['expected_tlog_entries']
