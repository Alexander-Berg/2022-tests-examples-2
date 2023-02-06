import bson
import pytest

_MOCK_NOW = '2022-02-15T00:00:00.000000+00:00'

_BILLING_MANUAL_TRANSACTIONS_SETTINGS = {
    'subventions': {
        'product': 'subventions',
        'detailed_product': 'subventions',
        'service_id': 137,
        'paid_to': 'driver',
        'description': 'subventions',
        'processor': 'subventions',
        'validators_list': [
            {
                'validator_name': 'numeric_field',
                'fields': {'amount': 'amount'},
                'args': {},
            },
            {
                'validator_name': 'max_amount_by_taxi_order',
                'fields': {'amount': 'amount', 'order_id': 'order_id'},
                'args': {},
            },
        ],
        'amount_details_calculator': 'calc_num_transactions_and_total_amount',
    },
}


@pytest.mark.skip
@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(
    BILLING_MANUAL_TRANSACTIONS_FIRST_N_ROWS_ERRORS=4,
    BILLING_MANUAL_TRANSACTIONS_MAX_COUNT=100,
    BILLING_MANUAL_TRANSACTIONS_SETTINGS=_BILLING_MANUAL_TRANSACTIONS_SETTINGS,
    BILLING_MANUAL_TRANSACTIONS_VALIDATION_ROWS_CHUNK=2,
    MAX_SUBVENTION_BONUS_VALUE_BY_CURRENCY={'RUB': 2000000000},
)
@pytest.mark.parametrize(
    'data_path',
    [
        'subventions.json',
        'subventions_after_exception.json',
        'subventions_with_exception.json',
        'subventions_no_order.json',
        'subventions_schema_failed.json',
        'validator_max_amount_by_currency.json',
        'validator_numeric_field.json',
    ],
)
async def test_process_doc_manual_transactions_upload(
        data_path,
        do_mock_billing_docs,
        do_mock_billing_reports,
        mock_order_archive,
        stq_runner,
        reschedulable_stq_runner,
        load_py_json,
        mockserver,
        yt_apply,
):
    test_json = load_py_json(data_path)

    @mockserver.handler('/mds_s3/attachments/test_file_id')
    async def _mock_mds3(request, *args):
        mds_file = test_json['mds_file']
        newline = test_json.get('newline', '\n')
        content = newline.join(mds_file)
        return mockserver.make_response(
            response=content,
            content_type='application/json',
            headers={'ETag': 'asdf'},
        )

    @mock_order_archive('/v1/order_proc/retrieve')
    def _get_order(request):
        if request.json['id'] == 'exception':
            bson_doc = bson.BSON.encode({})
            return mockserver.make_response(
                response=bson_doc, content_type='application/x-bson-binary',
            )
        bson_doc = bson.BSON.encode({'doc': {'alias_id': 'some_alias_id'}})
        return mockserver.make_response(
            response=bson_doc, content_type='application/x-bson-binary',
        )

    docs = [test_json['doc']]
    order_doc = test_json.get('order_doc')
    if order_doc:
        taxi_order_file = order_doc.get('ref')
        if taxi_order_file:
            order_doc = load_py_json(taxi_order_file)
        docs.append(order_doc)
    process_docs = do_mock_billing_docs(docs)
    do_mock_billing_reports()

    task = stq_runner.billing_functions_manual_transactions
    was_exc = False
    try:
        await reschedulable_stq_runner(task, 123456)
    except RuntimeError:
        was_exc = True
    assert was_exc == test_json.get('was_exception', False)
    assert process_docs.update_requests == test_json['expected_docs_updated']


@pytest.mark.now(_MOCK_NOW)
@pytest.mark.config(
    BILLING_MANUAL_TRANSACTIONS_SETTINGS=_BILLING_MANUAL_TRANSACTIONS_SETTINGS,
)
@pytest.mark.parametrize('data_path', ['create_subventions.json'])
async def test_process_doc_manual_transactions(
        data_path,
        do_mock_billing_docs,
        do_mock_billing_reports,
        stq_runner,
        reschedulable_stq_runner,
        load_py_json,
):
    test_json = load_py_json(data_path)
    process_docs = do_mock_billing_docs([test_json['doc']])
    do_mock_billing_reports()
    task = stq_runner.billing_functions_manual_transactions
    await reschedulable_stq_runner(task, 123456)
    assert process_docs.update_requests == test_json['expected_docs_updated']
