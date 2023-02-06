import typing

import pytest

from test_taxi_exp import helpers

EXPERIMENT_NAME = 'test_predicate_by_schema'

MAX_ELEMENTS_COUNT = 100


class Case(typing.NamedTuple):
    predicate: dict
    is_valid: bool


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(predicate={'type': 'true'}, is_valid=True),
        Case(
            predicate={
                'type': 'in_set',
                'init': {
                    'arg_name': 'zone',
                    'set_elem_type': 'string',
                    'set': ['msk', 'spb'],
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'any_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'phone_id',
                                'set_elem_type': 'int',
                                'set': [1, 2, 3],
                            },
                        },
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'zone',
                                'set_elem_type': 'string',
                                'set': ['msk'],
                            },
                        },
                        {
                            'type': 'gt',
                            'init': {
                                'arg_name': 'now',
                                'arg_type': 'version',
                                'value': '1.1.1',
                            },
                        },
                        {
                            'type': 'in_file',
                            'init': {
                                'arg_name': 'user_id',
                                'file': '12345',
                                'set_elem_type': 'string',
                            },
                        },
                    ],
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'any_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'phone_id',
                                'set_elem_type': 'int',
                                'set': [1, 2, 3],
                            },
                        },
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'zone',
                                'set_elem_type': 'string',
                                'set': ['msk'],
                            },
                        },
                        {
                            'type': 'gt',
                            'init': {
                                'arg_name': 'now',
                                'arg_type': 'application_version',
                                'value': '1.1.1',
                            },
                        },
                        {
                            'type': 'in_file',
                            'init': {
                                'arg_name': 'user_id',
                                'file': '12345',
                                'set_elem_type': 'string',
                            },
                        },
                    ],
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {
                    'arg_name': 'now',
                    'arg_type': 'datetime',
                    'value': '2018-09-26T16:53:48.372Z',
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {
                    'arg_name': 'now',
                    'arg_type': 'timepoint',
                    'value': '2018-09-26T16:53:48.372Z',
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {
                    'arg_name': 'now',
                    'arg_type': 'datetime',
                    'value': 1,
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {
                    'arg_name': 'now',
                    'arg_type': 'timepoint',
                    'value': 1,
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {'arg_name': 'now', 'arg_type': 'string', 'value': 1},
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {'arg_name': 'now', 'arg_type': 'version', 'value': 1},
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'gt',
                'init': {
                    'arg_name': 'now',
                    'arg_type': 'application_version',
                    'value': 1,
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={'type': 'user_has', 'init': {'tag': 'test_tag'}},
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'falls_inside',
                'init': {
                    'arg_name': 'point_a',
                    'arg_type': 'linear_ring',
                    'value': [
                        [37.415735087745546, 55.962822419120066],
                        [37.41534884964739, 55.9626478984902],
                        [37.41498406922136, 55.96239514307337],
                        [37.414726577155946, 55.96216044013059],
                        [37.414737305992, 55.96184750065012],
                        [37.41480167900836, 55.96158270372036],
                    ],
                },
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'falls_inside',
                'init': {
                    'arg_name': 'point_a',
                    'arg_type': 'linear_ring',
                    'value': [[175.0, -50.0], [175.0, 50.0], [-175.0, 0.0]],
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'falls_inside',
                'init': {
                    'arg_name': 'point_a',
                    'arg_type': 'linear_ring',
                    'value': [
                        [
                            [37.415735087745546, 55.962822419120066],
                            [37.41534884964739, 55.9626478984902],
                            [37.41498406922136, 55.96239514307337],
                            [37.414726577155946, 55.96216044013059],
                            [37.414737305992, 55.96184750065012],
                            [37.41480167900836, 55.96158270372036],
                        ],
                    ],
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'in_set',
                'init': {
                    'arg_name': 'zone_id',
                    'set_elem_type': 'int',
                    'set': [value for value in range(MAX_ELEMENTS_COUNT + 1)],
                },
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'type': 'has_tag',
                'init': {'arg_name': 'zone', 'value': 'tag_moscow'},
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'type': 'has_tag',
                'init': {
                    'arg_name': 'zone_id',
                    'value': 'tag_moscow',
                    'entity': 'uuid',
                },
            },
            is_valid=True,
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 0,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': 100,
                    },
                },
                is_valid=True,
            ),
            id='pass mod_sha1_with_salt with old salt',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'segmentation',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 0,
                        'range_to': 50,
                        'salt': 'new_salt',
                        'divisor': 100,
                    },
                },
                is_valid=True,
            ),
            id='pass segmentation',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'segmentation',
                                'init': {
                                    'arg_name': 'user_id',
                                    'range_from': 0,
                                    'range_to': 50,
                                    'salt': 'new_salt',
                                    'divisor': 100,
                                },
                            },
                            {
                                'type': 'mod_sha1_with_salt',
                                'init': {
                                    'arg_name': 'user_id',
                                    'range_from': 0,
                                    'range_to': 0,
                                    'salt': 'salt',
                                    'divisor': 100,
                                },
                            },
                        ],
                    },
                },
                is_valid=False,
            ),
            id='fail segmentation and mod_sha1_with_salt',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 0,
                        'range_to': 0,
                        'salt': 'salt',
                        'divisor': 100,
                    },
                },
                is_valid=True,
            ),
            id='pass disabled by args mod_sha1_with_salt',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 0,
                        'range_to': 50,
                        'round_up': 12.00,
                        'salt': 'salt',
                        'divisor': 100,
                    },
                },
                is_valid=True,
            ),
            id='pass mod_sha1_with_salt with roup_up',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 0,
                        'range_to': 50,
                        'round_up': '12.00',
                        'salt': 'salt',
                        'divisor': 100,
                    },
                },
                is_valid=False,
            ),
            id='round_up must be string',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'range_from': 0,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': 100,
                        'arguments': [
                            {'round_up': 12.00, 'arg_name': 'user_id'},
                            {'arg_name': 'user_id'},
                        ],
                    },
                },
                is_valid=True,
            ),
            id='pass mod_sha1_with_salt with arguments',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'range_from': 0,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': 100,
                        'arguments': [
                            {'arg_name': 'test', 'round_up': '12.00'},
                        ],
                    },
                },
                is_valid=False,
            ),
            id='round_up must be string in arguments',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'range_from': -1,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': 100,
                        'arguments': [{'arg_name': 'test', 'round_up': 12.00}],
                    },
                },
                is_valid=False,
            ),
            id='range_from must be biggest or equal zero',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'range_from': 1,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': -100,
                        'arguments': [{'arg_name': 'test', 'round_up': 12.00}],
                    },
                },
                is_valid=False,
            ),
            id='divisor must be biggest or equal zero',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'user_id',
                        'range_from': 100,
                        'range_to': 50,
                        'salt': 'salt',
                        'divisor': 100,
                    },
                },
                is_valid=False,
            ),
            id='range_to must be lower than range_from',
        ),
        Case(
            predicate={'type': 'is_null', 'init': {'arg_name': 'user_id'}},
            is_valid=True,
        ),
        Case(
            predicate={
                'init': {
                    'arg_name': 'arg',
                    'set_elem_type': 'int',
                    'value': '228',
                },
                'type': 'contains',
            },
            is_valid=False,
        ),
        Case(
            predicate={
                'init': {
                    'arg_name': 'arg',
                    'set_elem_type': 'int',
                    'value': 228,
                },
                'type': 'contains',
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'init': {
                    'arg_name': 'arg',
                    'set_elem_type': 'string',
                    'value': '228',
                },
                'type': 'contains',
            },
            is_valid=True,
        ),
        Case(
            predicate={
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['5d9b2c7d035dcf9f29e11d8d'],
                                'arg_name': 'personal_phone_id',
                                'transform': 'replace_phone_to_phone_id',
                                'phone_type': 'uber',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {'init': {'arg_name': 'test'}, 'type': 'is_null'},
                        {
                            'init': {
                                'value': [
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                    [37.038117609374986, 55.93553344495757],
                                    [37.20565911328124, 55.937075097294915],
                                ],
                                'arg_name': 'dfdsaf',
                                'arg_type': 'linear_ring',
                            },
                            'type': 'falls_inside',
                        },
                    ],
                },
                'type': 'all_of',
            },
            is_valid=True,
        ),
        pytest.param(
            id='time segmentation predicate with salt and daily increment',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    arg_name='test',
                    start_time='2022-02-17T00:00:00+03:00',
                    range_from=0,
                    range_to=40,
                    period=120,
                    salt='salt',
                    daily_timestamp_increment=20,
                ),
                is_valid=True,
            ),
        ),
        pytest.param(
            id='time segmentation predicate simple',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    arg_name='test',
                    start_time='2022-02-17T00:00:00+03:00',
                    range_from=0,
                    range_to=40,
                    period=120,
                ),
                is_valid=True,
            ),
        ),
        pytest.param(
            id='time segmentation, bad date',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    start_time='bad date',
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, negative range_from',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=-1, range_to=40, period=120,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, negative range_to',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=0, range_to=-1, period=120,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, negative period',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=0, range_to=40, period=-1,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, negative daily timestamp increment',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=0,
                    range_to=40,
                    period=120,
                    salt='test',
                    daily_timestamp_increment=-1,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, range_from greater than range_to',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=10, range_to=0, period=120,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, range_to greater than period',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=0, range_to=140, period=120,
                ),
                is_valid=False,
            ),
        ),
        pytest.param(
            id='time segmentation, daily increment bigger than period',
            *Case(
                predicate=helpers.experiment.time_segmentation(
                    range_from=0,
                    range_to=40,
                    period=120,
                    salt='test',
                    daily_timestamp_increment=130,
                ),
                is_valid=False,
            ),
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_has_tag': True,
                'enable_save_salts': True,
                'enable_write_segmentation_for_new_salts': True,
                'enable_segmentation_for_front': True,
            },
        },
        'settings': {
            'common': {'in_set_max_elements_count': MAX_ELEMENTS_COUNT},
        },
    },
)
@pytest.mark.pgsql(
    'taxi_exp', files=['default.sql', 'fill.sql', 'fill_salts.sql'],
)
async def test_check_predicate(taxi_exp_client, predicate, is_valid):
    experiment = helpers.experiment.generate(
        EXPERIMENT_NAME, match_predicate=predicate,
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment,
    )
    message = await response.text()

    if is_valid:
        assert response.status == 200, message
    else:
        assert response.status != 200, message
        return

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200
    body = await response.json()
    assert body['match']['predicate'] == predicate
