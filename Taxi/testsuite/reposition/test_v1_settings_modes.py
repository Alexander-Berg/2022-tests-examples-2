from datetime import datetime
from datetime import timedelta
import json

import pytest

from .reposition_select import select_named
from .reposition_select import select_table


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_get_modes_types(taxi_reposition):
    response = taxi_reposition.get('/v1/settings/modes/types')
    assert response.status_code == 200
    assert response.json() == {'mode_types': ['ToPoint', 'InArea']}


@pytest.mark.nofilldb()
@pytest.mark.parametrize('offer', [False, True])
@pytest.mark.parametrize('display_rules', [False, True])
@pytest.mark.parametrize('bonus', [None, 'short', 'long'])
@pytest.mark.parametrize('submodes', [False, True])
@pytest.mark.parametrize('tag_settings', [None, 'permitted', 'prohibited'])
@pytest.mark.parametrize(
    'geo_nodes_settings', [None, 'permitted', 'prohibited'],
)
@pytest.mark.parametrize('work_modes', [None, ['driver-fix']])
@pytest.mark.pgsql('reposition')
def test_get(
        taxi_reposition,
        load,
        pgsql,
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

    response = taxi_reposition.get('/v1/settings/modes')
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


@pytest.mark.pgsql('reposition')
def test_put_pin_surge_to_point(taxi_reposition, pgsql):
    data = {
        'backend_only': False,
        'display_rules': [{'image': 'keep_moving', 'text': 'move'}],
        'allowed_distance': {'min': 2000, 'max': 180000},
        'mode_type': 'ToPoint',
        'max_pin_surge_rules': {'max_pin': 10, 'max_surge': 10},
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == 400
    wanted = {'error': {'text': 'pin and surge bounds are deprecated'}}
    assert response.json() == wanted


@pytest.mark.pgsql('reposition')
def test_put_bad_offer_radius(taxi_reposition, pgsql):
    data = {
        'backend_only': True,
        'display_rules': [],
        'allowed_distance': {'min': 2000, 'max': 180000},
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'Offer radius is required for backend-only mode'},
    }


@pytest.mark.parametrize('names', [(['fast', 'slow']), ([])])
@pytest.mark.pgsql('reposition')
def test_put_bad_default_submode(taxi_reposition, pgsql, names):
    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'submodes': {'names': names, 'default': 'fast_slow'},
    }
    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'Default submode is not matched'},
    }


@pytest.mark.pgsql('reposition')
def test_put_bad_highlighted_submode(taxi_reposition, pgsql):
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
    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'Highlighted submode is not matched'},
    }


@pytest.mark.pgsql('reposition')
def test_put_bad_or_missing_translations(taxi_reposition, pgsql):
    data = {
        'backend_only': False,
        'display_rules': [
            {'image': 'dr_image_1', 'text': 'dr_key_1'},
            {'image': 'dr_image_2', 'text': 'dr_key_2'},
        ],
        'allowed_distance': {'min': 2000, 'max': 180000},
        'mode_type': 'ToPoint',
        'completion_bonus': {
            'period': 600,
            'image_id': 'bonus_image_id',
            'tanker_key': 'bonus_tanker_key',
        },
        'submodes': {'names': ['fast', 'slow'], 'default': 'fast'},
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=crazy', json=data)
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert 'text' in data['error']
    lines = data['error']['text'].split('\n')
    assert len(lines) == 3
    assert lines[0] == 'tanker key errors:'
    errors = {}
    for line in lines[1:]:
        spl = line.split(':')
        assert len(spl) == 2
        error_type, keys = map(lambda x: x.strip(), spl)
        errors[error_type] = set(map(lambda x: x.strip(), keys.split(',')))
    assert errors == {
        'no tanker key': {
            'reposition.crazy.active_panel.subtitle',
            'reposition.crazy.active_panel.title',
            'reposition.crazy.bonus_tanker_key.headline_title',
            'reposition.crazy.bonus_tanker_key.headline_subtitle',
            'reposition.crazy.bonus_tanker_key.subline_title',
            'reposition.crazy.bonus_tanker_key.subline_subtitle',
            'reposition.crazy.error.usages_limit_exceeded',
            'reposition.crazy.fast.name',
            'reposition.crazy.fast.subname',
            'reposition.crazy.finish_dialog.body',
            'reposition.crazy.finish_dialog.title',
            'reposition.crazy.ready_panel.subtitle',
            'reposition.crazy.ready_panel.title',
            'reposition.crazy.score_panel.title',
            'reposition.crazy.slow.name',
            'reposition.crazy.slow.subname',
            'reposition.crazy.subname',
            'reposition.crazy.subname.limited',
            'reposition.crazy.subname.limitless',
            'reposition.crazy.text_header',
            'reposition.crazy.title',
            'reposition.dr_key_1.short',
            'reposition.dr_key_1.title',
            'reposition.dr_key_2',
            'reposition.dr_key_2.short',
            'reposition.dr_key_2.title',
        },
        'unexpected arguments': {'reposition.dr_key_1'},
    }


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.parametrize('idx', range(0, 8))
@pytest.mark.parametrize('tag_settings', [None, 'permitted', 'prohibited'])
@pytest.mark.parametrize(
    'geo_nodes_settings', [None, 'permitted', 'prohibited'],
)
@pytest.mark.parametrize(
    'non_reposition_tag,non_reposition_tag_dp', [(False, True), (True, False)],
)
@pytest.mark.parametrize('work_modes', [None, ['driver-fix']])
@pytest.mark.pgsql('reposition')
def test_put(
        taxi_reposition,
        pgsql,
        mockserver,
        idx,
        tag_settings,
        non_reposition_tag,
        non_reposition_tag_dp,
        geo_nodes_settings,
        work_modes,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        if 'random' in tag:
            return mockserver.make_response(
                json.dumps({'items': [], 'limit': 0, 'offset': 0}),
                content_type='application/json',
            )

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint' if idx & 0b100 else 'InArea',
    }
    pin_surge = None
    if idx & 0b001:
        if data['mode_type'] == 'InArea':
            data['max_pin_surge_rules'] = {'max_pin': 10, 'max_surge': 10}
            pin_surge = 10
    if idx & 0b0001:
        data['display_rules'] = [
            {
                'image': 'keep_moving_1',
                'text': 'move_1',
                'tags_permitted': (
                    ['random_dp'] if non_reposition_tag_dp else None
                ),
                'tags_prohibited': None,
            },
            {
                'image': 'keep_moving_2',
                'text': 'move_2',
                'tags_permitted': None,
                'tags_prohibited': None,
            },
        ]
    if idx & 0b0010:
        data['completion_bonus'] = {
            'period': 600,
            'image_id': 'bonus_image',
            'tanker_key': 'bonus_translation',
        }
    if idx & 0b0100:
        data['submodes'] = {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'slow',
        }
    if tag_settings:
        field = 'tags_' + tag_settings
        data[field] = [tag_settings]

        if non_reposition_tag:
            data[field].append('random')
    if geo_nodes_settings:
        field = 'geo_nodes_' + geo_nodes_settings
        data[field] = [geo_nodes_settings]
    if work_modes:
        data['work_modes'] = work_modes

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    if pin_surge is not None:
        assert response.status_code == 400
        assert response.json() == {
            'error': {'text': 'pin and surge bounds are deprecated'},
        }
        return

    if tag_settings and non_reposition_tag:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': 'Tag "random" doesn\'t belong to "reposition" topic',
            },
        }
        return

    if idx & 0b0001 and non_reposition_tag_dp:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': (
                    'Tag "random_dp" doesn\'t belong to "reposition" topic'
                ),
            },
        }
        return

    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    mode_type = 'ToPoint' if idx & 0b0100 else 'InArea'
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
            pin_surge,
            pin_surge,
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
    if idx & 0b0001:
        assert rows == [
            (1, 1, 'keep_moving_1', 'move_1', None, None, None),
            (2, 1, 'keep_moving_2', 'move_2', None, None, None),
        ]
    else:
        assert rows == []

    rows = select_table(
        'config.completion_bonuses', 'mode_id', pgsql['reposition'],
    )
    if idx & 0b0010:
        assert rows == [
            (1, timedelta(0, 600), 'bonus_image', 'bonus_translation'),
        ]
    else:
        assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])
    if idx & 0b0100:
        assert rows == [
            (1, 'fast', 1, True, 0, False),
            (2, 'slow', 1, False, 1, True),
        ]
    else:
        assert rows == []

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
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


@pytest.mark.parametrize('idx', range(0, 8))
@pytest.mark.parametrize('tag_settings', [None, 'permitted', 'prohibited'])
@pytest.mark.parametrize(
    'geo_nodes_settings', [None, 'permitted', 'prohibited'],
)
@pytest.mark.parametrize('work_modes', [None, ['driver-fix']])
@pytest.mark.pgsql('reposition')
def test_put_override(
        taxi_reposition,
        pgsql,
        mockserver,
        idx,
        tag_settings,
        geo_nodes_settings,
        work_modes,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

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
    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
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
        'mode_type': 'ToPoint' if idx & 0b100 else 'InArea',
    }
    if idx & 0b0001:
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
    if idx & 0b0010:
        data['completion_bonus'] = {
            'period': 600,
            'image_id': 'overridden_image',
            'tanker_key': 'overridden_translation',
        }
    if idx & 0b0100:
        data['submodes'] = {
            'names': ['fast', 'slow'],
            'default': 'fast',
            'highlight': 'fast',
        }
    pin_surge = None
    if tag_settings:
        field = 'tags_' + tag_settings
        data[field] = [tag_settings]
    if geo_nodes_settings:
        field = 'geo_nodes_' + geo_nodes_settings
        data[field] = [geo_nodes_settings]
    if work_modes:
        data['work_modes'] = work_modes

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    mode_type = 'ToPoint' if idx & 0b100 else 'InArea'
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
            pin_surge,
            pin_surge,
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
    if idx & 0b001:
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
    if idx & 0b010:
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
    if idx & 0b100:
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
def test_put_submodes_override_with_active_reference(
        taxi_reposition, pgsql, mockserver, conflict,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

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

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])

    if conflict is None:
        assert response.status_code == 200
        assert rows == [
            (1, 'superslow', 1, False, 0, False),
            (1001, 'fast', 1, False, 2, False),
            (1002, 'slow', 1, True, 1, True),
        ]
    else:
        assert response.status_code == 409
        assert rows == backup
        assert response.json() == {
            'error': {
                'text': (
                    'Unable to delete submode, possible it has active '
                    + 'references'
                ),
            },
        }


@pytest.mark.parametrize('has_display_rules', [False, True])
@pytest.mark.pgsql('reposition')
def test_put_submodes_display_rules(
        taxi_reposition, pgsql, mockserver, has_display_rules,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

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

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
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
        for i in range(0, len(rows)):
            rows[i] = list(rows[i])[1:]
        assert rows == [
            [1, 'keep_moving', 'move', 2, None, None],
            [1, 'keep_moving_1', 'move_1', 1, None, None],
            [1, 'keep_moving_2', 'move_2', 1, None, None],
        ]


@pytest.mark.parametrize('has_display_rules', [False, True])
@pytest.mark.pgsql('reposition')
def test_put_override_submodes_display_rules(
        taxi_reposition, pgsql, mockserver, has_display_rules,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    data = {
        'backend_only': False,
        'display_rules': [{'image': 'keep_moving', 'text': 'move'}],
        'allowed_distance': {'min': 2000, 'max': 180000},
        'submodes': {'names': ['fast', 'slow'], 'default': 'fast'},
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
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

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
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
        for i in range(0, len(rows)):
            rows[i] = list(rows[i])[1:]
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


@pytest.mark.config(
    REPOSITION_CLIENT_ATTRIBUTES_SCHEMA={
        'type': 'object',
        'properties': {
            'dead10cc': {
                'type': 'object',
                'properties': {'deadcafe': {'type': 'string'}},
            },
            'deadbeef': {'type': 'string'},
        },
    },
)
@pytest.mark.parametrize(
    'client_attributes,status_code',
    [
        (None, 200),  # TODO(amgaraev): 200 -> 400, when attributes -> required
        ({'dead10cc': 'any_string'}, 400),
        (
            {'dead10cc': {'deadcafe': 'any_string'}, 'deadbeef': 'any_string'},
            200,
        ),
    ],
)
def test_put_client_attributes(
        taxi_reposition, pgsql, mockserver, client_attributes, status_code,
):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint',
        'client_attributes': client_attributes,
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
    assert response.status_code == status_code

    if status_code == 200:
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
                client_attributes,
                False,
                None,
                None,
                None,
            ),
        ]


@pytest.mark.parametrize('experimental', [False, True])
@pytest.mark.pgsql('reposition')
def test_put_experimental(taxi_reposition, pgsql, mockserver, experimental):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    data = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {'min': 500, 'max': 100000},
        'mode_type': 'ToPoint',
        'experimental': experimental,
    }

    response = taxi_reposition.put('/v1/settings/modes?mode=home', json=data)
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


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
def test_delete_non_existent(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v1/settings/modes?mode=home')
    assert response.status_code == 200

    rows = select_table(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )
    assert rows == []


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'mode_ref.sql'])
def test_delete_with_active_reference(taxi_reposition, pgsql):
    response = taxi_reposition.delete('/v1/settings/modes?mode=home')
    assert response.status_code == 409
    assert response.json() == {
        'error': {
            'text': 'Unable to delete mode, possible it has active references',
        },
    }

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    assert len(rows) == 1

    rows = select_table(
        'etag_data.update_requests', 'update_request_id', pgsql['reposition'],
    )
    assert rows == []


@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.parametrize('idx', range(0, 8))
def test_delete(taxi_reposition, pgsql, load, idx):
    queries = [load('mode_home.sql')]
    if idx & 0b001:
        queries.append(load('display_rules.sql'))
    if idx & 0b010:
        queries.append(load('home_bonus.sql'))
    if idx & 0b100:
        queries.append(load('submodes_home.sql'))
    pgsql['reposition'].apply_queries(queries)

    response = taxi_reposition.delete('/v1/settings/modes?mode=home')
    assert response.status_code == 200
    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    assert rows == []

    if idx & 0b001:
        rows = select_table(
            'config.display_rules', 'display_id', pgsql['reposition'],
        )
        assert rows == []
    if idx & 0b010:
        rows = select_table(
            'config.completion_bonuses', 'mode_id', pgsql['reposition'],
        )
        assert rows == []
    if idx & 0b100:
        rows = select_table(
            'config.submodes', 'submode_id', pgsql['reposition'],
        )
        assert rows == []

    upd_requests = select_named(
        'SELECT update_state, update_modes, update_offered_modes, created_at,'
        'started_at, finished_at, cancelled FROM etag_data.update_requests',
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


@pytest.mark.config(REPOSITION_SETTINGS_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.pgsql('reposition')
@pytest.mark.parametrize('fail_services', [False, True])
def test_2pc_put(taxi_reposition, pgsql, load, mockserver, fail_services):
    @mockserver.json_handler('/tags/v1/topics/items')
    def mock_tags(tags_request):
        assert tags_request.args['topic'] == 'reposition'
        tag = tags_request.args['tag_name']

        if tag == 'random':
            return mockserver.make_response(
                json.dumps({'items': [], 'limit': 0, 'offset': 0}),
                content_type='application/json',
            )

        return mockserver.make_response(
            json.dumps(
                {
                    'items': [
                        {
                            'topic': 'reposition',
                            'tag': tag,
                            'is_financial': False,
                            'is_audited': True,
                        },
                    ],
                    'limit': 0,
                    'offset': 0,
                },
            ),
            content_type='application/json',
        )

    @mockserver.json_handler('/reposition_watcher/v1/admin/modes/item')
    def mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/modes/item')
    def mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_watcher/v1/admin/modes/item/check')
    def mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/modes/item/check')
    def mock_matcher_check(tags_request):
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
    response = taxi_reposition.put(f'/v1/settings/modes?mode=home', json=data)

    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': (
                    'Failed to set mode in reposition-watcher: '
                    'got BadRequestRepositionWatcherError '
                    'service RepositionWatcher error'
                ),
            },
        }
        return
    assert response.status_code == 200


@pytest.mark.config(REPOSITION_SETTINGS_2PC_ENABLED=True)
@pytest.mark.now('2018-10-15T18:18:46')
@pytest.mark.nofilldb()
@pytest.mark.parametrize('fail_services', [False, True])
def test_2pc_delete(taxi_reposition, pgsql, load, mockserver, fail_services):
    queries = [load('mode_home.sql'), load('submodes_home.sql')]
    pgsql['reposition'].apply_queries(queries)

    @mockserver.json_handler('/reposition_watcher/v1/admin/modes/item')
    def mock_watcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/modes/item')
    def mock_matcher(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_watcher/v1/admin/modes/item/check')
    def mock_watcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    @mockserver.json_handler('/reposition_matcher/v1/admin/modes/item/check')
    def mock_matcher_check(tags_request):
        if fail_services:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error'}), 400,
            )
        return {}

    response = taxi_reposition.delete(f'/v1/settings/modes?mode=home')
    if fail_services:
        assert response.status_code == 400
        assert response.json() == {
            'error': {
                'text': (
                    'Failed to delete mode in reposition-watcher: '
                    'got BadRequestRepositionWatcherError '
                    'service RepositionWatcher error'
                ),
            },
        }
        return
    assert response.status_code == 200

    rows = select_table('config.modes', 'mode_id', pgsql['reposition'])
    assert rows == []

    rows = select_table('config.submodes', 'submode_id', pgsql['reposition'])
    assert rows == []
