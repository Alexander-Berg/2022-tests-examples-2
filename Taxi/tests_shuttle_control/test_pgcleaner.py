# pylint: disable=C5521, W0621
import datetime

from psycopg2.extras import DateTimeRange
import pytest

from tests_shuttle_control.utils import select_named


class AnyDateTime:
    def __eq__(self, other):
        return isinstance(other, datetime.datetime)


@pytest.mark.now('2020-05-28T13:40:55')
@pytest.mark.pgsql(
    'shuttle_control', files=['main.sql', 'workshifts.sql', 'pauses.sql'],
)
async def test_shuttle_archivation(taxi_shuttle_control, pgsql):
    assert (
        await taxi_shuttle_control.post(
            '/service/cron', json={'task_name': 'pgcleaner-stopped-shuttles'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT * FROM archive.routes
        ORDER BY route_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'is_cyclic': False,
            'is_dynamic': False,
            'name': 'main_route',
            'route_id': 1,
            'version': 1,
            'archived_at': AnyDateTime(),
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.route_points
        ORDER BY route_id, point_order
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {'route_id': 1, 'point_id': 1, 'point_order': 1},
        {'route_id': 1, 'point_id': 5, 'point_order': 2},
    ]

    rows = select_named(
        """
        SELECT * FROM archive.points
        ORDER BY point_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {'point_id': 1, 'position': '(30,60)'},
        {'point_id': 5, 'position': '(30,60)'},
    ]

    rows = select_named(
        """
        SELECT * FROM archive.stops
        ORDER BY point_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'stop_id': 1,
            'point_id': 1,
            'name': 'main_stop',
            'ya_transport_stop_id': 'stop__123',
            'archived_at': AnyDateTime(),
            'is_terminal': False,
        },
        {
            'stop_id': 5,
            'point_id': 5,
            'name': 'stop_5',
            'ya_transport_stop_id': 'stop__5',
            'archived_at': AnyDateTime(),
            'is_terminal': True,
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.shuttles
        ORDER BY shuttle_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'capacity': 16,
            'driver_id': '(dbid_0,uuid_0)',
            'ended_at': datetime.datetime(2020, 5, 28, 11, 40, 55),
            'is_fake': False,
            'route_id': 1,
            'shuttle_id': 1,
            'started_at': None,
            'archived_at': AnyDateTime(),
            'work_mode': 'shuttle_fix',
            'scheduled_departure': None,
            'subscription_id': None,
            'view_id': None,
            'vfh_id': None,
            'remaining_pauses': 0,
            'pause_id': 2,
            'pause_state': 'requested',
            'use_external_confirmation_code': False,
        },
        {
            'capacity': 16,
            'driver_id': '(dbid_2,uuid_0)',
            'ended_at': datetime.datetime(2020, 5, 28, 11, 40, 55),
            'is_fake': False,
            'route_id': 1,
            'shuttle_id': 11,
            'started_at': None,
            'archived_at': AnyDateTime(),
            'work_mode': 'shuttle_fix',
            'scheduled_departure': None,
            'subscription_id': 11,
            'view_id': None,
            'vfh_id': None,
            'remaining_pauses': 0,
            'pause_id': None,
            'pause_state': 'inactive',
            'use_external_confirmation_code': False,
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.drivers_workshifts_subscriptions
        ORDER BY subscription_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'archived_at': AnyDateTime(),
            'driver_id': '(dbid_2,uuid_0)',
            'status': 'finished',
            'subscribed_at': datetime.datetime(2019, 9, 14, 10, 15, 16),
            'subscription_id': 11,
            'workshift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.workshifts
        ORDER BY workshift_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'created_at': AnyDateTime(),
            'archived_at': AnyDateTime(),
            'max_simultaneous_subscriptions': 10,
            'personal_goal': None,
            'route_name': 'route1',
            'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'work_time': DateTimeRange(
                datetime.datetime(2020, 9, 14, 10, 30),
                datetime.datetime(2020, 9, 14, 14, 0),
                '[]',
            ),
            'workshift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'max_pauses_allowed': 0,
            'pause_duration': datetime.timedelta(0),
            'simultaneous_pauses_per_shift': 0,
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.bookings
        ORDER BY booking_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'created_at': datetime.datetime(2020, 5, 18, 15, 0),
            'dropoff_stop_id': 5,
            'finished_at': datetime.datetime(2020, 5, 18, 17, 0),
            'pickup_stop_id': 1,
            'shuttle_id': 1,
            'shuttle_lap': 1,
            'status': 'finished',
            'ticket': '0400',
            'user_id': 'user_id_1',
            'yandex_uid': '0123456789',
            'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'app_version': None,
            'app_platform': None,
            'archived_at': AnyDateTime(),
            'cancel_reason': None,
            'origin': 'application',
            'service_origin_id': None,
            'dropoff_lap': 1,
            'processing_type': 'legacy',
            'external_passenger_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.booking_tickets
        ORDER BY booking_id, code
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'status': 'confirmed',
            'code': '0400',
            'archived_at': AnyDateTime(),
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.status_change_time
        ORDER BY booking_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'changed_at': AnyDateTime(),
            'status': 'created',
        },
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'changed_at': AnyDateTime(),
            'status': 'finished',
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.feedbacks
        ORDER BY booking_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'message': 'some_message',
            'choices': ['choice1', 'choice2'],
            'created_at': datetime.datetime(2020, 5, 18, 19, 0, 0),
            'rating_variant_id': None,
            'survey_answers': None,
            'archived_at': AnyDateTime(),
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.matching_offers
        ORDER BY offer_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {
            'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'shuttle_id': 1,
            'order_point_a': '(30,60)',
            'order_point_b': '(31,61)',
            'pickup_stop_id': 1,
            'pickup_lap': 1,
            'dropoff_stop_id': 1,
            'dropoff_lap': 1,
            'price': '(10.0000,RUB)',
            'created_at': datetime.datetime(2020, 1, 17, 18, 0),
            'expires_at': datetime.datetime(2022, 1, 24, 18, 18),
            'archived_at': AnyDateTime(),
            'passengers_count': 1,
            'yandex_uid': '0123456789',
            'route_id': 1,
            'dropoff_timestamp': None,
            'pickup_timestamp': None,
            'suggested_route_view': None,
            'suggested_traversal_plan': None,
            'external_confirmation_code': None,
            'external_passenger_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT * FROM archive.pauses
        ORDER BY pause_id
        """,
        pgsql['shuttle_control'],
    )

    print('rows', rows)

    assert rows == [
        {
            'pause_id': 1,
            'shuttle_id': 1,
            'pause_requested': datetime.datetime(2020, 5, 28, 11, 40, 55),
            'expected_pause_start': None,
            'pause_started': datetime.datetime(2020, 5, 28, 11, 41, 55),
            'expected_pause_finish': None,
            'pause_finished': datetime.datetime(2020, 5, 28, 11, 45, 55),
            'archived_at': AnyDateTime(),
        },
        {
            'pause_id': 2,
            'shuttle_id': 1,
            'pause_requested': datetime.datetime(2020, 5, 28, 12, 40, 55),
            'expected_pause_start': None,
            'pause_started': None,
            'expected_pause_finish': None,
            'pause_finished': None,
            'archived_at': AnyDateTime(),
        },
    ]

    rows = select_named(
        """
        SELECT * FROM state.pauses
        ORDER BY pause_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []


@pytest.mark.now('2020-05-29T13:20:55')
@pytest.mark.pgsql('shuttle_control', files=['main_matches.sql'])
async def test_delete_unused_matching_offers(taxi_shuttle_control, pgsql):
    assert (
        await taxi_shuttle_control.post(
            '/service/cron', json={'task_name': 'pgcleaner-unused-offers'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT * FROM state.matching_offers
        ORDER BY pickup_stop_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'offer_id': '5c76c35b-98df-481c-ac21-0555c5e51d21',
            'yandex_uid': '123456',
            'shuttle_id': 1,
            'route_id': 1,
            'order_point_a': '(30,60)',
            'order_point_b': '(30,60)',
            'pickup_stop_id': 1,
            'pickup_lap': 1,
            'dropoff_stop_id': 2,
            'dropoff_lap': 1,
            'price': '(0.0000,RUB)',
            'passengers_count': 1,
            'created_at': datetime.datetime(2020, 5, 29, 12, 00, 55),
            'expires_at': datetime.datetime(2020, 5, 29, 12, 40, 55),
            'external_confirmation_code': None,
            'external_passenger_id': None,
            'payment_type': None,
            'payment_method_id': None,
            'dropoff_timestamp': None,
            'pickup_timestamp': None,
            'suggested_route_view': None,
            'suggested_traversal_plan': None,
        },
        {
            'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'yandex_uid': '1234562',
            'shuttle_id': 1,
            'route_id': 1,
            'order_point_a': '(30,60)',
            'order_point_b': '(30,60)',
            'pickup_stop_id': 2,
            'pickup_lap': 1,
            'dropoff_stop_id': 3,
            'dropoff_lap': 1,
            'price': '(0.0000,RUB)',
            'passengers_count': 1,
            'created_at': datetime.datetime(2020, 5, 29, 12, 00, 55),
            'expires_at': datetime.datetime(2020, 5, 29, 13, 40, 55),
            'external_confirmation_code': None,
            'external_passenger_id': None,
            'payment_type': None,
            'payment_method_id': None,
            'dropoff_timestamp': None,
            'pickup_timestamp': None,
            'suggested_route_view': None,
            'suggested_traversal_plan': None,
        },
        {
            'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            'yandex_uid': '1234563',
            'shuttle_id': 1,
            'route_id': 1,
            'order_point_a': '(30,60)',
            'order_point_b': '(30,60)',
            'pickup_stop_id': 3,
            'pickup_lap': 1,
            'dropoff_stop_id': 3,
            'dropoff_lap': 2,
            'price': '(0.0000,RUB)',
            'passengers_count': 1,
            'created_at': datetime.datetime(2020, 5, 29, 12, 00, 55),
            'expires_at': datetime.datetime(2020, 5, 29, 13, 40, 55),
            'external_confirmation_code': None,
            'external_passenger_id': None,
            'payment_type': None,
            'payment_method_id': None,
            'dropoff_timestamp': None,
            'pickup_timestamp': None,
            'suggested_route_view': None,
            'suggested_traversal_plan': None,
        },
    ]


@pytest.mark.now('2020-05-29T13:20:55')
@pytest.mark.pgsql('shuttle_control', files=['main_shifts.sql'])
async def test_delete_unused_subscriptions(taxi_shuttle_control, pgsql):
    assert (
        await taxi_shuttle_control.post(
            '/service/cron',
            json={'task_name': 'pgcleaner-unused-subscriptions'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT subscription_id FROM state.drivers_workshifts_subscriptions
        ORDER BY subscription_id
        """,
        pgsql['shuttle_control'],
    )

    assert rows == [
        {'subscription_id': 1},
        {'subscription_id': 2},
        {'subscription_id': 3},
        {'subscription_id': 6},
        {'subscription_id': 7},
    ]


@pytest.mark.now('2020-06-20T13:20:55')
@pytest.mark.pgsql('shuttle_control', files=['main_shifts.sql'])
async def test_delete_past_workshifts(taxi_shuttle_control, pgsql):

    assert (
        await taxi_shuttle_control.post(
            '/service/cron', json={'task_name': 'pgcleaner-past-workshifts'},
        )
    ).status_code == 200

    rows = select_named(
        'SELECT workshift_id FROM config.workshifts', pgsql['shuttle_control'],
    )
    assert rows == [{'workshift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'}]

    rows = select_named(
        """
        SELECT subscription_id FROM state.drivers_workshifts_subscriptions
        ORDER BY subscription_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'subscription_id': 1},
        {'subscription_id': 2},
        {'subscription_id': 3},
        {'subscription_id': 7},
    ]


@pytest.mark.now('2020-06-20T13:20:55')
@pytest.mark.pgsql('shuttle_control', files=['main_shifts.sql'])
async def test_delete_past_templates(taxi_shuttle_control, pgsql):
    assert (
        await taxi_shuttle_control.post(
            '/service/cron', json={'task_name': 'pgcleaner-past-templates'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT template_id FROM config.workshift_templates
        ORDER BY template_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
        {'template_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730776'},
    ]
