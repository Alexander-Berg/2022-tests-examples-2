import pytest

from taxi import discovery

from taxi_billing_calculators.stq.main import task as stq_main_task
from . import common


@pytest.mark.now('2021-05-12T00:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_PREPAID_DRIVER_PARTNER_DUE_SELECTOR='2020-01-07T00:00:00+00:00',
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_CALCULATORS_START_WRITE_DUE_ENTRIES=(
        '2018-10-18T00:00:00.000000+00:00'
    ),
    BILLING_OLD_JOURNAL_LIMIT_DAYS=1,
    BILLING_PARK_COMMISSION_CALCULATE_BY_KIND={
        '__default__': False,
        'workshift_bought': True,
    },
    BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE='enable',
    BILLING_PARK_COMMISSION_FLOW_BY_KIND={
        '__default__': {
            '__default__': [
                {
                    'start_date': '2099-01-01T00:00:00+00:00',
                    'end_date': '2099-01-01T00:00:00+00:00',
                },
            ],
        },
        'workshift_bought': {
            '__default__': [{'start_date': '2099-01-01T00:00:00+00:00'}],
            '00': [{'start_date': '2000-01-01T00:00:00+00:00'}],
        },
    },
    BILLING_CALCULATORS_CHECK_DRIVER_PARTNER_RAW_V2=True,
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('order_paid-1001.json', 1001),
        ('order_paid-1002.json', 1002),
        ('order_paid_prepaid.json', 1002),
        ('order_paid_prepaid_driver_partner.json', 1002),
        ('order_paid_ride_fact-1001.json', 1001),
        ('order_paid_tips_fact-1001.json', 1001),
        ('order_paid_ride_tips_fact-1001.json', 1001),
        ('order_paid_fact_prepaid_driver_partner.json', 1002),
        ('workshift_bought-1001.json', 1001),
        ('workshift_bought-1002.json', 1002),
        pytest.param(
            'workshift_bought_billing_park_commission.json',
            1002,
            marks=pytest.mark.config(
                BILLING_SEND_INCOME_ENTRIES_MODE='enable',
                BILLING_CALCULATORS_PRODUCE_AGGREGATOR_COMMISSION_SINCE=(
                    '2021-05-12T09:06:14+00:00'
                ),
                BILLING_INCOME_ENTRIES_JOURNAL_FILTERS={
                    'black_list': [{'sub_account': '%park_only%'}],
                    'white_list': [
                        {
                            'agreement_id': 'taxi/yandex_ride',
                            'entity_external_id': 'taximeter_driver_id%',
                            'sub_account': '%commission%',
                        },
                        {
                            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                            'entity_external_id': 'taximeter_driver_id%',
                            'sub_account': '%commission%',
                        },
                        {
                            'agreement_id': 'taxi/yandex_ride',
                            'entity_external_id': 'taximeter_driver_id%',
                            'sub_account': '%workshift%',
                        },
                    ],
                },
                BILLING_INCOME_ENTRIES_PARK_ONLY_FILTERS={
                    'black_list': [],
                    'white_list': [
                        {
                            'agreement_id': 'taxi/yandex_ride',
                            'entity_external_id': 'taximeter_driver_id%',
                            'sub_account': (
                                'commission/workshift/aggregator/park_only'
                            ),
                        },
                    ],
                },
            ),
        ),
        ('workshift_bought_billing_park_commission_filter_zero.json', 1002),
        (
            'workshift_bought_billing_park_commission_no_work_rule_id.json',
            1002,
        ),
        ('workshift_bought_billing_park_commission_rule_not_found.json', 1002),
        ('taximeter_payment_from_billing_orders.json', 1001),
        ('taximeter_payment_from_billing_orders_via_fleet_info.json', 1001),
        ('taximeter_payment_from_process_events.json', 1001),
        ('b2b_trip_payment_no_reversal.json', 1000),
        ('b2b_trip_payment_journal_reversal_from_doc_revesal.json', 1004),
        ('driver_partner_raw_v1.json', 1001),
        ('driver_partner_raw_v1_404.json', 1001),
        ('driver_partner_raw_v1_already_withdrawn.json', 1001),
        ('driver_partner_raw_v1_cancel_withdraw.json', 1001),
        ('driver_partner_raw_v1_too_many_clids.json', 1001),
        ('driver_partner_raw_v2.json', 1001),
        ('driver_partner_raw_v2_il_tax.json', 1001),
        ('driver_partner_raw_v2_404.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        stq_client_patched,
):
    json_data = load_json(data_path)
    dwm_response = json_data.get('dwm_response')

    @patch_aiohttp_session(discovery.find_service('driver-work-modes').url)
    def _patch_driver_work_modes_request(method, url, **kwargs):
        assert dwm_response
        for key in dwm_response:
            if key in url:
                return response_mock(**(dwm_response[key]))
        raise AssertionError(f'Unexpected driver-work-modes by url {url}')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _patch_fleet_parks_request_new(*args, **kwargs):
        if 'fleet_parks_response' in json_data:
            return json_data['fleet_parks_response']
        return {'parks': [{'id': '6ebbef0a9e654d8ba80d8831459df144'}]}

    @mockserver.json_handler(
        '/processing/v1/pro/contractors_income/create-event',
    )
    def _patch_scope_queue_create_event_request(request):
        pass

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        asserts=False,
    )
    for expected, actual in results:
        assert actual == expected


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_OLD_JOURNAL_LIMIT_DAYS=365,
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [('b2b_trip_payment_with_journal_reversal.json', 1004)],
)
# pylint: disable=invalid-name
async def test_process_doc_journal_reversal(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
    )


@pytest.mark.config(
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('b2b_trip_payment_br_no_skip_by_new_later_version.json', 1006),
        ('b2b_trip_payment_br_skip_by_version.json', 1007),
    ],
)
async def test_br_skip_by_version(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        asserts=False,
    )
    for expected, actual in results:
        assert actual == expected


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_CALCULATORS_START_WRITE_DUE_ENTRIES=(
        '2018-10-18T00:00:00.000000+00:00'
    ),
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_TAXIMETER_OWN_JOURNAL_OBJ_ID_SINCE_DUE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('order_paid_add_due_entries.json', 1002),
        ('taximeter_payment_add_due_entries.json', 1001),
        ('taximeter_payment_add_due_entries_park_ride_cash.json', 1001),
        ('workshift_bought_add_due_entries.json', 1002),
        ('b2b_trip_payment_add_due_entries.json', 1000),
    ],
)
# pylint: disable=invalid-name
async def test_add_due_entries(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    @patch_aiohttp_session(discovery.find_service('fleet-parks').url, 'POST')
    def _patch_fleet_parks_request(method, url, headers, **kwargs):
        return response_mock(json={'parks': [{'id': '%some_driver_id%'}]})

    json_data = load_json(data_path)
    dwm_response = json_data.get('dwm_response')

    @patch_aiohttp_session(
        discovery.find_service('driver-work-modes').url, 'GET',
    )
    def _patch_driver_work_modes_request(
            method, url, headers, params, **kwargs,
    ):
        assert dwm_response
        for key in dwm_response:
            if key in url:
                return response_mock(**(dwm_response[key]))
        raise AssertionError(f'Unexpected driver-work-modes by url {url}')

    @patch_aiohttp_session(discovery.find_service('processing').url, 'POST')
    def _patch_scope_queue_create_event_request(
            method, url, headers, **kwargs,
    ):
        pass

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
    )
    for expected, actual in results:
        assert actual == expected


@pytest.mark.parametrize('data_path,doc_id', [('order_paid-1002.json', 1002)])
@pytest.mark.config(
    BILLING_TLOG_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2019-05-01T00:00:00+00:00',
    },
)
# pylint: disable=invalid-name
async def test_process_doc_ignored_by_due_date(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    json_data = load_json(data_path)
    finish_reason = ''

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _mock_docs_select(request, *args, **kwargs):
        result = []
        for one_doc in json_data['reports']['docs/select']['docs']:
            if all(
                    one_doc[key] == value
                    for key, value in request.json.items()
                    if key in ('external_obj_id', 'kind')
            ):
                result.append(one_doc)
        return {'docs': result}

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal finish_reason
        if 'is_ready_for_processing' in url:
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'ready': True, 'doc': one_doc})
            assert False, 'Doc not found'
        elif 'search' in url:
            result = []
            for one_doc in json_data['docs']:
                if all(
                        one_doc[key] == value
                        for key, value in json.items()
                        if key != 'use_master'
                ):
                    result.append(one_doc)
            return response_mock(json={'docs': result})
        elif 'finish_processing' in url:
            finish_reason = json['details']['reason']
            return response_mock(json={})
        raise AssertionError('Unexpected call to billing-docs')

    @patch_aiohttp_session(
        discovery.find_service('billing_accounts').url, 'POST',
    )
    def _patch_billing_accounts_request(method, url, headers, json, **kwargs):
        raise AssertionError('Unexpected call to billing-accounts')

    await stq_main_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=common.create_task_info(),
        doc_id=doc_id,
    )
    assert finish_reason.startswith('Due date is too old')


@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_CALCULATORS_START_WRITE_DUE_ENTRIES=(
        '2018-10-18T00:00:00.000000+00:00'
    ),
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_DRIVER_MODES_ENABLED=True,
)
@pytest.mark.parametrize(
    'data_path, doc_id',
    [
        ('order_paid_add_due_entries_orders.json', 1002),
        ('order_paid_add_due_entries_driver_fix.json', 1002),
        ('order_paid_add_due_entries_driver_fix_fact.json', 1002),
        ('order_paid_add_due_entries_uberdriver.json', 1002),
        ('b2b_trip_payment_driver_fix.json', 1004),
        ('b2b_trip_payment_driver_fix_fact.json', 1004),
        ('order_paid_ride_tips_fact-1001-driver-fix.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_driver_mode_entries(
        data_path,
        doc_id,
        monkeypatch,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
):
    @patch_aiohttp_session(discovery.find_service('fleet-parks').url, 'POST')
    def _patch_fleet_parks_request(method, url, headers, **kwargs):
        return response_mock(json={'parks': [{'id': '%some_driver_id%'}]})

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        asserts=False,
    )
    for expected, actual in results:
        assert actual == expected


@pytest.mark.now('2021-05-12T00:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_CALCULATORS_CREATE_BY_TYPE_TAXIMETER_REQUEST_DOCS={
        '__default__': True,
    },
    BILLING_PREPAID_DRIVER_PARTNER_DUE_SELECTOR='2020-01-07T00:00:00+00:00',
    BILLING_TAXIMETER_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
    BILLING_CALCULATORS_START_WRITE_DUE_ENTRIES=(
        '2021-06-18T00:00:00.000000+00:00'
    ),
    BILLING_CALCULATORS_BYPASS_USE_V2_EXECUTE_DUE_SELECTOR=(
        '2021-05-01T00:00:00+00:00'
    ),
    BILLING_OLD_JOURNAL_LIMIT_DAYS=1,
    BILLING_PARK_COMMISSION_CALCULATE_BY_KIND={
        '__default__': False,
        'workshift_bought': True,
    },
    BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE='enable',
    BILLING_PARK_COMMISSION_FLOW_BY_KIND={
        '__default__': {
            '__default__': [
                {
                    'start_date': '2099-01-01T00:00:00+00:00',
                    'end_date': '2099-01-01T00:00:00+00:00',
                },
            ],
        },
        'workshift_bought': {
            '__default__': [{'start_date': '2099-01-01T00:00:00+00:00'}],
            '00': [{'start_date': '2000-01-01T00:00:00+00:00'}],
        },
    },
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('order_paid_use_v2_execute.json', 1001),
        ('taximeter_payment_v2_execute.json', 1001),
        ('workshift_bought_use_v2_execute.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_v2_execute(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        stq_client_patched,
):
    json_data = load_json(data_path)
    dwm_response = json_data.get('dwm_response')

    @patch_aiohttp_session(discovery.find_service('driver-work-modes').url)
    def _patch_driver_work_modes_request(method, url, **kwargs):
        assert dwm_response
        for key in dwm_response:
            if key in url:
                return response_mock(**(dwm_response[key]))
        raise AssertionError(f'Unexpected driver-work-modes by url {url}')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _patch_fleet_parks_request_new(*args, **kwargs):
        if 'fleet_parks_response' in json_data:
            return json_data['fleet_parks_response']
        return {'parks': [{'id': '6ebbef0a9e654d8ba80d8831459df144'}]}

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        asserts=False,
    )
    for expected, actual in results:
        assert actual == expected
