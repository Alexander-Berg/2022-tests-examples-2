from datetime import datetime
import socket

import pytest

from . import tags_cache_utils as tags_cache
from .reposition_select import select_named
from .reposition_select import select_table_named


host = socket.gethostbyaddr(socket.gethostname())[0]

ETAG_DATA_UPDATER_CONFIG = {
    'update_defer_time': 300,
    'updating_state_ttl': 60,
    'drivers_per_iteration': 4,
    'drivers_bulk_size': 2,
    'parallel_threads_count': 1,
}


@pytest.mark.config(REPOSITION_ETAG_DATA_UPDATER_ENABLED=False)
@pytest.mark.pgsql('reposition', files=['drivers.sql'])
@pytest.mark.now('2018-11-26T12:00:00+0000')
def test_disabled(taxi_reposition, pgsql):
    assert (
        taxi_reposition.post(
            '/service/tests-control',
            {'task_name': 'etag-data-updater@' + host},
        ).status_code
        == 200
    )

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


@pytest.mark.config(
    #  REPOSITION_EVENT_USAGES_EXP_HASH_CALC_ENABLED=False,
    REPOSITION_ETAG_DATA_UPDATER_ENABLED=True,
    REPOSITION_ETAG_DATA_UPDATER_CONFIG=ETAG_DATA_UPDATER_CONFIG,
    TAGS_CACHE_SETTINGS=tags_cache.create_tags_cache_config(),
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid777_uuid', 'poi_prohibited'),
        ('dbid_uuid', 'dbid777_uuid', 'permit_home_move'),
        ('dbid_uuid', '1488_driverSS', 'prohibit_home_move'),
        ('dbid_uuid', '1488_driverSS', 'permit_poi_move'),
        ('dbid_uuid', 'dbid777_uuid1', 'prohibit_poi_track'),
    ],
    topic_relations=[
        ('reposition', 'poi_prohibited'),
        ('reposition', 'permit_home_move'),
        ('reposition', 'prohibit_home_move'),
        ('reposition', 'permit_poi_move'),
        ('reposition', 'prohibit_poi_track'),
    ],
)
@pytest.mark.now('2018-11-26T22:00:00+0000')
@pytest.mark.parametrize('geo_hierarchy_filtration', [False, True])
def test_etag_data_updater(
        taxi_reposition,
        pgsql,
        mockserver,
        experiments3,
        load,
        geo_hierarchy_filtration,
        testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    experiments3.add_experiment(
        name='reposition_highlight_alternative_submode',
        consumers=['reposition/driver_locations'],
        match={
            'consumers': ['reposition/driver_locations'],
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'driver_id',
                    'value': 'driverSS',
                },
            },
            'enabled': True,
        },
        clauses=[],
        default_value={'modes_submodes': {'my_district': '90'}},
    )

    queries = [
        load('drivers.sql'),
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
        taxi_reposition.post(
            '/service/tests-control',
            {'task_name': 'etag-data-updater@' + host},
        ).status_code
        == 200
    )

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
    assert len(processed_drivers) == (
        ETAG_DATA_UPDATER_CONFIG['drivers_per_iteration']
    ) or len(processed_drivers) == len(total_drivers)

    rows = select_named(
        """
        SELECT driver_id, valid_since, data, is_sequence_start
        FROM etag_data.states
        INNER JOIN settings.driver_ids
        ON states.driver_id_id = driver_ids.driver_id_id
        ORDER BY driver_id, revision
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
                                        'title': (
                                            '{"tanker_key":"no_orders"}\n'
                                        ),
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
                        'title': '{"tanker_key":"home"}\n',
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
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
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
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day",'
                                '"tanker_key":"my_district"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 26, 23, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day",'
                                '"tanker_key":"my_district"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 27, 21, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {'status': 'no_state'},
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day",'
                                '"tanker_key":"my_district"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 12, 2, 21, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {
                    'location': {
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'address': {
                            'title': 'some address',
                            'subtitle': 'Postgresql',
                        },
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'session_id': 'q2VolejRRPejNmGQ',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'status': 'active',
                    'active_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'finish_dialog': {
                        'title': '{"tanker_key":"home"}\n',
                        'body': '{"tanker_key":"home"}\n',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":1}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
            'is_sequence_start': True,
        },
        {
            'data': {
                'state': {
                    'location': {
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'address': {
                            'title': 'some address',
                            'subtitle': 'Postgresql',
                        },
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'session_id': 'q2VolejRRPejNmGQ',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'status': 'active',
                    'active_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'finish_dialog': {
                        'title': '{"tanker_key":"home"}\n',
                        'body': '{"tanker_key":"home"}\n',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 27, 0, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {
                    'location': {
                        'id': '4q2Volej25ejNmGQ',
                        'point': [3.0, 4.0],
                        'address': {
                            'title': 'some address',
                            'subtitle': 'Postgresql',
                        },
                        'type': 'point',
                    },
                    'mode_id': 'home',
                    'session_id': 'q2VolejRRPejNmGQ',
                    'state_id': 'q2VolejRRPejNmGQ_active',
                    'started_at': '2018-11-26T20:11:00.540859+00:00',
                    'finish_until': '2018-11-26T22:11:00.540859+00:00',
                    'status': 'active',
                    'active_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'finish_dialog': {
                        'title': '{"tanker_key":"home"}\n',
                        'body': '{"tanker_key":"home"}\n',
                    },
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.track"}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 12, 3, 0, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
            'is_sequence_start': True,
        },
        {
            'data': {
                'state': {
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'valid_since': datetime(2018, 11, 27, 0, 0),
            'is_sequence_start': False,
        },
        {
            'data': {
                'state': {
                    'session_id': '3GWpmbkRRNazJn4K',
                    'state_id': '3GWpmbkRRNazJn4K_disabled',
                    'status': 'disabled',
                    'client_attributes': {},
                },
                'usages': {
                    'home': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":2,"period":"day",'
                                '"tanker_key":"home","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"home"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"home"}\n',
                            'title': '{"tanker_key":"home"}\n',
                        },
                    },
                    'poi': {
                        'start_screen_usages': {
                            'title': (
                                '{"limit_count":1,"period":"day",'
                                '"tanker_key":"poi","used_count":0}\n'
                            ),
                            'subtitle': (
                                '{"period":"day","tanker_key":"poi"}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': '{"period":"week","tanker_key":"poi"}\n',
                            'title': '{"tanker_key":"poi"}\n',
                        },
                    },
                    'SuperSurge': {
                        'start_screen_usages': {'title': '', 'subtitle': ''},
                        'usage_allowed': True,
                        'usage_limit_dialog': {'body': '', 'title': ''},
                    },
                    'my_district': {
                        'start_screen_usages': {
                            'subtitle': (
                                '{"period":"day","tanker_key":"my_district"}\n'
                            ),
                            'title': (
                                '{"limit_duration":120,"period":"day",'
                                '"tanker_key":"my_district",'
                                '"used_duration":0}\n'
                            ),
                        },
                        'usage_allowed': True,
                        'usage_limit_dialog': {
                            'body': (
                                '{"period":"week",'
                                '"tanker_key":"my_district"}\n'
                            ),
                            'title': '{"tanker_key":"my_district"}\n',
                        },
                    },
                },
            },
            'driver_id': '(dbid777,uuid1)',
            'valid_since': datetime(2018, 12, 3, 0, 0),
            'is_sequence_start': False,
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
        INNER JOIN settings.driver_ids
        ON offered_modes.driver_id_id = driver_ids.driver_id_id
        ORDER BY driver_id, revision
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
                        'subtitle': '{"tanker_key":"SuperSurge"}\n',
                        'title': '{"tanker_key":"SuperSurge"}\n',
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
        INNER JOIN settings.driver_ids
        ON modes.driver_id_id = driver_ids.driver_id_id
        ORDER BY driver_id, revision
        """,
        pgsql['reposition'],
    )

    expected = [
        {
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
            'data': {
                'poi': {
                    'type': 'free_point',
                    'locations': {},
                    'ready_panel': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': '{"tanker_key":"poi"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.move"}\n'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.move"}\n',
                            'title': (
                                '{"tanker_key":"poi.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'tutorial_body': (
                        '{"day_limit":1,"tanker_key":'
                        '"poi","week_limit":7}\n'
                    ),
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":1,'
                        '"is_limitless":false,"tanker_key":"poi"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': (
                            '{"day_limit":1,'
                            '"is_limitless":false,"tanker_key":"poi"}\n'
                        ),
                    },
                },
                'home': {
                    'type': 'single_point',
                    'location': {
                        'name': 'home_name_1',
                        'is_valid': True,
                        'location': {
                            'type': 'point',
                            'id': '4q2VolejNlejNmGQ',
                            'point': [1.0, 2.0],
                            'address': {
                                'title': 'home_address_1',
                                'subtitle': 'city',
                            },
                        },
                    },
                    'ready_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'title': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                        },
                    ],
                    'tutorial_body': '{"day_limit":2,"tanker_key":"home"}\n',
                    'change_allowed': False,
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":2,'
                        '"is_limitless":false,"tanker_key":"home"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': (
                            '{"day_limit":2,'
                            '"is_limitless":false,"tanker_key":"home"}\n'
                        ),
                    },
                    'address_change_alert_dialog': {
                        'body': '{"days":4,"tanker_key":"home"}\n',
                        'title': '{"tanker_key":"home"}\n',
                    },
                    'address_change_forbidden_dialog': {
                        'body': (
                            '{"next_change_date":1543536000'
                            ',"tanker_key":"home"}\n'
                        ),
                        'title': '{"tanker_key":"home"}\n',
                    },
                },
                'my_district': {
                    'type': 'in_area',
                    'ready_panel': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': '{"tanker_key":"my_district"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [],
                    'tutorial_body': (
                        '{"day_duration_limit":120,'
                        '"tanker_key":"my_district",'
                        '"week_duration_limit":360}\n'
                    ),
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'start_screen_subtitle': (
                        '{"is_limitless":false,'
                        '"tanker_key":"my_district"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': (
                            '{"is_limitless":false,'
                            '"tanker_key":"my_district"}\n'
                        ),
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '90',
                        'submodes': {
                            '30': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'order': 1,
                                'restrictions': [],
                            },
                            '60': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'order': 2,
                                'restrictions': [],
                            },
                            '90': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'order': 3,
                                'restrictions': [],
                            },
                        },
                    },
                },
            },
            'is_sequence_start': True,
        },
        {
            'driver_id': '(1488,driverSS)',
            'valid_since': datetime(2018, 11, 29, 21, 0),
            'data': {
                'poi': {
                    'type': 'free_point',
                    'locations': {},
                    'ready_panel': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': '{"tanker_key":"poi"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"poi.restrictions.track"}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"poi.restrictions.move"}\n'
                            ),
                            'text': '{"tanker_key":"poi.restrictions.move"}\n',
                            'title': (
                                '{"tanker_key":"poi.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'tutorial_body': (
                        '{"day_limit":1,"tanker_key":'
                        '"poi","week_limit":7}\n'
                    ),
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":1,'
                        '"is_limitless":false,"tanker_key":"poi"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': (
                            '{"day_limit":1,'
                            '"is_limitless":false,"tanker_key":"poi"}\n'
                        ),
                    },
                },
                'home': {
                    'type': 'single_point',
                    'location': {
                        'name': 'home_name_1',
                        'is_valid': True,
                        'location': {
                            'type': 'point',
                            'id': '4q2VolejNlejNmGQ',
                            'point': [1.0, 2.0],
                            'address': {
                                'title': 'home_address_1',
                                'subtitle': 'city',
                            },
                        },
                    },
                    'ready_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'title': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                        },
                    ],
                    'tutorial_body': '{"day_limit":2,"tanker_key":"home"}\n',
                    'change_allowed': True,
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":2,'
                        '"is_limitless":false,"tanker_key":"home"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': (
                            '{"day_limit":2,'
                            '"is_limitless":false,"tanker_key":"home"}\n'
                        ),
                    },
                    'address_change_alert_dialog': {
                        'body': '{"days":4,"tanker_key":"home"}\n',
                        'title': '{"tanker_key":"home"}\n',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}\n',
                    },
                },
                'my_district': {
                    'type': 'in_area',
                    'ready_panel': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': '{"tanker_key":"my_district"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [],
                    'tutorial_body': (
                        '{"day_duration_limit":120,'
                        '"tanker_key":"my_district",'
                        '"week_duration_limit":360}\n'
                    ),
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'start_screen_subtitle': (
                        '{"is_limitless":false,'
                        '"tanker_key":"my_district"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': (
                            '{"is_limitless":false,'
                            '"tanker_key":"my_district"}\n'
                        ),
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '90',
                        'submodes': {
                            '30': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'order': 1,
                                'restrictions': [],
                            },
                            '60': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'order': 2,
                                'restrictions': [],
                            },
                            '90': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'order': 3,
                                'restrictions': [],
                            },
                        },
                    },
                },
            },
            'is_sequence_start': False,
        },
        {
            'driver_id': '(dbid777,uuid)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
            'data': {
                'home': {
                    'type': 'single_point',
                    'ready_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'title': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                        },
                        {
                            'image_id': 'keep_moving',
                            'short_text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'text': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                            'title': (
                                '{"tanker_key":"home.restrictions.move"}\n'
                            ),
                        },
                    ],
                    'tutorial_body': '{"day_limit":2,"tanker_key":"home"}\n',
                    'change_allowed': True,
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":2,'
                        '"is_limitless":false,"tanker_key":"home"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': (
                            '{"day_limit":2,'
                            '"is_limitless":false,"tanker_key":"home"}\n'
                        ),
                    },
                    'address_change_alert_dialog': {
                        'body': '{"days":4,"tanker_key":"home"}\n',
                        'title': '{"tanker_key":"home"}\n',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}\n',
                    },
                },
                'my_district': {
                    'type': 'in_area',
                    'ready_panel': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': '{"tanker_key":"my_district"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [],
                    'tutorial_body': (
                        '{"day_duration_limit":120,'
                        '"tanker_key":"my_district",'
                        '"week_duration_limit":360}\n'
                    ),
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'start_screen_subtitle': (
                        '{"is_limitless":false,'
                        '"tanker_key":"my_district"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': (
                            '{"is_limitless":false,'
                            '"tanker_key":"my_district"}\n'
                        ),
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '60',
                        'submodes': {
                            '30': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'order': 1,
                                'restrictions': [],
                            },
                            '60': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'order': 2,
                                'restrictions': [],
                            },
                            '90': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'order': 3,
                                'restrictions': [],
                            },
                        },
                    },
                },
            },
            'is_sequence_start': True,
        },
        {
            'driver_id': '(dbid777,uuid1)',
            'valid_since': datetime(2018, 11, 26, 22, 0),
            'data': {
                'poi': {
                    'type': 'free_point',
                    'locations': {},
                    'ready_panel': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': '{"tanker_key":"poi"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [],
                    'tutorial_body': (
                        '{"day_limit":1,"tanker_key":"poi",'
                        '"week_limit":7}\n'
                    ),
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":1,'
                        '"is_limitless":false,"tanker_key":"poi"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"poi"}\n',
                        'subtitle': (
                            '{"day_limit":1,'
                            '"is_limitless":false,"tanker_key":"poi"}\n'
                        ),
                    },
                },
                'home': {
                    'type': 'single_point',
                    'ready_panel': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': '{"tanker_key":"home"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [
                        {
                            'image_id': 'follow_track',
                            'short_text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'text': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                            'title': (
                                '{'
                                '"tanker_key":"home.restrictions.track"'
                                '}\n'
                            ),
                        },
                    ],
                    'tutorial_body': '{"day_limit":2,"tanker_key":"home"}\n',
                    'change_allowed': True,
                    'client_attributes': {},
                    'start_screen_subtitle': (
                        '{"day_limit":2,'
                        '"is_limitless":false,"tanker_key":"home"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"home"}\n',
                        'subtitle': (
                            '{"day_limit":2,'
                            '"is_limitless":false,"tanker_key":"home"}\n'
                        ),
                    },
                    'address_change_alert_dialog': {
                        'body': '{"days":4,"tanker_key":"home"}\n',
                        'title': '{"tanker_key":"home"}\n',
                    },
                    'address_change_forbidden_dialog': {
                        'body': '',
                        'title': '{"tanker_key":"home"}\n',
                    },
                },
                'my_district': {
                    'type': 'in_area',
                    'ready_panel': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': '{"tanker_key":"my_district"}\n',
                    },
                    'permitted_work_modes': ['orders'],
                    'restrictions': [],
                    'tutorial_body': (
                        '{"day_duration_limit":120,'
                        '"tanker_key":"my_district",'
                        '"week_duration_limit":360}\n'
                    ),
                    'client_attributes': {},
                    'highlighted_radius': 91000,
                    'max_allowed_radius': 180000,
                    'min_allowed_radius': 2000,
                    'start_screen_subtitle': (
                        '{"is_limitless":false,'
                        '"tanker_key":"my_district"}\n'
                    ),
                    'start_screen_text': {
                        'title': '{"tanker_key":"my_district"}\n',
                        'subtitle': (
                            '{"is_limitless":false,'
                            '"tanker_key":"my_district"}\n'
                        ),
                    },
                    'submodes_info': {
                        'highlighted_submode_id': '60',
                        'submodes': {
                            '30': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"30"}\n'
                                ),
                                'order': 1,
                                'restrictions': [],
                            },
                            '60': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"60"}\n'
                                ),
                                'order': 2,
                                'restrictions': [],
                            },
                            '90': {
                                'name': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'subname': (
                                    '{"mode_tanker_key":"my_district"'
                                    ',"tanker_key":"90"}\n'
                                ),
                                'order': 3,
                                'restrictions': [],
                            },
                        },
                    },
                },
            },
            'is_sequence_start': True,
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


@pytest.mark.pgsql('reposition', files=['drivers.sql', 'partial_update.sql'])
@pytest.mark.config(
    REPOSITION_ETAG_DATA_UPDATER_ENABLED=True,
    REPOSITION_ETAG_DATA_UPDATER_CONFIG={
        'update_defer_time': 300,
        'updating_state_ttl': 60,
        'drivers_per_iteration': 2,
        'drivers_bulk_size': 1,
        'parallel_threads_count': 1,
    },
)
@pytest.mark.now('2018-11-26T22:00:00+0000')
def test_partial_etag_data_updater(
        taxi_reposition, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/client_notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': '123123'}

    @testpoint('client_notify_pushes')
    def client_notify_pushes(data):
        for i in range(data['count']):
            mock_client_notify.wait_call()

    drivers = sorted(
        select_named(
            'SELECT * FROM etag_data.drivers_update_state',
            pgsql['reposition'],
        ),
        key=lambda k: k['driver_id_id'],
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
        taxi_reposition.post(
            '/service/tests-control',
            {'task_name': 'etag-data-updater@' + host},
        ).status_code
        == 200
    )

    drivers = sorted(
        select_named(
            'SELECT * FROM etag_data.drivers_update_state',
            pgsql['reposition'],
        ),
        key=lambda k: k['driver_id_id'],
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
            'tags_revision': 0,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 9,
            'updated_at': datetime(2018, 11, 26, 22, 00),
            'updating': datetime(2018, 11, 26, 22, 00),
            'tags_revision': 0,
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
        taxi_reposition.post(
            '/service/tests-control',
            {'task_name': 'etag-data-updater@' + host},
        ).status_code
        == 200
    )

    drivers = sorted(
        select_named(
            'SELECT * FROM etag_data.drivers_update_state',
            pgsql['reposition'],
        ),
        key=lambda k: k['driver_id_id'],
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
            'tags_revision': 0,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 9,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': 0,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 10,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': 0,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
        {
            'driver_id_id': 11,
            'updated_at': datetime(2018, 11, 26, 22, 0),
            'updating': datetime(2018, 11, 26, 22, 0),
            'tags_revision': 0,
            'tags_hash': 0,
            'exps_revision': -1,
            'exps_hash': 0,
        },
    ]
