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
    'communication_name': 'comname',
}

EXPECTED_ENTITY = {
    'id': 'my_lab_entity',
    'phone': '+77778887766',
    'email': 'entity_lab@yandex.ru',
    'web_site': 'www.my_main_lab.ru',
    'communication_name': 'comname',
    'legal_name_short': 'my_entity_lab',
    'legal_name_full': 'my_awesome_entity_lab',
    'legal_address': 'there',
    'ogrn': 'ogrn',
    'web_license_resource': 'www.license.com',
}


@pytest.mark.servicetest
async def test_lab_entities_db(taxi_persey_labs):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', ADMIN_LAB_ENTITY,
    )
    assert response.status_code == 200
    response = await taxi_persey_labs.get(
        '/internal/v1/lab-entity?id=my_lab_entity',
    )
    assert response.status_code == 200
    assert response.json() == EXPECTED_ENTITY
    response = await taxi_persey_labs.get('/core/v1/lab-entities')
    assert response.status_code == 200
    assert response.json()['lab_entities'][0] == EXPECTED_ENTITY
