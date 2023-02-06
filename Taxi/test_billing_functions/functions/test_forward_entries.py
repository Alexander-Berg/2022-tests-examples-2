import datetime

import asynctest
import pytest

from billing.accounts import service as _accounts
from testsuite.utils import ordered_object

from billing_functions.functions import forward_entries

JOURNAL_FILTERS = {
    'white_list': [
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%commission%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%commission%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%fine%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%fine%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%promocode%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%promocode%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%subvention%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%subvention%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'payment%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'payment%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'tips%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'tips%',
        },
        {
            'agreement_id': 'taxi/park_services',
            'entity_external_id': 'taximeter_driver_id/%',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': '%workshift%',
        },
        {
            'agreement_id': 'taxi/park_ride',
            'entity_external_id': 'taximeter_driver_id/%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'payout',
        },
        {
            'agreement_id': 'taxi/yandex_marketing',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'referral',
        },
        {
            'agreement_id': 'taxi/yandex_marketing',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'payment/scout',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id%',
            'sub_account': 'toll_road%',
        },
        {
            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
            'entity_external_id': 'taximeter_driver_id%',
            'sub_account': 'toll_road%',
        },
    ],
    'black_list': [
        {'agreement_id': 'taxi/park_ride', 'sub_account': 'order_cost'},
        {'agreement_id': 'taxi/periodic_payments', 'sub_account': 'withdraw'},
        {'agreement_id': 'taxi/periodic_payments', 'sub_account': 'withhold'},
        {'agreement_id': 'taxi/yandex_ride/mode/driver_fix/fact'},
        {'sub_account': '%park_only'},
        {'sub_account': 'payment/cash'},
        {'sub_account': 'toll_road/cash'},
        {'sub_account': 'payment/driver_partner'},
    ],
}
CASH_FILTERS = {
    'white_list': [
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'payment/cash',
        },
    ],
    'black_list': [],
}
PARK_ONLY_FILTERS = {
    'white_list': [
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'commission/aggregator/park_only',
        },
        {
            'agreement_id': 'taxi/yandex_ride',
            'entity_external_id': 'taximeter_driver_id/%',
            'sub_account': 'platform/order/commission_inc_vat/park_only',
        },
    ],
    'black_list': [],
}


@pytest.mark.json_obj_hook(
    Query=forward_entries.Query, SelectedEntry=_accounts.SelectedEntry,
)
@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
@pytest.mark.config(
    BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE='enable',
    BILLING_INCOME_ENTRIES_JOURNAL_ACCURACY=0.001,
    BILLING_SEND_INCOME_ENTRIES_MODE='enable',
    BILLING_INCOME_ENTRIES_JOURNAL_FILTERS=JOURNAL_FILTERS,
    BILLING_INCOME_ENTRIES_CASH_FILTERS=CASH_FILTERS,
    BILLING_INCOME_ENTRIES_PARK_ONLY_FILTERS=PARK_ONLY_FILTERS,
    BILLING_FUNCTIONS_SEND_ENTRIES_TO_BILLING_FIN_PAYOUTS=True,
    BILLING_FUNCTIONS_TOPICS_FOR_FIN_PAYOUTS_STQ=['topic'],
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        pytest.param(
            'test_bulk.json',
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_SEND_INCOME_ENTRIES_CONTEXT=True,
            ),
        ),
        'test_park_commission.json',
        pytest.param(
            'test_taxi_order.json',
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_SEND_INCOME_ENTRIES_CONTEXT=True,
            ),
        ),
        'test_taxi_order_commission.json',
        'test_aggregator_commission.json',
        'test_platform_order_commission_park_only.json',
    ],
)
# pylint: disable=invalid-name
async def test_process_entries(
        test_data_json,
        *,
        make_context,
        mock_tlog,
        mock_processing,
        patched_stq_queue,
        load_py_json,
):
    test_data = load_py_json(test_data_json)

    context = make_context(test_data['entries'])

    await forward_entries.execute(context, test_data['query'])
    assert mock_tlog.journal_v1 == test_data['expected_tlog_v1_requests']
    assert mock_tlog.journal_v2 == test_data['expected_tlog_v2_requests']

    stq_calls = patched_stq_queue.pop_calls()
    ordered_object.assert_eq(
        stq_calls, test_data['expected_stq_calls'], ['', 'task_id'],
    )

    assert (
        mock_processing.processing_v1
        == test_data['expected_processing_requests']
    )


@pytest.fixture(name='make_context')
def make_make_context(stq3_context):
    def _make_context(entries):
        stq3_context.journal = asynctest.Mock(spec=_accounts.Journal)
        stq3_context.journal.select_by_id_or_die.return_value = entries
        stq3_context.journal.max_age_for_new_entries = datetime.timedelta(92)
        return stq3_context

    return _make_context
