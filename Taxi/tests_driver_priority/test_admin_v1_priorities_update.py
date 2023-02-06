import copy
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils


URL = 'admin/v1/priorities/update'
CHECK_URL = 'admin/v1/priorities/check-update'

NOW = datetime.datetime.now(datetime.timezone.utc)


BRANDING_PRIORITY = {
    'name': 'branding',
    'description': 'description',
    'status': 'active',
    'tanker_keys_prefix': 'branding',
    'agglomerations': {
        'enabled_in': [constants.MSK],
        'disabled_in': [constants.SPB, constants.TULA],
    },
}

BRANDING_PRESETS_RELATIONS = [
    {'name': 'default', 'agglomerations': [], 'description': 'description'},
    {
        'name': 'actual_preset',
        'agglomerations': [constants.MSK],
        'description': 'description',
    },
    {'name': 'preset2', 'agglomerations': [], 'description': 'description'},
]

BRANDING_EXPERIMENTS = [
    {'name': 'exp0', 'agglomerations': ['br_moscow', 'br_root']},
    {'name': 'exp1', 'description': 'spb exp', 'agglomerations': ['br_spb']},
]

BRANDING_STATE = {
    'priority': BRANDING_PRIORITY,
    'presets': BRANDING_PRESETS_RELATIONS,
    'experiments': BRANDING_EXPERIMENTS,
}

LOYALTY_PRIORITY = {
    'name': 'loyalty',
    'description': 'description',
    'status': 'active',
    'tanker_keys_prefix': 'loyalty',
    'agglomerations': {'enabled_in': [constants.SPB], 'disabled_in': []},
}

LOYALTY_PRESETS_RELATIONS = [
    {'name': 'default', 'agglomerations': [], 'description': 'description'},
    {
        'name': 'actual_preset',
        'agglomerations': [],
        'description': 'description',
    },
    {
        'name': 'outdated_preset',
        'agglomerations': [constants.SPB],
        'description': 'description',
    },
    {
        'name': 'without_versions',
        'agglomerations': [],
        'description': 'description',
    },
]

LOYALTY_EXPERIMENTS = [
    {'name': 'exp2', 'description': 'loyalty_exp', 'agglomerations': ['spb']},
]

LOYALTY_STATE = {
    'priority': LOYALTY_PRIORITY,
    'presets': LOYALTY_PRESETS_RELATIONS,
    'experiments': LOYALTY_EXPERIMENTS,
}


def _patch_priority(
        value: Dict[str, Any],
        update: Optional[Dict[str, Any]] = None,
        remove: Optional[List[str]] = None,
) -> Dict[str, Any]:
    result = copy.deepcopy(value)
    if update is not None:
        result.update(update)
    if remove is not None:
        for key in remove:
            if key in result:
                result.pop(key)
    return result


def _patch_preset(
        value: List[Dict[str, Any]], updated_presets: Dict[str, Any],
) -> List[Dict[str, Any]]:
    presets = copy.deepcopy(value)
    for preset in presets:
        name = preset['name']
        if name in updated_presets:
            for key in ['agglomerations', 'description']:
                if key in updated_presets[name]:
                    preset[key] = updated_presets[name][key]
    return presets


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'driver_priority', queries=db_tools.get_pg_default_data(NOW),
)
@pytest.mark.parametrize(
    'request_body, expected_code, current_state, '
    'recalculation_task_agglomerations',
    [
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY, {'name': 'not_exists'},
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            404,
            None,
            None,
            id='not existing priority',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [constants.SPB, constants.MSK],
                            'disabled_in': [constants.SPB, constants.TULA],
                        },
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            400,
            None,
            None,
            id='agglomeration included and excluded simultaneously',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS[1:],
            },
            400,
            None,
            None,
            id='missed some existing presets',
        ),
        pytest.param(
            {
                'priority': LOYALTY_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS[:2],
            },
            400,
            None,
            None,
            id='passed some different presets',
        ),
        pytest.param(
            {
                'priority': LOYALTY_PRIORITY,
                'presets': LOYALTY_PRESETS_RELATIONS[:1] * 2,
            },
            400,
            None,
            None,
            id='one preset passed more than one time',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {'default': {'agglomerations': [constants.SPB]}},
                ),
            },
            400,
            None,
            None,
            id='default preset cannot have any relation',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'actual_preset': {'agglomerations': [constants.SPB]},
                        'preset2': {'agglomerations': [constants.SPB]},
                    },
                ),
            },
            400,
            None,
            None,
            id='different presets relations with same agglomeration',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': BRANDING_EXPERIMENTS + LOYALTY_EXPERIMENTS,
            },
            400,
            None,
            None,
            id='add existing experiment from another priority',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': [
                    {'name': 'exp0', 'agglomerations': ['copy', 'copy']},
                ],
            },
            400,
            None,
            None,
            id='forbid multiple agglomerations for single priority',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': [{'name': 'exp0', 'agglomerations': []}],
            },
            400,
            None,
            None,
            id='empty list of agglomerations for experiment',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {'tanker_keys_prefix': 'invalid_tanker_key'},
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            404,
            None,
            None,
            id='tanker key was not found',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            None,
            id='no changes for branding priority',
        ),
        pytest.param(
            {
                'priority': LOYALTY_PRIORITY,
                'presets': LOYALTY_PRESETS_RELATIONS,
                'experiments': LOYALTY_EXPERIMENTS,
            },
            200,
            LOYALTY_STATE,
            None,
            id='no changes for loyalty priority',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': BRANDING_EXPERIMENTS,
            },
            200,
            BRANDING_STATE,
            None,
            id='no changes for branding priority, with experiments',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': [],
            },
            200,
            BRANDING_STATE,
            None,
            id='remove all experiments',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': [
                    {
                        'name': 'exp0',
                        'agglomerations': ['br_tula', 'br_root'],
                        'description': 'add tula and remove moscow',
                    },
                    {
                        'name': 'exp1',
                        'description': 'remove spb, add moscow',
                        'agglomerations': ['br_moscow'],
                    },
                ],
            },
            200,
            BRANDING_STATE,
            None,
            id='transform experiments agglomerations and descriptions',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': BRANDING_PRESETS_RELATIONS,
                'experiments': [
                    {
                        'name': 'exp0',
                        'agglomerations': ['br_root', 'br_moscow'],
                    },  # swap agglomerations for ordering test
                    {'name': 'new_branding_exp', 'agglomerations': ['br_spb']},
                    # use new exp in br_spb instead of exp1
                ],
            },
            200,
            BRANDING_STATE,
            None,
            id='transform experiments for branding priority',
        ),
        pytest.param(
            {
                'priority': BRANDING_PRIORITY,
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'actual_preset': {'agglomerations': []},
                        'preset2': {'agglomerations': []},
                    },
                ),
            },
            200,
            BRANDING_STATE,
            [constants.MSK],
            id='remove all relations from branding',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [],
                            'disabled_in': [constants.SPB, constants.TULA],
                        },
                        'status': 'disabled',
                        'tanker_keys_prefix': 'loyalty',
                        'description': 'updated',
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            [],
            id='change branding priority fields except agglomerations',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [],
                            'disabled_in': [],
                        },
                        'status': 'disabled',
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            [],
            id='status change affects all agglomerations',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [constants.MSK],
                            'disabled_in': [],
                        },
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            [constants.SPB, constants.TULA],
            id='clear priority exclusion list',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [],
                            'disabled_in': [constants.SPB, constants.TULA],
                        },
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            [constants.MSK],
            id='clear priority enabled list',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': [
                                'br_russia',
                                'minsk',
                                constants.MSK,
                            ],
                            'disabled_in': [constants.SPB, constants.TULA],
                        },
                    },
                ),
                'presets': BRANDING_PRESETS_RELATIONS,
            },
            200,
            BRANDING_STATE,
            ['br_russia', 'minsk'],
            id='only append priority enabled list',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': ['br_russia'],
                            'disabled_in': ['minsk'],
                        },
                    },
                ),
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'actual_preset': {
                            'agglomerations': [constants.SPB, constants.TULA],
                            'description': 'created',
                        },
                        'preset2': {
                            'agglomerations': ['br_russia'],
                            'description': 'updated',
                        },
                    },
                ),
            },
            200,
            BRANDING_STATE,
            [
                'br_russia',
                'minsk',
                constants.MSK,
                constants.SPB,
                constants.TULA,
            ],
            id='full change for priority and presets',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': ['penza', 'penza', constants.TULA],
                            'disabled_in': ['kazan', constants.MSK],
                        },
                    },
                ),
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'actual_preset': {'agglomerations': []},
                        'preset2': {
                            'agglomerations': [
                                'br_russia',
                                'br_russia',
                                'kazan',
                            ],
                        },
                    },
                ),
            },
            200,
            BRANDING_STATE,
            [
                'br_russia',
                'kazan',
                constants.MSK,
                'penza',
                constants.SPB,
                constants.TULA,
            ],
            id='swap agglomerations, add some duplicates',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {'agglomerations': {'enabled_in': [], 'disabled_in': []}},
                ),
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'actual_preset': {'agglomerations': []},
                        'preset2': {'agglomerations': []},
                    },
                ),
            },
            200,
            BRANDING_STATE,
            [constants.MSK, constants.SPB, constants.TULA],
            id='drop all agglomeration relations',
        ),
        pytest.param(
            {
                'priority': _patch_priority(
                    BRANDING_PRIORITY,
                    {
                        'agglomerations': {
                            'enabled_in': ['br_moscow', 'moscow'],
                            'disabled_in': ['br_spb', 'spb', 'tula'],
                        },
                    },
                ),
                'presets': _patch_preset(
                    BRANDING_PRESETS_RELATIONS,
                    {
                        'default': {'description': 'updated'},
                        'actual_preset': {'agglomerations': ['br_germany']},
                        'preset2': {'agglomerations': ['moscow']},
                    },
                ),
            },
            200,
            BRANDING_STATE,
            ['br_germany', 'br_moscow', 'br_spb', constants.MSK],
            id='move agglomeration between presets',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        request_body: Dict[str, Any],
        expected_code: int,
        current_state: Optional[Dict[str, Any]],
        recalculation_task_agglomerations: Optional[List[str]],
        pgsql,
):
    db = pgsql['driver_priority']
    priority_name = request_body['priority']['name']
    headers = {'X-Idempotency-Token': str(uuid.uuid4())}

    experiments_before = db_tools.get_priority_experiments(priority_name, db)

    check_response = await taxi_driver_priority.post(
        CHECK_URL, request_body, headers=headers,
    )
    assert check_response.status_code == expected_code

    response = await taxi_driver_priority.post(
        URL, request_body, headers=headers,
    )
    assert response.status_code == expected_code

    db_tools.check_recalculation_task(db, recalculation_task_agglomerations)

    data = response.json()
    if expected_code != 200:
        assert data['message']
        return

    assert data == {'status': 'succeeded'}
    assert current_state is not None
    utils.validate_check_response(
        check_response.json(),
        request_body,
        expected_diff={'new': request_body, 'current': current_state},
    )

    priority_data = db_tools.get_priority_fields(priority_name, db)
    for key, value in priority_data.items():
        assert request_body['priority'][key] == value

    priority_relations = db_tools.get_priority_relations(priority_name, db)
    for key in ['enabled_in', 'disabled_in']:
        assert set(priority_relations[key]) == set(
            request_body['priority']['agglomerations'][key],
        )

    preset_relations = db_tools.get_priority_presets_relations(
        priority_name, db,
    )
    for item, expected in zip(preset_relations, request_body['presets']):
        assert item['name'] == expected['name']
        assert set(item['agglomerations']) == set(expected['agglomerations'])
        if 'description' in expected:
            assert item['description'] == expected['description']
        else:
            assert item['description'] is None

    experiments_after = db_tools.get_priority_experiments(priority_name, db)
    if 'experiments' not in request_body:
        assert experiments_before == experiments_after
    else:
        for item, expected in zip(
                experiments_after, request_body['experiments'],
        ):
            # TODO: make common function for agglomeration_item check
            assert item['name'] == expected['name']
            assert set(item['agglomerations']) == set(
                expected['agglomerations'],
            )
            if 'description' in expected:
                assert item['description'] == expected['description']
            else:
                assert item['description'] is None
