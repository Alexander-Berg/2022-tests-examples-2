import pytest

from taxi import discovery

from . import common


@pytest.mark.config(
    BILLING_GET_MVP_OEBS_ID=True, BILLING_DRIVER_MODES_ENABLED=True,
)
@pytest.mark.parametrize(
    'test_data_path, doc_id',
    [
        ('personal_wallet_charge.json', 1010),
        ('personal_wallet_charge_no_contract.json', 1010),
        ('personal_wallet_charge_refund.json', 1010),
        ('personal_wallet_charge_with_order_completed_at.json', 1010),
        ('personal_wallet_charge_v2.json', 1010),
        ('personal_wallet_topup.json', 4242),
        ('personal_wallet_topup_refund.json', 4242),
        ('personal_wallet_transfer.json', 4242),
        ('personal_wallet_charge_driver_fix.json', 1010),
    ],
)
async def test_process_personal_wallet_docs(
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

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v1/journal/append' in url:
            nonlocal entries_sent_to_tlog
            entries_sent_to_tlog = json['entries']
            return response_mock(json={})
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
