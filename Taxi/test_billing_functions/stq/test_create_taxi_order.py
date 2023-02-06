import pytest

from billing_functions.stq import create_taxi_order
from test_billing_functions import mocks

TEST_DOC_ID = 18061991


@pytest.mark.parametrize(
    'test_data_json',
    [
        'order_completed.json',
        'order_amended.json',
        'order_amended_no_performer.json',
        'order_completed_with_nones.json',
        pytest.param(
            'order_completed_delayed_due_to_migration_mode.json',
            marks=pytest.mark.config(
                BILLING_FUNCTIONS_TAXI_ORDER_MIGRATION={
                    'by_zone': {
                        '__default__': {
                            'test': [
                                {'since': '1999-12-31T23:59:59.999999+03:00'},
                            ],
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.now('2020-12-31T23:59:59.999999+03:00')
async def test_create_taxi_order_tasks(
        test_data_json,
        *,
        load_py_json,
        stq3_context,
        do_mock_billing_reports,
        do_mock_billing_docs,
        patched_stq_queue,
        mockserver,
        monkeypatch,
):
    test_data = load_py_json(test_data_json)

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _v1_tariff_zones(_):
        return test_data['tariff_zones_responses'].pop(0)

    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _v1_parks_billing_client_id_retrieve(_):
        return test_data['billing_client_id_retrieve_responses'].pop(0)

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _v1_parks_retrieve(_):
        return test_data['parks_retrieve_responses'].pop(0)

    tariffs = mocks.Tariffs(test_data['db_tariffs'])
    monkeypatch.setattr(stq3_context, 'tariffs', tariffs)
    do_mock_billing_reports()
    billing_docs = do_mock_billing_docs([test_data['input_doc']])

    await create_taxi_order.task(stq3_context, TEST_DOC_ID)

    assert billing_docs.created_docs == test_data['expected_docs']
    assert patched_stq_queue.pop_calls() == test_data['expected_stq_calls']
