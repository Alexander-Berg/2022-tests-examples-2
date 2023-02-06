import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_SHA256_TASK_ID = (
    '6ca86fff7679b402eca065fe4d695e6dace0bdec7f244fc64e5a8b18b44f8e60'
)
_RESUBSCRIBE_TO_DEFAULT_REASON = 'resubscribe_to_default'
_RESUBSCRIBE_TO_SAME_OFFER_REASON = 'resubscribe_to_same_offer'
_RESUBSCRIBE_TO_NEW_OFFER_REASON = 'resubscribe_to_new_offer'
_RESUBSCRIBE_TO_SAME_TITLE_OFFER_REASON = 'resubscribe_to_same_title_offer'
_STQ_CALL_REASON = 'different_profile_usage'
_DRIVER_PROFILE = 'park_uuid'

_MOSCOW_TZ = pytz.timezone('Europe/Moscow')
_NOW = _MOSCOW_TZ.localize(dt.datetime(2020, 12, 17, 12))
_NOW_MINUS_1_HOUR = _MOSCOW_TZ.localize(dt.datetime(2020, 12, 17, 11))
_NOW_MINUS_2_HOUR = _MOSCOW_TZ.localize(dt.datetime(2020, 12, 17, 10))
_NOW_PLUS_1_HOUR = _MOSCOW_TZ.localize(dt.datetime(2020, 12, 17, 13))


def create_expected_stats(
        checks: int = 1,
        errors: int = 0,
        current_mode_unavailable: int = 1,
        version_changes: int = 0,
        changes_to_same_class: int = 0,
        other_changes: int = 0,
):
    return {
        'other_changes': other_changes,
        'changes_to_same_class': changes_to_same_class,
        'checks': checks,
        'current_mode_unavailable': current_mode_unavailable,
        'errors': errors,
        'version_changes': version_changes,
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ONLINE_EVENTS_CONSUMER_SETTINGS={
        'unsubscribe_on_different_profile_online': True,
        'unsubscribe_if_mode_became_unavailable': True,
        'max_pipeline_size': 1,
        'outdate_interval_min': 1,
        'processing_retry_interval_ms': 100,
    },
    DRIVER_MODE_SUBSCRIPTION_OUTDATED_MODES_RESUBSCRIPTION_SETTINGS={
        'dry_run': False,
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'custom_orders_template': (
                offer_templates.DEFAULT_CUSTOM_ORDERS_TEMPLATE
            ),
            'uberdriver_template': offer_templates.DEFAULT_UBERDRIVER_TEMPLATE,
            'orders_template_2': offer_templates.DEFAULT_ORDERS_TEMPLATE,
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {
            'freemode_class_1': 'orders_template',
            'freemode_class_2': 'orders_template',
            'freemode_class_3': 'orders_template',
            'updated_orders': 'orders_template',
            'custom_orders_outdated': 'custom_orders_template',
            'eda_orders': 'orders_template',
        },
        'by_work_mode': {
            'versioned_mode': 'orders_template',
            'freemode_outdated': 'custom_orders_template',
            'freemode_actual': 'orders_template_2',
        },
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='unavailable_mode_resubscription.json')
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='freemode_outdated', stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='freemode_outdated_and_unavailable_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='freemode_unavailable_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(rule_name='freemode_actual'),
                mode_rules.Patch(
                    rule_name='freemode_denied_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(rule_name='freemode_different_class_1'),
                mode_rules.Patch(rule_name='freemode_different_class_2'),
                mode_rules.Patch(
                    rule_name='freemode_different_class_3',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='freemode_different_class_4',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='custom_orders_outdated_1',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='custom_orders_outdated_2',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='updated_orders_1', stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='updated_orders_1',
                    starts_at=_NOW_MINUS_1_HOUR,
                    stops_at=_NOW_PLUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='versioned_mode', stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='versioned_mode',
                    starts_at=_NOW_MINUS_1_HOUR,
                    stops_at=_NOW_PLUS_1_HOUR,
                ),
                mode_rules.Patch(rule_name='updated_orders_2'),
                mode_rules.Patch(
                    rule_name='custom_orders_outdated_no_class',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='eda_orders',
                    offers_group='eda',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
            ],
            mode_classes=[
                mode_rules.ModeClass(
                    'freemode_class_1',
                    [
                        'freemode_outdated',
                        'freemode_actual',
                        'freemode_denied_by_geography',
                        'freemode_unavailable_by_geography',
                        'freemode_outdated_and_unavailable_by_geography',
                    ],
                ),
                mode_rules.ModeClass(
                    'freemode_class_2',
                    [
                        'freemode_different_class_1',
                        'freemode_different_class_2',
                        'freemode_different_class_3',
                    ],
                ),
                mode_rules.ModeClass(
                    'updated_orders', ['updated_orders_1', 'updated_orders_2'],
                ),
                mode_rules.ModeClass('versioned_mode', ['versioned_mode']),
                mode_rules.ModeClass(
                    'freemode_class_3', ['freemode_different_class_4'],
                ),
                mode_rules.ModeClass(
                    'custom_orders_outdated', ['custom_orders_outdated_1'],
                ),
                mode_rules.ModeClass('eda_orders', ['eda_orders']),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'current_mode, udid, expected_target_mode, '
    'expected_reason, expected_stats',
    [
        pytest.param(
            'freemode_actual',
            'udid',
            None,
            None,
            create_expected_stats(current_mode_unavailable=0),
            id='actual_mode_no_resubscription',
        ),
        pytest.param(
            'freemode_denied_by_geography',
            'udid',
            'freemode_actual',
            _RESUBSCRIBE_TO_SAME_TITLE_OFFER_REASON,
            create_expected_stats(changes_to_same_class=1),
            id='resubcribe_by_geography',
        ),
        pytest.param(
            'freemode_outdated',
            'udid',
            'freemode_actual',
            _RESUBSCRIBE_TO_NEW_OFFER_REASON,
            create_expected_stats(changes_to_same_class=1),
            id='resubscribe_by_outdated',
        ),
        pytest.param(
            'versioned_mode',
            'udid',
            'versioned_mode',
            _RESUBSCRIBE_TO_SAME_OFFER_REASON,
            create_expected_stats(version_changes=1),
            id='resubscribe_to_new_version',
        ),
        pytest.param(
            'freemode_outdated',
            'udid_no_time_check',
            None,
            None,
            create_expected_stats(current_mode_unavailable=0),
            id='ignore_outdated',
        ),
        pytest.param(
            'freemode_outdated_and_unavailable_by_geography',
            'udid_no_time_check',
            'freemode_actual',
            _RESUBSCRIBE_TO_SAME_TITLE_OFFER_REASON,
            create_expected_stats(changes_to_same_class=1),
            id='resubscribe_by_conditions_only',
        ),
        pytest.param(
            'freemode_different_class_4',
            'udid',
            'orders',
            _RESUBSCRIBE_TO_DEFAULT_REASON,
            create_expected_stats(other_changes=1),
            id='no_available_modes',
        ),
        pytest.param(
            'freemode_different_class_3',
            'udid',
            'orders',
            _RESUBSCRIBE_TO_DEFAULT_REASON,
            create_expected_stats(other_changes=1),
            id='multiple_available_modes',
        ),
        pytest.param(
            'custom_orders_outdated_no_class',
            'udid',
            'orders',
            _RESUBSCRIBE_TO_DEFAULT_REASON,
            create_expected_stats(other_changes=1),
            id='no_class',
        ),
        pytest.param(
            'freemode_actual',
            'udid_disabled',
            None,
            None,
            create_expected_stats(checks=0, current_mode_unavailable=0),
            id='disabled_udid',
        ),
        pytest.param(
            'custom_orders_outdated_1',
            'udid',
            None,
            None,
            create_expected_stats(checks=0, current_mode_unavailable=0),
            id='disabled_mode_class',
        ),
        pytest.param(
            'custom_orders_outdated_2',
            'udid',
            None,
            None,
            create_expected_stats(checks=0, current_mode_unavailable=0),
            id='disabled_work_mode',
        ),
        pytest.param(
            'updated_orders_1',
            'udid',
            'orders',
            _RESUBSCRIBE_TO_DEFAULT_REASON,
            create_expected_stats(other_changes=1),
            id='do_not_prioritize_current_work_mode',
        ),
        pytest.param(
            'eda_orders',
            'udid',
            None,
            None,
            create_expected_stats(
                checks=1, current_mode_unavailable=1, errors=1,
            ),
            id='non_taxi',
        ),
    ],
)
async def test_sync_stq_unavailable_mode_resubscription(
        taxi_driver_mode_subscription,
        taxi_driver_mode_subscription_monitor,
        mode_rules_data,
        mode_geography_defaults,
        pgsql,
        stq_runner,
        mockserver,
        mocked_time,
        testpoint,
        current_mode: str,
        expected_target_mode: Optional[str],
        udid: str,
        expected_stats: Dict[str, Any],
        expected_reason: Optional[str],
):
    mode_geography_defaults.set_defaults(
        work_modes_available_by_default=[
            'freemode_outdated',
            'freemode_actual',
            'freemode_different_class_1',
            'freemode_different_class_2',
            'freemode_different_class_3',
            'freemode_different_class_4',
            'custom_orders_outdated_1',
            'custom_orders_outdated_2',
            'custom_orders_outdated_no_class',
            'updated_orders_1',
            'updated_orders_2',
            'versioned_mode',
        ],
    )
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'freemode_denied_by_geography', 'br_root', False,
            ),
            geography_tools.ModeGeographyConfiguration(
                'freemode_outdated_and_unavailable_by_geography',
                'br_root',
                False,
            ),
        ],
        pgsql,
    )

    scenario.Scene.mock_driver_trackstory(mockserver, scenario.MOSCOW_POSITION)

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        assert request.json == {'profile_id_in_set': [_DRIVER_PROFILE]}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': _DRIVER_PROFILE,
                    'data': {'unique_driver_id': udid},
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _v1_profiles(request):
        assert request.json == {'id_in_set': [udid]}

        data = []
        for index in range(4):
            park_id = 'park-id' + str(index)
            driver_profile_id = 'uuid' + str(index)
            data.append(
                {
                    'park_id': park_id,
                    'driver_profile_id': driver_profile_id,
                    'park_driver_profile_id': (
                        park_id + '_' + driver_profile_id
                    ),
                },
            )
        return {'profiles': [{'unique_driver_id': udid, 'data': data}]}

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, current_mode, mocked_time, _NOW_MINUS_2_HOUR.isoformat(),
        )
        return response

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_profiles(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': dbid_uuid,
                    'data': {
                        'taximeter_version': '8.80 (562)',
                        'locale': 'ru',
                    },
                }
                for dbid_uuid in ['park-id3_uuid3', 'park-id2_uuid2']
            ],
        }

    @testpoint('handle-mode-set-testpoint')
    def handle_mode_set_cpp_testpoint(data):
        pass

    await taxi_driver_mode_subscription.invalidate_caches()

    await taxi_driver_mode_subscription.tests_control(reset_metrics=True)

    await stq_runner.subscription_sync.call(
        task_id=_SHA256_TASK_ID,
        kwargs={
            'park_driver_id': _DRIVER_PROFILE,
            'unsubscribe_reason': _STQ_CALL_REASON,
        },
    )

    if expected_target_mode:
        assert handle_mode_set_cpp_testpoint.has_calls
        data = handle_mode_set_cpp_testpoint.next_call()['data']
        assert data['mode'] == expected_target_mode
        assert data['source'] == 'subscription_sync'
        assert data['change_reason'] == expected_reason
    else:
        assert not handle_mode_set_cpp_testpoint.has_calls

    actual_stats = await taxi_driver_mode_subscription_monitor.get_metric(
        'mode-resubscribe',
    )

    assert actual_stats == expected_stats


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ONLINE_EVENTS_CONSUMER_SETTINGS={
        'unsubscribe_on_different_profile_online': False,
        'unsubscribe_if_mode_became_unavailable': True,
        'max_pipeline_size': 1,
        'outdate_interval_min': 1,
        'processing_retry_interval_ms': 100,
    },
    DRIVER_MODE_SUBSCRIPTION_OUTDATED_MODES_RESUBSCRIPTION_SETTINGS={
        'dry_run': False,
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='unavailable_mode_resubscription.json')
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='freemode_outdated', stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='freemode_outdated_and_unavailable_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(
                    rule_name='freemode_unavailable_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
                mode_rules.Patch(rule_name='freemode_actual'),
                mode_rules.Patch(
                    rule_name='freemode_denied_by_geography',
                    stops_at=_NOW_MINUS_1_HOUR,
                ),
            ],
            mode_classes=[
                mode_rules.ModeClass(
                    'freemode_class_1',
                    [
                        'freemode_outdated',
                        'freemode_actual',
                        'freemode_denied_by_geography',
                        'freemode_unavailable_by_geography',
                        'freemode_outdated_and_unavailable_by_geography',
                    ],
                ),
            ],
        ),
    ],
)
async def test_sync_stq_unavailable_mode_resubscription_no_position(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        pgsql,
        stq_runner,
        mockserver,
        mocked_time,
        testpoint,
):
    mode_geography_defaults.set_defaults(
        work_modes_available_by_default=[
            'freemode_outdated',
            'freemode_actual',
            'freemode_different_class_1',
            'freemode_different_class_2',
            'freemode_different_class_3',
            'freemode_different_class_4',
            'custom_orders_outdated_1',
            'custom_orders_outdated_2',
            'custom_orders_outdated_no_class',
        ],
    )
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'freemode_denied_by_geography', 'br_root', False,
            ),
        ],
        pgsql,
    )

    scenario.Scene.mock_driver_trackstory(mockserver, driver_position=None)

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        assert request.json == {'profile_id_in_set': [_DRIVER_PROFILE]}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': _DRIVER_PROFILE,
                    'data': {'unique_driver_id': 'udid_no_time_check'},
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _v1_profiles(request):
        assert request.json == {'id_in_set': ['udid_no_time_check']}

        data = []
        return {
            'profiles': [
                {'unique_driver_id': 'udid_no_time_check', 'data': data},
            ],
        }

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            'freemode_denied_by_geography',
            mocked_time,
            _NOW_MINUS_2_HOUR.isoformat(),
        )
        return response

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_profiles(request):
        return {'profiles': []}

    @testpoint('handle-mode-set-testpoint')
    def handle_mode_set_cpp_testpoint(data):
        pass

    await taxi_driver_mode_subscription.invalidate_caches()

    await stq_runner.subscription_sync.call(
        task_id=_SHA256_TASK_ID,
        kwargs={
            'park_driver_id': _DRIVER_PROFILE,
            'unsubscribe_reason': _STQ_CALL_REASON,
        },
    )

    assert not handle_mode_set_cpp_testpoint.has_calls
