import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

_SHA256_TASK_ID = (
    '6ca86fff7679b402eca065fe4d695e6dace0bdec7f244fc64e5a8b18b44f8e60'
)
_UNSUBSCRIBE_REASON = 'different_profile_usage'
_DRIVER_PROFILE = 'park_uuid'


@pytest.mark.now('2020-12-17T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_FEATURES={
        '__default__': {
            'is_exclusive': False,
            'unsubscribe_on_different_profile_online': False,
        },
        'driver_fix': {
            'is_exclusive': False,
            'unsubscribe_on_different_profile_online': True,
        },
    },
    DRIVER_MODE_SUBSCRIPTION_ONLINE_EVENTS_CONSUMER_SETTINGS={
        'unsubscribe_on_different_profile_online': True,
        'unsubscribe_if_mode_became_unavailable': True,
        'max_pipeline_size': 1,
        'outdate_interval_min': 1,
        'processing_retry_interval_ms': 100,
    },
)
@pytest.mark.parametrize(
    'expect_unsubscribe_call',
    [
        pytest.param(2),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BACKGROUND_EXCLUSIVE_PROFILES_LIMIT=1,
                ),
            ],
        ),
    ],
)
async def test_sync_stq_different_profile_usage(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        stq_runner,
        mockserver,
        mocked_time,
        testpoint,
        expect_unsubscribe_call: int,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        assert request.json == {'profile_id_in_set': [_DRIVER_PROFILE]}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': _DRIVER_PROFILE,
                    'data': {'unique_driver_id': 'udid'},
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _v1_profiles(request):
        assert request.json == {'id_in_set': ['udid']}

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
        return {'profiles': [{'unique_driver_id': 'udid', 'data': data}]}

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        driver_data = request.json['driver']
        driver_profile = (
            driver_data['park_id'] + '_' + driver_data['driver_profile_id']
        )
        mode = (
            'driver_fix'
            if driver_profile in ('park-id3_uuid3', 'park-id2_uuid2')
            else 'orders'
        )
        response = common.mode_history_response(request, mode, mocked_time)
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
    def _handle_mode_set_cpp_testpoint(data):
        assert data['park_id_driver_profile_id'] in (
            'park-id3_uuid3',
            'park-id2_uuid2',
        )
        assert data['mode'] == 'orders'
        assert data['source'] == 'subscription_sync'
        assert data['change_reason'] == _UNSUBSCRIBE_REASON

    await taxi_driver_mode_subscription.invalidate_caches()

    await stq_runner.subscription_sync.call(
        task_id=_SHA256_TASK_ID,
        kwargs={
            'park_driver_id': _DRIVER_PROFILE,
            'unsubscribe_reason': _UNSUBSCRIBE_REASON,
        },
    )

    assert (
        _handle_mode_set_cpp_testpoint.times_called == expect_unsubscribe_call
    )


@pytest.mark.now('2020-12-17T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_FEATURES={
        '__default__': {
            'is_exclusive': False,
            'unsubscribe_on_different_profile_online': False,
        },
        'driver_fix': {
            'is_exclusive': False,
            'unsubscribe_on_different_profile_online': True,
        },
    },
)
async def test_different_profile_nogroup_driver_fix(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        stq_runner,
        mockserver,
        mocked_time,
        testpoint,
        pgsql,
):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'UPDATE config.mode_rules SET offers_group_id = null WHERE mode_id = '
        '(SELECT id FROM config.modes WHERE name = \'driver_fix\')',
    )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        assert request.json == {'profile_id_in_set': [_DRIVER_PROFILE]}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': _DRIVER_PROFILE,
                    'data': {'unique_driver_id': 'udid'},
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _v1_profiles(request):
        assert request.json == {'id_in_set': ['udid']}

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
        return {'profiles': [{'unique_driver_id': 'udid', 'data': data}]}

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        driver_data = request.json['driver']
        driver_profile = (
            driver_data['park_id'] + '_' + driver_data['driver_profile_id']
        )
        mode = (
            'driver_fix'
            if driver_profile in ('park-id3_uuid3', 'park-id2_uuid2')
            else 'orders'
        )
        response = common.mode_history_response(request, mode, mocked_time)
        return response

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    await taxi_driver_mode_subscription.invalidate_caches()

    await stq_runner.subscription_sync.call(
        task_id=_SHA256_TASK_ID,
        kwargs={
            'park_driver_id': _DRIVER_PROFILE,
            'unsubscribe_reason': _UNSUBSCRIBE_REASON,
        },
    )

    assert not _handle_mode_set_cpp_testpoint.has_calls
