# pylint: disable=redefined-outer-name
import dataclasses

import pandas  # noqa: F401 https://github.com/spulec/freezegun/issues/98
import pytest

from taxi.util import dates

import mayak_inspector.generated.service.pytest_init  # noqa: F401

pytest_plugins = ['mayak_inspector.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def ydb_fixture(patch):
    @patch(
        'mayak_inspector.generated.service'
        '.ydb_client.plugin.BaseYdbDriver._init_driver',
    )
    async def init_driver(*args, **kwargs):
        pass

    return init_driver


@pytest.fixture(autouse=True)
def ydb_fixture_execute(patch):
    @patch(
        'mayak_inspector.generated.service'
        '.ydb_client.plugin.YdbClient.execute',
    )
    async def _execute(*args, **kwargs):
        return []


@pytest.fixture(autouse=True)
def mock_unique_drivers_custom(mock_unique_drivers, mockserver):
    @mock_unique_drivers('/v1/driver/profiles/retrieve_by_uniques')
    async def _retrieve_by_uniques(request):
        profiles = [
            {
                'unique_driver_id': udid,
                'data': [
                    {
                        'park_driver_profile_id': f'park_{udid}',
                        'park_id': 'park',
                        'driver_profile_id': udid,
                    },
                ],
            }
            for udid in request.json['id_in_set']
        ]
        return mockserver.make_response(
            status=200, json=dict(profiles=profiles),
        )


@pytest.fixture(autouse=True)
def mock_driver_profiles_custom(mock_driver_profiles, mockserver):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        licenses = [
            {
                'park_driver_profile_id': park_driver_profile_id,
                'data': {
                    'license': {'pd_id': f'pd_id_{park_driver_profile_id}'},
                    'car_id': f'car_id_{park_driver_profile_id}',
                    'last_login_at': dates.utcnow().isoformat(),
                },
            }
            for park_driver_profile_id in request.json['id_in_set']
            if park_driver_profile_id != 'park_wrong_udid'
        ]
        return mockserver.make_response(
            status=200, json=dict(profiles=licenses),
        )


@pytest.fixture(autouse=True)
def mock_personal_custom(mock_personal, mockserver):
    @mock_personal('/v1/driver_licenses/bulk_retrieve')
    async def _bulk_retrieve(request):
        response = dict(
            items=[
                dict(id=item['id'], value=item['id'])
                for item in request.json['items']
            ],
        )
        return mockserver.make_response(status=200, json=response)


@pytest.fixture(autouse=True)
def mock_fleet_vehicles_custom(mock_fleet_vehicles, mockserver):
    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def _cache_retrieve(request):
        response = dict(
            vehicles=[
                {
                    'park_id_car_id': park_id_car_id,
                    'data': {'number': f'car_number_{park_id_car_id}'},
                }
                for park_id_car_id in request.json['id_in_set']
            ],
        )
        return mockserver.make_response(status=200, json=response)


@pytest.fixture
def mock_actions_history(patch):
    from mayak_inspector.common.utils import yt_utils

    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'
    actions_history = list()

    @patch(repo_module + '.upsert_actions_history')
    async def _upsert_actions_history(_action_history):
        actions_ = [dataclasses.asdict(action_) for action_ in _action_history]
        for action_ in actions_:
            action_['action_params'] = yt_utils.yson_load(
                action_['action_params'],
            )
            action_['triggered_context'] = yt_utils.yson_load(
                action_['triggered_context'],
            )
            action_['extra'] = yt_utils.yson_load(action_['extra'])
        actions_history.extend(actions_)

    return actions_history


@pytest.fixture
def mock_get_actions_history_last(patch):
    from mayak_inspector.storage.ydb import extractors

    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'
    actions_history = list()

    @patch(repo_module + '.get_actions_history_last')
    async def _get_actions_history_last(*args, **kwargs):
        return actions_history

    def set_actions_history(new_actions_history, now):
        nonlocal actions_history
        actions_history = [
            extractors.ActionRecordAdmin(
                mayak_action_uuid=action['mayak_action_uuid'],
                action_type=action['action_type'],
                rule_name=action['rule_name'],
                zone=action['zone'],
                tariff=action['tariff'],
                updated_at=now,
                triggered_context=action['triggered_context'],
                action_params=action['action_params'],
                reasons=list(),
            )
            for action in new_actions_history
        ]

    return set_actions_history


@pytest.fixture
def mock_processor(stq3_context):
    from mayak_inspector.common.jobs import extras
    from mayak_inspector.common.models import metrics_event
    from mayak_inspector.common.models import processor

    async def process(events, job_params=None, entity_id=None):
        if job_params is None:
            job_params = extras.ReadMetrics(
                mayak_import_uuid='1', bucket_id=1, type_id=1,
            )
        proc = processor.Processor(stq3_context)
        ent_proc = proc.make_entity_processor()
        for event in events:
            await ent_proc.process_entity(
                entity_id=entity_id or event['entity_id'],
                events=[metrics_event.MetricsEvent(**event)],
                params=dict(job_params=job_params),
            )

    return process
