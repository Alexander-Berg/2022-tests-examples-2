import copy

from tests_eats_billing_processor import consts


def make_raw_events_stq_args(order_nr, billing_extra_data=None):
    return {'order_nr': order_nr, 'billing_extra_data': billing_extra_data}


def make_billing_events_stq_kwargs(order_nr):
    return {'order_nr': order_nr}


def make_storage_search_request(order_nr):
    return {'external_obj_id': order_nr}


def make_storage_search_response(billing_docs):
    return {'docs': billing_docs}


def make_storage_create_request(billing_docs):
    return billing_docs


def make_storage_finish_request(doc_id, status):
    return {'doc_id': doc_id, 'status': status, 'details': {}}


def make_business_rules_request(
        counteragent_type, counteragent_details, billing_date,
):
    return {
        'counteragent_type': counteragent_type,
        'counteragent_details': counteragent_details,
        'billing_date': billing_date,
    }


def make_business_rules_response(
        client_id, commission, acquiring_commission, fix_commission,
):
    return {
        'client_id': client_id,
        'commissions': {
            'commission': str(commission),
            'acquiring_commission': str(acquiring_commission),
            'fix_commission': str(fix_commission),
        },
    }


def make_billing_doc(
        order_nr,
        kind,
        data,
        doc_id=None,
        event_at=consts.OTHER_DATE,
        external_event_ref='',
        status='new',
        service=consts.SERVICE,
        service_user_id=consts.SERVICE_USER_ID,
):
    doc = {
        'kind': kind,
        'external_obj_id': order_nr,
        'external_event_ref': external_event_ref,
        'event_at': event_at,
        'service_user_id': service_user_id,
        'data': data,
        'tags': [],
        'status': status,
        'service': service,
        'journal_entries': [],
    }
    if doc_id is not None:
        doc['doc_id'] = doc_id
    return doc


def make_order_created_doc(
        doc_id=0,
        order_nr=consts.ORDER_NR,
        order_type='retail',
        created_at=consts.ORDER_CREATED_DATE,
):
    return make_billing_doc(
        doc_id=doc_id,
        order_nr=order_nr,
        kind='OrderCreated',
        data={'orderType': order_type, 'createdAt': created_at},
    )


def check_billing_events_stq_call(
        stq,
        expected_times_called,
        expected_task_id=None,
        expected_kwargs=None,
):
    assert (
        stq.eats_billing_processor_process_billing_events.times_called
        == expected_times_called
    )
    if expected_times_called == 0:
        return

    call_info = stq.eats_billing_processor_process_billing_events.next_call()
    assert call_info['id'] == expected_task_id
    assert (
        call_info['queue'] == 'eats_billing_processor_process_billing_events'
    )

    kwargs = call_info['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == expected_kwargs


def billing_docs_are_equal(doc1, doc2):
    """
    Сравнивает 2 биллинг-дока, игнорируя атрибуты 'event_at'.
    """

    doc1_copy = copy.deepcopy(doc1)
    doc2_copy = copy.deepcopy(doc2)

    doc1_copy.pop('event_at')
    doc2_copy.pop('event_at')

    if ('event_at' in doc1_copy['data']) and ('event_at' in doc2_copy['data']):
        doc1_copy['data'].pop('event_at')
        doc2_copy['data'].pop('event_at')
    elif ('event_at' in doc1_copy['data']) or (
        'event_at' in doc2_copy['data']
    ):
        return False

    def deep_equals(x, y):
        if not isinstance(x, type(y)):
            return False
        if isinstance(x, dict):
            x_keys = sorted(x.keys())
            y_keys = sorted(y.keys())
            if x_keys != y_keys:
                return False
            for key in x_keys:
                if not deep_equals(x[key], y[key]):
                    return False
            return True
        if isinstance(x, list):
            if len(x) != len(y):
                return False
            if not x:
                return True
            for i, y_value in enumerate(y):
                if deep_equals(x[0], y_value):
                    x.pop(0)
                    y.pop(i)
                    return deep_equals(x, y)
            return False
        return x == y

    return deep_equals(doc1_copy, doc2_copy)


def billing_doc_lists_are_equal(doc_list1, doc_list2):
    """
    Сравнивает 2 списка биллинг-доков,
    игнорируя атрибуты 'event_at' в биллинг-доках.
    """

    if not isinstance(doc_list1, list):
        return False
    if not isinstance(doc_list2, list):
        return False
    if len(doc_list1) != len(doc_list2):
        return False

    for doc1 in doc_list1:
        found = False
        for doc2 in doc_list2:
            if billing_docs_are_equal(doc1, doc2):
                found = True
                break
        if not found:
            return False

    for doc2 in doc_list2:
        found = False
        for doc1 in doc_list1:
            if billing_docs_are_equal(doc1, doc2):
                found = True
                break
        if not found:
            return False

    return True


async def raw_processing_test_func(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
):
    storage_search = mock_storage_search(
        expected_request=expected_search_request, response=search_response,
    )
    storage_store = mock_storage_store(expected_request=expected_store_request)
    storage_finish = mock_storage_finish(
        expected_requests=expected_finish_requests,
    )

    await stq_runner.eats_billing_processor_process_raw_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )

    times_called = 1 if expected_search_request else 0
    assert storage_search.times_called == times_called

    times_called = 1 if expected_store_request else 0
    assert storage_store.times_called == times_called

    times_called = (
        len(expected_finish_requests) if expected_finish_requests else 0
    )
    assert storage_finish.times_called == times_called

    times_called = 1 if expected_output_stq_args else 0
    check_billing_events_stq_call(
        stq,
        expected_times_called=times_called,
        expected_task_id='test_input_task',
        expected_kwargs=expected_output_stq_args,
    )


async def billing_processing_test_func(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
):
    v1_create_error_handler = mock_create_handler()

    storage_search = mock_storage_search(
        expected_request=expected_search_request, response=search_response,
    )
    storage_store = mock_storage_store(expected_request=expected_store_request)
    storage_finish = mock_storage_finish(
        expected_requests=expected_finish_requests,
    )
    business_rules = mock_business_rules(
        expected_requests=expected_business_rules_requests,
        responses=business_rules_responses,
    )

    await stq_runner.eats_billing_processor_process_billing_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )

    times_called = 1 if expected_search_request else 0
    assert storage_search.times_called == times_called

    times_called = 1 if expected_store_request else 0
    assert storage_store.times_called == times_called

    times_called = (
        len(expected_finish_requests) if expected_finish_requests else 0
    )
    assert storage_finish.times_called == times_called

    times_called = (
        len(expected_business_rules_requests)
        if expected_business_rules_requests
        else 0
    )
    assert business_rules.times_called == times_called

    assert v1_create_error_handler.times_called == 0
