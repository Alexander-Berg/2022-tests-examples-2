# flake8: noqa IS001
import datetime
import enum
from typing import List, Dict, Any, Optional

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import diagnostics
from tests_driver_mode_subscription import saga_tools


REQUEST_PARAMS = {'park_id': 'park0', 'driver_profile_id': 'uuid0'}

REQUEST_HEADER = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

_NOW = '2019-05-01T05:00:00+00:00'

_SAGA_EXECUTION_FAILED = 'failed'
_SAGA_COMPENSATION_FAILED = 'compensation failed'

_DEFAULT_TAXIMETER_POLLING_POLICY = {'polling_policy': 'default'}

_ORDERS_TAXIMETER_POLLING_POLICY = {'polling_policy': 'orders_clause'}

_DRIVER_FIX_TAXIMETER_POLLING_POLICY = {'polling_policy': 'driver_fix_clause'}


def _get_features(features: List[str]):
    items = []
    for feature in features:
        items.append({'name': feature})
    return items


def _make_feature_toggles_value(clause_name: str):
    return {'clause': clause_name}


# TODO: this function can be removed for ApplyRules::DbOnly
def _clear_rule_id(response):
    assert 'rule_id' in response['current_mode']
    assert response['current_mode']['rule_id'] != ''
    response['current_mode']['rule_id'] = ''
    if 'subscription_process' in response:
        assert 'rule_id' in response['subscription_process']['target_mode']
        response['subscription_process']['target_mode']['rule_id'] = ''
    return response


class DriverProfileResponseType(enum.Enum):
    ALL_OK = 'ALL_OK'
    NO_VERSION = 'NO_VERSION'
    NO_PROFILE_DATA = 'NO_PROFILE_DATA'
    NO_PROFILE = 'NO_PROFILE'
    ERROR = 'ERROR'


def _mock_driver_profiles(mockserver, result_type: DriverProfileResponseType):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def handler(request):
        if result_type == DriverProfileResponseType.NO_PROFILE_DATA:
            return {'profiles': [{'park_driver_profile_id': 'dbid_uuid'}]}
        if result_type == DriverProfileResponseType.NO_VERSION:
            return {
                'profiles': [
                    {'data': {}, 'park_driver_profile_id': 'dbid_uuid'},
                ],
            }
        if result_type == DriverProfileResponseType.NO_PROFILE:
            return {'profiles': []}
        if result_type == DriverProfileResponseType.ERROR:
            return mockserver.make_response(status=500)

        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {'taximeter_version': '8.80 (562)'},
                },
            ],
        }

    return handler


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'subscription_in_progress',
    [
        pytest.param(False, id='no_active_saga'),
        pytest.param(
            True,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['sagas.sql'],
                ),
            ],
            id='has_active_saga',
        ),
    ],
)
@pytest.mark.parametrize(
    'current_mode_display_profile, current_mode_feature_toggles, '
    'target_mode_feature_toggles, current_mode_polling_policy, '
    'target_mode_polling_policy, driver_profiles_response',
    [
        pytest.param(
            'driver_fix',
            {},
            {},
            {},
            {},
            DriverProfileResponseType.ALL_OK,
            id='no_experiment',
        ),
        pytest.param(
            'driver_fix_longterm',
            {},
            _make_feature_toggles_value('orders_clause'),
            _DEFAULT_TAXIMETER_POLLING_POLICY,
            _ORDERS_TAXIMETER_POLLING_POLICY,
            DriverProfileResponseType.ALL_OK,
            id='default_current_clause',
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
                pytest.mark.experiments3(
                    filename='test_taximeter_polling_policy.json',
                ),
            ],
        ),
        pytest.param(
            'driver_fix',
            _make_feature_toggles_value('driver_fix_clause'),
            _make_feature_toggles_value('orders_clause'),
            _DRIVER_FIX_TAXIMETER_POLLING_POLICY,
            _ORDERS_TAXIMETER_POLLING_POLICY,
            DriverProfileResponseType.ALL_OK,
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
                pytest.mark.experiments3(
                    filename='test_taximeter_polling_policy.json',
                ),
            ],
            id='all_configs',
        ),
        pytest.param(
            'driver_fix',
            {},
            {},
            {},
            {},
            DriverProfileResponseType.NO_PROFILE_DATA,
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
            ],
            id='driver_profiles_no_profile_data',
        ),
        pytest.param(
            'driver_fix',
            {},
            {},
            {},
            {},
            DriverProfileResponseType.NO_PROFILE,
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
            ],
            id='driver_profiles_no_profile',
        ),
        pytest.param(
            'driver_fix',
            {},
            {},
            {},
            {},
            DriverProfileResponseType.NO_VERSION,
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
            ],
            id='driver_profiles_no_taximeter_version',
        ),
        pytest.param(
            'driver_fix',
            {},
            {},
            {},
            {},
            DriverProfileResponseType.ERROR,
            marks=[
                pytest.mark.experiments3(filename='test_feature_toggles.json'),
            ],
            id='driver_profiles_error',
        ),
    ],
)
async def test_mode_diagnostics(
        mockserver,
        mocked_time,
        taxi_config,
        mode_rules_data,
        taxi_driver_mode_subscription,
        subscription_in_progress: bool,
        current_mode_display_profile: str,
        current_mode_feature_toggles: Dict[str, Any],
        target_mode_feature_toggles: Dict[str, Any],
        current_mode_polling_policy: Dict[str, Any],
        target_mode_polling_policy: Dict[str, Any],
        driver_profiles_response: DriverProfileResponseType,
):
    mode_names = ['driver_fix', 'orders']
    mode_types = ['driver_fix_type', 'orders_type']
    current_mode_features = {
        'driver_fix': {'roles': [{'name': 'role1'}]},
        'tags': {'assign': ['driver_fix']},
        'reposition': {'profile': 'reposition_profile'},
    }
    target_mode_features = {
        'geobooking': {},
        'tags': {'assign': ['orders']},
        'active_transport': {'type': 'bicycle'},
    }
    driver_fix_mode_settings = {
        'rule_id': 'id_rule1',
        'shift_close_time': '00:01',
    }
    target_mode_display_profile = 'orders_display_profile'

    before_now = mocked_time.now() - datetime.timedelta(hours=1)

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            patches=[
                mode_rules.Patch(
                    rule_name=mode_names[0],
                    display_mode=mode_types[0],
                    display_profile=current_mode_display_profile,
                    features=current_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
                mode_rules.Patch(
                    rule_name=mode_names[1],
                    display_mode=mode_types[1],
                    display_profile=target_mode_display_profile,
                    features=target_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request,
            mode_names[0],
            mocked_time,
            mode_settings=driver_fix_mode_settings,
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park0_uuid0',
                    'data': {'unique_driver_id': 'udid0'},
                },
            ],
        }

    driver_profiles_mock = _mock_driver_profiles(
        mockserver, driver_profiles_response,
    )

    response = await taxi_driver_mode_subscription.get(
        'v1/admin/mode/diagnostics',
        params=REQUEST_PARAMS,
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    response_data = _clear_rule_id(response.json())
    assert _clear_rule_id(response.json()) == response_data

    expected_response = {
        'current_mode': {
            'rule_id': '',
            'name': mode_names[0],
            'offers_group': 'taxi',
            'started_at': mocked_time.now().strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
            'ui': diagnostics.ui(
                mode_types[0],
                current_mode_display_profile,
                current_mode_feature_toggles,
                current_mode_polling_policy,
            ),
            'subscription': diagnostics.subscription(driver_fix_mode_settings),
            'features': [
                {
                    'name': 'driver_fix',
                    'settings': {'roles': [{'name': 'role1'}]},
                },
                {'name': 'tags', 'settings': current_mode_features['tags']},
                {
                    'name': 'reposition',
                    'settings': current_mode_features['reposition'],
                },
            ],
        },
    }
    if subscription_in_progress:
        response_data['subscription_process']['steps'].sort(
            key=lambda step: (step['display_order'], step['name']),
        )

        expected_response['subscription_process'] = {
            'target_mode': {
                'rule_id': '',
                'name': mode_names[1],
                'offers_group': 'taxi',
                'started_at': mocked_time.now().strftime(
                    '%Y-%m-%dT%H:%M:%S+00:00',
                ),
                'ui': diagnostics.ui(
                    mode_types[1],
                    target_mode_display_profile,
                    target_mode_feature_toggles,
                    target_mode_polling_policy,
                ),
                'features': [
                    {'name': 'tags', 'settings': target_mode_features['tags']},
                    {
                        'name': 'active_transport',
                        'settings': target_mode_features['active_transport'],
                    },
                    {'name': 'geobooking', 'settings': {}},
                ],
                'subscription': diagnostics.subscription(
                    {'key': 'next_value'}, settings_type='geobooking',
                ),
            },
            'status': 'preparing',  # cause there is no previous mode is db
            'steps': [],
        }

    assert response_data == expected_response
    assert driver_profiles_mock.has_calls


class SagaStepDiagnostics:
    def __init__(
            self,
            name: str,
            order: int,
            status: str,
            is_compensation: bool = False,
    ):
        self.name = name
        self.display_order = order
        self.status = status
        self.is_compesnation = is_compensation

    def to_dict(self):
        return {
            'name': self.name,
            'display_order': self.display_order,
            'status': self.status,
            'is_compensation': self.is_compesnation,
        }


class StepRow:
    def __init__(
            self,
            name: str,
            execution_status: str,
            compensation_status: Optional[str] = None,
    ):
        self.name = name
        self.execution_status = execution_status
        self.compensation_status = compensation_status

    def to_insert_value(self, saga_id: int):
        return (
            f'({saga_id}, \'{self.name}\', \'{self.execution_status}\', '
            + (
                f'\'{self.compensation_status}\''
                if self.compensation_status
                else 'null'
            )
            + ')'
        )


def _insert_saga_steps_db_data(pgsql, steps: List[StepRow]):
    if not steps:
        return

    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'INSERT INTO state.saga_steps (saga_id, name, execution_status, compensation_status) VALUES '
        + ', '.join([step.to_insert_value(2) for step in steps]),
    )


@pytest.mark.now(_NOW)
@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
        'allow_saga_compensation': True,
        'enable_saga_persistent': True,
    },
)
@pytest.mark.parametrize(
    'expected_saga_status, expected_saga_steps, steps_in_db',
    [
        pytest.param(
            _SAGA_EXECUTION_FAILED,
            [
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'waiting'),
                SagaStepDiagnostics(
                    'active_transport_change_step', 2, 'waiting',
                ),
                SagaStepDiagnostics('mode_change_step', 2, 'waiting'),
                SagaStepDiagnostics(
                    'reposition_mode_change_step', 2, 'waiting',
                ),
                SagaStepDiagnostics('tags_change_step', 2, 'waiting'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'waiting'),
                SagaStepDiagnostics('subscription_sync_step', 3, 'waiting'),
            ],
            [],
            id='no_executed_steps',
        ),
        pytest.param(
            _SAGA_EXECUTION_FAILED,
            [
                # current epoch: no execution status = failed
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'failed'),
                # future epochs
                SagaStepDiagnostics(
                    'active_transport_change_step', 2, 'waiting',
                ),
                SagaStepDiagnostics('mode_change_step', 2, 'waiting'),
                SagaStepDiagnostics(
                    'reposition_mode_change_step', 2, 'waiting',
                ),
                SagaStepDiagnostics('tags_change_step', 2, 'waiting'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'waiting'),
                SagaStepDiagnostics('subscription_sync_step', 3, 'waiting'),
            ],
            [StepRow('driver_fix_stop_step', 'failed')],
            id='execute_first_epoch_failed',
        ),
        pytest.param(
            _SAGA_EXECUTION_FAILED,
            [
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                # current epoch: no execution status = failed
                SagaStepDiagnostics('active_transport_change_step', 2, 'ok'),
                SagaStepDiagnostics('mode_change_step', 2, 'failed'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'failed'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'failed'),
                # future epoch
                SagaStepDiagnostics('subscription_sync_step', 3, 'waiting'),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('active_transport_change_step', 'ok'),
                StepRow('reposition_mode_change_step', 'ok'),
                StepRow('tags_change_step', 'failed'),
                StepRow('mode_change_step', 'failed'),
                StepRow('ui_profile_change_step', 'failed'),
            ],
            id='execute_second_epoch_failed',
        ),
        pytest.param(
            _SAGA_COMPENSATION_FAILED,
            [
                # completed steps from execute plan
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                SagaStepDiagnostics(
                    'active_transport_change_step', 2, 'blocked',
                ),
                SagaStepDiagnostics('mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'failed'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'ok'),
                # compensation plan
                SagaStepDiagnostics('mode_change_step', 3, 'waiting', True),
                SagaStepDiagnostics(
                    'reposition_mode_change_step', 3, 'waiting', True,
                ),
                SagaStepDiagnostics('tags_change_step', 3, 'waiting', True),
                SagaStepDiagnostics(
                    'ui_profile_change_step', 3, 'waiting', True,
                ),
                SagaStepDiagnostics(
                    'driver_fix_stop_step', 4, 'waiting', True,
                ),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('tags_change_step', 'failed'),
                StepRow('mode_change_step', 'ok'),
                StepRow('ui_profile_change_step', 'ok'),
                StepRow('active_transport_change_step', 'blocked'),
                StepRow('reposition_mode_change_step', 'ok'),
            ],
            id='execute_second_epoch_blocked',
        ),
        pytest.param(
            # do not compensate ModeIsChanged epoch
            _SAGA_EXECUTION_FAILED,
            [
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                SagaStepDiagnostics('active_transport_change_step', 2, 'ok'),
                SagaStepDiagnostics('mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'ok'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'ok'),
                SagaStepDiagnostics('subscription_sync_step', 3, 'blocked'),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('mode_change_step', 'ok'),
                StepRow('ui_profile_change_step', 'ok'),
                StepRow('tags_change_step', 'ok'),
                StepRow('active_transport_change_step', 'ok'),
                StepRow('reposition_mode_change_step', 'ok'),
                StepRow('subscription_sync_step', 'blocked'),
            ],
            id='execute_last_epoch_blocked',
        ),
        pytest.param(
            _SAGA_EXECUTION_FAILED,
            [
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                SagaStepDiagnostics('active_transport_change_step', 2, 'ok'),
                SagaStepDiagnostics('mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'ok'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'ok'),
                SagaStepDiagnostics('subscription_sync_step', 3, 'failed'),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('mode_change_step', 'ok'),
                StepRow('ui_profile_change_step', 'ok'),
                StepRow('tags_change_step', 'ok'),
                StepRow('active_transport_change_step', 'ok'),
                StepRow('reposition_mode_change_step', 'ok'),
                StepRow('subscription_sync_step', 'failed'),
            ],
            id='execute_last_epoch_failed',
        ),
        pytest.param(
            _SAGA_COMPENSATION_FAILED,
            [
                # completed steps from execute plan
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                SagaStepDiagnostics('active_transport_change_step', 2, 'ok'),
                SagaStepDiagnostics('mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'blocked'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'ok'),
                # compensation plan
                SagaStepDiagnostics(
                    'active_transport_change_step', 3, 'failed', True,
                ),
                SagaStepDiagnostics('mode_change_step', 3, 'waiting', True),
                SagaStepDiagnostics(
                    'reposition_mode_change_step', 3, 'waiting', True,
                ),
                SagaStepDiagnostics(
                    'ui_profile_change_step', 3, 'waiting', True,
                ),
                SagaStepDiagnostics(
                    'driver_fix_stop_step', 4, 'waiting', True,
                ),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('mode_change_step', 'ok'),
                StepRow('tags_change_step', 'blocked'),
                StepRow('ui_profile_change_step', 'ok'),
                StepRow('active_transport_change_step', 'ok', 'failed'),
                StepRow('reposition_mode_change_step', 'ok'),
            ],
            id='compensate_first_epoch_failed',
        ),
        pytest.param(
            _SAGA_COMPENSATION_FAILED,
            [
                # completed steps from execute plan
                SagaStepDiagnostics('driver_fix_stop_step', 1, 'ok'),
                SagaStepDiagnostics('active_transport_change_step', 2, 'ok'),
                SagaStepDiagnostics('mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('reposition_mode_change_step', 2, 'ok'),
                SagaStepDiagnostics('tags_change_step', 2, 'blocked'),
                SagaStepDiagnostics('ui_profile_change_step', 2, 'ok'),
                # compensation plan
                SagaStepDiagnostics(
                    'active_transport_change_step', 3, 'ok', True,
                ),
                SagaStepDiagnostics('mode_change_step', 3, 'blocked', True),
                SagaStepDiagnostics(
                    'reposition_mode_change_step', 3, 'ok', True,
                ),
                SagaStepDiagnostics('tags_change_step', 3, 'ok', True),
                SagaStepDiagnostics('ui_profile_change_step', 3, 'ok', True),
                SagaStepDiagnostics(
                    'driver_fix_stop_step', 4, 'waiting', True,
                ),
            ],
            [
                StepRow('driver_fix_stop_step', 'ok'),
                StepRow('mode_change_step', 'ok', 'blocked'),
                StepRow('tags_change_step', 'blocked', 'ok'),
                StepRow('ui_profile_change_step', 'ok', 'ok'),
                StepRow('active_transport_change_step', 'ok', 'ok'),
                StepRow('reposition_mode_change_step', 'ok', 'ok'),
            ],
            id='compensate_second_epoch_blocked',
        ),
    ],
)
async def test_mode_diagnostics_saga_steps(
        mockserver,
        mocked_time,
        taxi_config,
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        expected_saga_status: str,
        expected_saga_steps: List[SagaStepDiagnostics],
        steps_in_db: List[StepRow],
):
    mode_names = ['driver_fix', 'orders']
    mode_types = ['driver_fix_type', 'orders_type']
    current_mode_features = {
        'driver_fix': {'roles': [{'name': 'role1'}]},
        'tags': {'assign': ['driver_fix']},
        'reposition': {'profile': 'reposition_profile'},
    }
    target_mode_features = {
        'tags': {'assign': ['orders']},
        'active_transport': {'type': 'bicycle'},
    }
    driver_fix_mode_settings = {
        'rule_id': 'id_rule1',
        'shift_close_time': '00:01',
    }

    before_now = mocked_time.now() - datetime.timedelta(hours=1)

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            patches=[
                mode_rules.Patch(
                    rule_name=mode_names[0],
                    display_mode=mode_types[0],
                    features=current_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
                mode_rules.Patch(
                    rule_name=mode_names[1],
                    display_mode=mode_types[1],
                    features=target_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
            ],
        ),
    )

    _insert_saga_steps_db_data(pgsql, steps_in_db)

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request,
            mode_names[0],
            mocked_time,
            mode_settings=driver_fix_mode_settings,
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park1_uuid1',
                    'data': {'unique_driver_id': 'udid1'},
                },
            ],
        }

    _mock_driver_profiles(mockserver, DriverProfileResponseType.ALL_OK)

    response = await taxi_driver_mode_subscription.get(
        'v1/admin/mode/diagnostics',
        params={'park_id': 'park1', 'driver_profile_id': 'uuid1'},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    response_data = _clear_rule_id(response.json())
    assert _clear_rule_id(response.json()) == response_data

    subscription_process = response_data.get('subscription_process', None)
    assert subscription_process is not None
    assert subscription_process['status'] == expected_saga_status
    subscription_process['steps'].sort(
        key=lambda step: (step['display_order'], step['name']),
    )
    assert subscription_process['steps'] == [
        step.to_dict() for step in expected_saga_steps
    ]


@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        saga_tools.make_insert_saga_query(
            park_id='park1',
            driver_id='uuid1',
            next_mode='orders',
            next_mode_timepoint='2019-05-01T05:00:00+00:00',
            next_mode_settings={'key': 'next_value'},
            prev_mode='driver_fix',
            prev_mode_timepoint='2019-05-01T04:00:00+00:00',
            started_at=datetime.datetime.fromisoformat(
                '2019-05-01T05:00:00+00:00',
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
        'allow_saga_compensation': True,
        'enable_saga_persistent': True,
    },
)
async def test_mode_diagnostics_failed_planning(
        mockserver,
        mocked_time,
        taxi_config,
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
):
    mode_names = ['driver_fix', 'orders']
    mode_types = ['driver_fix_type', 'orders_type']
    current_mode_features = {
        'driver_fix': {'roles': [{'name': 'role1'}]},
        'tags': {'assign': ['driver_fix']},
        'reposition': {'profile': 'reposition_profile'},
    }
    target_mode_features = {
        'tags': {'assign': ['orders']},
        'active_transport': {'type': 'bicycle'},
    }
    driver_fix_mode_settings = {
        'rule_id': 'id_rule1',
        'shift_close_time': '00:01',
    }

    before_now = mocked_time.now() - datetime.timedelta(hours=1)

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            patches=[
                mode_rules.Patch(
                    rule_name=mode_names[0],
                    display_mode=mode_types[0],
                    features=current_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
                mode_rules.Patch(
                    rule_name=mode_names[1],
                    display_mode=mode_types[1],
                    features=target_mode_features,
                    starts_at=pytz.utc.localize(before_now),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request,
            mode_names[0],
            mocked_time,
            mode_settings=driver_fix_mode_settings,
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'park1_uuid1',
                    'data': {'unique_driver_id': 'udid1'},
                },
            ],
        }

    _mock_driver_profiles(mockserver, DriverProfileResponseType.ALL_OK)

    response = await taxi_driver_mode_subscription.get(
        'v1/admin/mode/diagnostics',
        params={'park_id': 'park1', 'driver_profile_id': 'uuid1'},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    response_data = _clear_rule_id(response.json())
    assert _clear_rule_id(response.json()) == response_data

    subscription_process = response_data.get('subscription_process', None)
    assert subscription_process is not None
    assert subscription_process['status'] == 'planning failed'
    assert subscription_process['steps'] == []
