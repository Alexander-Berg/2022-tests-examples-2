import pytest


def get_tags_request(operation, tag_name, blocked_until=None):
    result = {
        'provider_id': 'callcenter-qa',
        operation: [
            {
                'entity_type': 'dbid_uuid',
                'tags': [
                    {'name': tag_name, 'entity': 'test_park_id_driver_uuid'},
                ],
            },
        ],
    }
    if blocked_until:
        result[operation][0]['tags'][0]['until'] = blocked_until

    return result


@pytest.mark.now('2021-07-16T07:00:00.000000+0000')
@pytest.mark.parametrize(
    ['task_args', 'expected_tags_request'],
    (
        pytest.param(
            {
                'phone_pd_id': 'test_phone_pd_id',
                'tag_name': 'aggressive_driver',
                'operation': 'append',
                'blocked_until': '2021-08-16T07:00:00+0000',
            },
            get_tags_request(
                'append', 'aggressive_driver', '2021-08-16T07:00:00+0000',
            ),
        ),
        pytest.param(
            {
                'phone_pd_id': 'test_phone_pd_id',
                'tag_name': 'aggressive_driver',
                'operation': 'remove',
            },
            get_tags_request('remove', 'aggressive_driver'),
        ),
    ),
)
async def test_base(
        taxi_callcenter_qa,
        task_args,
        expected_tags_request,
        stq_runner,
        testpoint,
        mockserver,
        mock_tags,
        mock_driver_profiles,
):
    @testpoint('tag_status_update::task-finished')
    def handle_finished(data):
        assert data == task_args

    @testpoint('tag_status_update::task-reschedule-in-tags-error')
    def handle_tags_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-driver-profiles-error')
    def handle_driver_profiles_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-error')
    def handle_error_task(data):
        pass

    await stq_runner.callcenter_qa_tag_status_update.call(
        task_id='task_id', kwargs=task_args,
    )

    assert mock_driver_profiles.driver_profiles_retrieve.times_called == 1
    assert mock_tags.tags_upload.times_called == 1

    assert (
        mock_tags.tags_upload.next_call()['request'].json
        == expected_tags_request
    )

    assert handle_finished.times_called == 1
    assert handle_tags_error_task.times_called == 0
    assert handle_driver_profiles_error_task.times_called == 0
    assert handle_error_task.times_called == 0


@pytest.mark.now('2021-07-16T07:00:00.000000+0000')
@pytest.mark.parametrize(
    'task_args',
    (
        pytest.param(
            {
                'phone_pd_id': 'test_phone_pd_id',
                'tag_name': 'aggressive_driver',
                'operation': 'append',
            },
        ),
    ),
)
async def test_miss_blocked_until(
        taxi_callcenter_qa,
        task_args,
        stq_runner,
        testpoint,
        mockserver,
        mock_tags,
        mock_driver_profiles,
):
    @testpoint('tag_status_update::task-finished')
    def handle_finished(data):
        assert data == task_args

    @testpoint('tag_status_update::task-reschedule-in-tags-error')
    def handle_tags_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-driver-profiles-error')
    def handle_driver_profiles_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-error')
    def handle_error_task(data):
        pass

    await stq_runner.callcenter_qa_tag_status_update.call(
        task_id='task_id', kwargs=task_args,
    )

    assert mock_driver_profiles.driver_profiles_retrieve.times_called == 0

    assert handle_finished.times_called == 0
    assert handle_tags_error_task.times_called == 0
    assert handle_driver_profiles_error_task.times_called == 0
    assert handle_error_task.times_called == 1


@pytest.mark.config(
    CALLCENTER_QA_TAG_STATUS_UPDATE_SETTINGS={
        'task_beginning_delay': 0,
        'delay_after_invalid_receiving_driver_profile': 3600,
    },
)
@pytest.mark.now('2021-07-16T07:00:00.000000+0000')
@pytest.mark.parametrize(
    'task_args',
    (
        pytest.param(
            {
                'phone_pd_id': 'test_phone_pd_id',
                'tag_name': 'aggressive_driver',
                'operation': 'append',
                'blocked_until': '2021-08-16T07:00:00+0000',
            },
        ),
    ),
)
async def test_driver_profiles_error(
        taxi_callcenter_qa, task_args, stq_runner, testpoint, mockserver,
):
    @testpoint('tag_status_update::task-finished')
    def handle_finished(data):
        assert data == task_args

    @testpoint('tag_status_update::task-reschedule-in-tags-error')
    def handle_tags_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-driver-profiles-error')
    def handle_driver_profiles_error_task(data):
        assert data == 3600

    @testpoint('tag_status_update::task-reschedule-in-error')
    def handle_error_task(data):
        pass

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone', prefix=True,
    )
    async def _retrieve(request):
        return mockserver.make_response(status=500, json={})

    await stq_runner.callcenter_qa_tag_status_update.call(
        task_id='task_id', kwargs=task_args,
    )

    assert handle_finished.times_called == 0
    assert handle_tags_error_task.times_called == 0
    assert handle_driver_profiles_error_task.times_called == 1
    assert handle_error_task.times_called == 0


@pytest.mark.config(
    CALLCENTER_QA_TAG_STATUS_UPDATE_SETTINGS={
        'task_beginning_delay': 0,
        'delay_after_invalid_assign_tags': 3600,
    },
)
@pytest.mark.now('2021-07-16T07:00:00.000000+0000')
@pytest.mark.parametrize(
    'task_args',
    (
        pytest.param(
            {
                'phone_pd_id': 'test_phone_pd_id',
                'tag_name': 'aggressive_driver',
                'operation': 'append',
                'blocked_until': '2021-08-16T07:00:00+0000',
            },
        ),
    ),
)
async def test_tags_error(
        taxi_callcenter_qa,
        task_args,
        stq_runner,
        testpoint,
        mockserver,
        mock_driver_profiles,
):
    @testpoint('tag_status_update::task-finished')
    def handle_finished(data):
        assert data == task_args

    @testpoint('tag_status_update::task-reschedule-in-tags-error')
    def handle_tags_error_task(data):
        assert data == 3600

    @testpoint('tag_status_update::task-reschedule-in-driver-profiles-error')
    def handle_driver_profiles_error_task(data):
        pass

    @testpoint('tag_status_update::task-reschedule-in-error')
    def handle_error_task(data):
        pass

    @mockserver.json_handler('/tags/v2/upload', prefix=True)
    async def _upload(request):
        raise mockserver.TimeoutError()

    await stq_runner.callcenter_qa_tag_status_update.call(
        task_id='task_id', kwargs=task_args,
    )

    assert handle_finished.times_called == 0
    assert handle_tags_error_task.times_called == 1
    assert handle_driver_profiles_error_task.times_called == 0
    assert handle_error_task.times_called == 0
