import pytest
import pytz

from taxi_billing_subventions.common import models


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path,'
    'expected_docs_path,'
    'expected_change_doc_id,'
    'expected_status,',
    [
        (
            'create_multiple_rules.json',
            'create_multiple_rules_docs.json',
            (
                'chelyabinsk:ekb:moscow:volgodonsk:'
                '1d9e292abd87e7c620aed01d642070894fba4c69'
            ),
            200,
        ),
        (
            'create_driver_fix_with_time.json',
            'create_driver_fix_with_time_docs.json',
            'moscow:282bb3b55719fc2c13bba7454a2731d34fb4af2e',
            200,
        ),
    ],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_v2(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        patch_insert_rules,
        request_data_path,
        expected_docs_path,
        expected_change_doc_id,
        expected_status,
        request_headers,
):
    actual_docs = []
    patch_insert_rules(actual_docs)
    request, expected_docs = load_py_json_dir(
        '', request_data_path, expected_docs_path,
    )
    headers = request_headers
    headers.update(
        {'X-Yandex-Login': 'foobar', 'X-YaTaxi-Draft-Tickets': 'TAXIRATE-44'},
    )
    response = await billing_subventions_client.post(
        '/v2/rules/create', headers=headers, json=request,
    )
    assert response.status == expected_status
    assert actual_docs == expected_docs
    if expected_status == 200:
        response_data = await response.json()
        assert response_data['data'] == request
        assert response_data['change_doc_id'] == expected_change_doc_id
        assert bool(patched_tvm_ticket_check.calls)


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path',
    [
        'create_discount_with_incorrect_time_range_format.json',
        'create_single_order_goal_with_minutes.json',
        'create_single_order_goal_with_one_trip.json',
        'create_single_order_with_days_span_missing.json',
        'create_single_order_with_trips_bound_missing.json',
        'create_single_order_with_extra_field.json',
        'create_incorrect_daily_guarantees_start_gt_end.json',
        'create_incorrect_daily_guarantees_start_in_past.json',
        'duplicate_daily_guarantees.json',
        'create_rule_with_nonexistent_zone.json',
        'create_rule_no_currency_for_zone.json',
        'create_additive_rule_with_commission.json',
        'create_daily_guarantee_rule_over_time_limit.json',
        'create_geo_booking_rule_over_time_limit.json',
        'create_single_order_rule_over_time_limit.json',
        'create_single_order_rule_incorrect_amount.json',
        'create_driver_fix_rule_with_negative_hour.json',
        'create_driver_fix_rule_with_hour_24.json',
        'create_driver_fix_rule_with_negative_minute.json',
        'create_driver_fix_rule_with_minute_60.json',
        'create_driver_fix_rule_with_negative_rate.json',
        'create_driver_fix_rule_with_negative_fraud_rate.json',
        'create_driver_fix_rule_with_fraud_rate_over_1.json',
        'create_driver_fix_rule_with_duplicate_interval.json',
        'create_driver_fix_rule_with_duplicate_tariff_classes.json',
        'create_driver_fix_rule_without_rates.json',
        'create_driver_fix_rule_incorrect_date.json',
        'create_driver_fix_rule_incorrect_commission_rate.json',
        'create_driver_fix_rule_incorrect_rate.json',
        # second interval contained within
        'create_driver_fix_rule_duplicate_key_1.json',
        # second interval contained within, equal start
        'create_driver_fix_rule_duplicate_key_2.json',
        # second interval contained within, equal end
        'create_driver_fix_rule_duplicate_key_3.json',
        # second interval contained within, equal start+end
        'create_driver_fix_rule_duplicate_key_4.json',
        # second interval overlaps start but not end
        'create_driver_fix_rule_duplicate_key_5.json',
        # second interval overlaps end but not start
        'create_driver_fix_rule_duplicate_key_6.json',
        # second interval overlaps start, but equal end
        'create_driver_fix_rule_duplicate_key_7.json',
        # second interval overlaps end, but equal start
        'create_driver_fix_rule_duplicate_key_8.json',
        # second interval overlaps entire range
        'create_driver_fix_rule_duplicate_key_9.json',
        'create_driver_fix_rule_without_geoarea.json',
        'create_goal_rule_with_bad_date_range.json',
        'create_goal_rule_with_days_span_missing.json',
        'create_goal_rule_with_days_span_malformed.json',
        'create_goal_rule_with_days_span_too_big.json',
        'create_goal_rule_with_days_span_too_small.json',
        'create_goal_rule_with_trips_bounds_empty.json',
        'create_goal_rule_with_trips_bounds_same_bonus.json',
        'create_goal_rule_with_trips_bounds_same_bounds.json',
        'create_goal_rule_with_trips_bounds_unordered_by_bonus.json',
        'create_goal_rule_with_trips_bounds_unordered_by_bounds.json',
    ],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_v2_validation_error(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        patch_insert_rules,
        request_data_path,
        request_headers,
):
    await _make_bad_request(
        patch_insert_rules,
        load_py_json_dir,
        billing_subventions_client,
        request_headers,
        request_data_path,
    )


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path',
    [
        # new rule contained within
        'duplicate_key_1.json',
        # new rule contained within, equal start
        'duplicate_key_2.json',
        # new rule contained within, equal end
        'duplicate_key_3.json',
        # new rule contained within, equal start+end
        'duplicate_key_4.json',
        # new rule overlaps start but not end
        'duplicate_key_5.json',
        # new rule overlaps end but not start
        'duplicate_key_6.json',
        # new rule overlaps start, but equal end
        'duplicate_key_7.json',
        # new rule overlaps end, but equal start
        'duplicate_key_8.json',
        # new rule overlaps entire range
        'duplicate_key_9.json',
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_v2_duplicate_driver_fix_key')
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_v2_duplicate_driver_fix_key(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        patch_insert_rules,
        request_data_path,
        request_headers,
):
    await _make_bad_request(
        patch_insert_rules,
        load_py_json_dir,
        billing_subventions_client,
        request_headers,
        request_data_path,
    )


async def _make_bad_request(
        patch_insert_rules,
        load_py_json_dir,
        billing_subventions_client,
        request_headers,
        request_data_path,
):
    actual_docs = []
    patch_insert_rules(actual_docs)
    request = load_py_json_dir('', request_data_path)
    headers = request_headers
    headers.update(
        {'X-Yandex-Login': 'foobar', 'X-YaTaxi-Draft-Tickets': 'TAXIRATE-44'},
    )
    response = await billing_subventions_client.post(
        '/v2/rules/create', headers=headers, json=request,
    )
    assert response.status == 400
    assert actual_docs == []


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'headers_path, request_data_path',
    [
        ('no_headers.json', 'create_multiple_rules.json'),
        ('no_login_header.json', 'create_multiple_rules.json'),
    ],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_v2_incorrect_headers(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        patch_insert_rules,
        headers_path,
        request_data_path,
        request_headers,
):
    actual_docs = []
    patch_insert_rules(actual_docs)
    additional_headers, request = load_py_json_dir(
        '', headers_path, request_data_path,
    )
    headers = request_headers
    headers.update(additional_headers)
    response = await billing_subventions_client.post(
        '/v2/rules/create', headers=headers, json=request,
    )
    assert response.status == 400
    assert actual_docs == []


@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_v2_not_authorized_response(billing_subventions_client):
    response = await billing_subventions_client.post(
        '/v2/rules/create', headers={}, json={},
    )
    assert response.status == 403


@pytest.fixture(name='get_zone_patched')
def get_zone_patched_fixture(patch):
    @patch('taxi_billing_subventions.caches.ZonesCache.get_zone')
    def get_zone(name):  # pylint: disable=unused-variable
        if name == 'no_such_zone':
            raise KeyError(name)
        if name == 'zone_without_currency':
            return models.Zone(
                name,
                'id',
                pytz.utc,
                None,
                None,
                models.Vat.make_naive(12000),
                'rus',
            )
        if name == 'tel_aviv':
            return models.Zone(
                name,
                'tel_aviv',
                pytz.timezone('Israel'),
                'ILS',
                None,
                models.Vat.make_naive(11700),
                'rus',
            )
        return models.Zone(
            name,
            'id',
            pytz.utc,
            'RUB',
            None,
            models.Vat.make_naive(12000),
            'rus',
        )


@pytest.fixture(name='patch_insert_rules')
def patch_insert_rules_fixture(patch):
    def do_patch(actual_docs):
        @patch('taxi_billing_subventions.common.db.rule.insert_rules')
        # pylint: disable=unused-variable
        async def insert_rules(collection, docs):
            del collection
            actual_docs.extend(docs)

    return do_patch


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path, '
    'expected_docs_path, expected_change_doc_id, expected_status',
    [
        (
            'create_goal_rule.json',
            'create_goal_rule_docs.json',
            'chelyabinsk:6d058d3ed5d706d4cfafdc2ca63821a674d20db9',
            200,
        ),
        (
            'create_goal_rule_real.json',
            'create_goal_rule_real_docs.json',
            'tel_aviv:71df002c1d04783ed6e2fc0f598c2e18d9a6c0df',
            200,
        ),
    ],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_create_goal_rule(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        patch_insert_rules,
        request_data_path,
        expected_docs_path,
        expected_change_doc_id,
        expected_status,
        request_headers,
):
    actual_docs = []
    patch_insert_rules(actual_docs)
    request, expected_docs = load_py_json_dir(
        '', request_data_path, expected_docs_path,
    )
    headers = request_headers
    headers.update(
        {'X-Yandex-Login': 'foobar', 'X-YaTaxi-Draft-Tickets': 'TAXIRATE-44'},
    )
    response = await billing_subventions_client.post(
        '/v2/rules/create', headers=headers, json=request,
    )
    assert response.status == expected_status
    assert actual_docs == expected_docs
    if expected_status == 200:
        response_data = await response.json()
        assert response_data['data'] == request
        assert response_data['change_doc_id'] == expected_change_doc_id
        assert bool(patched_tvm_ticket_check.calls)
