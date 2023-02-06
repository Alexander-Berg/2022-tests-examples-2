from datetime import datetime
from datetime import timedelta

import pytest

from .reposition_select import select_named


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('is_backend_only', [False, True])
def test_make_offer_backend_only(
        taxi_reposition, pgsql, mockserver, load, is_backend_only, testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    queries = [load('drivers.sql')]

    is_backend_only_mode_error_expected = not is_backend_only

    if is_backend_only:
        queries.append(load('simple_modes_offer_only_true.sql'))
    else:
        queries.append(load('simple_modes_offer_only_false.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'SuperSurge',
                    'destination': [30, 60],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2099-08-09T10:31:42+03',
                    'finish_until': '2018-08-09T19:31:42+03',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': ['tag1', 'tag2'],
                    'completed_tags': ['completed_tag1'],
                    'tariff_class': 'comfort',
                },
            ],
        },
    )
    assert response.status_code == 200

    is_backend_only_from_db = select_named(
        'SELECT offer_only '
        'FROM config.modes '
        'WHERE mode_name=\'SuperSurge\'',
        pgsql['reposition'],
    ) == [{'offer_only': True}]

    assert is_backend_only_from_db == is_backend_only

    is_backend_only_error = response.json() == {
        'results': [
            {
                'driver_id': 'uuid',
                'error': 'wrong backend only state on mode \'SuperSurge\'',
                'park_db_id': 'dbid',
            },
        ],
    }

    assert is_backend_only_error == is_backend_only_mode_error_expected

    if is_backend_only_error:
        return

    assert response.json() == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_EVENTS_UPLOADER_MODE_TYPES_WHITELIST={
        'SuperSurge': ['offer_created', 'offer_expired'],
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
def test_make_offer(taxi_reposition, pgsql, mockserver, config, testpoint):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'SuperSurge',
                    'destination': [30, 60],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2099-08-09T10:31:42+03',
                    'finish_until': '2018-08-09T19:31:42+03',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': ['tag1', 'tag2'],
                    'completed_tags': ['completed_tag1'],
                    'tariff_class': 'comfort',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }

    # no finish_until
    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'SuperSurge',
                    'destination': [20, 40],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2099-08-09T10:31:42+03',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': [],
                    'completed_tags': ['completed_tag2'],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-O3GWpmbk5ezJn4KR',
            },
        ],
    }

    rows = select_named(
        """
        SELECT *
        FROM state.offers
        NATURAL JOIN settings.points
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )
    assert rows == [
        {
            'offer_id': 1,
            'valid_until': datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-atlas',
            'restrictions': '({})',
        },
        {
            'offer_id': 2,
            'valid_until': datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 2,
            'mode_id': 1488,
            'updated': datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-atlas',
            'restrictions': '({})',
        },
    ]

    rows = select_named(
        'SELECT event_id, event_type, driver_id_id, occured_at, tags, '
        'extra_data '
        'FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )
    assert rows == [
        {
            'event_id': 1,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 3,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 4,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]

    rows = select_named(
        'SELECT * FROM etag_data.offered_modes', pgsql['reposition'],
    )

    assert rows == [
        {
            'driver_id_id': 5,
            'revision': 2,
            'valid_since': datetime(2018, 10, 15, 18, 18, 46),
            'data': {
                'SuperSurge': {
                    'restrictions': [],
                    'client_attributes': {},
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"SuperSurge"}\n',
                        'title': '{"tanker_key":"SuperSurge"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'locations': {
                        '4q2VolejRejNmGQB': {
                            'description': 'Very nice description',
                            'destination_radius': 100.0,
                            'expires_at': '2099-08-09T07:31:42+00:00',
                            'image_id': 'icon',
                            'location': {
                                'id': '4q2VolejRejNmGQB',
                                'point': [30.0, 60.0],
                                'address': {
                                    'title': 'Address in Moscow',
                                    'subtitle': 'Moscow',
                                },
                                'type': 'point',
                            },
                            'offered_at': '2018-10-15T18:18:46+00:00',
                            'restrictions': [],
                        },
                        'O3GWpmbk5ezJn4KR': {
                            'description': 'Very nice description',
                            'destination_radius': 100.0,
                            'expires_at': '2099-08-09T07:31:42+00:00',
                            'image_id': 'icon',
                            'location': {
                                'id': 'O3GWpmbk5ezJn4KR',
                                'point': [20.0, 40.0],
                                'type': 'point',
                                'address': {
                                    'title': 'Address in Moscow',
                                    'subtitle': 'Moscow',
                                },
                            },
                            'offered_at': '2018-10-15T18:18:46+00:00',
                            'restrictions': [],
                        },
                    },
                },
            },
            'is_sequence_start': True,
        },
    ]


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
def test_make_offer_non_existent_mode(taxi_reposition):
    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'Around The World',
                    'destination': [30, 60],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2018-08-09T07:31:42+03',
                    'finish_until': '2018-08-09T19:31:42+03',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': ['tag1'],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': 'Mode \'Around The World\' not found',
            },
        ],
    }


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
def test_make_offer_bad_date_format(taxi_reposition):
    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'SuperSurge',
                    'destination': [30, 60],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2018-08-09T10:31:42+',
                    'finish_until': '2018-08-09T19:31:42',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': ['tag1'],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()['results'][0]['error'] is not None  # can't parse


@pytest.mark.now('2018-08-08T18:18:46+03')
@pytest.mark.config(
    REPOSITION_EVENTS_UPLOADER_MODE_TYPES_WHITELIST={
        'SuperSurge': ['offer_created', 'offer_expired'],
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
def test_make_offer_no_tags(
        taxi_reposition, pgsql, mockserver, config, testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    response = taxi_reposition.post(
        '/v1/reposition/make_offer',
        json={
            'offers': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'mode': 'SuperSurge',
                    'destination': [30, 60],
                    'city': 'Moscow',
                    'address': 'Address in Moscow',
                    'start_until': '2018-08-09T10:31:42+03',
                    'finish_until': '2018-08-09T19:31:42+03',
                    'image_id': 'icon',
                    'name': 'Name',
                    'description': 'Very nice description',
                    'tags': [],
                    'completed_tags': [],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()['results'][0]['point_id'] is not None

    rows = select_named(
        'SELECT event_id, event_type, driver_id_id, occured_at, tags, '
        'extra_data '
        'FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )
    assert rows == [
        {
            'event_id': 1,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime(2018, 8, 8, 15, 18, 46),  # ignore tz
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime(2018, 8, 9, 7, 31, 42),  # ignore tz
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]

    rows = select_named(
        'SELECT * FROM etag_data.offered_modes', pgsql['reposition'],
    )

    assert rows == [
        {
            'driver_id_id': 5,
            'revision': 1,
            'valid_since': datetime(2018, 8, 8, 15, 18, 46),
            'data': {
                'SuperSurge': {
                    'restrictions': [],
                    'client_attributes': {},
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"SuperSurge"}\n',
                        'title': '{"tanker_key":"SuperSurge"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'locations': {
                        '4q2VolejRejNmGQB': {
                            'description': 'Very ' 'nice ' 'description',
                            'destination_radius': 100.0,
                            'expires_at': '2018-08-09T07:31:42+00:00',
                            'image_id': 'icon',
                            'location': {
                                'id': '4q2VolejRejNmGQB',
                                'point': [30.0, 60.0],
                                'address': {
                                    'title': 'Address in Moscow',
                                    'subtitle': 'Moscow',
                                },
                                'type': 'point',
                            },
                            'offered_at': '2018-08-08T15:18:46+00:00',
                            'restrictions': [],
                        },
                    },
                },
            },
            'is_sequence_start': True,
        },
    ]


@pytest.mark.now('2018-08-08T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'simple.sql', 'hundred_drivers_and_points.sql'],
)
def test_make_hundred_offers(
        taxi_reposition, pgsql, mockserver, load_json, config, testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    request = {'offers': []}

    for idx in range(1, 100):
        minutes = 0
        if idx % 2 == 0:
            minutes += 5
        if idx % 3 == 0:
            minutes += 10
        if idx % 4 == 0:
            minutes += 15
        if idx % 7 == 0:
            minutes = None
        finish_until = (
            '2018-08-09T19:{}:42+03'.format(minutes)
            if minutes is not None
            else None
        )

        request['offers'].append(
            {
                'driver_id': 'uuid_' + str(idx),
                'park_db_id': 'dbid',
                'mode': 'SuperSurge',
                'destination': [30, 60],
                'city': 'Moscow',
                'address': 'Address in Moscow',
                'start_until': '2018-08-09T10:31:42+03',
                'finish_until': finish_until,
                'image_id': 'icon',
                'name': 'Name',
                'description': 'Very nice description',
                'tags': ['reposition_super_surge'],
                'completed_tags': ['reposition_super_surge_completed'],
            },
        )

    response = taxi_reposition.post('/v1/reposition/make_offer', json=request)

    assert response.status_code == 200
    assert response.json() == load_json('hundred_offers_response.json')

    offers_rows = select_named(
        """
        SELECT valid_until, due, image_id, description, used,
        tariff_class, session_tags, completed_tags
        FROM state.offers
        LEFT JOIN check_rules.duration ON offers.due_id = duration.duration_id
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )

    expected_offers_rows = []
    for idx in range(1, 100):
        due = datetime(2018, 8, 9, 16, 0, 42)
        if idx % 2 == 0:
            due += timedelta(minutes=5)
        if idx % 3 == 0:
            due += timedelta(minutes=10)
        if idx % 4 == 0:
            due += timedelta(minutes=15)
        if idx % 7 == 0:
            due = None

        expected_offers_rows.append(
            {
                'valid_until': datetime(2018, 8, 9, 7, 31, 42),
                'due': due,
                'image_id': 'icon',
                'description': 'Very nice description',
                'used': False,
                'tariff_class': '__default__',
                'session_tags': ['reposition_super_surge'],
                'completed_tags': ['reposition_super_surge_completed'],
            },
        )

    assert offers_rows == expected_offers_rows

    rows = select_named(
        'SELECT * FROM etag_data.offered_modes', pgsql['reposition'],
    )

    assert len(rows) == 99  # due to range from [1; 100)
