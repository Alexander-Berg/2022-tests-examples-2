# pylint: disable=too-many-lines,import-only-modules
from datetime import datetime
from datetime import timedelta
import json

import pytest

from .utils import select_named
from .utils import select_table


async def test_get_modes_types(taxi_reposition_api):
    response = await taxi_reposition_api.get('/v1/admin/modes/types')

    assert response.status_code == 200
    assert response.json() == {'mode_types': ['ToPoint', 'InArea']}


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize(
    'offer,'
    'display_rules,'
    'bonus,'
    'submodes,'
    'tag_settings,'
    'geo_nodes_settings,'
    'work_modes',
    [
        pytest.param(False, False, None, False, None, None, None),
        pytest.param(
            True,
            True,
            'short',
            True,
            'permitted',
            'prohibited',
            ['driver-fix'],
        ),
        pytest.param(
            True, True, 'long', True, 'prohibited', 'permitted', None,
        ),
    ],
)
async def test_get(
        taxi_reposition_api,
        pgsql,
        load,
        offer,
        display_rules,
        bonus,
        submodes,
        tag_settings,
        geo_nodes_settings,
        work_modes,
):
    queries = [load('mode_home.sql')]

    if offer:
        queries.append(load('mode_offer.sql'))
    if display_rules:
        queries.append(load('display_rules.sql'))
    if bonus:
        query = 'home_bonus_long.sql' if bonus == 'long' else 'home_bonus.sql'
        queries.append(load(query))
    if submodes:
        queries.append(load('submodes_home.sql'))
        queries.append(load('submodes_display_rules.sql'))
    if tag_settings:
        queries.append(load('home_tag_' + tag_settings + '.sql'))
    if geo_nodes_settings:
        queries.append(load('home_geo_nodes_' + geo_nodes_settings + '.sql'))
    if work_modes:
        queries.append(load('home_work_modes.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.get('/v1/admin/modes')

    assert response.status_code == 200

    data = {
        'home': {
            'backend_only': False,
            'display_rules': [],
            'allowed_distance': {'min': 2000, 'max': 180000},
            'mode_type': 'ToPoint',
            'client_attributes': {'dead10cc': 'deadbeef'},
            'experimental': False,
        },
    }

    if offer:
        data['home']['backend_only'] = True
        data['home']['offer_radius'] = 111

    if display_rules:
        data['home']['display_rules'] = [
            {'image': 'keep_moving', 'text': 'move'},
            {'image': 'path', 'text': 'follow_track'},
        ]

    if bonus:
        period = (
            timedelta(days=10).total_seconds()
            if bonus == 'long'
            else timedelta(minutes=10).total_seconds()
        )
        data['home']['completion_bonus'] = {
            'period': period,
            'image_id': 'image',
            'tanker_key': 'bonus.tanker',
        }

    if submodes:
        data['home']['submodes'] = {
            'names': ['fast', 'slow', 'veryslow'],
            'default': 'fast',
            'highlight': 'fast',
            'display_rules': {
                'fast': [
                    {'image': 'move', 'text': 'home.restrictions.move'},
                    {'image': 'track', 'text': 'home.restrictions.track'},
                ],
                'slow': [
                    {'image': 'track', 'text': 'home.restrictions.track'},
                ],
            },
        }

    if tag_settings:
        field = 'tags_' + tag_settings
        data['home'][field] = [tag_settings]

    if geo_nodes_settings:
        field = 'geo_nodes_' + geo_nodes_settings
        data['home'][field] = [geo_nodes_settings]

    data['home']['work_modes'] = work_modes if work_modes else ['orders']

    assert response.json() == data


async def test_put_bad_offer_radius(taxi_reposition_api):
    data = {
        'backend_only': True,
        'display_rules': [],
        'allowed_distance': {'min': 2000, 'max': 180000},
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Offer radius is required for backend-only mode',
    }


@pytest.mark.parametrize('names', [(['fast', 'slow']), ([])])
async def test_put_bad_default_submode(taxi_reposition_api, names):
    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'submodes': {'names': names, 'default': 'fast_slow'},
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Default submode is not matched',
    }


async def test_put_bad_highlighted_submode(taxi_reposition_api):
    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'submodes': {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'fast_slow',
        },
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Highlighted submode is not matched',
    }


@pytest.mark.pgsql('reposition')
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.parametrize(
    'display_rules,'
    'geo_nodes_settings,'
    'tag_settings,'
    'submodes,'
    'mode_type,'
    'completion_bonuses',
    (
        (True, None, None, False, 'ToPoint', True),
        (False, None, None, True, 'InArea', False),
        (True, 'permitted', 'prohibited', False, 'InArea', True),
        (False, 'prohibited', 'permitted', False, 'ToPoint', False),
    ),
)
async def test_put(
        taxi_reposition_api,
        pgsql,
        mockserver,
        tag_settings,
        geo_nodes_settings,
        display_rules,
        submodes,
        mode_type,
        completion_bonuses,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     if 'random' in tag:
    #         return mockserver.make_response(
    #             json.dumps({'items': [], 'limit': 0, 'offset': 0}),
    #             content_type='application/json',
    #         )
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': (
            [
                {
                    'image': 'keep_moving_1',
                    'text': 'move_1',
                    'tags_permitted': None,
                    'tags_prohibited': None,
                },
                {
                    'image': 'keep_moving_2',
                    'text': 'move_2',
                    'tags_permitted': None,
                    'tags_prohibited': None,
                },
            ]
            if display_rules
            else []
        ),
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': mode_type,
    }

    if completion_bonuses:
        data['completion_bonus'] = {
            'period': 600,
            'image_id': 'bonus_image',
            'tanker_key': 'bonus_translation',
        }

    if submodes:
        data['submodes'] = {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'slow',
        }

    if tag_settings:
        field = 'tags_' + tag_settings
        data[field] = [tag_settings]

    if geo_nodes_settings:
        field = 'geo_nodes_' + geo_nodes_settings
        data[field] = [geo_nodes_settings]

    data['work_modes'] = ['orders']

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    tags_permitted = ['permitted'] if tag_settings == 'permitted' else None
    tags_prohibited = ['prohibited'] if tag_settings == 'prohibited' else None

    geo_nodes_permitted = (
        ['permitted'] if geo_nodes_settings == 'permitted' else None
    )
    geo_nodes_prohibited = (
        ['prohibited'] if geo_nodes_settings == 'prohibited' else None
    )

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            500,
            100000,
            mode_type,
            tags_permitted,
            tags_prohibited,
            None,
            None,
            None,
            False,
            ['orders'],
            geo_nodes_permitted,
            geo_nodes_prohibited,
        ),
    ]

    rows = select_table(
        'config.display_rules', 'display_id', pgsql['reposition'],
    )

    if display_rules:
        assert rows == [
            (1, 1, 'keep_moving_1', 'move_1', None, None, None),
            (2, 1, 'keep_moving_2', 'move_2', None, None, None),
        ]
    else:
        assert rows == []

    rows = select_table(
        'config.completion_bonuses', 'mode_id', pgsql['reposition'],
    )

    if completion_bonuses:
        assert rows == [
            (1, timedelta(0, 600), 'bonus_image', 'bonus_translation'),
        ]
    else:
        assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    if submodes:
        assert rows == [
            (1, 'fast', 1, True, 0, False),
            (2, 'slow', 1, False, 1, True),
        ]
    else:
        assert rows == []

    upd_requests = select_named(
        """
        SELECT
            update_state,
            update_modes,
            update_offered_modes,
            created_at,
            started_at,
            finished_at,
            cancelled
        FROM
            etag_data.update_requests
        """,
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': True,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize(
    'tag_settings,'
    'geo_nodes_settings,'
    'work_modes,'
    'display_rules,'
    'submodes,'
    'completion_bonuses,'
    'mode_type',
    [
        (None, None, None, False, False, False, 'ToPoint'),
        (
            'permitted',
            'prohibited',
            ['driver-fix'],
            True,
            False,
            False,
            'InArea',
        ),
        (
            'prohibited',
            'permitted',
            ['driver-fix'],
            False,
            True,
            False,
            'ToPoint',
        ),
        ('prohibited', 'permitted', None, False, True, True, 'InArea'),
    ],
)
async def test_put_override(
        taxi_reposition_api,
        pgsql,
        mockserver,
        tag_settings,
        geo_nodes_settings,
        work_modes,
        display_rules,
        submodes,
        completion_bonuses,
        mode_type,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {
            'reposition': [
                'permitted',
                'prohibited',
                'dr_1_permitted_tag',
                'dr_2_prohibited_tag_1',
                'dr_2_prohibited_tag_2',
            ],
        }

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': [{'image': 'keep_moving', 'text': 'move'}],
        'completion_bonus': {
            'period': 300,
            'image_id': 'bonus_image',
            'tanker_key': 'bonus_translation',
        },
        'allowed_distance': {'min': 2000, 'max': 180000},
        'mode_type': 'InArea',
        'submodes': {'names': ['slow'], 'default': 'slow'},
        'tags_permitted': ['permitted'],
        'geo_nodes_prohibited': ['prohibited'],
        'work_modes': ['anything'],
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            2000,
            180000,
            'InArea',
            ['permitted'],
            None,
            None,
            None,
            None,
            False,
            ['anything'],
            None,
            ['prohibited'],
        ),
    ]

    rows = select_table(
        'config.display_rules', 'display_id', pgsql['reposition'],
    )

    assert rows == [(1, 1, 'keep_moving', 'move', None, None, None)]

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    assert rows == [(1, 'slow', 1, True, 0, True)]

    data = {
        'backend_only': True,
        'display_rules': [],
        'offer_radius': 666,
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': mode_type,
    }

    if display_rules:
        data['display_rules'] = [
            {
                'image': 'path_1',
                'text': 'follow_track_1',
                'tags_permitted': ['dr_1_permitted_tag'],
                'tags_prohibited': [],
            },
            {
                'image': 'path_2',
                'text': 'follow_track_2',
                'tags_permitted': None,
                'tags_prohibited': [
                    'dr_2_prohibited_tag_1',
                    'dr_2_prohibited_tag_2',
                ],
            },
        ]

    if completion_bonuses:
        data['completion_bonus'] = {
            'period': 600,
            'image_id': 'overridden_image',
            'tanker_key': 'overridden_translation',
        }

    if submodes:
        data['submodes'] = {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'fast',
        }

    if tag_settings:
        field = 'tags_' + tag_settings
        data[field] = [tag_settings]

    if geo_nodes_settings:
        field = 'geo_nodes_' + geo_nodes_settings
        data[field] = [geo_nodes_settings]

    if work_modes:
        data['work_modes'] = work_modes

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    tags_permitted = ['permitted'] if tag_settings == 'permitted' else None
    tags_prohibited = ['prohibited'] if tag_settings == 'prohibited' else None

    geo_nodes_permitted = (
        ['permitted'] if geo_nodes_settings == 'permitted' else None
    )
    geo_nodes_prohibited = (
        ['prohibited'] if geo_nodes_settings == 'prohibited' else None
    )

    assert rows == [
        (
            1,
            'home',
            True,
            666,
            500,
            100000,
            mode_type,
            tags_permitted,
            tags_prohibited,
            None,
            None,
            None,
            False,
            work_modes,
            geo_nodes_permitted,
            geo_nodes_prohibited,
        ),
    ]

    rows = select_table(
        'config.display_rules', 'display_id', pgsql['reposition'],
    )

    if display_rules:
        assert rows == [
            (
                2,
                1,
                'path_1',
                'follow_track_1',
                None,
                ['dr_1_permitted_tag'],
                [],
            ),
            (
                3,
                1,
                'path_2',
                'follow_track_2',
                None,
                None,
                ['dr_2_prohibited_tag_1', 'dr_2_prohibited_tag_2'],
            ),
        ]
    else:
        assert rows == []

    rows = select_table(
        'config.completion_bonuses', 'mode_id', pgsql['reposition'],
    )

    if completion_bonuses:
        assert rows == [
            (
                1,
                timedelta(0, 600),
                'overridden_image',
                'overridden_translation',
            ),
        ]
    else:
        assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    if submodes:
        assert rows == [
            (1, 'slow', 1, False, 1, False),
            (2, 'fast', 1, True, 0, True),
        ]
    else:
        assert rows == []


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'submodes_home.sql',
        'submodes_display_rules.sql',
        'active_session.sql',
    ],
)
@pytest.mark.parametrize('conflict', [None, False, True])
async def test_put_submodes_override_with_active_reference(
        taxi_reposition_api, pgsql, mockserver, conflict,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'submodes': {
            'names': ['superslow', 'slow', 'fast'],
            'default': 'slow',
        },
    }

    if conflict is False:
        data['submodes'] = {
            'names': ['slow', 'superslow'],
            'default': 'superslow',
        }
    elif conflict is True:
        del data['submodes']

    backup = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    if conflict is None:
        assert response.status_code == 200
        assert rows == [
            (1, 'superslow', 1, False, 0, False),
            (1001, 'fast', 1, False, 2, False),
            (1002, 'slow', 1, True, 1, True),
        ]
    else:
        assert response.status_code == 400
        assert rows == backup
        assert response.json() == {
            'code': '400',
            'message': (
                'Unable to delete submode, possibly it has active references: '
            ),
        }


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('has_display_rules', [False, True])
async def test_put_submodes_display_rules(
        taxi_reposition_api, pgsql, mockserver, has_display_rules,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'submodes': {'names': ['fast', 'slow'], 'default': 'fast'},
    }

    if has_display_rules:
        data['submodes']['display_rules'] = {
            'fast': [
                {'image': 'keep_moving_1', 'text': 'move_1'},
                {'image': 'keep_moving_2', 'text': 'move_2'},
            ],
            'slow': [{'image': 'keep_moving', 'text': 'move'}],
        }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    assert rows == [
        (1, 'fast', 1, True, 0, True),
        (2, 'slow', 1, False, 1, False),
    ]

    if has_display_rules:
        rows = select_table(
            'config.display_rules', 'image', pgsql['reposition'],
        )

        for idx, item in enumerate(rows):
            rows[idx] = list(item)[1:]

        assert rows == [
            [1, 'keep_moving', 'move', 2, None, None],
            [1, 'keep_moving_1', 'move_1', 1, None, None],
            [1, 'keep_moving_2', 'move_2', 1, None, None],
        ]


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('has_display_rules', [False, True])
async def test_put_override_submodes_display_rules(
        taxi_reposition_api, pgsql, mockserver, has_display_rules,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': [{'image': 'keep_moving', 'text': 'move'}],
        'allowed_distance': {'min': 2000, 'max': 180000},
        'submodes': {'names': ['fast', 'slow'], 'default': 'fast'},
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            2000,
            180000,
            'ToPoint',
            None,
            None,
            None,
            None,
            None,
            False,
            None,
            None,
            None,
        ),
    ]

    rows = select_table(
        'config.display_rules', 'display_id', pgsql['reposition'],
    )

    assert rows == [(1, 1, 'keep_moving', 'move', None, None, None)]

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    assert rows == [
        (1, 'fast', 1, True, 0, True),
        (2, 'slow', 1, False, 1, False),
    ]

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
    }

    if has_display_rules:
        data['submodes'] = {
            'names': ['fast'],
            'default': 'fast',
            'display_rules': {
                'fast': [
                    {'image': 'keep_moving_1', 'text': 'move_1'},
                    {'image': 'keep_moving_2', 'text': 'move_2'},
                ],
            },
        }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            500,
            100000,
            'ToPoint',
            None,
            None,
            None,
            None,
            None,
            False,
            None,
            None,
            None,
        ),
    ]

    rows = select_table(
        'config.display_rules', 'submode_id', pgsql['reposition'],
    )

    if has_display_rules:
        for idx, item in enumerate(rows):
            rows[idx] = list(item)[1:]

        assert rows == [
            [1, 'keep_moving_1', 'move_1', 1, None, None],
            [1, 'keep_moving_2', 'move_2', 1, None, None],
        ]
    else:
        assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    if has_display_rules:
        assert rows == [(1, 'fast', 1, True, 0, True)]
    else:
        assert rows == []


#  @pytest.mark.config(
#  REPOSITION_API_CLIENT_ATTRIBUTES_SCHEMA={
#  'type': 'object',
#  'properties': {
#  'dead10cc': {
#  'type': 'object',
#  'properties': {'deadcafe': {'type': 'string'}},
#  },
#  'deadbeef': {'type': 'string'},
#  },
#  },
#  )
#  @pytest.mark.parametrize(
#  'client_attributes,status_code',
#  [
#  (None, 200),  # TODO(amgaraev): 200 -> 400, when attributes -> required
#  ({'dead10cc': 'any_string'}, 400),
#  (
#  {'dead10cc': {'deadcafe': 'any_string'}, 'deadbeef': 'any_string'},
#  200,
#  ),
#  ],
#  )
#  async def test_put_client_attributes(
#  taxi_reposition_api, pgsql, mockserver, client_attributes, status_code,
#  ):
#  @mockserver.json_handler('/tags/v1/topics_relations')
#  def _mock_v1_topics_relations(request):
#  return {'reposition': ['permitted', 'prohibited']}

#  @mockserver.json_handler('/tags/v1/topics/items')
#  def _mock_tags(tags_request):
#  assert tags_request.args['topic'] == 'reposition'
#  tag = tags_request.args['tag_name']

#  return mockserver.make_response(
#  json.dumps(
#  {
#  'items': [
#  {
#  'topic': 'reposition',
#  'tag': tag,
#  'is_financial': False,
#  },
#  ],
#  'limit': 0,
#  'offset': 0,
#  },
#  ),
#  content_type='application/json',
#  )

#  data = {
#  'backend_only': False,
#  'display_rules': [],
#  'allowed_distance': {'min': 500, 'max': 100000},
#  'mode_type': 'ToPoint',
#  'client_attributes': client_attributes,
#  }

#  response = await taxi_reposition_api.put(
#  '/v1/admin/modes?mode=home', json=data,
#  )
#  assert response.status_code == status_code

#  if status_code == 200:
#  rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
#  assert rows == [
#  (
#  1,
#  'home',
#  False,
#  None,
#  500,
#  100000,
#  'ToPoint',
#  None,
#  None,
#  None,
#  None,
#  client_attributes,
#  False,
#  None,
#  ),
#  ]


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize(
    'bad_mode_tag, bad_submode_dr_tag, bad_mode_dr_tag',
    [
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
async def test_put_bad_tag(
        taxi_reposition_api,
        pgsql,
        mockserver,
        bad_mode_tag,
        bad_submode_dr_tag,
        bad_mode_dr_tag,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint',
        'tags_permitted': ['bad'] if bad_mode_tag else None,
        'submodes': {
            'names': ['fast'],
            'default': 'fast',
            'display_rules': {
                'fast': [
                    {
                        'image': 'keep_moving_1',
                        'text': 'move_1',
                        'tags_permitted': (
                            ['bad'] if bad_submode_dr_tag else None
                        ),
                    },
                ],
            },
        },
        'display_rules': [
            {
                'image': 'keep_moving_1',
                'text': 'move_1',
                'tags_prohibited': ['bad'] if bad_mode_dr_tag else None,
            },
        ],
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    if bad_mode_tag or bad_submode_dr_tag or bad_mode_dr_tag:
        assert response.json() == {
            'code': '400',
            'message': (
                'Topic relations error: '
                'Tag "bad" doesn\'t belong to "reposition" topic'
            ),
        }

        assert not select_table('config.modes', 'mode_id', pgsql['reposition'])

        return

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            500,
            100000,
            'ToPoint',
            None,
            None,
            None,
            None,
            None,
            False,
            None,
            None,
            None,
        ),
    ]


@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('experimental', [False, True])
async def test_put_experimental(
        taxi_reposition_api, pgsql, mockserver, experimental,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint',
        'experimental': experimental,
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == [
        (
            1,
            'home',
            False,
            None,
            500,
            100000,
            'ToPoint',
            None,
            None,
            None,
            None,
            None,
            experimental,
            None,
            None,
            None,
        ),
    ]


async def test_delete_non_existent(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.delete('/v1/admin/modes?mode=home')

    assert response.status_code == 200

    rows = select_table(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )

    assert rows == []


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'mode_ref.sql'])
async def test_delete_with_active_reference(taxi_reposition_api, pgsql):
    response = await taxi_reposition_api.delete('/v1/admin/modes?mode=home')

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Mode or submodes for mode \'home\' has dependencies',
    }

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert len(rows) == 1

    rows = select_table(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )

    assert rows == []


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.parametrize(
    'submodes,display_rules,completion_bonuses',
    [
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, True),
    ],
)
async def test_delete(
        taxi_reposition_api,
        pgsql,
        load,
        submodes,
        display_rules,
        completion_bonuses,
):
    queries = [load('mode_home.sql')]

    if display_rules:
        queries.append(load('display_rules.sql'))

    if completion_bonuses:
        queries.append(load('home_bonus.sql'))

    if submodes:
        queries.append(load('submodes_home.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.delete('/v1/admin/modes?mode=home')

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])

    assert rows == []

    if display_rules:
        assert not select_table(
            'config.display_rules', 'display_id', pgsql['reposition'],
        )

    if completion_bonuses:
        assert not select_table(
            'config.completion_bonuses', 'mode_id', pgsql['reposition'],
        )

    if submodes:
        assert not select_table(
            'config.submodes', 'submode_id', pgsql['reposition'],
        )

    upd_requests = select_named(
        """
        SELECT
            update_state,
            update_modes,
            update_offered_modes,
            created_at,
            started_at,
            finished_at,
            cancelled
        FROM
            etag_data.update_requests
        """,
        pgsql['reposition'],
    )

    assert upd_requests == [
        {
            'update_state': True,
            'update_modes': True,
            'update_offered_modes': False,
            'created_at': datetime(2018, 10, 15, 18, 18, 46),
            'started_at': None,
            'finished_at': None,
            'cancelled': False,
        },
    ]


@pytest.mark.pgsql('reposition')
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(REPOSITION_API_ADMIN_2PC_ENABLED=True)
@pytest.mark.parametrize('fail_services', [False, True])
async def test_2pc_put(
        taxi_reposition_api, pgsql, load, mockserver, fail_services,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        return {'reposition': ['permitted', 'prohibited']}

    # unused for some reason
    # @mockserver.json_handler('/tags/v1/topics/items')
    # def _mock_tags(tags_request):
    #     assert tags_request.args['topic'] == 'reposition'
    #     tag = tags_request.args['tag_name']
    #
    #     if tag == 'random':
    #         return mockserver.make_response(
    #             json.dumps({'items': [], 'limit': 0, 'offset': 0}),
    #             content_type='application/json',
    #         )
    #
    #     return mockserver.make_response(
    #         json.dumps(
    #             {
    #                 'items': [
    #                     {
    #                         'topic': 'reposition',
    #                         'tag': tag,
    #                         'is_financial': False,
    #                     },
    #                 ],
    #                 'limit': 0,
    #                 'offset': 0,
    #             },
    #         ),
    #         content_type='application/json',
    #     )

    @mockserver.json_handler('/reposition-watcher/v1/admin/modes/item')
    def _mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/modes/item')
    def _mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-watcher/v1/admin/modes/item/check')
    def _mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/modes/item/check')
    def _mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint',
        'submodes': {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'slow',
        },
    }

    response = await taxi_reposition_api.put(
        '/v1/admin/modes?mode=home', json=data,
    )

    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                'Failed to set mode in reposition-matcher: PUT '
                '/v1/admin/modes/item/check, status code 400'
            ),
        }

        return

    assert response.status_code == 200


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.config(REPOSITION_API_ADMIN_2PC_ENABLED=True)
@pytest.mark.parametrize('fail_services', [False, True])
async def test_2pc_delete(
        taxi_reposition_api, pgsql, load, mockserver, fail_services,
):
    queries = [load('mode_home.sql'), load('submodes_home.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition-watcher/v1/admin/modes/item')
    def _mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/modes/item')
    def _mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-watcher/v1/admin/modes/item/check')
    def _mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    @mockserver.json_handler('/reposition-matcher/v1/admin/modes/item/check')
    def _mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )

        return {}

    response = await taxi_reposition_api.delete(f'/v1/admin/modes?mode=home')
    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'code': '400',
            'message': (
                'Failed to delete mode in reposition-matcher: DELETE '
                '/v1/admin/modes/item/check, status code 400'
            ),
        }

        return

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])
    assert rows == []
