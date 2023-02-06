import typing
from typing import Dict
from typing import List
from typing import Optional

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'with_traits_experiment'


class Case(typing.NamedTuple):
    trait_tags: List[str]
    expected_status: int
    expected_trait_tags: Optional[List[str]] = None
    code: Optional[str] = None
    custom_match_predicate: Optional[Dict] = None
    expected_custom_match_predicate: Optional[Dict] = None


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        pytest.param(
            *Case(trait_tags=[], expected_trait_tags=[], expected_status=200),
        ),
        pytest.param(
            *Case(trait_tags=[], expected_trait_tags=[], expected_status=200),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_save_salts': True}},
                },
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['analytical'],
                expected_trait_tags=['analytical'],
                expected_status=200,
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['another_tag'],
                expected_status=400,
                code='NON_REGISTERED_SERVICE_TAGS',
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['analytical', 'another'],
                expected_trait_tags=['analytical', 'another'],
                expected_status=200,
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'settings': {
                        'common': {
                            'trait_tags_v2': {
                                'another': {
                                    'availability': ['__tariff_editor__'],
                                },
                            },
                        },
                    },
                },
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['analytical', 'another'],
                expected_trait_tags=['analytical', 'another'],
                expected_status=200,
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'settings': {
                        'backend': {
                            'trait_tags_v2': {
                                'another': {
                                    'availability': ['__tariff_editor__'],
                                },
                            },
                        },
                    },
                },
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['analytical', 'another'],
                expected_status=400,
                code='NON_REGISTERED_SERVICE_TAGS',
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'settings': {
                        'common': {
                            'trait_tags_v2': {
                                'another': {
                                    'availability': ['__tariff_editor__'],
                                },
                            },
                        },
                        'backend': {
                            'trait_tags_v2': {
                                'and_another': {
                                    'availability': ['__tariff_editor__'],
                                },
                            },
                        },
                    },
                },
            ),
        ),
        pytest.param(
            *Case(
                trait_tags=['analytical', 'another'],
                expected_status=400,
                code='NON_REGISTERED_SERVICE_TAGS',
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_trait_tags(
        taxi_exp_client,
        trait_tags,
        expected_trait_tags,
        expected_status,
        code,
        custom_match_predicate,
        expected_custom_match_predicate,
):
    data = experiment.generate(trait_tags=trait_tags)
    if custom_match_predicate:
        data['match']['predicate'] = custom_match_predicate
    response = await taxi_exp_client.post(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )

    assert response.status == expected_status, await response.text()

    if response.status != 200:
        body = await response.json()
        assert body['code'] == code
        return

    data['trait_tags'] = expected_trait_tags
    if expected_custom_match_predicate:
        data['match']['predicate'] = expected_custom_match_predicate
    await helpers.experiment_check_tests(
        taxi_exp_client, EXPERIMENT_NAME, data,
    )
