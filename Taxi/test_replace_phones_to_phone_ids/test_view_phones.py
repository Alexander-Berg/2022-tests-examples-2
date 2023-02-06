# pylint: disable=invalid-name,unused-variable,redefined-outer-name
import copy

import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'test_convert_phones'
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


@pytest.fixture
def common(patch_user_api, patch_personal):
    for phone_id, phone in zip(USER_API_PHONE_IDS, PHONES):
        patch_user_api.add(phone_id, phone)
    for phone_id, phone in zip(PERSONAL_PHONE_IDS, PHONES):
        patch_personal.add(phone_id, phone)


@pytest.fixture
def prepare_data(taxi_exp_client, common):
    async def _prepare(is_type, phone_ids, transform):
        predicate = copy.deepcopy(MATCH_PREDICATE)
        predicate['init']['set'] = PHONES
        predicate['init']['transform'] = transform
        experiment_body = experiment.generate(
            EXPERIMENT_NAME,
            clauses=[experiment.make_clause('First', predicate=predicate)],
            default_value={},
        )

        response = await taxi_exp_client.post(
            f'/v1/{is_type}s/drafts/check/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={'name': EXPERIMENT_NAME},
            json=experiment_body,
        )
        assert response.status == 200
        body = await response.json()
        assert body['change_doc_id'] == f'{is_type}_{EXPERIMENT_NAME}'
        result = await response.json()
        assert result['data']
        experiment_with_replaced_phones = result['data'][is_type]
        assert sorted(
            experiment_with_replaced_phones['clauses'][0]['predicate']['init'][
                'set'
            ],
        ) == sorted(phone_ids)

        return experiment_with_replaced_phones

    return _prepare


@pytest.mark.parametrize('is_type', ['config', 'experiment'])
@pytest.mark.parametrize(
    ('transform', 'phone_ids'),
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
        taxi_exp_client, prepare_data, is_type, transform, phone_ids,
):
    experiment_with_replaced_phones = await prepare_data(
        is_type, phone_ids, transform,
    )

    # convert experiment/config with phones
    response = await taxi_exp_client.post(
        f'/v1/{is_type}s/view-phones/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_with_replaced_phones,
    )
    assert response.status == 200
    experiment_for_human = await response.json()
    assert (
        experiment_for_human['clauses'][0]['predicate']['init']['set']
        == PHONES
    )
