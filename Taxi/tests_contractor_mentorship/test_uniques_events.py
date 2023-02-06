import pytest


MENTORSHIP_ID_1 = (
    b'01',
    b'newbie_udid_01',
    b'newbie_dbid_uuid_01',
    b'bad_status_01',
    b'mentor_udid_01',
    b'mentor_dbid_uuid_01',
)

MENTORSHIP_ID_3 = (
    b'03',
    b'newbie_udid_03',
    b'newbie_dbid_uuid_03',
    b'in_progress',
    b'mentor_udid_03',
    b'mentor_dbid_uuid_03',
)

MENTORSHIP_ID_4 = (
    b'04',
    b'newbie_udid_04',
    b'newbie_dbid_uuid_04',
    b'matched',
    b'mentor_udid_04',
    b'mentor_dbid_uuid_04',
)

MENTORSHIP_ID_6 = (
    b'06',
    b'newbie_udid_06',
    b'newbie_dbid_uuid_06',
    b'requested',
    None,
    None,
)

MENTORSHIP_ID_7 = (
    b'07',
    b'newbie_udid_07',
    b'newbie_dbid_uuid_07',
    b'requested',
    None,
    None,
)

STOPPED_MENTORSHIP_ID_2 = (
    b'02',
    b'newbie_udid_02',
    b'newbie_dbid_uuid_02',
    b'stopped_not_newbie',
    None,
    None,
)

STOPPED_MENTORSHIP_ID_4 = (
    b'04',
    b'newbie_udid_04',
    b'newbie_dbid_uuid_04',
    b'stopped_not_newbie',
    b'mentor_udid_04',
    b'mentor_dbid_uuid_04',
)

CONFIG = {
    '__default__': {
        '__default__': {
            'logs-enabled': False,
            'is-enabled': False,
            'sleep-ms': 5000,
        },
    },
    'contractor-mentorship': {
        '__default__': {
            'logs-enabled': True,
            'is-enabled': True,
            'sleep-ms': 10,
        },
    },
}


def get_mentorships_by_udids(udid1, udid2, ydb):
    return ydb.execute(
        f'SELECT id, newbie_unique_driver_id, newbie_park_driver_profile_id, '
        'status, mentor_unique_driver_id, mentor_park_driver_profile_id '
        'FROM mentorships '
        'WHERE newbie_unique_driver_id IN ("{}", "{}") OR '
        'mentor_unique_driver_id IN ("{}", "{}") '
        'ORDER BY id;'.format(udid1, udid2, udid1, udid2),
    )


def check_for_equality(mentorships, expected_mentorships):
    assert len(mentorships) == 1
    assert len(mentorships[0].rows) == len(expected_mentorships)
    for [mentorship, expected_mentorship] in zip(
            mentorships[0].rows, expected_mentorships,
    ):
        assert mentorship['id'] == expected_mentorship[0]
        assert mentorship['newbie_unique_driver_id'] == expected_mentorship[1]
        assert (
            mentorship['newbie_park_driver_profile_id']
            == expected_mentorship[2]
        )
        assert mentorship['status'] == expected_mentorship[3]
        assert mentorship['mentor_unique_driver_id'] == expected_mentorship[4]
        assert (
            mentorship['mentor_park_driver_profile_id']
            == expected_mentorship[5]
        )


@pytest.mark.config(UNIQUE_DRIVERS_SERVICES_CONSUMERS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'event_type, secondary_unique_driver',
    [('divide', 'decoupled_unique_driver'), ('merge', 'merged_unique_driver')],
)
async def test_contractor_mentorship_handle_uniques_event_task_creation(
        taxi_contractor_mentorship,
        logbroker_helper,
        testpoint,
        stq,
        event_type,
        secondary_unique_driver,
):
    @testpoint(
        'contractor-mentorship-uniques-{}-events::ProcessMessage'.format(
            event_type,
        ),
    )
    def processed(data):
        # pylint: disable=unused-variable
        pass

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    lb_helper = logbroker_helper(taxi_contractor_mentorship)

    lb_message = {
        'producer': {'source': 'admin', 'login': 'login'},
        'unique_driver': {
            'id': 'unique_driver_id',
            'park_driver_profile_ids': [
                {'id': 'pid1_dpid1'},
                {'id': 'pid2_dpid2'},
            ],
        },
        secondary_unique_driver: {
            'id': 'decoupled_unique_driver_id',
            'park_driver_profile_ids': [{'id': 'pid3_dpid3'}],
        },
    }

    await lb_helper.send_json(
        'uniques-{}-events'.format(event_type),
        lb_message,
        topic='/taxi/unique-drivers/testing/uniques-{}-events'.format(
            event_type,
        ),
        cookie='cookie',
    )

    async with taxi_contractor_mentorship.spawn_task(
            'contractor-mentorship-uniques-{}-events'.format(event_type),
    ):
        await commit.wait_call()

    stq.contractor_mentorship_handle_uniques_event.times_called == 1

    kwargs = stq.contractor_mentorship_handle_uniques_event.next_call()[
        'kwargs'
    ]
    del kwargs['log_extra']

    assert kwargs == {
        'main_unique_driver': {
            'id': 'unique_driver_id',
            'park_driver_profile_ids': ['pid1_dpid1', 'pid2_dpid2'],
        },
        'secondary_unique_driver': {
            'id': 'decoupled_unique_driver_id',
            'park_driver_profile_ids': ['pid3_dpid3'],
        },
        'uniques_event_type': 'uniques_{}_events'.format(event_type),
    }


@pytest.mark.config(CONTRACTOR_MENTORSHIP_HANDLING_UNIQUES_EVENTS_ENABLED=True)
@pytest.mark.parametrize(
    'kwargs, expected_mentorships, expected_message',
    [
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_01',
                    'park_driver_profile_ids': [],
                },
                'secondary_unique_driver': {
                    'id': 'new_newbie_udid_01',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_01'],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [MENTORSHIP_ID_1],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_01',
                    'park_driver_profile_ids': [],
                },
                'secondary_unique_driver': {
                    'id': 'new_mentor_udid_01',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_01',
                        'mentor_dbid_uuid_02',
                    ],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                MENTORSHIP_ID_1,
                (
                    b'02',
                    b'newbie_udid_02',
                    b'newbie_dbid_uuid_02',
                    b'bad_status_02',
                    b'mentor_udid_01',
                    b'mentor_dbid_uuid_02',
                ),
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
                },
                'secondary_unique_driver': {
                    'id': 'new_newbie_udid_03',
                    'park_driver_profile_ids': [
                        'newbie_dbid_uuid_03',
                        'newbie_dbid_uuid_04',
                    ],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'03',
                    b'new_newbie_udid_03',
                    b'newbie_dbid_uuid_03',
                    b'created',
                    None,
                    None,
                ),
            ],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_03',
                'new_unique_driver_id': 'new_newbie_udid_03',
                'send_push': False,
            },
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': [
                        'newbie_dbid_uuid_02',
                        'newbie_dbid_uuid_03',
                    ],
                },
                'secondary_unique_driver': {
                    'id': 'new_newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'03',
                    b'newbie_udid_03',
                    b'newbie_dbid_uuid_03',
                    b'created',
                    None,
                    None,
                ),
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': [],
                },
                'secondary_unique_driver': {
                    'id': 'new_mentor_udid_04',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_04',
                        'mentor_dbid_uuid_05',
                    ],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'04',
                    b'newbie_udid_04',
                    b'newbie_dbid_uuid_04',
                    b'in_progress',
                    b'new_mentor_udid_04',
                    b'mentor_dbid_uuid_04',
                ),
                (
                    b'05',
                    b'newbie_udid_05',
                    b'newbie_dbid_uuid_05',
                    b'bad_status_03',
                    b'new_mentor_udid_04',
                    b'mentor_dbid_uuid_05',
                ),
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_03',
                        'mentor_dbid_uuid_04',
                    ],
                },
                'secondary_unique_driver': {
                    'id': 'new_mentor_udid_04',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_05'],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'04',
                    b'newbie_udid_04',
                    b'newbie_dbid_uuid_04',
                    b'in_progress',
                    b'mentor_udid_04',
                    b'mentor_dbid_uuid_04',
                ),
                (
                    b'05',
                    b'newbie_udid_05',
                    b'newbie_dbid_uuid_05',
                    b'bad_status_03',
                    b'new_mentor_udid_04',
                    b'mentor_dbid_uuid_05',
                ),
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_06',
                    'park_driver_profile_ids': [],
                },
                'secondary_unique_driver': {
                    'id': 'new_mentor_udid_06',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_06',
                        'mentor_dbid_uuid_07',
                        'mentor_dbid_uuid_08',
                    ],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'06',
                    b'newbie_udid_06',
                    b'newbie_dbid_uuid_06',
                    b'in_progress',
                    b'new_mentor_udid_06',
                    b'mentor_dbid_uuid_06',
                ),
                (
                    b'07',
                    b'newbie_udid_07',
                    b'newbie_dbid_uuid_07',
                    b'failed',
                    b'new_mentor_udid_06',
                    b'mentor_dbid_uuid_07',
                ),
                (
                    b'08',
                    b'newbie_udid_08',
                    b'newbie_dbid_uuid_08',
                    b'matched',
                    b'new_mentor_udid_06',
                    b'mentor_dbid_uuid_08',
                ),
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_06',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_08',
                        'mentor_dbid_uuid_09',
                    ],
                },
                'secondary_unique_driver': {
                    'id': 'new_mentor_udid_06',
                    'park_driver_profile_ids': [
                        'mentor_dbid_uuid_06',
                        'mentor_dbid_uuid_07',
                    ],
                },
                'uniques_event_type': 'uniques_divide_events',
            },
            [
                (
                    b'06',
                    b'newbie_udid_06',
                    b'newbie_dbid_uuid_06',
                    b'in_progress',
                    b'new_mentor_udid_06',
                    b'mentor_dbid_uuid_06',
                ),
                (
                    b'07',
                    b'newbie_udid_07',
                    b'newbie_dbid_uuid_07',
                    b'failed',
                    b'new_mentor_udid_06',
                    b'mentor_dbid_uuid_07',
                ),
                (
                    b'08',
                    b'newbie_udid_08',
                    b'newbie_dbid_uuid_08',
                    b'matched',
                    b'mentor_udid_06',
                    b'mentor_dbid_uuid_08',
                ),
            ],
            None,
        ),
    ],
)
@pytest.mark.ydb(files=['uniques_divide_events.sql'])
async def test_uniques_divide_events(
        testpoint,
        stq_runner,
        ydb,
        kwargs,
        expected_mentorships,
        expected_message,
):
    @testpoint('yt-logger-uniques-event')
    def yt_logger_uniques_event(message):
        del message['created_at']
        del message['timestamp']
        assert message == expected_message

    await stq_runner.contractor_mentorship_handle_uniques_event.call(
        task_id='task_id', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert yt_logger_uniques_event.times_called == bool(expected_message)

    mentorships = get_mentorships_by_udids(
        kwargs['main_unique_driver']['id'],
        kwargs['secondary_unique_driver']['id'],
        ydb,
    )

    check_for_equality(mentorships, expected_mentorships)


@pytest.mark.config(CONTRACTOR_MENTORSHIP_HANDLING_UNIQUES_EVENTS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_uniques_merge_events_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'newbie_not_matched': True,
        'newbie_wo_orders_or_mentor_w_first_communication': True,
        'mentor_wo_first_communication': True,
    },
    clauses=[],
)
@pytest.mark.parametrize(
    'kwargs, has_finished, expected_mentorships, expected_message',
    [
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_01',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_01'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_02',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [MENTORSHIP_ID_1, STOPPED_MENTORSHIP_ID_2],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_02',
                'new_unique_driver_id': 'newbie_udid_01',
                'send_push': True,
                'status': 'failed_merge_unique',
            },
            id='!driver.role; merged_driver=newbie_w/_orders_w/o_mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_02',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_01',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_01'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [MENTORSHIP_ID_1, STOPPED_MENTORSHIP_ID_2],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_01',
                'new_unique_driver_id': 'newbie_udid_02',
                'send_push': True,
                'status': 'failed_merge_unique',
            },
            id='!merged_driver.role; driver=newbie_w/_orders_w/o_mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                (
                    b'03',
                    b'newbie_udid_00',
                    b'newbie_dbid_uuid_03',
                    b'in_progress',
                    b'mentor_udid_03',
                    b'mentor_dbid_uuid_03',
                ),
            ],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_03',
                'new_unique_driver_id': 'newbie_udid_00',
                'send_push': False,
            },
            id='!driver.role; merged_driver=newbie_w/_orders_and_mentor_w/_first_communication',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [MENTORSHIP_ID_3],
            None,
            id='!merged_driver.role; driver=newbie_w/_orders_and_mentor_w/_first_communication',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_04',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [STOPPED_MENTORSHIP_ID_4],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_04',
                'new_unique_driver_id': 'newbie_udid_00',
                'send_push': True,
                'status': 'failed_merge_unique',
            },
            id='!driver.role; merged_driver=newbie_w/_orders_and_mentor_w/o_first_communication',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_04',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_04'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [STOPPED_MENTORSHIP_ID_4],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_00',
                'new_unique_driver_id': 'newbie_udid_04',
                'send_push': True,
                'status': 'failed_merge_unique',
            },
            id='!merged_driver.role; driver=newbie_w/_orders_and_mentor_w/o_first_communication',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_02',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            False,
            [
                (
                    b'02',
                    b'newbie_udid_00',
                    b'newbie_dbid_uuid_02',
                    b'requested',
                    None,
                    None,
                ),
            ],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_02',
                'new_unique_driver_id': 'newbie_udid_00',
                'send_push': False,
            },
            id='!driver.role; merged_driver=newbie_w/o_orders',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            False,
            [MENTORSHIP_ID_3],
            None,
            id='!merged_driver.role; driver=newbie_w/o_orders',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_00',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'mentor_udid_03',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_03'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                (
                    b'03',
                    b'newbie_udid_03',
                    b'newbie_dbid_uuid_03',
                    b'in_progress',
                    b'mentor_udid_00',
                    b'mentor_dbid_uuid_03',
                ),
            ],
            None,
            id='!driver.role; merged_driver=mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_03',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_03'],
                },
                'secondary_unique_driver': {
                    'id': 'mentor_udid_01',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_01'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            False,
            [MENTORSHIP_ID_1, MENTORSHIP_ID_3],
            None,
            id='!merged_driver.role; driver=mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_03',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_03'],
                },
                'secondary_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                MENTORSHIP_ID_3,
                (
                    b'04',
                    b'newbie_udid_04',
                    b'newbie_dbid_uuid_04',
                    b'matched',
                    b'mentor_udid_03',
                    b'mentor_dbid_uuid_04',
                ),
            ],
            None,
            id='driver=mentor; merged_driver=mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_04'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_02',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            False,
            [STOPPED_MENTORSHIP_ID_2, MENTORSHIP_ID_4],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_02',
                'new_unique_driver_id': 'mentor_udid_04',
                'send_push': True,
                'status': 'failed_merge_unique',
            },
            id='driver=mentor; merged_driver=newbie_w/o_mentor',
        ),
        pytest.param(
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
                },
                'secondary_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                MENTORSHIP_ID_3,
                (
                    b'04',
                    b'newbie_udid_04',
                    b'newbie_dbid_uuid_04',
                    b'matched',
                    b'newbie_udid_03',
                    b'mentor_dbid_uuid_04',
                ),
            ],
            None,
            id='driver=newbie_w/_mentor_w/_first_communication; merged_driver=mentor',
        ),
    ],
)
@pytest.mark.ydb(files=['uniques_merge_events.sql'])
async def test_uniques_merge_events(
        testpoint,
        mockserver,
        stq_runner,
        ydb,
        kwargs,
        has_finished,
        expected_mentorships,
        expected_message,
):
    @testpoint('yt-logger-uniques-event')
    def yt_logger_uniques_event(message):
        del message['created_at']
        del message['timestamp']
        assert message == expected_message

    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def has_finished_response(request):
        return mockserver.make_response(
            status=200, json={'has_finished': has_finished},
        )

    await stq_runner.contractor_mentorship_handle_uniques_event.call(
        task_id='task_id', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert yt_logger_uniques_event.times_called == bool(expected_message)

    mentorships = get_mentorships_by_udids(
        kwargs['main_unique_driver']['id'],
        kwargs['secondary_unique_driver']['id'],
        ydb,
    )

    check_for_equality(mentorships, expected_mentorships)


@pytest.mark.config(CONTRACTOR_MENTORSHIP_HANDLING_UNIQUES_EVENTS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_uniques_merge_events_settings',
    consumers=['contractor-mentorship'],
    clauses=[
        {
            'value': {
                'newbie_not_matched': True,
                'newbie_wo_orders_or_mentor_w_first_communication': True,
                'mentor_wo_first_communication': False,
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'country_id',
                    'value': 'rus',
                },
            },
        },
        {
            'value': {
                'newbie_not_matched': False,
                'newbie_wo_orders_or_mentor_w_first_communication': True,
                'mentor_wo_first_communication': False,
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'country_id',
                    'value': 'gha',
                },
            },
        },
    ],
    default_value={
        'newbie_not_matched': False,
        'newbie_wo_orders_or_mentor_w_first_communication': False,
        'mentor_wo_first_communication': False,
    },
)
@pytest.mark.parametrize(
    'kwargs, has_finished, expected_mentorships, expected_message',
    [
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_03',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                (
                    b'03',
                    b'newbie_udid_00',
                    b'newbie_dbid_uuid_03',
                    b'in_progress',
                    b'mentor_udid_03',
                    b'mentor_dbid_uuid_03',
                ),
            ],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_03',
                'new_unique_driver_id': 'newbie_udid_00',
                'send_push': False,
            },
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_04',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [MENTORSHIP_ID_4],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_05',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_05'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [
                (
                    b'05',
                    b'newbie_udid_00',
                    b'newbie_dbid_uuid_05',
                    b'in_progress',
                    b'mentor_udid_05',
                    b'mentor_dbid_uuid_05',
                ),
            ],
            {
                'role': 'newbie',
                'old_unique_driver_id': 'newbie_udid_05',
                'new_unique_driver_id': 'newbie_udid_00',
                'send_push': False,
            },
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_06',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_06'],
                },
                'secondary_unique_driver': {
                    'id': 'mentor_udid_04',
                    'park_driver_profile_ids': ['mentor_dbid_uuid_04'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            False,
            [
                (
                    b'04',
                    b'newbie_udid_04',
                    b'newbie_dbid_uuid_04',
                    b'matched',
                    b'newbie_udid_06',
                    b'mentor_dbid_uuid_04',
                ),
                MENTORSHIP_ID_6,
            ],
            None,
        ),
        (
            {
                'main_unique_driver': {
                    'id': 'newbie_udid_07',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_07'],
                },
                'secondary_unique_driver': {
                    'id': 'newbie_udid_00',
                    'park_driver_profile_ids': ['newbie_dbid_uuid_00'],
                },
                'uniques_event_type': 'uniques_merge_events',
            },
            True,
            [MENTORSHIP_ID_7],
            None,
        ),
    ],
)
@pytest.mark.ydb(files=['uniques_merge_events.sql'])
async def test_experiment_uniques_merge_events_settings(
        testpoint,
        mockserver,
        stq_runner,
        ydb,
        kwargs,
        has_finished,
        expected_mentorships,
        expected_message,
):
    @testpoint('yt-logger-uniques-event')
    def yt_logger_uniques_event(message):
        del message['created_at']
        del message['timestamp']
        assert message == expected_message

    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def has_finished_response(request):
        return mockserver.make_response(
            status=200, json={'has_finished': has_finished},
        )

    await stq_runner.contractor_mentorship_handle_uniques_event.call(
        task_id='task_id', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert yt_logger_uniques_event.times_called == bool(expected_message)

    mentorships = get_mentorships_by_udids(
        kwargs['main_unique_driver']['id'],
        kwargs['secondary_unique_driver']['id'],
        ydb,
    )

    check_for_equality(mentorships, expected_mentorships)


@pytest.mark.parametrize('handling_uniques_events_enabled', (True, False))
@pytest.mark.ydb(files=['uniques_merge_events.sql'])
async def test_two_newbies_uniques_merge(
        testpoint,
        stq_runner,
        ydb,
        taxi_config,
        handling_uniques_events_enabled,
):
    taxi_config.set(
        CONTRACTOR_MENTORSHIP_HANDLING_UNIQUES_EVENTS_ENABLED=handling_uniques_events_enabled,
    )

    kwargs = {
        'main_unique_driver': {
            'id': 'newbie_udid_02',
            'park_driver_profile_ids': ['newbie_dbid_uuid_02'],
        },
        'secondary_unique_driver': {
            'id': 'newbie_udid_03',
            'park_driver_profile_ids': ['newbie_dbid_uuid_03'],
        },
        'uniques_event_type': 'uniques_merge_events',
    }

    expected_mentorships = get_mentorships_by_udids(
        kwargs['main_unique_driver']['id'],
        kwargs['secondary_unique_driver']['id'],
        ydb,
    )
    assert len(expected_mentorships) == 1
    expected_mentorships = expected_mentorships[0].rows

    @testpoint('yt-logger-uniques-event')
    def yt_logger_uniques_event(message):
        pass

    await stq_runner.contractor_mentorship_handle_uniques_event.call(
        task_id='task_id',
        args=[],
        kwargs=kwargs,
        expect_fail=handling_uniques_events_enabled,
    )

    assert yt_logger_uniques_event.times_called == 0

    mentorships = get_mentorships_by_udids(
        kwargs['main_unique_driver']['id'],
        kwargs['secondary_unique_driver']['id'],
        ydb,
    )

    check_for_equality(mentorships, expected_mentorships)
