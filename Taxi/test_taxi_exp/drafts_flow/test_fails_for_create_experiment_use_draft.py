import datetime
import typing

import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'check_map_style'
CURRENT_YEAR = datetime.datetime.now().year


class Case(typing.NamedTuple):
    experiment_body: dict
    params: dict
    code: dict


@pytest.mark.parametrize(
    'experiment_body,params,code',
    [
        pytest.param(
            *Case(
                experiment_body={},
                params={'name': EXPERIMENT_NAME},
                code={'number': 400, 'text': 'CHECK_SCHEMA_ERROR'},
            ),
            id='incorrect_body',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'incorrect name'},
                code={'number': 400, 'text': 'BAD_EXPERIMENT_OR_CONFIG_NAME'},
            ),
            id='incorrect_name',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(
                    action_time={
                        'from': '2000-01-01T00:00:00+0300',
                        'to': f'{CURRENT_YEAR + 3}-12-31T23:59:59+0300',
                    },
                ),
                params={'name': EXPERIMENT_NAME},
                code={'number': 400, 'text': 'LIFETIME_EXCEEDS_LIMIT'},
            ),
            id='incorrect_lifetime',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'closed_experiment'},
                code={'number': 409, 'text': 'EXPERIMENT_ALREADY_EXISTS'},
            ),
            id='exists_experiment',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'removed_experiment'},
                code={
                    'number': 409,
                    'text': 'REMOVED_EXPERIMENT_ALREADY_EXISTS',
                },
            ),
            id='exists_removed_experiment',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'config_test_draft'},
                code={'number': 409, 'text': 'CONFIG_ALREADY_EXISTS'},
            ),
            id='exists_config_same_name_as_experiment',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'removed_config'},
                code={'number': 409, 'text': 'REMOVED_CONFIG_ALREADY_EXISTS'},
            ),
            id='exists_removed_config_same_name_as_experiment',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_config(),
                params={'name': 'closed_experiment'},
                code={'number': 409, 'text': 'EXPERIMENT_ALREADY_EXISTS'},
            ),
            id='exists_experiment_same_name_as_config',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_config(),
                params={'name': 'removed_experiment'},
                code={
                    'number': 409,
                    'text': 'REMOVED_EXPERIMENT_ALREADY_EXISTS',
                },
            ),
            id='exists_removed_experiment_same_name_as_config',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_config(),
                params={'name': 'config_test_draft'},
                code={'number': 409, 'text': 'CONFIG_ALREADY_EXISTS'},
            ),
            id='exists_config',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_config(),
                params={'name': 'removed_config'},
                code={'number': 409, 'text': 'REMOVED_CONFIG_ALREADY_EXISTS'},
            ),
            id='exists_removed_config',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(
                    match_predicate=experiment.infile_predicate(
                        'non_existed_file_id',
                    ),
                ),
                params={'name': EXPERIMENT_NAME},
                code={'number': 409, 'text': 'DRAFT_CHECKING_ERROR_FOR_FILES'},
            ),
            id='experiment_with_non_existed_file',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(
                    match_predicate=experiment.userhas_predicate(
                        'non_existed_tag',
                    ),
                ),
                params={'name': EXPERIMENT_NAME},
                code={'number': 409, 'text': 'DRAFT_CHECKING_ERROR_FOR_TAGS'},
            ),
            id='experiment_with_non_existed_tag',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(financial=False),
                params={'name': EXPERIMENT_NAME},
                code={
                    'number': 400,
                    'text': 'FINANCIAL_FALSE_IN_NEW_EXPERIMENT',
                },
            ),
            id='experiment_with_false_financial',
        ),
    ],
)
@pytest.mark.config(
    EXP_EXTENDED_DRAFTS=[
        {'DRAFT_NAME': '__default__', 'NEED_CHECKING_FILES': True},
    ],
)
@pytest.mark.pgsql(
    'taxi_exp',
    files=(
        'default.sql',
        'closed_experiment.sql',
        'removed_experiment.sql',
        'config_test_draft.sql',
        'removed_config.sql',
    ),
)
async def test_fails_for_create_experiment_use_draft_checking(
        experiment_body, params, code, taxi_exp_client,
):
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == code['number']
    body = await response.json()
    assert body['code'] == code['text']
