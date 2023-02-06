# pylint: disable=invalid-name,unused-variable,redefined-outer-name
import copy

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

PHONES = ['+79998886655', '+79998886644', '+76668886643']
PERSONAL_PHONE_IDS = [
    '8acf3a0383de4fd9a6d8866e6c218284',
    '7dd39170d35b47169771f508f3b0fdba',
    '6134ca6ac4754dcaaa566c853e9b8bc7',
]
USER_API_PHONE_IDS = [
    '5d68ee201ef4755d66d55faf',
    '5d68ee221ef4755d66d55fb0',
    '5d68ee221ef4755d66d55fb1',
]
EXPERIMENT_NAME = 'test_convert_phones'
MATCH_PREDICATE = {
    'type': 'in_set',
    'init': {
        'set': PHONES,
        'set_elem_type': 'string',
        'arg_name': 'phone_id',
        'phone_type': 'yandex',
        'transform': '',
    },
}


@pytest.fixture(autouse=True)
def common(patch_user_api, patch_personal):
    for phone_id, phone in zip(USER_API_PHONE_IDS, PHONES):
        patch_user_api.add(phone_id, phone)
    for phone_id, phone in zip(PERSONAL_PHONE_IDS, PHONES):
        patch_personal.add(phone_id, phone)


@pytest.mark.parametrize(
    ('transform', 'expected_predicate_values'),
    [
        ('replace_phone_to_personal_phone_id', PERSONAL_PHONE_IDS),
        ('replace_phone_to_phone_id', USER_API_PHONE_IDS),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi_exp', 'dst': 'personal'}],
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
        'features': {'common': {'enable_convert_phone_to_phone_id': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_replace_phones_to_phone_ids(
        taxi_exp_client, patch_personal, transform, expected_predicate_values,
):
    match_predicate = copy.deepcopy(MATCH_PREDICATE)
    match_predicate['init']['transform'] = transform
    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment.generate(
            name=EXPERIMENT_NAME, match_predicate=match_predicate,
        ),
    )
    assert response.status == 200

    # getting experiment with phones
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params={'name': EXPERIMENT_NAME},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    experiment_for_human = await response.json()
    assert experiment_for_human['match']['predicate']['init']['set'] == PHONES
    last_modified_at = experiment_for_human.pop('last_modified_at')

    # check what experiment safe phone_ids whitout phone number
    result = await helpers.get_updates(
        taxi_exp_client, newer_than=last_modified_at - 1, limit=1,
    )
    assert result['experiments']
    experiment_for_service = result['experiments'][0]
    assert sorted(
        experiment_for_service['match']['predicate']['init']['set'],
    ) == sorted(expected_predicate_values)
