# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary


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


@pytest.fixture
def external_mocks(mockserver, load_binary, driver_trackstory_v2_shorttracks):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert len(request.json['id_in_set']) == 1
        dbid_uuid = request.json['id_in_set'][0]
        return {
            'profiles': [
                {
                    'park_driver_profile_id': dbid_uuid,
                    'data': {'car_id': 'shuttle_car_id'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'dbid_0_shuttle_car_id',
                    'data': {
                        'number': 'A666MP77',
                        'park_id': 'park_id',
                        'car_id': 'car_id',
                    },
                },
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(100, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            response=load_binary('route_response_1.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    # '2020-05-18T15:00:00+0000' -> 1589814000
    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 29.0,
                        'lat': 60.0,
                        'timestamp': 1589814000,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_0',
                },
                {
                    'position': {
                        'lon': 30.0,
                        'lat': 60.0,
                        'timestamp': 1589814000,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_1',
                },
                {
                    'position': {
                        'lon': 30.0,
                        'lat': 60.0,
                        'timestamp': 1589814000,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_2',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())


@pytest.mark.parametrize(
    'booking_id, cost',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 0),
        ('acfff773-398f-4913-b9e9-03bf5eda23ac', 10),
    ],
)
@pytest.mark.parametrize('add_typed_experiment', [False, True])
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
async def test_main(
        taxi_shuttle_control,
        experiments3,
        booking_id,
        cost,
        add_typed_experiment,
        full_address: bool,
        pgsql,
        external_mocks,
        load_json,
):
    exp_name = 'test_typed_experiment'
    exp_value = {'important_bool': True}

    experiments3.add_experiment(
        name=exp_name,
        consumers=['shuttle-control/v1_booking_information'],
        match={'enabled': add_typed_experiment, 'predicate': {'type': 'true'}},
        clauses=[],
        default_value=exp_value,
    )

    response = await taxi_shuttle_control.get(
        '/4.0/shuttle-control/v1/booking/information?booking_id=' + booking_id,
        headers={'X-Yandex-UID': '0123456789'},
    )

    expected_response = load_json('test_main_expected_response.json')

    expected_response['booking_id'] = booking_id
    expected_response['cost'] = {'total': f'{cost} $SIGN$$CURRENCY$'}
    expected_response['typed_experiments']['items'] = (
        []
        if not add_typed_experiment
        else [{'name': exp_name, 'value': exp_value}]
    )
    expected_response['ui']['card_details'][
        'text'
    ] = f'Стоимость {cost} $SIGN$$CURRENCY$'
    if full_address:
        expected_response['source_point'] = {
            'full_text': 'full_text',
            'position': [30.0, 60.0],
            'short_text': 'text',
            'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
        }
        expected_response['destination_point'] = {
            'full_text': 'full_text',
            'position': [31.0, 61.0],
            'short_text': 'text',
            'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
        }
    else:
        expected_response['source_point'] = {
            'full_text': '',
            'position': [30.0, 60.0],
            'short_text': '',
        }
        expected_response['destination_point'] = {
            'full_text': '',
            'position': [31.0, 61.0],
            'short_text': '',
        }

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'booking_id, cost',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 0),
        ('acfff773-398f-4913-b9e9-03bf5eda23ac', 10),
    ],
)
@pytest.mark.parametrize('add_typed_experiment', [False, True])
@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
async def test_main_out_of_workshift(
        taxi_shuttle_control,
        experiments3,
        booking_id,
        cost,
        add_typed_experiment,
        full_address: bool,
        pgsql,
        external_mocks,
        load_json,
):
    exp_name = 'test_typed_experiment'
    exp_value = {'important_bool': True}

    experiments3.add_experiment(
        name=exp_name,
        consumers=['shuttle-control/v1_booking_information'],
        match={'enabled': add_typed_experiment, 'predicate': {'type': 'true'}},
        clauses=[],
        default_value=exp_value,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': True},
        clauses=[],
    )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.drivers_workshifts_subscriptions
        SET subscribed_at = '2020-05-28T09:50:00+0000'
        """,
    )

    response = await taxi_shuttle_control.get(
        '/4.0/shuttle-control/v1/booking/information?booking_id=' + booking_id,
        headers={'X-Yandex-UID': '0123456789'},
    )

    expected_response = load_json('test_main_expected_response.json')

    expected_response['booking_id'] = booking_id
    expected_response['cost'] = {'total': f'{cost} $SIGN$$CURRENCY$'}
    expected_response['typed_experiments']['items'] = (
        []
        if not add_typed_experiment
        else [{'name': exp_name, 'value': exp_value}]
    )
    expected_response['ui']['card_details'][
        'text'
    ] = f'Стоимость {cost} $SIGN$$CURRENCY$'
    if full_address:
        expected_response['source_point'] = {
            'full_text': 'full_text',
            'position': [30.0, 60.0],
            'short_text': 'text',
            'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
        }
        expected_response['destination_point'] = {
            'full_text': 'full_text',
            'position': [31.0, 61.0],
            'short_text': 'text',
            'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
        }
    else:
        expected_response['source_point'] = {
            'full_text': '',
            'position': [30.0, 60.0],
            'short_text': '',
        }
        expected_response['destination_point'] = {
            'full_text': '',
            'position': [31.0, 61.0],
            'short_text': '',
        }

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2020-05-18T15:00:00+0000')
@pytest.mark.parametrize(
    'booking_id, uid, expected_ui',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            '0123456789',
            {
                'shuttle_visible_identificator': 'A666MP77',
                'subtitle': '',
                'title': 'Вы приехали',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1230',
                },
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'legacy_client',
            {
                'subtitle': 'Шаттл будет через 1 мин',
                'title': 'Билет 1524',
                'shuttle_visible_identificator': 'A666MP77',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1524',
                },
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            '0123456780',
            {
                'subtitle': 'До ост. stop_5',
                'title': 'Ехать 1 мин',
                'shuttle_visible_identificator': 'A666MP77',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1523',
                },
            },
        ),
    ],
    ids=['finished', 'driving_legacy_client', 'transporting'],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_ui_main_panel(
        taxi_shuttle_control, external_mocks, booking_id, uid, expected_ui,
):
    response = await taxi_shuttle_control.get(
        f'/4.0/shuttle-control/v1/booking/information?booking_id={booking_id}',
        headers={'X-Yandex-UID': uid},
    )

    assert response.status_code == 200
    assert response.json()['ui']['main_panel'] == expected_ui


@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.parametrize(
    'booking_id, uid, expected_ui',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            '0123456789',
            {
                'shuttle_visible_identificator': 'A666MP77',
                'subtitle': '',
                'title': 'Вы приехали',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1230',
                },
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'legacy_client',
            {
                'subtitle': 'Шаттл будет через 5 мин',
                'title': 'Билет 1524',
                'shuttle_visible_identificator': 'A666MP77',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1524',
                },
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            '0123456780',
            {
                'subtitle': 'До ост. stop_5',
                'title': 'Ехать 6 мин',
                'shuttle_visible_identificator': 'A666MP77',
                'footer': {
                    'payment_text': 'Оплата наличными',
                    'text': 'Билет 1523',
                },
            },
        ),
    ],
    ids=['finished', 'driving_legacy_client', 'transporting'],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_ui_main_panel_out_of_workshift(
        taxi_shuttle_control,
        external_mocks,
        booking_id,
        uid,
        expected_ui,
        experiments3,
        pgsql,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': True},
        clauses=[],
    )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.drivers_workshifts_subscriptions
        SET subscribed_at = '2020-05-28T09:50:00+0000'
        """,
    )

    response = await taxi_shuttle_control.get(
        f'/4.0/shuttle-control/v1/booking/information?booking_id={booking_id}',
        headers={'X-Yandex-UID': uid},
    )

    assert response.status_code == 200
    assert response.json()['ui']['main_panel'] == expected_ui


@pytest.mark.parametrize(
    'booking_id, uid, expected_ui',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', '0123456789', None),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
            '0123456722',
            {
                'title_text': 'Заголовок',
                'back_button_text': 'Назад',
                'items': [
                    {
                        'type': 'phone',
                        'link': 'tel:+7-000-000-00-00',
                        'text': 'Call me maybe',
                    },
                    {
                        'type': 'web',
                        'link': (
                            'some.site.com/order_id=2fef68c9-25d0-4174'
                            '-9dd0-bdd1b3738888&locale=ru&user-id=userid'
                        ),
                        'text': 'click me maybe',
                    },
                    {
                        'type': 'telegram',
                        'link': 'join.me/',
                        'text': 'text me maybe',
                    },
                ],
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            '0123456789',
            {
                'title_text': 'Заголовок',
                'back_button_text': 'Назад',
                'items': [
                    {
                        'type': 'phone',
                        'link': 'tel:+7-800-555-35-35',
                        'text': 'Call me maybe',
                    },
                ],
            },
        ),
    ],
    ids=[
        'disabled_action_on_finished',
        'route_with_all_types_by_route2',
        'route_with_phone_only_by_route1',
    ],
)
@pytest.mark.config(
    SHUTTLE_CONTROL_AVAILABLE_ACTIONS={
        'finished': [],
        'driving': ['cancel', 'contact_support'],
    },
)
@pytest.mark.experiments3(filename='support_ui_settings_config.json')
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_ui_support_panel(
        taxi_shuttle_control, external_mocks, booking_id, uid, expected_ui,
):
    response = await taxi_shuttle_control.get(
        f'/4.0/shuttle-control/v1/booking/information?booking_id={booking_id}',
        headers={
            'X-Yandex-UID': uid,
            'X-Request-Language': 'ru',
            'X-YaTaxi-UserId': 'userid',
        },
    )

    assert response.status_code == 200
    if expected_ui:
        assert response.json()['ui']['support_dialog'] == expected_ui
    else:
        assert 'support_dialog' not in response.json()['ui']


@pytest.mark.now('2020-05-18T15:00:00+0000')
@pytest.mark.parametrize(
    'booking_id, enable, shuffle, expected_feedback',
    [
        # driving
        ('2fef68c9-25d0-4174-9dd0-bdd1b3738888', False, True, None),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3738888', True, False, None),
        # cancelled
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730770', False, True, None),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
            True,
            False,
            {
                'title_text': 'Вы не поехали на Шаттле',
                'choices': [
                    {'id': 'choice1', 'text': 'Первый вариант'},
                    {'id': 'choice2', 'text': 'Второй вариант'},
                    {'id': 'choice3', 'text': 'Первый вариант'},
                    {'id': 'choice4', 'text': 'Второй вариант'},
                ],
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730770',
            True,
            True,
            {
                'title_text': 'Вы не поехали на Шаттле',
                'choices': [
                    {'id': 'choice1', 'text': 'Первый вариант'},
                    {'id': 'choice2', 'text': 'Второй вариант'},
                    {'id': 'choice3', 'text': 'Первый вариант'},
                    {'id': 'choice4', 'text': 'Второй вариант'},
                ],
            },
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730771',
            True,
            False,
            {
                'title_text': 'Шаттл уехал без вас',
                'choices': [
                    {'id': 'choice1', 'text': 'Первый вариант'},
                    {'id': 'choice2', 'text': 'Первый вариант'},
                    {'id': 'choice3', 'text': 'Первый вариант'},
                    {'id': 'choice4', 'text': 'Второй вариант'},
                ],
            },
        ),
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d23',
            True,
            True,
            {
                'title_text': 'Шаттл уехал без вас',
                'choices': [
                    {'id': 'choice1', 'text': 'Первый вариант'},
                    {'id': 'choice2', 'text': 'Первый вариант'},
                    {'id': 'choice3', 'text': 'Первый вариант'},
                    {'id': 'choice4', 'text': 'Второй вариант'},
                ],
            },
        ),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730773', True, False, None),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730774', True, True, None),
        ('acfff773-398f-4913-b9e9-03bf5eda26ac', True, True, None),
        # finished
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730769',
            True,
            False,
            {
                'title_text': 'Вы приехали на Шаттле',
                'rating': {
                    'variants': [
                        {
                            'reasons': {
                                'choices': [
                                    {
                                        'id': 'youre_too_mean',
                                        'text': 'Первый вариант',
                                    },
                                    {
                                        'id': 'i_dont_like_you',
                                        'text': 'Первый вариант',
                                    },
                                ],
                            },
                            'id': 'bad',
                            'text': 'Плохо',
                        },
                        {'id': 'ok', 'text': 'Нормально'},
                        {
                            'reasons': {
                                'choices': [
                                    {
                                        'id': 'best_driver',
                                        'text': 'Второй вариант',
                                    },
                                    {
                                        'id': 'nice_music',
                                        'text': 'Первый вариант',
                                    },
                                ],
                            },
                            'id': 'good',
                            'text': 'Хорошо',
                        },
                    ],
                    'type': 'bubbles',
                },
            },
        ),
    ],
)
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_feedback(
        taxi_shuttle_control,
        experiments3,
        external_mocks,
        booking_id,
        enable,
        shuffle,
        expected_feedback,
):
    experiments3.add_config(
        name='shuttle_feedback_settings',
        consumers=['shuttle-control/v1_booking_information'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
        clauses=[
            {
                'title': 'first',
                'predicate': {'type': 'true', 'init': {}},
                'value': {
                    'finished': {
                        'enable': enable,
                        'ttl': 60,
                        'shuffle_choices': shuffle,
                        'title_tanker_key': (
                            'shuttle_control.feedback.finished.title'
                        ),
                        'comment_placeholder_tanker_key': (
                            'shuttle_control.feedback.finished.'
                            'comment_placeholder'
                        ),
                        'ratings': {
                            'type': 'bubbles',
                            'variants': [
                                {
                                    'id': 'bad',
                                    'title_tanker_key': (
                                        'shuttle_control.feedback.rating.bad'
                                    ),
                                    'reasons': [
                                        {
                                            'id': 'youre_too_mean',
                                            'tanker_key': (
                                                'shuttle_control.choice1'
                                            ),
                                        },
                                        {
                                            'id': 'i_dont_like_you',
                                            'tanker_key': (
                                                'shuttle_control.choice1'
                                            ),
                                        },
                                    ],
                                },
                                {
                                    'id': 'ok',
                                    'title_tanker_key': (
                                        'shuttle_control.feedback.rating.ok'
                                    ),
                                },
                                {
                                    'id': 'good',
                                    'title_tanker_key': (
                                        'shuttle_control.feedback.rating.good'
                                    ),
                                    'reasons': [
                                        {
                                            'id': 'best_driver',
                                            'tanker_key': (
                                                'shuttle_control.choice2'
                                            ),
                                        },
                                        {
                                            'id': 'nice_music',
                                            'tanker_key': (
                                                'shuttle_control.choice1'
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                    'cancelled_by_user': {
                        'enable': enable,
                        'ttl': 60,
                        'shuffle_choices': shuffle,
                        'title_tanker_key': (
                            'shuttle_control.user_cancelled_feedback_title'
                        ),
                        'choices': [
                            {
                                'id': 'choice1',
                                'tanker_key': 'shuttle_control.choice1',
                            },
                            {
                                'id': 'choice2',
                                'tanker_key': 'shuttle_control.choice2',
                            },
                            {
                                'id': 'choice3',
                                'tanker_key': 'shuttle_control.choice1',
                            },
                            {
                                'id': 'choice4',
                                'tanker_key': 'shuttle_control.choice2',
                                'is_fixed_position': True,
                            },
                        ],
                    },
                    'cancelled_by_backend': {
                        'enable': enable,
                        'ttl': 60,
                        'shuffle_choices': shuffle,
                        'title_tanker_key': (
                            'shuttle_control.backend_cancelled_feedback_title'
                        ),
                        'choices': [
                            {
                                'id': 'choice1',
                                'tanker_key': 'shuttle_control.choice1',
                            },
                            {
                                'id': 'choice2',
                                'tanker_key': 'shuttle_control.choice1',
                            },
                            {
                                'id': 'choice3',
                                'tanker_key': 'shuttle_control.choice1',
                            },
                            {
                                'id': 'choice4',
                                'tanker_key': 'shuttle_control.choice2',
                                'is_fixed_position': True,
                            },
                        ],
                    },
                },
            },
        ],
    )

    response = await taxi_shuttle_control.get(
        f'/4.0/shuttle-control/v1/booking/information?booking_id={booking_id}',
        headers={
            'X-Yandex-UID': '0123456722',
            'X-Request-Language': 'ru',
            'X-YaTaxi-UserId': 'userid',
        },
    )

    assert response.status_code == 200
    if expected_feedback:
        feedback = response.json()['feedback']
        if shuffle:
            assert len(feedback['choices']) == len(
                expected_feedback['choices'],
            )

            assert feedback['choices'][3] == expected_feedback['choices'][3]
            assert feedback['choices'] != expected_feedback['choices']

            feedback['choices'].sort(key=lambda x: x['id'])

        assert feedback == expected_feedback
    else:
        assert 'feedback' not in response.json()
