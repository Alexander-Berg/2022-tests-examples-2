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
    'test_kinds': ['covid_fast', 'covid_slow'],
}

ADMIN_LAB = {
    'address': {
        'comment': 'Do not enter',
        'locality_id': 213,
        'position': [37.642214, 55.734438],
        'subtitle': 'where',
        'text': 'Somewhere',
        'title': 'some',
    },
    'contact_detailed': {
        'email': 'mail@yandex.ru',
        'phone': '+78888887766',
        'web_site': 'wwww.my_lab.ru',
    },
    'contact_person': {
        'contact_detailed': {
            'email': 'mail@yandex.ru',
            'phone': '+79998887766',
        },
        'name': 'Ivanov Ivan',
    },
    'contacts': 'some contacts',
    'description': 'some description',
    'id': 'my_lab',
    'is_active': True,
    'lab_entity_id': 'my_entity_lab',
    'name': 'MY_LAB',
    'tests_per_day': 10,
}


async def add_labs(taxi_persey_labs):
    post_entity = copy.deepcopy(ADMIN_LAB_ENTITY)
    post_entity['id'] = 'my_entity_lab'
    post_entity['custom_employee_address'] = True
    post_entity['custom_lab_id'] = True
    response = await taxi_persey_labs.post('admin/v1/lab-entity', post_entity)
    assert response.status_code == 200

    response = await taxi_persey_labs.post(
        'disp/v1/lab',
        ADMIN_LAB,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab'},
    )
    assert response.status_code == 200


@pytest.mark.now('2020-04-30T12:05:15+00')
@pytest.mark.config(
    PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213},
    PERSEY_LABS_RESTRICTIONS_OF_SHIFTS_CHANGE={
        '213': {
            'update_shifts_time': '10:15',
            'add_shifts_time': '12:35',
            'swap_employee_m': 30,
            'is_today_included': True,
        },
    },
)
@pytest.mark.servicetest
async def test_disp_settings(taxi_persey_labs, mockserver, load_json):
    await add_labs(taxi_persey_labs)

    response = await taxi_persey_labs.get(
        f'/disp/v1/settings?login=ya_login&lab_id=my_lab',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')
