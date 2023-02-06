import datetime
import json
import uuid

import pytest
from django.test import Client

MAX_LENGTH_IDS = 10
OVERRIDE_LENGTH_IDS = 100
OVERRIDE_EXPERIMENT = 'override'
ENDED_EXPERIMENT = 'ended_experiment'
DEFAULT_EXPERIMENT = 'default_experiment'
NEXT_YEAR = datetime.datetime.now().year + 1
PAST_YEAR = datetime.datetime.now().year - 1

CONFIG = {
    '__default__': MAX_LENGTH_IDS,
    'overrides': [
        {
            'name': OVERRIDE_EXPERIMENT,
            'override': OVERRIDE_LENGTH_IDS,
            'deadline': '{}-{}-{}'.format(NEXT_YEAR, 12, 12),
        },
        {
            'name': ENDED_EXPERIMENT,
            'override': OVERRIDE_LENGTH_IDS,
            'deadline': '{}-{}-{}'.format(PAST_YEAR, 12, 12),
        }
    ]
}


@pytest.mark.asyncenv('blocking')
def test_get_driver_card():
    response = Client().get('/api/experiments/get_experiment/exp7/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {
        'name': 'exp7',
        'salt': 'ef642f2ef2cb4bb5af92b2791e1ecd72',
        'active': True
    }


@pytest.mark.parametrize(
    'experiment_name,send_counts,status',
    [
        (
            DEFAULT_EXPERIMENT,
            MAX_LENGTH_IDS - 1,
            200,
        ),
        (
            DEFAULT_EXPERIMENT,
            MAX_LENGTH_IDS + 1,
            400,
        ),
        (
            OVERRIDE_EXPERIMENT,
            OVERRIDE_LENGTH_IDS - 1,
            200,
        ),
        (
            OVERRIDE_EXPERIMENT,
            OVERRIDE_LENGTH_IDS + 1,
            400,
        ),
        (
            ENDED_EXPERIMENT,
            OVERRIDE_LENGTH_IDS - 1,
            400,
        ),
        (
            ENDED_EXPERIMENT,
            OVERRIDE_LENGTH_IDS + 1,
            400,
        ),
    ],
)
@pytest.mark.config(EXPERIMENTS_RESTRICT_ID_COUNT=CONFIG)
@pytest.mark.asyncenv('blocking')
def test_ids_length_restrictions(experiment_name, send_counts, status):
    response = Client().post(
        '/api/user_experiments/set/',
        json.dumps(
            {
                'name': experiment_name,
                'user_id_last_digits': [
                    uuid.uuid4().hex for _ in xrange(send_counts)
                ]
            }
        ),
        'application/json',
    )
    assert response.status_code == status
