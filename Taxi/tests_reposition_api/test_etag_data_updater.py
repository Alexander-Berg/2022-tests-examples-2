# flake8: noqa E501
# pylint: disable=import-only-modules,too-many-lines

from datetime import datetime
import socket

import pytest

from .utils import select_named
from .utils import select_table_named

HOST = socket.gethostbyaddr(socket.gethostname())[0]


def get_task_name():
    return f'etag-data-updater@{HOST}'


@pytest.mark.now('2018-11-26T12:00:00+0000')
@pytest.mark.pgsql('reposition', files=['drivers.sql'])
@pytest.mark.config(
    REPOSITION_API_ETAG_DATA_UPDATER_CONFIG={
        'enabled': False,
        'update_defer_time_s': 300,
        'updating_state_ttl_s': 60,
        'drivers_per_iteration': 4,
        'drivers_bulk_size': 2,
        'parallel_threads_count': 1,
    },
)
async def test_disabled(taxi_reposition_api, pgsql):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    rows = select_table_named(
        'etag_data.drivers_update_state', 'driver_id_id', pgsql['reposition'],
    )

    for driver in rows:
        assert driver['updating'] is None
        assert driver['updated_at'] is None

    assert [] == select_table_named(
        'etag_data.states', 'driver_id_id', pgsql['reposition'],
    )
    assert [] == select_table_named(
        'etag_data.modes', 'driver_id_id', pgsql['reposition'],
    )
    assert [] == select_table_named(
        'etag_data.offered_modes', 'driver_id_id', pgsql['reposition'],
    )


@pytest.mark.now('2018-11-26T22:00:00+0000')
@pytest.mark.parametrize('geo_hierarchy_filtration', [False, True])
@pytest.mark.parametrize('stable_hash', [True, False])
@pytest.mark.driver_tags_match(
    dbid='dbid777',
    uuid='uuid',
    tags_info={
        'poi_prohibited': {'topics': ['reposition']},
        'permit_home_move': {'topics': ['reposition']},
    },
)
@pytest.mark.driver_tags_match(
    dbid='dbid777',
    uuid='uuid1',
    tags_info={'prohibit_poi_track': {'topics': ['reposition']}},
)
@pytest.mark.driver_tags_match(
    dbid='1488',
    uuid='driverSS',
    tags_info={
        'prohibit_home_move': {'topics': ['reposition']},
        'permit_poi_move': {'topics': ['reposition']},
    },
)
async def test_etag_data_updater(
        taxi_reposition_api,
        pgsql,
        mockserver,
        experiments3,
        load,
        geo_hierarchy_filtration,
        testpoint,
        taxi_config,
        stable_hash,
):
    hashes = []

    @testpoint('etag_hashes')
    async def _etag_hashes(data):
        hashes.append(data)

    experiments3.add_experiment(
        name='reposition_highlight_alternative_submode',
        consumers=['reposition/driver_locations'],
        match={
            'enabled': True,
            'predicate': {'type': 'true', 'init': {}},
            'consumers': [{'name': 'reposition/driver_locations'}],
        },
        clauses=[
            {
                'title': 'driverSS',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'driver_id',
                        'arg_type': 'string',
                        'value': 'driverSS',
                    },
                },
                'value': {'modes_submodes': {'my_district': '90'}},
            },
        ],
    )

    drivers_per_iteration = 4
    taxi_config.set_values(
        dict(
            #  REPOSITION_EVENT_USAGES_EXP_HASH_CALC_ENABLED=False,
            REPOSITION_API_ETAG_DATA_UPDATER_CONFIG={
                'enabled': True,
                'update_defer_time_s': 300,
                'updating_state_ttl_s': 60,
                'drivers_per_iteration': drivers_per_iteration,
                'drivers_bulk_size': 2,
                'parallel_threads_count': 1,
                'stable_hash': stable_hash,
            },
        ),
    )

    queries = [
        load('drivers.sql'),
        load('sample_drivers.sql'),
        load('user_modes.sql'),
        load('offered_modes.sql'),
        load('active_offer.sql'),
        load('active_sessions.sql'),
        load('feedback_data.sql'),
    ]

    if geo_hierarchy_filtration:
        queries.append(load('geo_hierarchy.sql'))

    pgsql['reposition'].apply_queries(queries)

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    total_drivers = select_named(
        'SELECT * FROM etag_data.drivers_update_state', pgsql['reposition'],
    )

    processed_drivers = select_named(
        """
        SELECT driver_id FROM etag_data.drivers_update_state
        INNER JOIN settings.driver_ids
        ON drivers_update_state.driver_id_id = driver_ids.driver_id_id
        WHERE updating IS NOT NULL AND updated_at IS NOT NULL
        """,
        pgsql['reposition'],
    )

    assert len(processed_drivers) == drivers_per_iteration or len(
        processed_drivers,
    ) == len(total_drivers)

    rows = select_named(
        """
        SELECT driver_id, valid_since, data, is_sequence_start
        FROM etag_data.states
        NATURAL JOIN settings.driver_ids
        ORDER BY driver_id, valid_since
        """,
        pgsql['reposition'],
    )

    expected = [
        {
            'data': {
                'state': {
                    'session_score': {
                        'items': [
                            {
                                'choices': [
                                    {
                                        'name': 'no_orders',
                                        'title': '{"tanker_key":"no_orders"}',
                                    },
                                ],
                                'custom_comment': {
                                    'is_available': False,
                                    'is_required': False,
                                },
                                'is_choice_required': False,
                                'score': 1,
                            },
                        ],
                        'session_id': 'LkQWjnegglewZ1p0',
                        'title': '{"tanker_key":"home"}',
                    },
                    'status': 'no_state',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 11, 26, 23, 0),
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 11, 27, 21, 0),
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 12, 2, 21, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.move"}',
                            'title': '{"tanker_key":"home.restrictions.move"}',
                        },
                    ],
                    'session_id': 'q2VolejRRPejNmGQ',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":1,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.move"}',
                            'title': '{"tanker_key":"home.restrictions.move"}',
                        },
                    ],
                    'session_id': 'q2VolejRRPejNmGQ',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 11, 27, 0, 0),
        },
        {
            'data': {
                'state': {
                    'active_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'client_attributes': {},
                    'finish_dialog': {
                        'body': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'location': {
                        'address': {
                            'subtitle': 'Postgresql',
                            'title': 'some address',
                        },
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.move"}',
                            'title': '{"tanker_key":"home.restrictions.move"}',
                        },
                    ],
                    'session_id': 'q2VolejRRPejNmGQ',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'status': 'active',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 12, 3, 0, 0),
        },
        {
            'data': {
                'state': {
                    'client_attributes': {},
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {
                'state': {
                    'client_attributes': {},
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 11, 27, 0, 0),
        },
        {
            'data': {
                'state': {
                    'client_attributes': {},
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                },
                'usages': {
                    'SuperSurge': {
                        'start_screen_usages': {'subtitle': '', 'title': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'home': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"home","period":"day"}',
                            'title': '{"tanker_key":"home","period":"day","used_count":0,"limit_count":2}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"home","period":"week"}',
                            'title': '{"tanker_key":"home"}',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"tanker_key":"my_district","period":"day"}'
                            ),
                            'title': '{"tanker_key":"my_district","period":"day","used_duration":0,"limit_duration":120}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"tanker_key":"my_district","period":"week"}'
                            ),
                            'title': '{"tanker_key":"my_district"}',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': '{"tanker_key":"poi","period":"day"}',
                            'title': '{"tanker_key":"poi","period":"day","used_count":0,"limit_count":1}',
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"tanker_key":"poi","period":"week"}',
                            'title': '{"tanker_key":"poi"}',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 12, 3, 0, 0),
        },
    ]

    if geo_hierarchy_filtration:
        # 1488_driverSS
        for idx in [0, 1, 2, 3]:
            del expected[idx]['data']['usages']['home']
            del expected[idx]['data']['usages']['poi']

        # uuid1_dbid777
        for idx in [7, 8, 9]:
            del expected[idx]['data']['usages']['home']

    assert rows == expected

    rows = select_named(
        """
        SELECT driver_id, valid_since, data FROM etag_data.offered_modes
        NATURAL JOIN settings.driver_ids
        ORDER BY driver_id, valid_since
        """,
        pgsql['reposition'],
    )

    expected = [
        {
            'data': {
                'SuperSurge': {
                    'restrictions': [],
                    'client_attributes': {},
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"SuperSurge"}',
                        'title': '{"tanker_key":"SuperSurge"}',
                    },
                    'permitted_work_modes': ['orders'],
                    'locations': {
                        '4q2VolejNlejNmGQ': {
                            'description': 'some text #1',
                            'destination_radius': 100.0,
                            'expires_at': '2018-11-27T22:00:00+00:00',
                            'image_id': 'icon_1',
                            'location': {
                                'id': '4q2VolejNlejNmGQ',
                                'point': [31.0, 61.0],
                                'address': {
                                    'title': 'some address_1',
                                    'subtitle': 'Postgresql_1',
                                },
                                'type': 'point',
                            },
                            'metadata': {'airport_queue_id': 'airport_q1'},
                            'offered_at': '2018-11-26T22:00:00+00:00',
                            'restrictions': [],
                        },
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {},
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {},
            'driver_id': '(dbid777,uuid1)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
    ]

    assert rows == expected

    rows = select_named(
        """
        SELECT driver_id, valid_since, data, is_sequence_start
        FROM etag_data.modes
        NATURAL JOIN settings.driver_ids
        ORDER BY driver_id, valid_since
        """,
        pgsql['reposition'],
    )

    expected = [
        {
            'data': {
                'home': {
                    'address_change_alert_dialog': {
                        'body': '{"tanker_key":"home","days":4}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '{"tanker_key":"home","next_change_date":1543536000}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'change_allowed': False,
                    'client_attributes': {},
                    'location': {
                        'is_valid': True,
                        'location': {
                            'address': {
                                'subtitle': 'city',
                                'title': 'home_address_1',
                            },
                            'id': '4q2VolejNlejNmGQ',
                            'point': [1.0, 2.0],
                            'type': 'point',
                        },
                        'name': 'home_name_1',
                    },
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'tutorial_body': '{"tanker_key":"home","day_limit":2}',
                    'type': 'single_point',
                },
                'my_district': {
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"my_district"}',
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'restrictions': [],
                    'start_screen_subtitle': (
                        '{"tanker_key":"my_district","is_limitless":false}'
                    ),
                    'start_screen_text': {
                        'subtitle': (
                            '{"tanker_key":"my_district","is_limitless":false}'
                        ),
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '90',
                        'submodes': {
                            '30': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                                'order': 1,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                            },
                            '60': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                                'order': 2,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                            },
                            '90': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                                'order': 3,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                            },
                        },
                    },
                    'tutorial_body': '{"tanker_key":"my_district","day_duration_limit":120,"week_duration_limit":360}',
                    'type': 'in_area',
                },
                'poi': {
                    'client_attributes': {},
                    'locations': {},
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"poi"}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.track"}',
                            'title': '{"tanker_key":"poi.restrictions.track"}',
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.move"}',
                            'title': '{"tanker_key":"poi.restrictions.move"}',
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'tutorial_body': (
                        '{"tanker_key":"poi","day_limit":1,"week_limit":7}'
                    ),
                    'type': 'free_point',
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {
                'home': {
                    'address_change_alert_dialog': {
                        'body': '{"tanker_key":"home","days":4}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}',
                    },
                    'change_allowed': True,
                    'client_attributes': {},
                    'location': {
                        'is_valid': True,
                        'location': {
                            'address': {
                                'subtitle': 'city',
                                'title': 'home_address_1',
                            },
                            'id': '4q2VolejNlejNmGQ',
                            'point': [1.0, 2.0],
                            'type': 'point',
                        },
                        'name': 'home_name_1',
                    },
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'tutorial_body': '{"tanker_key":"home","day_limit":2}',
                    'type': 'single_point',
                },
                'my_district': {
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"my_district"}',
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'restrictions': [],
                    'start_screen_subtitle': (
                        '{"tanker_key":"my_district","is_limitless":false}'
                    ),
                    'start_screen_text': {
                        'subtitle': (
                            '{"tanker_key":"my_district","is_limitless":false}'
                        ),
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '90',
                        'submodes': {
                            '30': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                                'order': 1,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                            },
                            '60': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                                'order': 2,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                            },
                            '90': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                                'order': 3,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                            },
                        },
                    },
                    'tutorial_body': '{"tanker_key":"my_district","day_duration_limit":120,"week_duration_limit":360}',
                    'type': 'in_area',
                },
                'poi': {
                    'client_attributes': {},
                    'locations': {},
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"poi"}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.track"}',
                            'title': '{"tanker_key":"poi.restrictions.track"}',
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.move"}',
                            'title': '{"tanker_key":"poi.restrictions.move"}',
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'tutorial_body': (
                        '{"tanker_key":"poi","day_limit":1,"week_limit":7}'
                    ),
                    'type': 'free_point',
                },
            },
            'driver_id': '(1488,driverSS)',
            'is_sequence_start': False,
            'valid_since': datetime(2018, 11, 29, 21, 0),
        },
        {
            'data': {
                'home': {
                    'address_change_alert_dialog': {
                        'body': '{"tanker_key":"home","days":4}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}',
                    },
                    'change_allowed': True,
                    'client_attributes': {},
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.move"}',
                            'title': '{"tanker_key":"home.restrictions.move"}',
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'tutorial_body': '{"tanker_key":"home","day_limit":2}',
                    'type': 'single_point',
                },
                'my_district': {
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"my_district"}',
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'restrictions': [],
                    'start_screen_subtitle': (
                        '{"tanker_key":"my_district","is_limitless":false}'
                    ),
                    'start_screen_text': {
                        'subtitle': (
                            '{"tanker_key":"my_district","is_limitless":false}'
                        ),
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '60',
                        'submodes': {
                            '30': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                                'order': 1,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                            },
                            '60': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                                'order': 2,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                            },
                            '90': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                                'order': 3,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                            },
                        },
                    },
                    'tutorial_body': '{"tanker_key":"my_district","day_duration_limit":120,"week_duration_limit":360}',
                    'type': 'in_area',
                },
            },
            'driver_id': '(dbid777,uuid)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
        {
            'data': {
                'home': {
                    'address_change_alert_dialog': {
                        'body': '{"tanker_key":"home","days":4}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}',
                    },
                    'change_allowed': True,
                    'client_attributes': {},
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"home"}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                            'text': '{"tanker_key":"home.restrictions.track"}',
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}'
                            ),
                        },
                    ],
                    'start_screen_subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"home","is_limitless":false,"day_limit":2}',
                        'title': '{"tanker_key":"home"}',
                    },
                    'tutorial_body': '{"tanker_key":"home","day_limit":2}',
                    'type': 'single_point',
                },
                'my_district': {
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"my_district"}',
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'restrictions': [],
                    'start_screen_subtitle': (
                        '{"tanker_key":"my_district","is_limitless":false}'
                    ),
                    'start_screen_text': {
                        'subtitle': (
                            '{"tanker_key":"my_district","is_limitless":false}'
                        ),
                        'title': '{"tanker_key":"my_district"}',
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '60',
                        'submodes': {
                            '30': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                                'order': 1,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"30"}',
                            },
                            '60': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                                'order': 2,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"60"}',
                            },
                            '90': {
                                'name': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                                'order': 3,
                                'restrictions': [],
                                'subname': '{"mode_tanker_key":"my_district","tanker_key":"90"}',
                            },
                        },
                    },
                    'tutorial_body': '{"tanker_key":"my_district","day_duration_limit":120,"week_duration_limit":360}',
                    'type': 'in_area',
                },
                'poi': {
                    'client_attributes': {},
                    'locations': {},
                    'permitted_work_modes': ['orders'],
                    'ready_panel': {
                        'subtitle': '{"tanker_key":"poi"}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'restrictions': [],
                    'start_screen_subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                    'start_screen_text': {
                        'subtitle': '{"tanker_key":"poi","is_limitless":false,"day_limit":1}',
                        'title': '{"tanker_key":"poi"}',
                    },
                    'tutorial_body': (
                        '{"tanker_key":"poi","day_limit":1,"week_limit":7}'
                    ),
                    'type': 'free_point',
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'is_sequence_start': True,
            'valid_since': datetime(2018, 11, 26, 22, 0),
        },
    ]

    if geo_hierarchy_filtration:
        # uuid1_dbid777
        del expected[3]['data']['home']

        # 1488_driverSS
        del expected[0]['data']['home']
        del expected[0]['data']['poi']
        # home would've no changes
        del expected[1]

    assert rows == expected

    stable_hashes = [
        {
            'exps_hash': 6925742255128569699,
            'tags_hash': 8463150082554682988,
            'driver_id_id': 2,
        },
        {'exps_hash': 0, 'tags_hash': -4266535750727032396, 'driver_id_id': 8},
        {'exps_hash': 0, 'tags_hash': -4701465161156252693, 'driver_id_id': 9},
    ]

    hashes.sort(key=lambda x: x['driver_id_id'])
    if stable_hash:
        assert hashes == stable_hashes
    else:
        assert hashes != stable_hashes


@pytest.mark.now('2018-11-26T22:00:00+0000')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'partial_update.sql'])
@pytest.mark.parametrize('stable_hash', [True, False])
@pytest.mark.uservice_oneshot
async def test_partial_etag_data_updater(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        pgsql,
        taxi_config,
        stable_hash,
):
    taxi_config.set_values(
        dict(
            REPOSITION_API_ETAG_DATA_UPDATER_CONFIG={
                'enabled': True,
                'update_defer_time_s': 300,
                'updating_state_ttl_s': 60,
                'drivers_per_iteration': 2,
                'drivers_bulk_size': 1,
                'parallel_threads_count': 1,
                'stable_hash': stable_hash,
            },
        ),
    )

    drivers = select_named(
        'SELECT * FROM etag_data.drivers_update_state'
        ' ORDER BY driver_id_id',
        pgsql['reposition'],
    )

    assert drivers == [
        {
            'driver_id_id': 2,
            'updated_at': datetime(2018, 11, 26, 21, 57),
            'updating': datetime(2018, 11, 26, 21, 57),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 8,
            'updated_at': datetime(2018, 11, 26, 21, 53),
            'updating': datetime(2018, 11, 26, 21, 53),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 9,
            'updated_at': datetime(2018, 11, 26, 21, 54),
            'updating': datetime(2018, 11, 26, 21, 54),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 10,
            'updated_at': datetime(2018, 11, 26, 21, 55),
            'updating': datetime(2018, 11, 26, 21, 55),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 11,
            'updated_at': datetime(2018, 11, 26, 21, 56),
            'updating': datetime(2018, 11, 26, 21, 56),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
    ]

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    assert {
        'error_failed_drivers': 0,
        'error_failed_job': 0,
        'error_failed_tasks': 0,
        'error_unknown_drivers': 0,
        'ok_partial_has_changes_drivers': 2,
        'ok_partial_no_changes_drivers': 0,
        'ok_partial_updated_drivers': 2,
        'ok_primary_updated_drivers': 0,
        'ok_secondary_updated_drivers': 0,
        'ok_successful_tasks': 1,
        'ok_total_drivers': 2,
        'ok_total_tasks': 1,
        'partial_update_latency_s': 390,
        'secondary_update_latency_s': 0,
    } == await taxi_reposition_api_monitor.get_metric('etag-data-updater')

    drivers = select_named(
        'SELECT * FROM etag_data.drivers_update_state'
        ' ORDER BY driver_id_id',
        pgsql['reposition'],
    )

    assert drivers == [
        {
            'driver_id_id': 2,
            'updated_at': datetime(2018, 11, 26, 21, 57),
            'updating': datetime(2018, 11, 26, 21, 57),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 8,
            'updated_at': datetime(2018, 11, 26, 22, 00),
            'updating': datetime(2018, 11, 26, 22, 00),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 9,
            'updated_at': datetime(2018, 11, 26, 22, 00),
            'updating': datetime(2018, 11, 26, 22, 00),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 10,
            'updated_at': datetime(2018, 11, 26, 21, 55),
            'updating': datetime(2018, 11, 26, 21, 55),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 11,
            'updated_at': datetime(2018, 11, 26, 21, 56),
            'updating': datetime(2018, 11, 26, 21, 56),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
    ]

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    assert {
        'error_failed_drivers': 0,
        'error_failed_job': 0,
        'error_failed_tasks': 0,
        'error_unknown_drivers': 0,
        'ok_partial_has_changes_drivers': 4,
        'ok_partial_no_changes_drivers': 0,
        'ok_partial_updated_drivers': 4,
        'ok_primary_updated_drivers': 0,
        'ok_secondary_updated_drivers': 0,
        'ok_successful_tasks': 2,
        'ok_total_drivers': 4,
        'ok_total_tasks': 2,
        'partial_update_latency_s': 270,
        'secondary_update_latency_s': 0,
    } == await taxi_reposition_api_monitor.get_metric('etag-data-updater')

    drivers = select_named(
        'SELECT * FROM etag_data.drivers_update_state'
        ' ORDER BY driver_id_id',
        pgsql['reposition'],
    )

    assert drivers == [
        {
            'driver_id_id': 2,
            'updated_at': datetime(2018, 11, 26, 21, 57),
            'updating': datetime(2018, 11, 26, 21, 57),
            'tags_revision': None,
            'tags_hash': None,
            'exps_revision': None,
            'exps_hash': None,
        },
        {
            'driver_id_id': 8,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 9,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 10,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 11,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': None,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
    ]
