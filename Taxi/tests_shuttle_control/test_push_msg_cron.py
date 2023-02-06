# pylint: disable=import-error
# pylint: disable=import-only-modules
import copy
import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

from tests_shuttle_control.utils import select_named

ROUTER = {
    '30.010000,60.010000': 120,
    '30.080000,60.080000': 140,
    '30.100000,60.100000': 600,
    '30.110000,60.110000': 110,
    '30.060000,60.060000': 45,
    '30.020000,60.020000': 55,
}

USERS_ARRIVING = {
    'user_id_1': {'locale': 'ru'},
    'user_id_3': {'locale': 'en'},
    'user_id_9': {'locale': 'ru_1'},
}

USERS_ARRIVING_OUT_OF_WORKSHIFT = {
    'user_id_1': {'locale': 'ru'},
    'user_id_2': {'locale': 'en'},
    'user_id_9': {'locale': 'ru_1'},
}

USERS_FINISHING = {
    'user_id_11': {'locale': 'ru_2'},
    'user_id_22': {'locale': 'ru_3'},
}

SPECIAL_TEXTS = {
    'ru': {'title': 'Специальный Тайтл!', 'text': 'Специальный Текст!'},
}

TEXTS = {
    'ru': {'title': 'Тайтл!', 'text': 'Текст!'},
    'en': {'title': 'Title!', 'text': 'Text!'},
}

ARRIVING_INTENT = 'shuttle.arriving'

FINISHING_INTENT = 'shuttle.finishing'


def make_push_msg(title, text, locale, intent):
    return {
        'data': {
            'payload': {},
            'repack': {
                'apns': {
                    'aps': {
                        'alert': {'body': text, 'title': title},
                        'content-available': 1,
                    },
                },
                'fcm': {'notification': {'body': text, 'title': title}},
                'hms': {'notification': {'body': text, 'title': title}},
            },
        },
        'intent': intent,
        'locale': locale,
    }


PUSH_MSG = {
    'ru_1': make_push_msg(
        SPECIAL_TEXTS['ru']['title'],
        SPECIAL_TEXTS['ru']['text'],
        'ru',
        ARRIVING_INTENT,
    ),
    'ru': make_push_msg(
        TEXTS['ru']['title'], TEXTS['ru']['text'], 'ru', ARRIVING_INTENT,
    ),
    'en': make_push_msg(
        TEXTS['en']['title'], TEXTS['en']['text'], 'en', ARRIVING_INTENT,
    ),
    'ru_2': make_push_msg(
        TEXTS['ru']['title'], TEXTS['ru']['text'], 'ru', FINISHING_INTENT,
    ),
    'ru_3': make_push_msg(
        TEXTS['en']['title'], TEXTS['en']['text'], 'en', FINISHING_INTENT,
    ),
}


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


@pytest.mark.now('2020-05-28T11:40:05')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.translations(
    client_messages={
        'push_msg_title': {'ru': 'Тайтл!', 'en': 'Title!'},
        'push_msg_text': {'ru': 'Текст!', 'en': 'Text!'},
        'push_title.special': {
            'ru': 'Специальный Тайтл!',
            'en': 'Special Title!',
        },
        'push_text.special': {
            'ru': 'Специальный Текст!',
            'en': 'Special Text!',
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_push_config.json')
async def test_cron_simple(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    user_arriveng = USERS_ARRIVING.copy()

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        request_data = json.loads(request.get_data())
        user_id = request_data['user']
        user_locale = user_arriveng[user_id]['locale']
        expected_data = copy.deepcopy(PUSH_MSG[user_locale])
        expected_data['user'] = user_id
        assert request_data == expected_data
        user_arriveng.pop(user_id)
        return {}

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.001,
                        'lat': 60.001,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.052,
                        'lat': 60.052,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 30.05,
                        'lat': 60.05,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
                {
                    'position': {
                        'lon': 30.095,
                        'lat': 60.095,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid4_uuid4',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        rlls = request.args['rll'].split('~')
        time = ROUTER[str(rlls[-1])]
        return mockserver.make_response(
            response=_proto_driving_summary(time, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    cron_request = {'task_name': 'push-messages-worker/shuttle.arriving'}
    await taxi_shuttle_control.post('/service/cron', cron_request)
    assert _mock_ucommunications.has_calls
    assert _mock_router.has_calls
    assert not user_arriveng.keys()

    rows = select_named(
        'SELECT booking_id FROM state.communications ' 'ORDER BY booking_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'booking_id': '2c76c53b-98aa-481c-ac21-0555c5e51d10'},
        {'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
        {'booking_id': '5c76c35b-98df-481c-ac21-0555c5e51d21'},
        {'booking_id': '7c76c53b-98bb-481c-ac21-0555c5e51d10'},
    ]


@pytest.mark.now('2019-09-14T09:58:00+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.translations(
    client_messages={
        'push_msg_title': {'ru': 'Тайтл!', 'en': 'Title!'},
        'push_msg_text': {'ru': 'Текст!', 'en': 'Text!'},
        'push_title.special': {
            'ru': 'Специальный Тайтл!',
            'en': 'Special Title!',
        },
        'push_text.special': {
            'ru': 'Специальный Текст!',
            'en': 'Special Text!',
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_push_config.json')
@pytest.mark.parametrize('must_skip_user_id_1', [True, False])
async def test_cron_simple_out_of_workshift(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        experiments3,
        must_skip_user_id_1,
        driver_trackstory_v2_shorttracks,
):
    user_arriveng = USERS_ARRIVING_OUT_OF_WORKSHIFT.copy()
    if must_skip_user_id_1:
        user_arriveng.pop('user_id_1')

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': True},
        clauses=[],
    )

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        request_data = json.loads(request.get_data())
        user_id = request_data['user']
        user_locale = user_arriveng[user_id]['locale']
        expected_data = copy.deepcopy(PUSH_MSG[user_locale])
        expected_data['user'] = user_id
        assert request_data == expected_data
        user_arriveng.pop(user_id)
        return {}

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.001,
                        'lat': 60.001,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.052,
                        'lat': 60.052,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 30.05,
                        'lat': 60.05,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
                {
                    'position': {
                        'lon': 30.095,
                        'lat': 60.095,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid4_uuid4',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        rlls = request.args['rll'].split('~')
        return mockserver.make_response(
            response=_proto_driving_summary(30 * (len(rlls) - 1), 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.communications
        SET created_at = '2019-09-14T09:00:00+0000'
        """,
    )

    if must_skip_user_id_1:
        pgsql['shuttle_control'].cursor().execute(
            """
            UPDATE config.workshifts
            SET work_time = '[2019-09-14 10:05, 2019-09-14 18:00]'::TSRANGE
            WHERE workshift_id = '427a330d-2506-464a-accf-346b31e288b1'
            """,
        )

    cron_request = {'task_name': 'push-messages-worker/shuttle.arriving'}
    await taxi_shuttle_control.post('/service/cron', cron_request)
    assert _mock_ucommunications.has_calls
    assert _mock_router.has_calls
    assert not user_arriveng.keys()

    rows = select_named(
        'SELECT booking_id FROM state.communications ' 'ORDER BY booking_id',
        pgsql['shuttle_control'],
    )
    expected_rows = [
        {'booking_id': '2c76c53b-98aa-481c-ac21-0555c5e51d10'},  # user_id_9
        {'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},  # user_id_1
        {'booking_id': '427a330d-2506-464a-accf-346b31e288b9'},  # user_id_2
        {'booking_id': '7c76c53b-98bb-481c-ac21-0555c5e51d10'},  # user_id_7
    ]
    if must_skip_user_id_1:
        expected_rows.pop(1)

    assert rows == expected_rows


@pytest.mark.now('2020-05-28T11:40:05')
@pytest.mark.pgsql('shuttle_control', files=['main_2.sql'])
@pytest.mark.translations(
    client_messages={
        'push_msg_title': {'ru': 'Тайтл!', 'en': 'Title!'},
        'push_msg_text': {'ru': 'Текст!', 'en': 'Text!'},
    },
)
@pytest.mark.experiments3(filename='experiments3_push_config.json')
async def test_cron_finishing_intent(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock_ucommunications(request):
        request_data = json.loads(request.get_data())
        user_id = request_data['user']
        user_locale = USERS_FINISHING[user_id]['locale']
        expected_data = copy.deepcopy(PUSH_MSG[user_locale])
        expected_data['user'] = user_id
        assert request_data == expected_data
        USERS_FINISHING.pop(user_id)
        return {}

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.051,
                        'lat': 60.051,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.011,
                        'lat': 60.011,
                        'timestamp': 1590709205,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        rlls = request.args['rll'].split('~')
        time = ROUTER[str(rlls[-1])]
        return mockserver.make_response(
            response=_proto_driving_summary(time, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    cron_request = {'task_name': 'push-messages-worker/shuttle.finishing'}
    await taxi_shuttle_control.post('/service/cron', cron_request)
    assert _mock_ucommunications.has_calls
    assert _mock_router.has_calls
    assert not USERS_FINISHING.keys()

    rows = select_named(
        'SELECT booking_id FROM state.communications ' 'ORDER BY booking_id',
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'booking_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
        {'booking_id': '427a330d-2506-464a-accf-346b31e288b9'},
        {'booking_id': '5c76c35b-98df-481c-ac21-0555c5e51d21'},
    ]
