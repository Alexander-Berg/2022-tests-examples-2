import copy

import pytest


ADMIN_LAB_ENTITY = {
    'BIK': 'bik',
    'OGRN': 'ogrn',
    'contact_detailed': {
        'email': 'entity_lab@yandex.ru',
        'phone': '+77778887766',
        'web_site': 'www.my_main_lab.ru',
    },
    'contacts': 'some contacts',
    'id': 'my_lab_entity',
    'taxi_corp_id': '123456',
    'legal_address': 'there',
    'legal_name_full': 'my_awesome_entity_lab',
    'legal_name_short': 'my_entity_lab',
    'postal_address': 'right there',
    'settlement_account': 'what is that',
    'contract_start_dt': 'date',
    'partner_commission': '2.73',
    'partner_uid': 'uid',
    'web_license_resource': 'www.license.com',
    'is_active': True,
}


async def add_entities(taxi_persey_labs):
    for entity in ['my_lab', 'aliens_lab', 'dudes_lab']:
        post_entity = copy.deepcopy(ADMIN_LAB_ENTITY)
        post_entity['id'] = entity
        post_entity['custom_employee_address'] = True
        post_entity['custom_lab_id'] = True
        response = await taxi_persey_labs.post(
            'admin/v1/lab-entity', post_entity,
        )
        assert response.status_code == 200


@pytest.mark.config(
    PERSEY_LABS_COORDINATORS={
        'my_lab': {
            '__entity_coordinators__': ['me', 'dirty'],
            'lab1': ['em', 'dirty'],
            'lab2': ['em'],
        },
        'aliens_lab': {'lab3': ['me']},
        'empty_lab': {},
    },
)
@pytest.mark.parametrize(
    'login, lab_entity_id, exp_response',
    [
        ('me', 'my_lab', {'confirmed': True}),
        ('dirty', 'my_lab', {'confirmed': True}),
        ('me', 'aliens_lab', {'confirmed': True, 'labs': {'lab3'}}),
        ('em', 'my_lab', {'confirmed': True, 'labs': {'lab1', 'lab2'}}),
        ('nonexistent', 'my_lab', {'confirmed': False}),
        ('nonexistent', 'aliens_lab', {'confirmed': False}),
        ('nonexistent', 'empty_lab', {'confirmed': False}),
        ('me', 'wrong_lab', {'confirmed': False}),
    ],
)
@pytest.mark.servicetest
async def test_disp_user_check(
        taxi_persey_labs, mockserver, login, lab_entity_id, exp_response,
):
    response = await taxi_persey_labs.get(
        f'/internal/v1/disp/user/check'
        f'?login={login}&lab_entity_id={lab_entity_id}',
    )
    assert response.status_code == 200
    assert response.json()['confirmed'] == exp_response['confirmed']

    resp_labs = response.json().get('labs')
    if resp_labs is not None:
        resp_labs = set(resp_labs)
    assert resp_labs == exp_response.get('labs')


@pytest.mark.config(
    PERSEY_LABS_COORDINATORS={
        'my_lab': {
            '__entity_coordinators__': ['me', 'dirty'],
            'lab1': ['em', 'dirty'],
            'lab2': ['em'],
        },
        'aliens_lab': {'lab3': ['me']},
        'empty_lab': {},
    },
)
@pytest.mark.parametrize(
    'login, exp_code, exp_response',
    [
        ('me', 200, [('my_lab', True), ('aliens_lab', False)]),
        ('dirty', 200, [('my_lab', True)]),
        ('em', 200, [('my_lab', False)]),
        ('stranger', 403, None),
    ],
)
@pytest.mark.servicetest
async def test_disp_user_lab_entity_list(
        taxi_persey_labs, mockserver, login, exp_code, exp_response,
):
    await add_entities(taxi_persey_labs)

    response = await taxi_persey_labs.get(
        f'/disp/v1/user/lab-entity/list?login={login}',
    )
    assert response.status_code == exp_code
    if exp_response is not None:
        response_ids = [
            (entity['id'], entity['is_user_coordinator'])
            for entity in response.json()['entity_labs']
        ]
        assert sorted(response_ids) == sorted(exp_response)
