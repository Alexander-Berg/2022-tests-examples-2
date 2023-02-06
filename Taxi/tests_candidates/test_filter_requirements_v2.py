import pytest


@pytest.mark.config(
    DRIVER_OPTIONS_BUILDER_SETTINGS=[
        {
            'description_key': 'delivery.description',
            'title_key': 'delivery.title',
            'options': [
                {
                    'blocking_tags': [],
                    'description_key': 'thermobag.requirements',
                    'exams': [],
                    'name': 'thermobag',
                    'prefix': 'delivery',
                    'title_key': 'thermobag',
                },
                {
                    'blocking_tags': [{'reason_key': 'tag_0', 'tag': 'tag_0'}],
                    'description_key': 'thermopack.requirements',
                    'exams': [],
                    'name': 'thermopack',
                    'prefix': 'delivery',
                    'title_key': 'thermopack',
                },
                {
                    'blocking_tags': [{'reason_key': 'tag_1', 'tag': 'tag_1'}],
                    'exams': [],
                    'name': 'medical_card',
                    'prefix': 'delivery',
                    'title_key': 'medical_card',
                },
            ],
        },
    ],
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={'enabled': True},
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # dbid0_uuid0
        ('dbid_uuid', 'dbid0_uuid0', 'tag_0'),
        ('dbid_uuid', 'dbid0_uuid0', 'thermobag'),
        ('dbid_uuid', 'dbid0_uuid0', 'thermopack'),
        # dbid0_uuid1
        ('dbid_uuid', 'dbid0_uuid1', 'tag_1'),
        ('dbid_uuid', 'dbid0_uuid1', 'thermopack'),
        ('dbid_uuid', 'dbid0_uuid1', 'medical_card'),
    ],
)
@pytest.mark.parametrize(
    'requirements, count',
    [
        ({}, 2),
        ({'thermobag': True}, 1),
        ({'thermopack': True}, 1),
        ({'medical_card': True}, 0),
    ],
)
async def test_sample(taxi_candidates, driver_positions, requirements, count):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.559667, 55.685688]},
        ],
    )
    request_body = {
        'tl': [37.308020, 55.903174],
        'br': [37.921881, 55.565338],
        'allowed_classes': ['econom', 'vip'],
        'zone_id': 'moscow',
        'requirements': requirements,
    }

    response = await taxi_candidates.post('count', json=request_body)
    assert response.status_code == 200
    assert 'total' in response.json()
    assert response.json()['total'] == count


@pytest.mark.config(
    DRIVER_OPTIONS_BUILDER_SETTINGS=[
        {
            'description_key': 'delivery.description',
            'title_key': 'delivery.title',
            'options': [
                {
                    'blocking_tags': [],
                    'exams': [],
                    'name': 'own_chair',
                    'prefix': 'other',
                    'title_key': 'own_chair_title',
                    'version': '1.12',
                },
                {
                    'blocking_tags': [],
                    'description_key': 'wanna_carry_children.requirements',
                    'exams': ['child_exam_1'],
                    'name': 'wanna_carry_children',
                    'prefix': 'delivery',
                    'title_key': 'wanna_carry_children',
                },
                {
                    'blocking_tags': [],
                    'description_key': (
                        'wanna_carry_children_no_exams.requirements'
                    ),
                    'exams': [],
                    'name': 'wanna_carry_children_no_exams',
                    'prefix': 'delivery',
                    'title_key': 'wanna_carry_children_no_exams',
                },
            ],
        },
    ],
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={'enabled': True},
    CANDIDATES_CHILDCHAIRS_OPTIONS={
        '__default__': {'child_classes': [], 'required_options': []},
        'countries': [],
        'zones': [
            {
                'names': ['taganrog'],
                'rule': {
                    'child_classes': ['econom'],
                    'required_options': ['wanna_carry_children_no_exams'],
                },
            },
            {
                'names': ['kiev'],
                'rule': {
                    'child_classes': ['econom', 'uberx'],
                    'required_options': ['wanna_carry_children'],
                },
            },
            {
                'names': ['moscow'],
                'rule': {
                    'child_classes': ['econom'],
                    'required_options': ['wanna_carry_children'],
                },
            },
        ],
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # dbid0_uuid0
        ('dbid_uuid', 'dbid0_uuid0', 'wanna_carry_children'),
        # dbid0_uuid1
        ('dbid_uuid', 'dbid0_uuid1', 'wanna_carry_children_no_exams'),
        ('dbid_uuid', 'dbid0_uuid1', 'own_chair'),
    ],
)
@pytest.mark.parametrize(
    'requirements, allowed_classes, zone, count',
    [
        # one of classes is child
        ({'childchair': 7}, ['econom', 'vip'], 'moscow', 2),
        # one driver has necessary option, but doesn't have exam
        ({'childchair': 7}, ['uberx', 'vip'], 'moscow', 0),
        # one of classes is child
        ({'childchair': 7}, ['uberx', 'vip'], 'kiev', 2),
        # no required_options in saratov
        ({'childchair': 7}, ['uberx', 'vip'], 'saratov', 2),
        # only option existence is required, not exam
        ({'childchair': 7}, ['uberx', 'vip'], 'taganrog', 1),
        # no chair requirements - no blocks
        ({}, ['uberx', 'vip'], 'saratov', 2),
        # test own chairs; only vip driver has own_chair tag
        ({'childchair': 10}, ['uberx', 'vip'], 'saratov', 1),
        # uberx driver does not have own_chair tag
        ({'childchair': 10}, ['uberx'], 'saratov', 0),
    ],
)
async def test_childchairs_options(
        taxi_candidates,
        driver_positions,
        requirements,
        allowed_classes,
        zone,
        count,
):
    await driver_positions(
        [
            {
                'dbid_uuid': 'dbid0_uuid0',
                'position': [37.680517, 55.787963],
            },  # econom, uberx
            {
                'dbid_uuid': 'dbid0_uuid1',
                'position': [37.559667, 55.685688],
            },  # vip
        ],
    )
    request_body = {
        'tl': [37.308020, 55.903174],
        'br': [37.921881, 55.565338],
        'allowed_classes': allowed_classes,
        'zone_id': zone,
        'requirements': requirements,
    }

    response = await taxi_candidates.post('count', json=request_body)
    assert response.status_code == 200
    assert 'total' in response.json()
    assert response.json()['total'] == count
