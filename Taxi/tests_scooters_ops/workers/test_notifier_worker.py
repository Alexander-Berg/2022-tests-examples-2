import copy

import pytest

from tests_scooters_ops import db_utils


SCOOTERS_OPS_LINKS_CONFIG = {
    'performer_profile': '/show-driver/{park_clid}_{performer_uuid}',
    'cargo_claim': '/corp-claims?claim_id={}',
    'vehicle_info': '/cars/{}/info',
}

PERIODIC_NAME = 'testsuite-notifier-worker'
SIMPLE_MISSION = {
    'mission_id': 'mission1',
    'cargo_claim_id': 'claim_1',
    'performer_id': 'performer_1',
    'status': 'performing',
    'revision': 1,
    'points': [
        {
            'point_id': 'point1',
            'status': 'visited',
            'region_id': 'moscow',
            'type': 'scooter',
            'typed_extra': {
                'scooter': {'id': 'scooter_1', 'number': 'Scooter 1'},
            },
            'cargo_point_id': '123',
            'jobs': [
                {
                    'job_id': 'job1',
                    'type': 'battery_exchange',
                    'status': 'completed',
                    'typed_extra': {},
                },
            ],
        },
        {
            'point_id': 'point2',
            'status': 'skipped',
            'type': 'scooter',
            'region_id': 'spb',
            'typed_extra': {
                'scooter': {'id': 'scooter_2', 'number': 'Scooter 2'},
            },
            'cargo_point_id': '456',
            'comment': 'Не смог',
            'fail_reasons': ['cant_open_deck', 'cant_find_scooter'],
            'jobs': [
                {
                    'job_id': 'job2',
                    'type': 'battery_exchange',
                    'status': 'failed',
                    'typed_extra': {},
                    'comment': 'Не смог',
                    'fail_reasons': ['cant_open_deck', 'cant_find_scooter'],
                },
            ],
        },
    ],
}

DEFAULT_DRIVER_PROFILE = {
    'profiles': [
        {
            'park_driver_profile_id': 'performer_1',
            'data': {
                'full_name': {
                    'first_name': '1',
                    'last_name': 'Performer',
                    'middle_name': 'Name',
                },
                'park_id': 'park_id',
                'uuid': 'performer-uuid',
                'phone_pd_ids': [{'pd_id': 'phone_id'}],
            },
        },
    ],
}

DEFAULT_PARKS_LIST = {
    'parks': [
        {
            'id': 'park_id',
            'login': '',
            'name': '',
            'is_active': True,
            'city_id': '',
            'locale': '',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': '',
            'demo_mode': False,
            'geodata': {'lon': 12.3, 'lat': 45.6, 'zoom': 11},
            'provider_config': {'type': 'none', 'clid': 'park-clid'},
        },
    ],
}


@pytest.mark.parametrize(
    'expected_calls_count',
    [
        pytest.param(
            1,
            id='config enabled',
            marks=pytest.mark.config(
                SCOOTERS_OPS_PERIODICS={
                    'sleep_time_ms': 100,
                    'notifier_worker': {
                        'enabled': True,
                        'sleep_time_ms': 30000,
                    },
                },
            ),
        ),
        pytest.param(
            0,
            id='config disabled',
            marks=pytest.mark.config(
                SCOOTERS_OPS_PERIODICS={
                    'sleep_time_ms': 100,
                    'notifier_worker': {
                        'enabled': False,
                        'sleep_time_ms': 30000,
                    },
                },
            ),
        ),
    ],
)
async def test_with_config(taxi_scooters_ops, expected_calls_count, testpoint):
    @testpoint('notifier-worker-result')
    def notifier_worker_testpoint(data):
        pass

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert notifier_worker_testpoint.times_called == expected_calls_count


async def test_without_config(taxi_scooters_ops, pgsql, testpoint):
    @testpoint('notifier-worker-result')
    def notifier_worker_testpoint(data):
        pass

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert notifier_worker_testpoint.times_called == 0


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
    SCOOTERS_OPS_LINKS=SCOOTERS_OPS_LINKS_CONFIG,
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
async def test_point_skipped_notification(
        taxi_scooters_ops, pgsql, testpoint, mockserver,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1_point1_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        assert request.json['id_in_set'] == ['performer_1']
        assert request.json['projection'] == [
            'data.full_name.first_name',
            'data.full_name.last_name',
            'data.full_name.middle_name',
            'data.park_id',
            'data.uuid',
            'data.phone_pd_ids',
        ]
        return DEFAULT_DRIVER_PROFILE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        assert request.json['query']['park']['ids'] == ['park_id']
        return DEFAULT_PARKS_LIST

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):
        assert (
            request.json['message'] == '<b>Пропуск самоката</b>\n\n'
            'В <a href="/corp-claims?claim_id=claim_1">'
            'заявке</a> пропущен самокат\n'
            'Курьер: <a href="/show-driver/park-clid_performer-uuid">'
            'Performer 1 Name</a>\n'
            'Cамокат: <a href="/cars/scooter_2/info">'
            'Scooter 2</a>\n\n'
            'Комментарий курьера:\n'
            'Не смог\n\n'
            'Причины:\n'
            'cant_open_deck\n'
            'cant_find_scooter\n'
        )

        assert request.json['user_role'] == 'admin'
        assert request.json['send_to_all'] is False
        assert request.json['format'] == 'html'
        assert request.json['regions'] == ['spb']
        return {}

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 1

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission1'], fields=['completed', 'recipients'],
    )
    assert notifications == [
        {
            'completed': True,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': True},
            },
        },
    ]


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
async def test_notification_not_send_twice(
        taxi_scooters_ops, pgsql, testpoint, mockserver,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1_point1_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': True},
            },
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        return {}

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):  # sab == scooter-accumulator-bot
        return {}

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 0

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission1'], fields=['completed', 'recipients'],
    )
    assert notifications == [
        {
            'completed': True,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': True},
            },
        },
    ]


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
    SCOOTERS_OPS_LINKS=SCOOTERS_OPS_LINKS_CONFIG,
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
async def test_notification_sended_with_failed_attempt(
        taxi_scooters_ops, pgsql, testpoint, mockserver,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1_point1_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': False},
            },
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        return {}

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):
        return {}

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 1

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission1'], fields=['completed', 'recipients'],
    )
    assert notifications == [
        {
            'completed': True,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 2, 'sended': True},
            },
        },
    ]


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
    SCOOTERS_OPS_LINKS=SCOOTERS_OPS_LINKS_CONFIG,
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
async def test_when_sab_400(taxi_scooters_ops, pgsql, testpoint, mockserver):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1_point1_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        return {}

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):
        return mockserver.make_response(status=400)

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 1

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission1'], fields=['completed', 'recipients'],
    )
    assert notifications == [
        {
            'completed': False,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': False},
            },
        },
    ]


DEFAULT_FINISHED_MANUALLY = (
    '<a href="/corp-claims?claim_id=claim_1">'
    'Заявка</a> была завершена вручную\n'
    'Курьер: <a href="/show-driver/park-clid_performer-uuid">'
    'Performer 1 Name</a>\n\n'
)


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
    SCOOTERS_OPS_LINKS=SCOOTERS_OPS_LINKS_CONFIG,
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
@pytest.mark.parametrize(
    'jobs, sa_booking_statuses, message_start, message_end',
    [
        pytest.param(
            [
                {
                    'job_id': 'job3',
                    'type': 'pickup_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_1',
                            },
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_2',
                            },
                        ],
                    },
                },
            ],
            ['REVOKED', 'REVOKED'],
            '<b>Успешное ручное завершение</b>\n\n',
            '<b>Отмененные бронирования:</b>\nbooking_1, booking_2\n\n',
            id='pickup_batteries_finished_manually_all_revoked',
        ),
        pytest.param(
            [
                {
                    'job_id': 'job3',
                    'type': 'pickup_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_1',
                            },
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_2',
                            },
                        ],
                    },
                },
            ],
            ['REVOKED', 'IN_PROCESS'],
            '<b>Непредвиденное ручное завершение</b>\n\n',
            '<b>Отмененные бронирования:</b>\n'
            'booking_1\n\n'
            '<b>Бронирования, которые нужно обработать вручную:</b>\n'
            'booking_2',
            id='pickup_batteries_finished_manually_one_revoked_one_in_process',
        ),
        pytest.param(
            [
                {
                    'job_id': 'job3',
                    'type': 'return_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'cells': [
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_1',
                            },
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_2',
                            },
                        ],
                    },
                },
            ],
            None,
            '<b>Непредвиденное ручное завершение</b>\n\n',
            '<b>Бронирования, которые нужно обработать вручную:</b>\n'
            'booking_1, booking_2',
            id='return_batteries_finished_manually',
        ),
        pytest.param(
            [
                {
                    'job_id': 'job3',
                    'type': 'dropoff_vehicles',
                    'status': 'performing',
                    'typed_extra': {'quantity': '3'},
                },
            ],
            None,
            '<b>Успешное ручное завершение</b>\n\n',
            '',
            id='other_jobs_finished_manually',
        ),
        pytest.param(
            [
                {
                    'job_id': 'job4',
                    'type': 'pickup_batteries',
                    'status': 'completed',
                    'typed_extra': {
                        'accumulators': [
                            {
                                'ui_status': 'pickuped',
                                'booking_id': 'booking_3',
                            },
                            {
                                'ui_status': 'pickuped',
                                'booking_id': 'booking_4',
                            },
                        ],
                    },
                },
                {
                    'job_id': 'job3',
                    'type': 'return_batteries',
                    'status': 'performing',
                    'typed_extra': {
                        'cells': [
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_1',
                            },
                            {
                                'ui_status': 'pending',
                                'booking_id': 'booking_2',
                            },
                        ],
                    },
                },
            ],
            None,
            '<b>Непредвиденное ручное завершение</b>\n\n',
            '<b>Бронирования, которые нужно обработать вручную:</b>\n'
            'booking_1, booking_2',
            id='return_batteries_not_first_job_mission_completed_manually',
        ),
    ],
)
async def test_mission_completed_manually_notification(
        taxi_scooters_ops,
        pgsql,
        testpoint,
        mockserver,
        jobs,
        sa_booking_statuses,
        message_start,
        message_end,
):
    mission = copy.deepcopy(SIMPLE_MISSION)
    point3 = {
        'point_id': 'point3',
        'status': 'arrived',
        'region_id': 'spb',
        'type': 'depot',
        'typed_extra': {'scooter': {'id': 'depot_id'}},
        'cargo_point_id': '456',
        'comment': 'Не смог',
        'jobs': jobs,
    }
    mission['points'].append(point3)
    db_utils.add_mission(pgsql, mission)
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1___mission_completed_manually',
            'mission_id': 'mission1',
            'type': 'mission_completed_manually',
            'completed': False,
            'recipients': {},
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        assert request.json['id_in_set'] == ['performer_1']
        assert request.json['projection'] == [
            'data.full_name.first_name',
            'data.full_name.last_name',
            'data.full_name.middle_name',
            'data.park_id',
            'data.uuid',
            'data.phone_pd_ids',
        ]
        return DEFAULT_DRIVER_PROFILE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        assert request.json['query']['park']['ids'] == ['park_id']
        return DEFAULT_PARKS_LIST

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/bookings',
    )
    def _mock_bookings(request):
        assert sa_booking_statuses is not None
        return {
            'bookings': [
                {
                    'booking_id': 'booking_1',
                    'status': sa_booking_statuses[0],
                    'cell_id': 'cell_id',
                    'cabinet_id': 'cabinet_id',
                    'cells_count': 1,
                    'cabinet_type': 'charge_station',
                },
                {
                    'booking_id': 'booking_2',
                    'status': sa_booking_statuses[1],
                    'cell_id': 'cell_id2',
                    'cabinet_id': 'cabinet_id',
                    'cells_count': 1,
                    'cabinet_type': 'charge_station',
                },
            ],
        }

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):
        expected_request = (
            message_start + DEFAULT_FINISHED_MANUALLY + message_end
        )

        assert request.json['message'] == expected_request

        assert request.json['user_role'] == 'admin'
        assert request.json['send_to_all'] is False
        assert request.json['format'] == 'html'
        assert sorted(request.json['regions']) == ['moscow', 'spb']
        return {}

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 1

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission1'], fields=['completed', 'recipients'],
    )
    assert notifications == [
        {
            'completed': True,
            'recipients': {
                'scooter_accumulator_bot': {'attempt': 1, 'sended': True},
            },
        },
    ]


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'notifier_worker': {'enabled': True, 'sleep_time_ms': 30000},
    },
    SCOOTERS_OPS_LINKS=SCOOTERS_OPS_LINKS_CONFIG,
)
@pytest.mark.experiments3(filename='exp3_performers_monitoring.json')
async def test_one_notification_broken(
        taxi_scooters_ops, pgsql, testpoint, mockserver,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'mission1_point1_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
        },
    )
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'fake_mission_point1_job1_job_skipped',
            'mission_id': 'fake_mission',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
        },
    )
    db_utils.add_notification(
        pgsql,
        {
            'idempotency_token': 'second_mission1_point2_job1_job_skipped',
            'mission_id': 'mission1',
            'point_id': 'point2',
            'job_id': 'job2',
            'type': 'job_skipped',
            'completed': False,
            'recipients': {},
        },
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _profiles_retrieve(request):
        return DEFAULT_DRIVER_PROFILE

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _parks_list(request):
        return DEFAULT_PARKS_LIST

    @mockserver.json_handler(
        '/scooter-accumulator-bot/scooter-accumulator-bot/v1/bot/message',
    )
    def mock_sab_client(request):
        return {}

    await taxi_scooters_ops.run_task('testsuite-notifier-worker')

    assert mock_sab_client.times_called == 2

    notifications = db_utils.get_notifications(
        pgsql, fields=['idempotency_token', 'completed'],
    )
    assert notifications == [
        {
            'completed': True,
            'idempotency_token': 'mission1_point1_job1_job_skipped',
        },
        {
            'completed': False,
            'idempotency_token': 'fake_mission_point1_job1_job_skipped',
        },
        {
            'completed': True,
            'idempotency_token': 'second_mission1_point2_job1_job_skipped',
        },
    ]
