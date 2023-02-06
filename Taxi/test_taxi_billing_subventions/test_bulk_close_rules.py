import pytest


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path,expected_rules_path',
    [
        ('empty_rule_list.json', 'test_ok_response/no_rules_changed.json'),
        (
            'test_ok_response/close_nmfg_and_first_add_rule.json',
            'test_ok_response/nmfg_and_first_add_rule_closed.json',
        ),
        (
            'test_ok_response/close_geo_booking_and_second_add_rule.json',
            'test_ok_response/geo_booking_and_second_add_rule_closed.json',
        ),
        (
            'test_ok_response/close_add_rule_with_same_end_date.json',
            'test_ok_response/add_rule_with_same_end_date_closed.json',
        ),
    ],
)
@pytest.mark.filldb(
    tariff_settings='for_test_ok_response',
    subvention_rules='for_test_ok_response',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_ok_response(
        billing_subventions_client,
        db,
        territories_mock,
        patched_tvm_ticket_check,
        load_py_json_dir,
        request_data_path,
        expected_rules_path,
        request_headers,
):
    request, expected_rules = load_py_json_dir(
        '', request_data_path, expected_rules_path,
    )
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55',
            'X-Yandex-Login': 'superuser',
        },
    )
    response = await billing_subventions_client.post(
        '/v1/rules/close', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == 200
    cursor = db.subvention_rules.find({}, ['_id', 'end']).sort([('_id', 1)])
    actual_rules = await cursor.to_list(None)
    assert actual_rules == expected_rules


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_missing_headers(
        billing_subventions_client,
        patched_tvm_ticket_check,
        request_headers,
        load_py_json_dir,
):
    headers = request_headers
    headers.update({'X-YaTaxi-Draft-Tickets': 'RUPRICING-55'})

    request = load_py_json_dir('', 'empty_rule_list.json')
    response = await billing_subventions_client.post(
        '/v1/rules/close', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == 400


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path',
    [
        'close_time_in_past.json',
        'close_time_later_than_end.json',
        'invalid_rule_id.json',
        'unknown_id_kind.json',
        'duplicate_rule_ids.json',
        'nonexistent_group_id.json',
        'daily_guarantee_with_not_midnight.json',
        'geo_booking_with_not_midnight.json',
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_validation_errors')
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_validation_errors(
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        request_headers,
        request_data_path,
):
    request = load_py_json_dir('', request_data_path)
    headers = request_headers
    headers.update(
        {'X-YaTaxi-Draft-Tickets': 'RUPRICING-55', 'X-Yandex-Login': 'foobar'},
    )
    response = await billing_subventions_client.post(
        '/v1/rules/close', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == 400
