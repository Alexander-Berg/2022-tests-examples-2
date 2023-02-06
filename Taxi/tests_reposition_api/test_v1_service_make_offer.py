# pylint: disable=import-only-modules,too-many-lines,invalid-name
# pylint: disable=unused-variable
import copy
import datetime

import pytest

from .fbs import MakeOfferFbs
from .fbs import MakeOfferOrigin
from .utils import select_named
from .utils import select_table_named

fbs_handler = MakeOfferFbs()


def build_driver_position_response(lon, lat):
    return {
        'position': {
            'direction': 328,
            'lon': lon,
            'lat': lat,
            'speed': 30,
            'timestamp': 1502366306,
        },
        'type': 'raw',
    }


def check_sessions_table(
        db,
        point_id=1,
        mode_id=1,
        submode_id=None,
        destination_point='(3,4)',
        destination_radius=None,
        start_point='(3.1,4.1)',
        session_deadline=None,
):
    rows = select_table_named('state.sessions', 'session_id', db)
    for row in rows:
        if row['point_id'] == point_id:
            assert row['active']
            assert not row['start'] is None
            assert row['end'] is None
            assert row['start_point'] == start_point
            assert row['mode_id'] == mode_id
            assert row['submode_id'] == submode_id
            assert row['destination_point'] == destination_point
            assert row['destination_radius'] == destination_radius
            assert row['session_deadline'] == session_deadline
            return
    assert False


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('is_backend_only', [False, True])
async def test_make_offer_backend_only(
        taxi_reposition_api,
        pgsql,
        mockserver,
        load,
        is_backend_only,
        testpoint,
):
    queries = [load('drivers.sql')]

    is_backend_only_mode_error_expected = not is_backend_only

    if is_backend_only:
        queries.append(load('simple_modes_offer_only_true.sql'))
    else:
        queries.append(load('simple_modes_offer_only_false.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )

    is_backend_only_from_db = select_named(
        'SELECT offer_only '
        'FROM config.modes '
        'WHERE mode_name=\'SuperSurge\'',
        pgsql['reposition'],
    ) == [{'offer_only': True}]

    assert is_backend_only == is_backend_only_from_db

    if is_backend_only_mode_error_expected:
        assert response.status_code == 200
        assert fbs_handler.parse_response(response.content) == {
            'results': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'error': 'Mode is incorrect in offer',
                },
            ],
        }
        return

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
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
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer(taxi_reposition_api, pgsql, mockserver, testpoint):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                    {
                        'driver_id': 'uuid1',
                        'park_db_id': 'dbid',
                        'mode': 'OfferedDistrict',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                    {
                        'driver_id': 'uuid2',
                        'park_db_id': 'dbid',
                        'mode': 'GeobookingOffers',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
            {
                'driver_id': 'uuid1',
                'park_db_id': 'dbid',
                'point_id': 'offer-O3GWpmbk5ezJn4KR',
            },
            {
                'driver_id': 'uuid2',
                'error': 'Failed to create offer',
                'park_db_id': 'dbid',
            },
        ],
    }

    # no finish_until
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [20, 40],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': ['completed_tag2'],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'auto_accept': False,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-PQZOpnel5aKBzyVX',
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
        {
            'offer_id': 2,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 2,
            'mode_id': 1490,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 6,
            'area_radius': 5000.0,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
        {
            'offer_id': 3,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 3,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT *
        FROM state.offers_metadata
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )
    assert not rows

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
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 3,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 4,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]


@pytest.mark.now('2018-10-15T18:18:46')
# @pytest.mark.config(ROUTER_MAPS_ENABLED=False)
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired', 'start'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_autoaccept_single(
        taxi_reposition_api, mockserver, pgsql, now, testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'auto_accept': True,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }

    # no finish_until
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'auto_accept': True,
                    },
                    {
                        'driver_id': 'uuid1',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [20, 40],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag3'],
                        'completed_tags': ['completed_tag2'],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'auto_accept': True,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': 'Failed to create offer',
            },
            {
                'driver_id': 'uuid1',
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': True,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
        {
            'offer_id': 2,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': True,
            'tariff_class': '__default__',
            'point_id': 2,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 6,
            'area_radius': None,
            'session_tags': ['tag3'],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT *
        FROM state.offers_metadata
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )
    assert not rows

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
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'driver_id_id': 5,
            'event_id': 3,
            'event_type': 'start',
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': {
                'session_id': '4q2VolejRejNmGQB',
                'status': 'active',
                'state_id': '4q2VolejRejNmGQB_active',
            },
        },
        {
            'event_id': 4,
            'event_type': 'offer_created',
            'driver_id_id': 6,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 5,
            'event_type': 'offer_expired',
            'driver_id_id': 6,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 6,
            'event_type': 'start',
            'driver_id_id': 6,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': {
                'session_id': 'O3GWpmbk5ezJn4KR',
                'status': 'active',
                'state_id': 'O3GWpmbk5ezJn4KR_active',
            },
        },
    ]

    check_sessions_table(
        db=pgsql['reposition'],
        point_id=1,
        mode_id=1488,
        destination_point='(30,60)',
        session_deadline=datetime.datetime(2018, 8, 9, 16, 31, 42),
    )

    check_sessions_table(
        db=pgsql['reposition'],
        point_id=2,
        mode_id=1488,
        destination_point='(20,40)',
    )

    expected_tags_rows = [
        {
            'driver_id': '(dbid,uuid)',
            'udid': None,
            'confirmation_token': 'reposition-nirvana/4q2VolejRejNmGQB_append',
            'merge_policy': 'append',
            'tags': ['tag1'],
            'ttl': datetime.datetime(2018, 8, 9, 16, 31, 42),
            'provider': 'reposition-nirvana',
            'created_at': now,
        },
        {
            'driver_id': '(dbid,uuid1)',
            'udid': None,
            'confirmation_token': 'reposition-nirvana/O3GWpmbk5ezJn4KR_append',
            'merge_policy': 'append',
            'tags': ['tag3'],
            'ttl': None,
            'provider': 'reposition-nirvana',
            'created_at': now,
        },
    ]

    rows_tags = select_named(
        """
        SELECT driver_id, udid, confirmation_token, merge_policy, tags, ttl,
        provider, created_at FROM state.uploading_tags
        INNER JOIN settings.driver_ids ON
        uploading_tags.driver_id_id = driver_ids.driver_id_id
        """,
        pgsql['reposition'],
    )

    assert rows_tags == expected_tags_rows


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_with_restrictions(
        taxi_reposition_api, pgsql, mockserver, testpoint,
):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'restrictions': [
                            {
                                'image_id': 'icon id 1',
                                'short_text': 'with finish until',
                                'text': 'some text',
                                'title': 'with finish until title',
                            },
                            {
                                'image_id': 'icon id 2',
                                'short_text': 'with finish until',
                                'text': 'new text',
                                'title': 'with finish until title',
                            },
                        ],
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }

    # no finish_until
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [20, 40],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': ['completed_tag2'],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'restrictions': [
                            {
                                'image_id': 'icon id 3',
                                'short_text': 'no finish until',
                                'text': 'some text',
                                'title': 'no finish until title',
                            },
                            {
                                'image_id': 'icon id 4',
                                'short_text': 'no finish until',
                                'text': 'new text',
                                'title': 'no finish until title',
                            },
                        ],
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': (
                '("{""(\\\\""icon id 1\\\\"",\\\\""with finish until\\\\"",'
                '\\\\""some text\\\\"",\\\\""with finish until title\\\\"")""'
                ',""(\\\\""icon id 2\\\\"",\\\\""with finish until\\\\"",\\\\'
                '""new text\\\\"",\\\\""with finish until title\\\\"")""}")'
            ),
            'draft_id': None,
        },
        {
            'offer_id': 2,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 2,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-nirvana',
            'restrictions': (
                '("{""(\\\\""icon id 3\\\\"",\\\\""no finish until\\\\"",\\\\'
                '""some text\\\\"",\\\\""no finish until title\\\\"")"",""('
                '\\\\""icon id 4\\\\"",\\\\""no finish until\\\\"",\\\\""'
                'new text\\\\"",\\\\""no finish until title\\\\"")""}")'
            ),
            'draft_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT *
        FROM state.offers_metadata
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )

    assert not rows

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
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 3,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 4,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_with_metadata(
        taxi_reposition_api, pgsql, mockserver, testpoint,
):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1', 'tag2'],
                        'completed_tags': ['completed_tag1'],
                        'tariff_class': 'comfort',
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'restrictions': [
                            {
                                'image_id': 'icon id 1',
                                'short_text': 'with finish until',
                                'text': 'some text',
                                'title': 'with finish until title',
                            },
                            {
                                'image_id': 'icon id 2',
                                'short_text': 'with finish until',
                                'text': 'new text',
                                'title': 'with finish until title',
                            },
                        ],
                        'metadata': {'airport_queue_id': 'airport1'},
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }

    # no finish_until
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [20, 40],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': ['completed_tag2'],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'metadata': {
                            'airport_queue_id': 'airport2',
                            'classes': ['econom', 'comfort'],
                        },
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': (
                '("{""(\\\\""icon id 1\\\\"",\\\\""with finish until\\\\"",'
                '\\\\""some text\\\\"",\\\\""with finish until title\\\\"")""'
                ',""(\\\\""icon id 2\\\\"",\\\\""with finish until\\\\"",\\\\'
                '""new text\\\\"",\\\\""with finish until title\\\\"")""}")'
            ),
            'draft_id': None,
        },
        {
            'offer_id': 2,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 2,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': None,
        },
    ]

    rows = select_named(
        """
        SELECT *
        FROM state.offers_metadata
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )
    assert rows == [
        {
            'offer_id': 1,
            'airport_queue_id': 'airport1',
            'classes': None,
            'is_dispatch_airport_pin': False,
            'is_surge_pin': False,
            'surge_pin_value': None,
        },
        {
            'offer_id': 2,
            'airport_queue_id': 'airport2',
            'classes': ['econom', 'comfort'],
            'is_dispatch_airport_pin': False,
            'is_surge_pin': False,
            'surge_pin_value': None,
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
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 3,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 4,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_draft_id_format(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'draft_id': 'bla-bla-bla-incorrect-id',
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': 'DraftId does not match the format in offer',
            },
        ],
    }


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_surge_pin_offer_limit_in_request(
        taxi_reposition_api, experiments3,
):
    experiments3.add_config(
        name='reposition_api_surge_pin_offer_limits',
        consumers=['reposition-api/surge_pin_offer_limits'],
        match={'predicate': {'type': 'true', 'init': {}}, 'enabled': True},
        clauses=[],
        default_value={'limits': {'SuperSurge': 0}},
    )

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'draft_id': 'source-name/my_awesome_draft_token_1',
                        'metadata': {
                            'is_surge_pin': True,
                            'surge_pin_value': 2,
                        },
                    },
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'draft_id': 'source-name/my_awesome_draft_token_1',
                        'metadata': {
                            'is_surge_pin': False,
                            'surge_pin_value': 2,
                        },
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': (
                    'The number of offers for this '
                    'specific mode has been exceeded.'
                ),
            },
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
            },
        ],
    }


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_surge_pin_offer_limit_in_db(
        taxi_reposition_api, experiments3, pgsql,
):
    def get_surge_pin_offer_count():
        return select_named(
            """
            SELECT count(*)
            FROM state.offers  AS o
            INNER JOIN state.offers_metadata AS om
                ON om.offer_id = o.offer_id
            INNER JOIN settings.points AS p
                ON p.offer_id = o.offer_id
            WHERE
                o.used = FALSE AND
                p.driver_id_id = 5 AND -- 5  <-> uuid_dbid
                om.is_surge_pin = TRUE
            """,
            pgsql['reposition'],
        )[0]['count']

    def get_offered_modes_count():
        rows = select_named(
            """
            SELECT data FROM etag_data.offered_modes
            WHERE driver_id_id = 5
            ORDER BY valid_since DESC;
            """,
            pgsql['reposition'],
        )
        if not rows:
            return 0

        return len(rows[0]['data']['SuperSurge']['locations'])

    experiments3.add_config(
        name='reposition_api_surge_pin_offer_limits',
        consumers=['reposition-api/surge_pin_offer_limits'],
        match={'predicate': {'type': 'true', 'init': {}}, 'enabled': True},
        clauses=[],
        default_value={'limits': {'SuperSurge': 2}},
    )

    assert get_surge_pin_offer_count() == 0
    assert get_offered_modes_count() == 0
    for _ in range(1, 5):
        response = await taxi_reposition_api.post(
            '/v1/service/make_offer',
            headers={'Content-Type': 'application/x-flatbuffers'},
            data=fbs_handler.build_request(
                {
                    'offers': [
                        {
                            'driver_id': 'uuid',
                            'park_db_id': 'dbid',
                            'mode': 'SuperSurge',
                            'destination': [30, 60],
                            'city': 'Moscow',
                            'address': 'Address in Moscow',
                            'start_until': '2018-11-09T10:31:42+0300',
                            'finish_until': '2018-12-09T19:31:42+0300',
                            'image_id': 'icon',
                            'name': 'Name',
                            'description': 'Very nice description',
                            'tags': [],
                            'completed_tags': [],
                            'origin': MakeOfferOrigin.kRepositionNirvana,
                            'metadata': {
                                'is_surge_pin': True,
                                'surge_pin_value': 2,
                            },
                        },
                    ],
                },
            ),
        )
        assert response.status_code == 200

    assert get_surge_pin_offer_count() == 2
    assert get_offered_modes_count() == 2

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-11-09T10:31:42+0300',
                        'finish_until': '2018-12-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'metadata': {
                            'is_surge_pin': True,
                            'surge_pin_value': 1,
                        },
                    },
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-11-09T10:31:42+0300',
                        'finish_until': '2018-12-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'metadata': {
                            'is_surge_pin': True,
                            'surge_pin_value': 2,
                        },
                    },
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-11-09T10:31:42+0300',
                        'finish_until': '2018-12-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                        'metadata': {
                            'is_surge_pin': True,
                            'surge_pin_value': 3,
                        },
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-VvJ4openRe7Az1XP',
            },
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-QABWJxbojagwOL0E',
            },
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': (
                    'The number of offers for this '
                    'specific mode has been exceeded.'
                ),
            },
        ],
    }
    assert get_surge_pin_offer_count() == 2
    assert get_offered_modes_count() == 2


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_with_draft_id(taxi_reposition_api, pgsql):
    for _ in range(3):
        response = await taxi_reposition_api.post(
            '/v1/service/make_offer',
            headers={'Content-Type': 'application/x-flatbuffers'},
            data=fbs_handler.build_request(
                {
                    'offers': [
                        {
                            'driver_id': 'uuid',
                            'park_db_id': 'dbid',
                            'mode': 'SuperSurge',
                            'destination': [30, 60],
                            'city': 'Moscow',
                            'address': 'Address in Moscow',
                            'start_until': '2099-08-09T10:31:42+0300',
                            'finish_until': '2018-08-09T19:31:42+0300',
                            'image_id': 'icon',
                            'name': 'Name',
                            'description': 'Very nice description',
                            'tags': ['tag1', 'tag2'],
                            'completed_tags': ['completed_tag1'],
                            'tariff_class': 'comfort',
                            'origin': MakeOfferOrigin.kRepositionNirvana,
                            'restrictions': [
                                {
                                    'image_id': 'icon id 1',
                                    'short_text': 'with finish until',
                                    'text': 'some text',
                                    'title': 'with finish until title',
                                },
                                {
                                    'image_id': 'icon id 2',
                                    'short_text': 'with finish until',
                                    'text': 'new text',
                                    'title': 'with finish until title',
                                },
                            ],
                            'draft_id': 'source-name/my_awesome_draft_token_1',
                            'metadata': {'airport_queue_id': 'airport1'},
                        },
                        {
                            'driver_id': 'uuid',
                            'park_db_id': 'dbid',
                            'mode': 'SuperSurge',
                            'destination': [20, 40],
                            'city': 'Moscow',
                            'address': 'Address in Moscow',
                            'start_until': '2099-08-09T10:31:42+0300',
                            'image_id': 'icon',
                            'name': 'Name',
                            'description': 'Very nice description',
                            'tags': [],
                            'completed_tags': ['completed_tag2'],
                            'origin': MakeOfferOrigin.kRepositionNirvana,
                            'draft_id': 'source-name/my_awesome_draft_token_2',
                            'metadata': {
                                'airport_queue_id': 'airport2',
                                'classes': ['econom', 'comfort'],
                            },
                        },
                    ],
                },
            ),
        )
        assert response.status_code == 200
        assert fbs_handler.parse_response(response.content) == {
            'results': [
                {
                    'driver_id': 'uuid',
                    'park_db_id': 'dbid',
                    'point_id': 'offer-4q2VolejRejNmGQB',
                },
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': 1,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': 'comfort',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(30,60)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': ['tag1', 'tag2'],
            'completed_tags': ['completed_tag1'],
            'origin': 'reposition-nirvana',
            'restrictions': (
                '("{""(\\\\""icon id 1\\\\"",\\\\""with finish until\\\\"",'
                '\\\\""some text\\\\"",\\\\""with finish until title\\\\"")""'
                ',""(\\\\""icon id 2\\\\"",\\\\""with finish until\\\\"",\\\\'
                '""new text\\\\"",\\\\""with finish until title\\\\"")""}")'
            ),
            'draft_id': 'source-name/my_awesome_draft_token_1',
        },
        {
            'offer_id': 2,
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 2,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': 'reposition-nirvana',
            'restrictions': '({})',
            'draft_id': 'source-name/my_awesome_draft_token_2',
        },
    ]

    rows = select_named(
        """
        SELECT *
        FROM state.offers_metadata
        ORDER BY offer_id
        """,
        pgsql['reposition'],
    )
    assert rows == [
        {
            'offer_id': 1,
            'airport_queue_id': 'airport1',
            'classes': None,
            'is_dispatch_airport_pin': False,
            'is_surge_pin': False,
            'surge_pin_value': None,
        },
        {
            'offer_id': 2,
            'airport_queue_id': 'airport2',
            'classes': ['econom', 'comfort'],
            'is_dispatch_airport_pin': False,
            'is_surge_pin': False,
            'surge_pin_value': None,
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
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 3,
            'event_type': 'offer_created',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 4,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_non_existent_mode(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'Around The World',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T07:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': ['tag1'],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': 'Mode is incorrect in offer',
            },
        ],
    }


@pytest.mark.now('2018-08-08T18:18:46+0300')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_no_tags(
        taxi_reposition_api, pgsql, mockserver, testpoint,
):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert (
        fbs_handler.parse_response(response.content)['results'][0]['point_id']
        is not None
    )

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
            'occured_at': datetime.datetime(
                2018, 8, 8, 15, 18, 46,
            ),  # ignore tz
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
        {
            'event_id': 2,
            'event_type': 'offer_expired',
            'driver_id_id': 5,
            'occured_at': datetime.datetime(
                2018, 8, 9, 7, 31, 42,
            ),  # ignore tz
            'tags': ['SuperSurge'],
            'extra_data': None,
        },
    ]


@pytest.mark.now('2018-08-08T18:18:46+0300')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_create_events(
        taxi_reposition_api, pgsql, mockserver, testpoint,
):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [30, 60],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [35, 63],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert (
        fbs_handler.parse_response(response.content)['results'][0]['point_id']
        is not None
    )

    rows = select_named(
        'SELECT event_created FROM state.uploading_reposition_events',
        pgsql['reposition'],
    )

    assert rows == [
        {'event_created': datetime.datetime(2018, 8, 8, 15, 18, 46)},
        {'event_created': datetime.datetime(2018, 8, 8, 15, 18, 46)},
        {'event_created': datetime.datetime(2018, 8, 8, 15, 18, 46)},
        {'event_created': datetime.datetime(2018, 8, 8, 15, 18, 46)},
    ]


@pytest.mark.now('2018-08-08T18:18:46+0300')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
async def test_make_offer_no_destination(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2018-08-09T10:31:42+0300',
                        'finish_until': '2018-08-09T19:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': [],
                        'origin': MakeOfferOrigin.kRepositionNirvana,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'error': 'Destination is unset in offer',
            },
        ],
    }


@pytest.mark.now('2018-08-08T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'simple.sql', 'hundred_drivers_and_points.sql'],
)
async def test_make_hundred_offers(
        taxi_reposition_api, pgsql, mockserver, load_json, testpoint,
):
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
            '2018-08-09T19:{}:42+0300'.format(minutes)
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
                'start_until': '2018-08-09T10:31:42+0300',
                'finish_until': finish_until,
                'image_id': 'icon',
                'name': 'Name',
                'description': 'Very nice description',
                'tags': ['reposition_super_surge'],
                'completed_tags': ['reposition_super_surge_completed'],
                'origin': MakeOfferOrigin.kRepositionNirvana,
            },
        )

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(request),
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == load_json(
        'hundred_offers_response.json',
    )

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
        due = datetime.datetime(2018, 8, 9, 16, 0, 42)
        if idx % 2 == 0:
            due += datetime.timedelta(minutes=5)
        if idx % 3 == 0:
            due += datetime.timedelta(minutes=10)
        if idx % 4 == 0:
            due += datetime.timedelta(minutes=15)
        if idx % 7 == 0:
            due = None

        expected_offers_rows.append(
            {
                'valid_until': datetime.datetime(2018, 8, 9, 7, 31, 42),
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


@pytest.mark.now('2018-08-08T18:18:46')
# @pytest.mark.config(ROUTER_MAPS_ENABLED=False)
# @pytest.mark.config(REPOSITION_ETAG_DATA_WRITE_ENABLED=True)
@pytest.mark.pgsql(
    'reposition',
    files=['mode_home.sql', 'simple.sql', 'hundred_drivers_and_points.sql'],
)
@pytest.mark.parametrize('mix_offers', [False, True])
async def test_make_hundred_offers_autoaccept(
        taxi_reposition_api,
        pgsql,
        mockserver,
        load_json,
        mix_offers,
        testpoint,
):
    @mockserver.json_handler('/driver-trackstory/position')
    def mock_driver_position(request):
        return build_driver_position_response(3.1, 4.1)

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
            '2018-08-09T19:{}:42+0300'.format(minutes)
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
                'start_until': '2018-08-09T10:31:42+0300',
                'finish_until': finish_until,
                'image_id': 'icon',
                'name': 'Name',
                'description': 'Very nice description',
                'tags': ['reposition_super_surge'],
                'completed_tags': ['reposition_super_surge_completed'],
                'origin': MakeOfferOrigin.kRepositionNirvana,
                'auto_accept': (not (not mix_offers or idx % 3 == 0)),
            },
        )

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(request),
    )

    assert response.status_code == 200

    expected_response = load_json('hundred_offers_response.json')

    permutation = [0 for _ in range(1, 100)]
    if not mix_offers:
        assert (
            fbs_handler.parse_response(response.content) == expected_response
        )
    else:
        for i in range(1, 34):
            permutation[i * 3 - 1] = i - 1
        idx = 0
        for i in range(1, 100):
            if i % 3 != 0:
                permutation[i - 1] = 33 + idx
                idx += 1
        new_responses = copy.deepcopy(expected_response)
        for i in range(1, 100):
            new_responses['results'][i - 1]['point_id'] = expected_response[
                'results'
            ][permutation[i - 1]]['point_id']

        assert fbs_handler.parse_response(response.content) == new_responses

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
        due = datetime.datetime(2018, 8, 9, 16, 0, 42)
        if idx % 2 == 0:
            due += datetime.timedelta(minutes=5)
        if idx % 3 == 0:
            due += datetime.timedelta(minutes=10)
        if idx % 4 == 0:
            due += datetime.timedelta(minutes=15)
        if idx % 7 == 0:
            due = None

        expected_offers_rows.append(
            {
                'valid_until': datetime.datetime(2018, 8, 9, 7, 31, 42),
                'due': due,
                'image_id': 'icon',
                'description': 'Very nice description',
                'used': not (not mix_offers or idx % 3 == 0),
                'tariff_class': '__default__',
                'session_tags': ['reposition_super_surge'],
                'completed_tags': ['reposition_super_surge_completed'],
            },
        )

    if not mix_offers:
        assert offers_rows == expected_offers_rows
    else:
        new_expected_offers = copy.deepcopy(expected_offers_rows)
        for idx in range(1, 100):
            new_expected_offers[permutation[idx - 1]] = copy.deepcopy(
                expected_offers_rows[idx - 1],
            )
        assert offers_rows == new_expected_offers


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            'SuperSurge': ['offer_created', 'offer_expired'],
        },
    },
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'simple.sql'])
@pytest.mark.parametrize(
    'origin, origin_str, ok',
    [
        (MakeOfferOrigin.kRepositionRelocator, 'reposition-relocator', False),
        (MakeOfferOrigin.kRepositionNirvana, 'reposition-nirvana', True),
        (MakeOfferOrigin.kSintegro, 'sintegro', True),
        (MakeOfferOrigin.kAirportPin, 'airport-pin', True),
        (MakeOfferOrigin.kRepositionAtlas, 'reposition-atlas', True),
        (
            MakeOfferOrigin.kDispatchAirportPartnerProtocol,
            'dispatch-airport-partner-protocol',
            True,
        ),
    ],
)
async def test_offer_origins(
        taxi_reposition_api, pgsql, mockserver, origin, origin_str, ok,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    response = await taxi_reposition_api.post(
        '/v1/service/make_offer',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'offers': [
                    {
                        'driver_id': 'uuid',
                        'park_db_id': 'dbid',
                        'mode': 'SuperSurge',
                        'destination': [20, 40],
                        'city': 'Moscow',
                        'address': 'Address in Moscow',
                        'start_until': '2099-08-09T10:31:42+0300',
                        'image_id': 'icon',
                        'name': 'Name',
                        'description': 'Very nice description',
                        'tags': [],
                        'completed_tags': ['completed_tag2'],
                        'origin': origin,
                        'auto_accept': False,
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200

    parsed_response = fbs_handler.parse_response(response.content)
    if not ok:
        assert 'error' in parsed_response['results'][0]
        return

    assert parsed_response == {
        'results': [
            {
                'driver_id': 'uuid',
                'park_db_id': 'dbid',
                'point_id': 'offer-4q2VolejRejNmGQB',
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
            'valid_until': datetime.datetime(2099, 8, 9, 7, 31, 42),
            'due_id': None,
            'image_id': 'icon',
            'description': 'Very nice description',
            'created': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'used': False,
            'tariff_class': '__default__',
            'point_id': 1,
            'mode_id': 1488,
            'updated': datetime.datetime(2018, 10, 15, 18, 18, 46),
            'name': 'Name',
            'address': 'Address in Moscow',
            'city': 'Moscow',
            'location': '(20,40)',
            'driver_id_id': 5,
            'area_radius': None,
            'session_tags': [],
            'completed_tags': ['completed_tag2'],
            'origin': origin_str,
            'restrictions': '({})',
            'draft_id': None,
        },
    ]
