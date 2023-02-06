import datetime
import typing

import pytest

from test_taxi_exp.helpers import db
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
                params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
                code={'number': 400, 'text': 'CHECK_SCHEMA_ERROR'},
            ),
            id='incorrect_body',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(),
                params={'name': 'incorrect name', 'last_modified_at': 1},
                code={'number': 404, 'text': 'EXPERIMENT_NOT_FOUND'},
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
                params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
                code={'number': 400, 'text': 'LIFETIME_EXCEEDS_LIMIT'},
            ),
            id='incorrect_action_time',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(
                    match_predicate=experiment.infile_predicate(
                        'non_existed_file_id',
                    ),
                ),
                params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
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
                params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
                code={'number': 409, 'text': 'DRAFT_CHECKING_ERROR_FOR_TAGS'},
            ),
            id='experiment_with_non_existed_tag',
        ),
        pytest.param(
            *Case(
                experiment_body=experiment.generate_default(financial=False),
                params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
                code={
                    'number': 400,
                    'text': 'ILLEGALLY_SETTING_FINANCIAL_TO_FALSE',
                },
            ),
            id='experiment_with_false_financial',
        ),
    ],
)
@pytest.mark.config(
    EXP_EXTENDED_DRAFTS=[
        {
            'DRAFT_NAME': '__default__',
            'NEED_CHECKING_FILES': True,
            'NEED_CHECKING_BODY': True,
        },
    ],
)
@pytest.mark.pgsql(
    'taxi_exp',
    files=('experiment.sql',),
    queries=[
        db.ADD_CONSUMER.format('test_consumer'),
        db.ADD_APPLICATION.format('ios'),
        db.ADD_APPLICATION.format('android'),
    ],
)
async def test_fails_for_create_experiment_use_draft_checking(
        experiment_body, params, code, taxi_exp_client,
):
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == code['number'], await response.text()
    body = await response.json()
    assert body['code'] == code['text']
