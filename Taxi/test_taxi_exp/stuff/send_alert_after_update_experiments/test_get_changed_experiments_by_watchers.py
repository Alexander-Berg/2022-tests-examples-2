import collections
import copy
import dataclasses

import pytest

from taxi_exp.stuff import send_alert_after_update_experiments as send_module
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'superapp'
FIRST_LOGIN = 'first-login'
FIRST_BODY = experiment.generate(
    name=NAME,
    watchers=[FIRST_LOGIN],
    schema='type: object\nadditionalProperties: false',
)


async def preparation(taxi_exp_client):
    first_body = copy.copy(FIRST_BODY)
    response = await helpers.init_exp(taxi_exp_client, first_body)
    last_modified_at = response['last_modified_at']

    first_body['last_modified_at'] = last_modified_at
    await helpers.update_exp(taxi_exp_client, first_body)


@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'watchers_alerts': {
                    'template_name': 'template.j2',
                    'chunk_size': 10,
                    'subject': 'Updation experiments report',
                    'date_threshold': 10,
                },
            },
        },
    },
)
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            {
                'first-login': [
                    {
                        'exp_id': 1,
                        'is_config': False,
                        'name': 'superapp',
                        'previous_rev': 1,
                        'current_rev': 2,
                        'revisions': [2],
                    },
                ],
            },
        ),
    ],
)
async def test_get_changed_experiments_by_watchers(taxi_exp_client, expected):
    await preparation(taxi_exp_client)
    taxi_exp_client.app.templates_store = {
        'template.j2': None,
        'message_with_links.j2': None,
    }
    alert_sender = send_module.AlertSender(taxi_exp_client.app)
    result = await alert_sender.get_changed_exps_by_watchers()
    check = collections.defaultdict(list)
    for key, value in result.items():
        for item in value:
            inner_item = dataclasses.asdict(item)
            inner_item.pop('update_time')
            check[key].append(inner_item)
    assert check == expected
