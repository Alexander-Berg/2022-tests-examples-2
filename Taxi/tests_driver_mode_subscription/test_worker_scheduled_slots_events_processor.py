# pylint: disable=C0302
# TODO split file

import datetime as dt
from typing import Any
from typing import Dict
import urllib.parse
import uuid

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools

_SLOT_ID_1 = uuid.UUID('a936b353-fcda-4b7a-b569-a7fb855819dd')
_OFFER_IDENTITY_1 = {'slot_id': str(_SLOT_ID_1), 'rule_version': 1}

_SLOT_ID_2 = uuid.UUID('b7ae5704-cbce-4f67-9a72-c128bad3e63f')
_OFFER_IDENTITY_2 = {'slot_id': str(_SLOT_ID_2), 'rule_version': 1}

_SLOT_ID_3 = uuid.UUID('9fc36842-1d90-4b68-b066-c05cd618f3df')
_OFFER_IDENTITY_3 = {'slot_id': str(_SLOT_ID_3), 'rule_version': 1}

_SLOT_ID_4 = uuid.UUID('0d96469a-bf98-4482-8dba-7c8f71860332')
_OFFER_IDENTITY_4 = {'slot_id': str(_SLOT_ID_4), 'rule_version': 1}

_QUOTA_ID = '7463f61d-0d9c-4fad-96e4-a06f33dcc9ab'

_DRIVER_PROFILE_1 = driver.Profile('parkid1_uuid1')
_DRIVER_PROFILE_2 = driver.Profile('parkid2_uuid2')
_DRIVER_PROFILE_3 = driver.Profile('parkid3_uuid3', None, 'en')
_DRIVER_PROFILE_4 = driver.Profile('parkid4_uuid4')


def build_slot_info(
        offer_identity: Dict[str, Any],
        slot_start_time: dt.datetime,
        slot_stop_time: dt.datetime,
):
    return {
        'identity': offer_identity,
        'visibility_info': {
            'invisibility_audit_reasons': ['reason1', 'reason2'],
        },
        'time_range': {
            'begin': slot_start_time.isoformat(),
            'end': slot_stop_time.isoformat(),
        },
        'activation_state': 'waiting',
        'description': {'icon': 'check_ok', 'captions': {}},
        'quota_id': _QUOTA_ID,
        'allowed_transport_types': ['auto'],
        'actions': [{'action_type': 'stop', 'label': 'Stop', 'icon': 'stop'}],
    }


def create_sent_event(
        event_id: str,
        slot_id: uuid.UUID,
        dbid_uuid: driver.Profile,
        message: str,
        icon: str,
        need_deeplink_button: bool,
        need_refresh: bool,
):
    deep_link_mode_settings_str = (
        f'{{"logistic_offer_identity":'
        f'{{"slot_id":"{str(slot_id)}","rule_version":1}}}}'
    )

    deep_link_mode_settings = urllib.parse.quote(deep_link_mode_settings_str)

    expected_deeplink = (
        'taximeter://screen/logistics_shifts/slot_info?'
        f'mode_rule_settings={deep_link_mode_settings}'
    )

    result: Dict[str, Any] = {
        'channel': f'contractor:{dbid_uuid.dbid_uuid()}',
        'event': 'logistics-shift-notification',
        'payload': {
            'actions': [
                {
                    'action_type': 'show_notification',
                    'icon': icon,
                    'message': message,
                },
            ],
            'id': event_id,
        },
        'service': 'yandex.pro',
    }

    if need_deeplink_button:
        result['payload']['actions'][0]['buttons'] = [
            {
                'button_type': 'deeplink',
                'deeplink': expected_deeplink,
                'is_primary': True,
                'label': (
                    'Подробнее' if dbid_uuid.locale() == 'ru' else 'Details'
                ),
            },
        ]

    if need_refresh:
        result['payload']['actions'].append({'action_type': 'refresh'})

    return result


async def logistic_change_offers(
        taxi_driver_mode_subscription, changed, cancelled,
):
    request = {'changed': changed, 'cancelled': cancelled}

    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

    return await taxi_driver_mode_subscription.post(
        'v1/logistic-workshifts/slots/change-offers',
        json=request,
        headers=headers,
    )


@pytest.fixture(name='lsc_metadata_mock')
def _lst_geoarea_by_slot_metadata(mockserver):
    @mockserver.json_handler(
        '/logistic-supply-conductor/'
        'internal/v1/offer/geoarea-by-slot/metadata',
    )
    def _lst_geoarea_by_slot_metadata(request):
        return {
            'polygons': [
                {
                    'timezone': 'Europe/Moscow',
                    'title': (
                        'Метро «Смоленская»'
                        if request.headers['Accept-Language'] == 'ru'
                        else 'Metro «Smolenskaya»'
                    ),
                    'offer_identity': _OFFER_IDENTITY_1,
                },
                {
                    'timezone': 'Europe/Moscow',
                    'title': (
                        'Хамовники'
                        if request.headers['Accept-Language'] == 'ru'
                        else 'Hamovniki'
                    ),
                    'offer_identity': _OFFER_IDENTITY_2,
                },
                {
                    # doesn't have any sense
                    # only for testing timezone localization
                    'timezone': 'Asia/Omsk',
                    'title': (
                        'Текстильщики'
                        if request.headers['Accept-Language'] == 'ru'
                        else 'Tekstilshiki'
                    ),
                    'offer_identity': _OFFER_IDENTITY_3,
                },
            ],
        }


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_EVENTS_PROCESSOR={
        'work_interval_ms': 0,
        'slot_starting_soon_operation': {
            'enabled': True,
            'left_bracket_offset_s': -3599,
            'right_bracket_offset_s': 3601,
            'chunk_size': 1,
            'notification_settings': {
                'message_tanker_key': (
                    'logistics.notifications.slot_starting_soon.message'
                ),
                'icon': 'waiting',
            },
        },
        'reservation_deletion_operation': {
            'enabled': True,
            'delay_s': 5,
            'max_age_m': 120,
            'chunk_size': 1,
            'notification_settings_by_reason': {
                'manual_stop': {
                    'message_tanker_key': (
                        'logistics.notifications.reservation_deletion.message'
                    ),
                    'icon': 'waiting_danger',
                },
            },
        },
        'reservation_creation_operation': {
            'enabled': True,
            'max_age_m': 120,
            'delay_s': 0,
            'chunk_size': 1,
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # should not be notified - start before left bracket
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 4, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 5, 0, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # should be notified
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            'some_mode',
            _OFFER_IDENTITY_2,
            dt.datetime(2020, 4, 4, 5, 00, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
            'some_quota2',
            10,
        ),
        # should be notified
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_3.hex,
            'some_mode',
            _OFFER_IDENTITY_3,
            dt.datetime(2020, 4, 4, 5, 30, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
            'some_quota3',
            10,
        ),
        # should not be notified - start after right bracket
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_4.hex,
            'some_mode',
            _OFFER_IDENTITY_4,
            dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 8, 00, tzinfo=dt.timezone.utc),
            'some_quota4',
            10,
        ),
        # should not be notified - start before left bracket
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_1.hex,
            _DRIVER_PROFILE_1,
            False,
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_1,
        ),
        # should be notified
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_2.hex,
            _DRIVER_PROFILE_2,
            False,
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_2,
        ),
        # should be notified
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_3.hex,
            _DRIVER_PROFILE_3,
            False,
            created_at=dt.datetime(
                2020, 4, 4, 4, 0, 0, tzinfo=dt.timezone.utc,
            ),
            accepted_mode_settings=_OFFER_IDENTITY_3,
        ),
        # should not be notified - start after right bracket
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_4.hex,
            _DRIVER_PROFILE_2,
            False,
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_4,
        ),
        # should not be notified - inside bracket, but deleted
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_2.hex,
            _DRIVER_PROFILE_4,
            True,
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_2,
        ),
        # should be notified, deleted slot with delay
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_1.hex,
            _DRIVER_PROFILE_1,
            is_deleted=True,
            deletion_reason='manual_stop',
            updated_ts=dt.datetime(
                2020, 4, 4, 4, 59, 54, 499999, tzinfo=dt.timezone.utc,
            ),
            created_at=dt.datetime(
                2020, 4, 4, 3, 59, 54, 499999, tzinfo=dt.timezone.utc,
            ),
            accepted_mode_settings=_OFFER_IDENTITY_1,
        ),
        # should not be notified, deleted slot at now
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_2.hex,
            _DRIVER_PROFILE_1,
            is_deleted=True,
            updated_ts=dt.datetime(
                2020, 4, 4, 5, 00, 00, tzinfo=dt.timezone.utc,
            ),
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_2,
        ),
        # should not be notified, deleted in past
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_2.hex,
            _DRIVER_PROFILE_1,
            is_deleted=True,
            updated_ts=dt.datetime(
                2020, 4, 4, 3, 00, 00, tzinfo=dt.timezone.utc,
            ),
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),  # do not log creation
            accepted_mode_settings=_OFFER_IDENTITY_2,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_events_processor(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        lsc_metadata_mock,
):
    scenario.Scene.mock_driver_trackstory(
        mockserver, driver_position=scenario.MOSCOW_POSITION,
    )
    scene = scenario.Scene(
        profiles={
            _DRIVER_PROFILE_3: driver.Mode('some_mode'),
            _DRIVER_PROFILE_1: driver.Mode('some_mode'),
            _DRIVER_PROFILE_2: driver.Mode('some_mode'),
            _DRIVER_PROFILE_4: driver.Mode('some_mode'),
        },
    )
    scene.setup(mockserver, mocked_time, mock_driver_profiles=True)

    @testpoint('scheduled-slots-events-processor-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint('scheduled-slots-events-processor-client-event')
    def event_testpoint(data):
        pass

    collected_logs = []

    @testpoint('yt_logger_logistic_workshifts_reservations')
    def _yt_logger(data_json):
        collected_logs.append(data_json)

    @mockserver.json_handler('/client-events/push')
    def client_events_push(request):
        return {'version': '1.1234'}

    def get_sent_events(event_testpoint):
        events = []
        while event_testpoint.has_calls:
            event = event_testpoint.next_call()['data']
            events.append(
                f'{event["slot_name"]}_'
                f'{event["park_id"]}_'
                f'{event["driver_profile_id"]}_'
                f'{event["event_type"]}',
            )

        return events

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    events_first_iter = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 2

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    events_second_iter = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 3

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    events_third_iter = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 3

    assert len(events_first_iter) == 3
    assert len(events_second_iter) == 2
    assert not events_third_iter

    expected_events = set(
        [
            (
                f'{_SLOT_ID_2.hex}_'
                f'{_DRIVER_PROFILE_2.park_id()}_'
                f'{_DRIVER_PROFILE_2.profile_id()}_'
                'starting_soon'
            ),
            (
                f'{_SLOT_ID_3.hex}_'
                f'{_DRIVER_PROFILE_3.park_id()}_'
                f'{_DRIVER_PROFILE_3.profile_id()}_'
                'starting_soon'
            ),
            (
                f'{_SLOT_ID_1.hex}_'
                f'{_DRIVER_PROFILE_1.park_id()}_'
                f'{_DRIVER_PROFILE_1.profile_id()}_'
                'reservation_deletion'
            ),
            (
                f'{_SLOT_ID_3.hex}_'
                f'{_DRIVER_PROFILE_3.park_id()}_'
                f'{_DRIVER_PROFILE_3.profile_id()}_'
                'reservation_creation'
            ),
            (
                f'{_SLOT_ID_1.hex}_'
                f'{_DRIVER_PROFILE_1.park_id()}_'
                f'{_DRIVER_PROFILE_1.profile_id()}_'
                'reservation_creation'
            ),
        ],
    )

    actual_events = set(events_first_iter + events_second_iter)

    assert actual_events == expected_events

    actual_sent_events = []
    while client_events_push.has_calls:
        actual_sent_events.append(
            client_events_push.next_call()['request'].json,
        )

    assert len(actual_sent_events) == 3

    actual_sent_events.sort(key=lambda slot: (slot['payload']['id']))

    expected_sent_events = [
        create_sent_event(
            '1e767b3f7afd1edad84fa2e0b30aae2bd4b0a465496a2d58d328a2ef94f18aeb',
            _SLOT_ID_2,
            _DRIVER_PROFILE_2,
            'Скоро начнётся слот: Хамовники, 08:00―10:00',
            icon='waiting',
            need_deeplink_button=True,
            need_refresh=False,
        ),
        create_sent_event(
            '6201b093825fbace2211cc5e5a2e81e37477322ed244fecdd5ab4fa183e6dfcc',
            _SLOT_ID_1,
            _DRIVER_PROFILE_1,
            'Слот отменен: Метро «Смоленская», 07:00―08:00',
            icon='waiting_danger',
            need_deeplink_button=False,
            need_refresh=True,
        ),
        create_sent_event(
            '79fde5131cd60916416420688024e5ffcd8755a5c38cf5e7299aa0a8799b4f44',
            _SLOT_ID_3,
            _DRIVER_PROFILE_3,
            # MSK: 08:30―10:00, translated to Omsk timezone
            'Slot starting soon: Tekstilshiki, 11:30―13:00',
            icon='waiting',
            need_deeplink_button=True,
            need_refresh=False,
        ),
    ]

    assert actual_sent_events == expected_sent_events

    assert (
        sorted(
            collected_logs,
            key=lambda doc: (
                doc['reservation_id'],
                1 if doc['canceled_at'] is None else 2,
            ),
        )
        == [
            {
                'dbid': _DRIVER_PROFILE_3.park_id(),
                'uuid': _DRIVER_PROFILE_3.profile_id(),
                'offer_identity': _OFFER_IDENTITY_3,
                'reserved_at': '2020-04-04T04:00:00.000000+0000',
                'canceled_at': None,
                'cancelation_reason': None,
                'reservation_id': 3,
            },
            {
                'dbid': _DRIVER_PROFILE_1.park_id(),
                'uuid': _DRIVER_PROFILE_1.profile_id(),
                'offer_identity': _OFFER_IDENTITY_1,
                'reserved_at': '2020-04-04T03:59:54.499999+0000',
                'canceled_at': None,
                'cancelation_reason': None,
                'reservation_id': 6,
            },
            {
                'dbid': _DRIVER_PROFILE_1.park_id(),
                'uuid': _DRIVER_PROFILE_1.profile_id(),
                'offer_identity': _OFFER_IDENTITY_1,
                'reserved_at': None,
                'canceled_at': '2020-04-04T04:59:54.499999+0000',
                'cancelation_reason': 'manual_stop',
                'reservation_id': 6,
            },
        ]
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS={
        'slot_change_delay_s': 60,
        'allowed_time_before_start_s': 1,
        'enabled_push_subscription_event': True,
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 4, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 5, 0, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # should be notified
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            'some_mode',
            _OFFER_IDENTITY_2,
            dt.datetime(2020, 4, 4, 5, 00, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
            'some_quota2',
            10,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_1.hex, _DRIVER_PROFILE_1, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_2.hex, _DRIVER_PROFILE_1, False,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_resubscription_events(
        pgsql,
        mocked_time,
        mockserver,
        mode_rules_data,
        mode_geography_defaults,
        stq_runner,
        lsc_metadata_mock,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='some_mode',
                    features={'logistic_workshifts': {}},
                ),
            ],
        ),
    )

    with pgsql['driver_mode_subscription'].cursor() as cursor:
        cursor.execute(
            saga_tools.make_insert_saga_query(
                _DRIVER_PROFILE_1.park_id(),
                _DRIVER_PROFILE_1.profile_id(),
                next_mode='some_mode',
                next_mode_timepoint='2020-04-05 12:00:00+01',
                next_mode_settings=_OFFER_IDENTITY_2,
                prev_mode='some_mode',
                prev_mode_timepoint='2020-04-05 12:00:00+01',
                prev_mode_settings=_OFFER_IDENTITY_1,
            ),
        )

    @mockserver.json_handler(
        r'/(logistic-supply-conductor/internal/v1/courier/)(?P<name>.+)',
        regex=True,
    )
    def _handlers_mock(request, name):
        return {}

    @mockserver.json_handler('/client-events/push')
    def client_events_push(request):
        return {'version': '1.1234'}

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/info/list',
    )
    def _slot_info_list_handler(request):
        slots = []

        for offer_identity, start_time, stop_time in [
                (
                    _OFFER_IDENTITY_1,
                    dt.datetime(2020, 4, 4, 4, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2020, 4, 4, 5, 0, tzinfo=dt.timezone.utc),
                ),
                (
                    _OFFER_IDENTITY_2,
                    dt.datetime(2020, 4, 4, 5, 00, tzinfo=dt.timezone.utc),
                    dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
                ),
        ]:
            slot = {
                'info': build_slot_info(offer_identity, start_time, stop_time),
            }
            slots.append(slot)

        return {'slots': slots}

    scene = scenario.Scene(
        profiles={_DRIVER_PROFILE_1: driver.Mode('some_mode')},
    )
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, _DRIVER_PROFILE_1)

    assert client_events_push.times_called == 1
    assert client_events_push.has_calls

    actual_event = client_events_push.next_call()['request'].json

    expected_event = create_sent_event(
        '77046440da56d3648b2b91e473f967c521788662edb02bc1b7dedba4cc31d6cc',
        _SLOT_ID_2,
        _DRIVER_PROFILE_1,
        'Закончен слот: Метро «Смоленская», 07:00―08:00\n'
        'Слот начался: Хамовники, 08:00―10:00',
        icon='waiting',
        need_deeplink_button=True,
        need_refresh=False,
    )

    assert actual_event == expected_event


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_EVENTS_PROCESSOR={
        'work_interval_ms': 0,
        'slot_starting_soon_operation': {
            'enabled': False,
            'left_bracket_offset_s': -3599,
            'right_bracket_offset_s': 3601,
            'chunk_size': 1,
        },
        'slot_changed_operation': {
            'enabled': True,
            'left_bracket_offset_s': -3599,
            'chunk_size': 1,
            'notification_settings': {
                'message_tanker_key': (
                    'logistics.notifications.slot_changed.message'
                ),
                'icon': 'waiting',
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 10, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 10, 0, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
            _DRIVER_PROFILE_1.park_id(),
            _DRIVER_PROFILE_1.profile_id(),
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_events_processor_slot_changed(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):
    scenario.Scene.mock_driver_trackstory(
        mockserver, driver_position=scenario.MOSCOW_POSITION,
    )
    scene = scenario.Scene(
        profiles={_DRIVER_PROFILE_1: driver.Mode('some_mode')},
    )
    scene.setup(mockserver, mocked_time, mock_driver_profiles=True)

    # Test case for bug fixed in EFFICIENCYDEV-16242
    # Simulate case when new offer_identity was requested
    # and lsc returned 404 error
    @mockserver.json_handler(
        '/logistic-supply-conductor/'
        'internal/v1/offer/geoarea-by-slot/metadata',
    )
    def _lst_geoarea_metadata(request):
        should_fail = any(
            offer_identity == _OFFER_IDENTITY_2
            for offer_identity in request.json['offer_identities']
        )
        if should_fail:
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'ERROR'},
            )

        return {
            'polygons': [
                {
                    'timezone': 'Europe/Moscow',
                    'title': (
                        'Метро «Смоленская»'
                        if request.headers['Accept-Language'] == 'ru'
                        else 'Metro «Smolenskaya»'
                    ),
                    'offer_identity': _OFFER_IDENTITY_1,
                },
            ],
        }

    await logistic_change_offers(
        taxi_driver_mode_subscription,
        [
            {
                'slot_id': str(_SLOT_ID_1),
                'new_offer_info': {
                    'identity': _OFFER_IDENTITY_2,
                    'time_range': {
                        'begin': '2020-04-04T10:00:00+00:00',
                        'end': '2020-04-04T12:00:00+00:00',
                    },
                },
            },
        ],
        [],
    )

    @testpoint('scheduled-slots-events-processor-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint('scheduled-slots-events-processor-client-event')
    def event_testpoint(data):
        pass

    @mockserver.json_handler('/client-events/push')
    def client_events_push(request):
        return {'version': '1.1234'}

    def get_sent_events(event_testpoint):
        events = []
        while event_testpoint.has_calls:
            event = event_testpoint.next_call()['data']
            events.append(
                f'{event["slot_name"]}_'
                f'{event["park_id"]}_'
                f'{event["driver_profile_id"]}_'
                f'{event["event_type"]}',
            )

        return events

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    actual_events = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 1

    expected_event = (
        f'{_SLOT_ID_2.hex}_'
        f'{_DRIVER_PROFILE_1.park_id()}_'
        f'{_DRIVER_PROFILE_1.profile_id()}_'
        'slot_changed'
    )

    assert actual_events == [expected_event]

    sent_events = []
    while client_events_push.has_calls:
        sent_events.append(client_events_push.next_call()['request'].json)

    assert len(sent_events) == 1

    sent_events.sort(key=lambda slot: (slot['payload']['id']))

    assert sent_events == [
        create_sent_event(
            '51a5eae0df5fd9080b4acffe068e40ff04e31749263105bf3a9385168fbbbaee',
            # Since EFFICIENCYDEV-16242
            # We are using accepted_mode_settings in notification,
            # so, we expect to have old slot_id here
            _SLOT_ID_1,
            _DRIVER_PROFILE_1,
            'Изменились условия работы слота: Метро «Смоленская», 13:00―15:00',
            icon='waiting',
            need_deeplink_button=True,
            need_refresh=True,
        ),
    ]

    # Check that event will be send after subsequent changes

    await logistic_change_offers(
        taxi_driver_mode_subscription,
        [
            {
                'slot_id': str(_SLOT_ID_2),
                'new_offer_info': {
                    'identity': _OFFER_IDENTITY_3,
                    'time_range': {
                        'begin': '2020-04-04T10:00:00+00:00',
                        'end': '2020-04-04T12:00:00+00:00',
                    },
                },
            },
        ],
        [],
    )

    client_events_push.flush()

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    actual_events = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 1

    # do not check content of push here - no need for that

    # check that no more sends made
    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()

    actual_events = get_sent_events(event_testpoint)

    assert actual_events == []


@pytest.mark.parametrize(
    'should_fail', (pytest.param([True]), pytest.param([False])),
)
async def test_worker_events_processor_errors_metric(
        taxi_driver_mode_subscription,
        testpoint,
        mockserver,
        taxi_driver_mode_subscription_monitor,
        should_fail,
):
    @testpoint('scheduled-slots-events-processor-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint(
        'scheduled-slots-events-processor-worker-testpoint-error-injection',
    )
    def _error_injection_testpoint(data):
        return {'inject_failure': True}

    metrics_before = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-events-processor',
    )

    if should_fail:
        with pytest.raises(taxi_driver_mode_subscription.TestsuiteTaskFailed):
            await taxi_driver_mode_subscription.run_distlock_task(
                'scheduled-slots-events-processor',
            )
    else:
        await taxi_driver_mode_subscription.run_distlock_task(
            'scheduled-slots-events-processor',
        )

    await worker_testpoint.wait_call()

    metrics_after = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-events-processor',
    )

    expected_successes = 0 if should_fail else 1
    expected_errors = 1 if should_fail else 0

    assert (
        expected_successes
        == metrics_after['successes'] - metrics_before['successes']
    )
    assert (
        expected_errors == metrics_after['errors'] - metrics_before['errors']
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_EVENTS_PROCESSOR={
        'work_interval_ms': 0,
        'slot_starting_soon_operation': {
            'enabled': True,
            'left_bracket_offset_s': -3599,
            'right_bracket_offset_s': 3601,
            'chunk_size': 1,
            'notification_settings': {
                'message_tanker_key': (
                    'logistics.notifications.slot_starting_soon.message'
                ),
                'icon': 'waiting',
            },
        },
        'reservation_deletion_operation': {
            'enabled': True,
            'delay_s': 5,
            'max_age_m': 120,
            'chunk_size': 1,
            'notification_settings_by_reason': {
                'manual_stop': {
                    'message_tanker_key': (
                        'logistics.notifications.reservation_deletion.message'
                    ),
                    'icon': 'waiting_danger',
                },
            },
        },
        'reservation_creation_operation': {
            'enabled': True,
            'max_age_m': 120,
            'delay_s': 0,
            'chunk_size': 1,
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # should not be notified - start before left bracket
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 4, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 5, 0, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # should be notified, deleted slot with delay
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_1.hex,
            _DRIVER_PROFILE_1,
            is_deleted=True,
            deletion_reason='manual_stop',
            updated_ts=dt.datetime(
                2020, 4, 4, 4, 59, 54, 499999, tzinfo=dt.timezone.utc,
            ),
            created_at=dt.datetime(
                2020, 4, 4, 3, 59, 54, 499999, tzinfo=dt.timezone.utc,
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_yt_logging_when_everything_fails(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        mode_rules_data,
):
    scenario.Scene.mock_driver_trackstory(mockserver, driver_position=None)
    scene = scenario.Scene(
        profiles={
            _DRIVER_PROFILE_3: driver.Mode('some_mode'),
            _DRIVER_PROFILE_1: driver.Mode('some_mode'),
            _DRIVER_PROFILE_2: driver.Mode('some_mode'),
            _DRIVER_PROFILE_4: driver.Mode('some_mode'),
        },
    )
    scene.setup(mockserver, mocked_time, mock_driver_profiles=False)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_profiles(request):
        raise mockserver.NetworkError()

    @mockserver.json_handler(
        '/logistic-supply-conductor/'
        'internal/v1/offer/geoarea-by-slot/metadata',
    )
    def _lst_geoarea_by_slot_metadata(request):
        raise mockserver.NetworkError()

    @testpoint('scheduled-slots-events-processor-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint('scheduled-slots-events-processor-client-event')
    def event_testpoint(data):
        pass

    collected_logs = []

    @testpoint('yt_logger_logistic_workshifts_reservations')
    def _yt_logger(data_json):
        collected_logs.append(data_json)

    @mockserver.json_handler('/client-events/push')
    def client_events_push(request):
        raise mockserver.NetworkError()

    def get_sent_events(event_testpoint):
        events = []
        while event_testpoint.has_calls:
            event = event_testpoint.next_call()['data']
            events.append(
                f'{event["slot_name"]}_'
                f'{event["park_id"]}_'
                f'{event["driver_profile_id"]}_'
                f'{event["event_type"]}',
            )

        return events

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    events_first_iter = get_sent_events(event_testpoint)

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-events-processor',
    )
    await worker_testpoint.wait_call()
    events_second_iter = get_sent_events(event_testpoint)

    assert client_events_push.times_called == 0

    assert not events_first_iter + events_second_iter

    assert (
        sorted(
            collected_logs,
            key=lambda doc: (
                doc['reservation_id'],
                1 if doc['canceled_at'] is None else 2,
            ),
        )
        == [
            {
                'dbid': _DRIVER_PROFILE_1.park_id(),
                'uuid': _DRIVER_PROFILE_1.profile_id(),
                'offer_identity': _OFFER_IDENTITY_1,
                'reserved_at': '2020-04-04T03:59:54.499999+0000',
                'canceled_at': None,
                'cancelation_reason': None,
                'reservation_id': 1,
            },
            {
                'dbid': _DRIVER_PROFILE_1.park_id(),
                'uuid': _DRIVER_PROFILE_1.profile_id(),
                'offer_identity': _OFFER_IDENTITY_1,
                'reserved_at': None,
                'canceled_at': '2020-04-04T04:59:54.499999+0000',
                'cancelation_reason': 'manual_stop',
                'reservation_id': 1,
            },
        ]
    )


@pytest.mark.parametrize(
    'should_fail, pg_fail_count',
    (
        pytest.param(True, 5, id='Fail after attempts'),
        pytest.param(False, 3, id='Success after attempts'),
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_EVENTS_PROCESSOR={
        'work_interval_ms': 0,
        'slot_starting_soon_operation': {
            'enabled': True,
            'left_bracket_offset_s': -3599,
            'right_bracket_offset_s': 3601,
            'chunk_size': 1,
            'notification_settings': {
                'message_tanker_key': (
                    'logistics.notifications.slot_starting_soon.message'
                ),
                'icon': 'waiting',
            },
        },
        'save_processed_events_settings': {
            'save_to_db_attempts': 5,
            'save_to_db_retry_ms': 0,
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # should be notified
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 5, 00, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 7, 00, tzinfo=dt.timezone.utc),
            'some_quota2',
            10,
        ),
        # should be notified
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_1.hex,
            _DRIVER_PROFILE_1,
            False,
            created_at=dt.datetime(
                2020, 4, 4, 1, 0, 0, tzinfo=dt.timezone.utc,
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_events_processor_pg_retry(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        mode_rules_data,
        lsc_metadata_mock,
        taxi_driver_mode_subscription_monitor,
        should_fail: bool,
        pg_fail_count: int,
):
    scenario.Scene.mock_driver_trackstory(
        mockserver, driver_position=scenario.MOSCOW_POSITION,
    )
    scene = scenario.Scene(
        profiles={_DRIVER_PROFILE_1: driver.Mode('some_mode')},
    )
    scene.setup(mockserver, mocked_time, mock_driver_profiles=True)

    @testpoint('scheduled-slots-events-processor-worker-testpoint')
    def worker_testpoint(data):
        pass

    @mockserver.json_handler('/client-events/push')
    def _client_events_push(request):
        return {'version': '1.1234'}

    pg_fail_attempt = 0

    @testpoint('scheduled-slots-events-processor-postgre-error-injection')
    def _error_injection_testpoint(data):
        nonlocal pg_fail_attempt
        nonlocal pg_fail_count

        pg_fail_attempt += 1
        return {'inject_failure': pg_fail_attempt <= pg_fail_count}

    metrics_before = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-events-processor',
    )

    if should_fail:
        with pytest.raises(taxi_driver_mode_subscription.TestsuiteTaskFailed):
            await taxi_driver_mode_subscription.run_distlock_task(
                'scheduled-slots-events-processor',
            )
    else:
        await taxi_driver_mode_subscription.run_distlock_task(
            'scheduled-slots-events-processor',
        )

    await worker_testpoint.wait_call()

    metrics_after = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-events-processor',
    )

    warnings = metrics_after['warnings'] - metrics_before['warnings']

    events_records = scheduled_slots_tools.get_processed_events(pgsql)

    assert bool(events_records) == (not should_fail)

    assert warnings == pg_fail_count - (1 if should_fail else 0)
