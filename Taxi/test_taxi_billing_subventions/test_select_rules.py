import math

import pytest

from taxi_billing_subventions import config


@pytest.fixture
def _request(request_headers, billing_subventions_client):
    async def _request_wrapper(request):
        return await billing_subventions_client.post(
            '/v1/rules/select', headers=request_headers, json=request,
        )

    return _request_wrapper


@pytest.mark.parametrize(
    'test_data_path',
    [
        'personal_subvention_by_driver_clid_success.json',
        'personal_subvention_by_driver_uid_success1.json',
        'personal_subvention_by_driver_uid_success2.json',
        'personal_subvention_by_driver_uid_success3.json',
        'personal_subvention_by_unique_driver_id_success1.json',
        'personal_subvention_by_unique_driver_id_success2.json',
        'personal_subvention_by_unique_driver_id_success3.json',
        'subventions_by_status_disabled.json',
        'personal_subventions_by_time_range_success1.json',
        'personal_subventions_by_time_range_success2.json',
        'personal_subventions_by_time_range_success3.json',
        'subventions_by_time_range_success1.json',
        'subventions_by_time_range_success2.json',
        'personal_subventions_by_time_range_not_found1.json',
        'select_geo_booking_rules.json',
        'select_daily_guarantees.json',
        'select_partially_approved_daily_guarantees.json',
        'subventions_with_subv_disable_all_tag.json',
        'subventions_with_subv_disable_mfg_geo_tag.json',
        'subventions_with_subv_disable_on_top_geo_tag.json',
        'subventions_with_subv_disable_mfg_tag.json',
        'subventions_with_subv_disable_on_top_tag.json',
        'subventions_with_subv_disable_nmfg_tag.json',
        'subventions_with_subv_disable_do_x_get_y_tag.json',
        'subventions_with_subv_disable_many_tags.json',
        'subventions_with_no_tags.json',
        'subventions_with_some_tags.json',
        'subventions_without_tags_constraint.json',
        'select_by_ids.json',
        'select_by_ids_and_time_range.json',
        'select_by_ids_and_types.json',
        'personal_subventions_by_ids.json',
        (
            'personal_subventions_by_ids_'
            'with_subv_disable_do_x_get_y_personal_tag.json'
        ),
        'personal_subventions_with_subv_disable_do_x_get_y_personal_tag.json',
        'personal_and_not_personal_subventions_by_ids.json',
        'select_geo_booking_rules_geoarea_msk.json',
        'select_geo_booking_rules_geoarea_kzn.json',
        'select_all_by_profile_payment_type_restriction.json',
        'select_by_profile_payment_type_restriction.json',
        'select_by_rule_profile_payment_type_restriction.json',
        'need_approval_rule_does_not_affect_limit.json',
        'daily_guarantees_ekb.json',
        'personal_subvention_by_driver_clid_moscow.json',
        'select_driver_fix_rules.json',
        'select_driver_fix_rules_for_zone_and_tag.json',
        'select_driver_fix_rules_for_zone_and_tag_and_classes.json',
        'select_goal_rules.json',
        'select_goal_not_personal.json',
        'select_goal_not_personal_with_config.json',
        'subv_disable_do_x_get_y_tag_not_disable_personal_doxgety.json',
        'subv_disable_do_x_get_y_personal_tag_not_disable_usual_doxgety.json',
    ],
)
@pytest.mark.parametrize('use_hint', [True, False])
@pytest.mark.filldb(
    personal_subvention_rules='for_test_select_rules',
    subvention_rules='for_test_select_rules',
    personal_subventions='for_test_select_rules',
    unique_drivers='for_test_select_rules',
    dbdrivers='for_test_select_rules',
    dbparks='for_test_select_rules',
    tariff_settings='for_test_select_rules',
)
async def test_select_rules(
        test_data_path, use_hint, load_py_json_dir, _request, monkeypatch,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    if 'config' in test_data:
        _set_config(monkeypatch, test_data['config'])

    _set_hint_config(monkeypatch, use_hint)

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(expected['subventions']) == _to_dict(actual['subventions'])


@pytest.mark.parametrize(
    'test_data_path',
    [
        'personal_subventions_limit_offset1.json',
        'personal_subventions_limit_offset2.json',
        'subventions_limit_offset1.json',
    ],
)
@pytest.mark.filldb(
    personal_subvention_rules='for_test_select_rules',
    subvention_rules='for_test_select_rules',
    personal_subventions='for_test_select_rules',
    unique_drivers='for_test_select_rules',
    dbdrivers='for_test_select_rules',
    dbparks='for_test_select_rules',
    tariff_settings='for_test_select_rules',
)
async def test_select_rules_limit_offset(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']['subventions']
    limit = request['limit']

    requests_count = math.ceil(len(expected) / limit)
    actual = []
    for i in range(requests_count):
        response = await _request(request)
        assert response.status == 200
        curr_actual = await response.json()
        curr_actual = curr_actual['subventions']
        curr_expected = expected[i * limit : (i + 1) * limit]
        assert _to_dict(curr_actual) == _to_dict(curr_expected)
        request['cursor'] = curr_actual[-1]['cursor']
        actual.extend(curr_actual)
    assert _to_dict(actual) == _to_dict(expected)


@pytest.mark.parametrize('test_data_path', ['all_daily_guarantees.json'])
@pytest.mark.filldb(
    subvention_rules='for_test_taximeter_tag',
    tariff_settings='for_test_select_rules',
)
async def test_taximeter_tag(test_data_path, load_py_json_dir, _request):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize(
    'test_data_path', ['daily_guarantees_via_one_step.json'],
)
@pytest.mark.filldb(
    subvention_rules='via_one_step', tariff_settings='for_test_select_rules',
)
async def test_rule_via_single_step(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize(
    'test_data_path', ['select_daily_guarantees_begin_ne_end.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_select_rules_begin_ne_end',
    tariff_settings='for_test_select_rules',
)
# pylint: disable=invalid-name
async def test_select_rules_begin_ne_end(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(expected['subventions']) == _to_dict(actual['subventions'])


def _to_dict(rules):
    result = {rule['subvention_rule_id']: rule for rule in rules}
    assert len(result) == len(rules)
    return result


@pytest.mark.parametrize('test_data_path', ['check_time_range.json'])
@pytest.mark.filldb(
    subvention_rules='for_test_select_rules_check_time_range',
    tariff_settings='for_test_select_rules',
)
# pylint: disable=invalid-name
async def test_check_time_range(test_data_path, load_py_json_dir, _request):
    test_data = load_py_json_dir('test_select_rules', test_data_path)

    for case in test_data['cases']:
        request = case['request']
        expected_status = case['expected_status']
        response = await _request(request)
        assert response.status == expected_status
        if expected_status == 200:
            expected_found = case['expected_found']
            actual = await response.json()
            assert expected_found == len(actual['subventions'])


@pytest.mark.parametrize(
    'test_data_path', ['different_types_subventions_cursor.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_different_types',
    tariff_settings='for_test_select_rules',
)
async def test_different_types_cursor(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']['subventions']
    limit = request['limit']

    requests_count = math.ceil(len(expected) / limit)
    actual = []
    for i in range(requests_count):
        response = await _request(request)
        assert response.status == 200
        curr_actual = await response.json()
        curr_actual = curr_actual['subventions']
        curr_expected = expected[i * limit : (i + 1) * limit]
        assert curr_actual == curr_expected
        request['cursor'] = curr_actual[-1]['cursor']
        actual.extend(curr_actual)
    assert actual == expected


@pytest.mark.parametrize(
    'test_data_path',
    ['select_mfg_rule.json', 'select_ridecount_on_top_rule.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_select_rule_response_schema',
    tariff_settings='for_test_select_rules',
)
# pylint: disable=invalid-name
async def test_select_rule_response_schema(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_select_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']
    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert actual == expected


@pytest.mark.parametrize(
    'test_data_path',
    [
        'daily_guarantee_full_branding.json',
        'daily_guarantee_no_branding.json',
        'daily_guarantee_any_branding.json',
        'daily_guarantee_without_branding.json',
    ],
)
@pytest.mark.filldb(
    subvention_rules='for_test_branding',
    tariff_settings='for_test_select_rules',
)
async def test_branding(test_data_path, load_py_json_dir, _request):
    test_data = load_py_json_dir('test_branding', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize(
    'test_data_path',
    [
        'daily_guarantee_full_branding.json',
        'daily_guarantee_no_branding.json',
        'daily_guarantee_both_branding_and_driver_branding.json',
        'daily_guarantee_without_driver_branding.json',
    ],
)
@pytest.mark.filldb(
    subvention_rules='for_test_branding',
    tariff_settings='for_test_select_rules',
)
async def test_driver_branding(test_data_path, load_py_json_dir, _request):
    test_data = load_py_json_dir('test_driver_branding', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize(
    'test_data_path',
    ['multiple_classes.json', 'no_classes.json', 'no_restriction.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_tariff_classes',
    tariff_settings='for_test_select_rules',
)
async def test_profile_tariff_classes(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_profile_tariff_classes', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize(
    'test_data_path',
    ['multiple_classes.json', 'no_classes.json', 'no_restriction.json'],
)
@pytest.mark.filldb(
    subvention_rules='for_test_tariff_classes',
    tariff_settings='for_test_select_rules',
)
async def test_order_tariff_classes(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_order_tariff_classes', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


@pytest.mark.parametrize('test_data_path', ['50.json'])
@pytest.mark.filldb(
    subvention_rules='for_test_driver_points',
    tariff_settings='for_test_select_rules',
)
async def test_profile_driver_points(
        test_data_path, load_py_json_dir, _request,
):
    test_data = load_py_json_dir('test_profile_driver_points', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(actual['subventions']) == _to_dict(expected['subventions'])


def _set_hint_config(monkeypatch, value: bool):
    monkeypatch.setattr(
        config.Config, 'BILLING_SUBVENTIONS_RULES_SELECT_USE_HINT', value,
    )


@pytest.mark.parametrize(
    'test_data_path', ['invalid_rule_ids.json', 'id_is_not_object_id.json'],
)
async def test_validation_error(
        test_data_path, load_py_json_dir, _request, monkeypatch,
):
    test_data = load_py_json_dir('test_validation_error', test_data_path)
    request = test_data['request']
    response = await _request(request)
    assert response.status == 400


@pytest.mark.parametrize(
    'test_data_path',
    [
        # Ensure that personal subventions that are not approved are not
        # returned
        'personal_subventions_by_time_range.json',
    ],
)
@pytest.mark.parametrize('use_hint', [True, False])
@pytest.mark.filldb(
    personal_subvention_rules='for_test_select_personal_rules',
    personal_subventions='for_test_select_personal_rules',
    tariff_settings='for_test_select_personal_rules',
)
async def test_select_personal_rules(
        test_data_path, use_hint, load_py_json_dir, _request, monkeypatch,
):
    test_data = load_py_json_dir('test_select_personal_rules', test_data_path)
    request = test_data['request']
    expected = test_data['expected']

    _set_hint_config(monkeypatch, use_hint)

    response = await _request(request)
    assert response.status == 200
    actual = await response.json()
    assert _to_dict(expected['subventions']) == _to_dict(actual['subventions'])


def _set_config(monkeypatch, config_value: dict):
    for key, value in config_value.items():
        monkeypatch.setattr(config.Config, key, value)
