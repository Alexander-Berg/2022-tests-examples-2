import pytest


@pytest.fixture(name='mock_driver_tags_v1_match_profile')
def _mock_driver_tags_v1_match_profile(mockserver):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock(request):
        return mockserver.make_response(
            status=200, json={'tags': ['eats_courier_from_region_1']},
        )


@pytest.fixture(name='mock_client_notify_push')
def _mock_client_notify_push(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def _mock(request):
        return {'notification_id': '1'}


@pytest.fixture(name='mock_get_locale_driver_profiles')
async def _mock_get_locale_driver_profiles(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock(request):
        if request.json['id_in_set'] == 'EXTERNAL-ID':
            return {
                'profiles': [
                    {
                        'park_driver_profile_id': 'EXTERNAL-ID',
                        'data': {'locale': 'en'},
                    },
                ],
            }
        return None


@pytest.fixture(name='tags_mock')
def _tags_mock(mockserver):
    class Context:
        def __init__(self):
            self.tags = {}
            self.times_called = 0

        def add_tags(self, dbid_uuid, tags):
            self.tags[dbid_uuid] = tags

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _assign(request):
        context.times_called += 1
        if context.tags:
            tags = [
                {'name': dbid_uuid, 'type': 'dbid_uuid', 'tags': tags}
                for dbid_uuid, tags in context.tags.items()
            ]
            assert tags == request.json['entities']
            return {}

        # unexpected behavior
        assert False
        return {}

    setattr(context, 'assign', _assign)
    return context


NOW = '2021-09-10T12:00:00+03:00'


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['fill_data_for_check_base_path.sql'],
)
async def test_set_quality_control_in_db(
        stq_runner, pgsql, mock_driver_tags_v1_match_profile,
):
    await stq_runner.eats_performer_shifts_events.call(
        task_id='test_happy_set_control_in_db',
        kwargs={
            'shift_event': 'started',
            'shift_id': '1',
            'performer_id': '1',
        },
    )

    cursor = pgsql['eda_couriers_schedule'].cursor()

    cursor.execute(
        """
        SELECT
            *
        FROM
            "performer_quality_controls";
    """,
    )

    row = cursor.fetchone()
    assert row[1] == '1'  # performer_id
    assert row[2] == 'some_control'  # control_type


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'eda_couriers_schedule',
    files=['fill_data_for_check_not_time_to_new_task.sql'],
)
async def test_check_data_time_in_quality_control(
        stq_runner, stq, mock_driver_tags_v1_match_profile,
):
    await stq_runner.eats_performer_shifts_events.call(
        task_id='test_not_time',
        kwargs={
            'shift_event': 'started',
            'shift_id': '1',
            'performer_id': '1',
        },
    )

    assert stq.eats_performer_shifts_quality_control_events.times_called == 0


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql(
    'eda_couriers_schedule',
    files=['fill_data_for_check_in_time_to_create_new_task.sql'],
)
async def test_create_new_stq_task(
        stq_runner, stq, mock_driver_tags_v1_match_profile,
):
    await stq_runner.eats_performer_shifts_events.call(
        task_id='test_create_new_task',
        kwargs={
            'shift_event': 'started',
            'shift_id': '1',
            'performer_id': '1',
        },
    )

    assert stq.eats_performer_shifts_quality_control_events.times_called == 1

    next_call = stq.eats_performer_shifts_quality_control_events.next_call()
    assert next_call['queue'] == 'eats_performer_shifts_quality_control_events'
    assert next_call['kwargs']['shift_id'] == '1'
    assert next_call['kwargs']['performer_id'] == '1'
    assert next_call['kwargs']['control_type'] == 'some_control'


@pytest.mark.now(NOW)
@pytest.mark.experiments3(
    filename='eats_performer_shifts_quality_control.json',
)
@pytest.mark.pgsql(
    'eda_couriers_schedule',
    files=['fill_data_for_check_not_right_control_type.sql'],
)
async def test_not_right_control(
        stq_runner, pgsql, mock_driver_tags_v1_match_profile,
):
    await stq_runner.eats_performer_shifts_quality_control_events.call(
        task_id='test_not_right_control',
        kwargs={
            'control_type': 'some_control',
            'shift_id': '1',
            'performer_id': '1',
        },
    )

    cursor = pgsql['eda_couriers_schedule'].cursor()

    cursor.execute(
        """
        SELECT
            *
        FROM
            "performer_quality_controls";
    """,
    )

    assert len(cursor.fetchall()) == 1


@pytest.fixture(name='call')
async def _get_courier_from_msk(mockserver):
    @mockserver.json_handler('/taxi-qc-exams-admin/qc-admin/v1/call')
    def _mock_handler(request):
        body = request.json

        if body == {
                'entity_id': 'EXTERNAL_ID',
                'entity_type': 'driver',
                'exam': 'some_other_control',
                'identity': {
                    'script': {
                        'name': 'eats_performer_shifts_quality_control_events',
                        'id': 'test_not_right_control',
                    },
                },
        }:
            return {}

        assert False
        return None


@pytest.mark.now(NOW)
@pytest.mark.experiments3(
    filename='eats_performer_shifts_quality_control.json',
)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['fill_data_to_send_request.sql'],
)
async def test_request_to_quality_control(
        stq_runner,
        call,
        mock_driver_tags_v1_match_profile,
        mock_client_notify_push,
        mock_get_locale_driver_profiles,
):
    await stq_runner.eats_performer_shifts_quality_control_events.call(
        task_id='test_not_right_control',
        kwargs={
            'control_type': 'some_other_control',
            'shift_id': '1',
            'performer_id': '1',
        },
    )


@pytest.mark.now(NOW)
@pytest.mark.experiments3(
    filename='experiments3_shifts_account_thresholds.json',
)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['fill_data_to_check_stopped_event.sql'],
)
async def test_update_courier_count_shifts(
        stq_runner, call, mock_driver_tags_v1_match_profile, pgsql,
):
    await stq_runner.eats_performer_shifts_events.call(
        task_id='check_courier_shifts_counter_1',
        kwargs={
            'shift_event': 'stopped',
            'shift_id': '1',
            'performer_id': '1',
        },
    )
    await stq_runner.eats_performer_shifts_events.call(
        task_id='check_courier_shifts_counter_2',
        kwargs={
            'shift_event': 'stopped',
            'shift_id': '2',
            'performer_id': '2',
        },
    )

    cursor = pgsql['eda_couriers_schedule'].cursor()

    cursor.execute(
        """
        SELECT
            total_shifts
        FROM
            "courier_shifts_counters";
    """,
    )
    shift_counters = cursor.fetchall()
    assert shift_counters[0][0] == 1
    assert shift_counters[1][0] == 4


@pytest.mark.experiments3(
    filename='experiments3_eats_performer_shifts_shift_start_tags.json',
)
@pytest.mark.pgsql(
    'eda_couriers_schedule', files=['eats_performer_shifts_shift_tags.sql'],
)
@pytest.mark.parametrize(
    'shift_id, tags_data',
    [
        pytest.param(
            '1',
            {
                'driver_id': 'EXTERNAL_ID',
                'tags': {'eats_priority_plan_couriers': {'ttl': 60}},
            },
            id='config matched, assign start tags',
        ),
        pytest.param('2', None, id='config didn\'t match'),
        pytest.param(
            '3',
            {'driver_id': 'EXTERNAL_ID_3', 'tags': {}},
            id='config matched, clear tags',
        ),
        pytest.param('4', None, id='shift doesn\'t exist'),
    ],
)
async def test_eats_performer_shifts_shift_tags(
        stq_runner,
        tags_mock,
        mock_driver_tags_v1_match_profile,
        tags_data,
        shift_id,
):

    if tags_data:
        tags_mock.add_tags(tags_data['driver_id'], tags_data['tags'])

    await stq_runner.eats_performer_shifts_shift_tags.call(
        task_id='task_id', kwargs={'shift_id': shift_id},
    )

    assert tags_mock.times_called == (1 if tags_data else 0)
