# pylint: disable=unused-variable
import pytest

COMPLETED_STATUS = 'completed'
IN_PROGRESS_STATUS = 'in_progress'


@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_mission_completion_lbkx_enabled.json')
@pytest.mark.parametrize(
    'stq_kwargs',
    [
        pytest.param(
            {
                'completions': 1,
                'event_id': 'event_id1',
                'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                'is_fully_completed': True,
                'log_extra': {'_link': ''},
                'stage_id': 'stage1',
                'version': 1,
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'notification_payload': {'client_id': 'client1'},
            },
            id='cfg_locale_enabled',
        ),
        pytest.param(
            {
                'completions': 1,
                'event_id': 'event_id1',
                'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                'is_fully_completed': True,
                'log_extra': {'_link': ''},
                'stage_id': 'stage1',
                'version': 1,
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'notification_payload': {'client_id': 'client1'},
            },
            id='cfg_enabled',
        ),
        pytest.param(
            {
                'completions': 1,
                'event_id': 'event_id1',
                'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                'is_fully_completed': True,
                'log_extra': {'_link': ''},
                'stage_id': 'stage1',
                'version': 1,
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'notification_payload': {'client_id': 'client1'},
            },
            id='all_disabled',
        ),
    ],
)
async def test_send_notifications_throw_completion_notify(
        taxi_cashback_levels, stq_runner, stq_kwargs, stq, testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    task_id = f'{stq_kwargs["task_description_id"]}/{stq_kwargs["event_id"]}'
    await stq_runner.cashback_levels_mission_completion_notify.call(
        task_id=task_id, kwargs=stq_kwargs,
    )

    assert stq.cashback_levels_send_mission_notifications.times_called == 1

    next_call = stq.cashback_levels_send_mission_notifications.next_call()
    assert next_call['queue'] == 'cashback_levels_send_mission_notifications'
    assert (
        next_call['id'] == f'send-push/{stq_kwargs["task_description_id"]}/'
        f'{stq_kwargs["event_id"]}'
    )
    assert (
        next_call['kwargs']['task_description_id']
        == stq_kwargs['task_description_id']
    )
    assert next_call['kwargs']['yandex_uid'] == stq_kwargs['yandex_uid']
    assert (
        next_call['kwargs']['notification_payload']
        == stq_kwargs['notification_payload']
    )


@pytest.mark.parametrize(
    ('is_cfg_enabled', 'stq_kwargs', 'event_id'),
    [
        pytest.param(
            True,
            {
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'mission_status': COMPLETED_STATUS,
                'notification_payload': {
                    'client_id': 'client1',
                    'locale': 'en',
                    'device_id': '',
                    'app_install_id': '',
                    'service': 'go',
                },
            },
            '1',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_tasks_notifications.json',
                ),
            ),
            id='cfg_locale_enabled_silent',
        ),
        pytest.param(
            True,
            {
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'mission_status': COMPLETED_STATUS,
                'notification_payload': {
                    'client_id': 'client1',
                    'device_id': '',
                    'app_install_id': 'some_app_install_id',
                    'locale': '',
                    'service': 'go',
                },
            },
            '12',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_tasks_notifications.json',
                ),
            ),
            id='cfg_enabled_silent',
        ),
        pytest.param(
            True,
            {
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'mission_status': IN_PROGRESS_STATUS,
                'notification_payload': {
                    'client_id': 'client1',
                    'locale': 'en',
                    'device_id': '',
                    'app_install_id': '',
                    'service': 'go',
                },
            },
            '1',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_tasks_notifications.json',
                ),
            ),
            id='cfg_locale_enabled_not_silent',
        ),
        pytest.param(
            False,
            {
                'task_description_id': 'task1_level1',
                'yandex_uid': '111',
                'mission_status': IN_PROGRESS_STATUS,
                'notification_payload': {
                    'client_id': 'client1',
                    'locale': '',
                    'device_id': 'some_device_id',
                    'app_install_id': '',
                    'service': 'go',
                },
            },
            '123',
            id='all_disabled',
        ),
    ],
)
async def test_send_notifications_stq_ok(
        taxi_cashback_levels,
        stq_runner,
        is_cfg_enabled,
        stq_kwargs,
        event_id,
        mockserver,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def _handle(request):
        req_json = request.json
        req_locale = req_json.get('locale', None)
        req_ntf = req_json.get('notification', None)
        req_data = req_json.get('data', None)
        req_meta = req_json.get('meta', None)
        is_final = req_data.get('is_final', None)

        kwargs_locale = stq_kwargs['notification_payload'].get('locale', None)
        kwargs_app_install_id = stq_kwargs['notification_payload'].get(
            'app_install_id', None,
        )
        kwargs_device_id = stq_kwargs['notification_payload'].get(
            'device_id', None,
        )
        kwargs_mission_status = stq_kwargs['mission_status']

        assert req_data
        assert req_meta
        assert is_final is not None

        assert 'some_data' in req_data.keys()
        assert 'some_meta' in req_meta.keys()

        if not kwargs_app_install_id:
            assert 'app_install_id' not in req_json.keys()
        if not kwargs_device_id:
            assert 'device_id' not in req_json.keys()

        if kwargs_mission_status == COMPLETED_STATUS:
            assert is_final
            assert req_ntf
            assert req_ntf.get('title')
            assert req_ntf.get('text')

            if not kwargs_locale:
                assert req_locale == 'ru'
            else:
                assert req_locale == kwargs_locale
        else:
            assert not is_final
            assert not req_ntf
            assert not req_locale

        return mockserver.make_response(json={'notification_id': '123id'})

    task_id = f'send-push/{stq_kwargs["task_description_id"]}/{event_id}'
    await stq_runner.cashback_levels_send_mission_notifications.call(
        task_id=task_id, kwargs=stq_kwargs, expect_fail=False,
    )

    client_notify_times_called = 1 if is_cfg_enabled else 0

    assert _handle.times_called == client_notify_times_called
