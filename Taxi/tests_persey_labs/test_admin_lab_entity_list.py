import pytest


def add_labs(fill_labs):
    entity_ids = []
    for i in range(3):
        eid = fill_labs.add_lab_entity(
            f'my_entity_{i}',
            fill_labs.l_e_contacts_id,
            fill_labs.l_e_billing_id,
            is_active=False,
        )
        entity_ids.append(eid)

    address_id = fill_labs.add_address(
        '35.5', '55.5', 213, 'Somewhere', 'some', 'where', 'Do not enter',
    )
    i = 0
    k = 0
    for entity_id in entity_ids:
        for _ in range(i):
            fill_labs.add_lab(
                f'my_lab_id_{k}',
                entity_id,
                f'MY_LAB_{k}',
                10,
                fill_labs.contacts_id,
                address_id,
                fill_labs.c_p_id,
            )
            k += 1
        i += 1


def get_ids(response):
    return {lab_entity['id'] for lab_entity in response['lab_entities']}


@pytest.mark.servicetest
async def test_admin_lab_entity_list_simple(
        taxi_persey_labs, fill_labs, load_json,
):
    add_labs(fill_labs)

    response = await taxi_persey_labs.post('admin/v1/lab-entity/list')
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')


@pytest.mark.servicetest
async def test_admin_lab_entity_list_pagination(
        taxi_persey_labs, fill_labs, load_json,
):
    add_labs(fill_labs)

    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity/list', {'results': 2},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert get_ids(response_body) == {'my_entity_0', 'my_entity_1'}

    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity/list', {'cursor': response_body['cursor']},
    )
    assert response.status_code == 200
    assert get_ids(response.json()) == {'my_entity_2'}
