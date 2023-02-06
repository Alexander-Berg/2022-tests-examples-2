import copy

import pytest

EXTERNAL_REF = 'external_ref_1'
SHIPPER = {
    'external_ref': EXTERNAL_REF,
    'billing': {
        'client_id': 'billing_client_id_1',
        'person_id': 'billing_person_id_1',
        'contract_id': 'billing_contract_id_1',
        'external_id': 'billing_external_id_1',
    },
}


@pytest.mark.parametrize('entities', ['shippers', 'carriers'])
async def test_successful_registration(find, request_register, entities):
    response = await request_register(entities)
    assert response.status_code == 200

    shippers = await find(entities)
    assert shippers == [SHIPPER]


@pytest.mark.parametrize('entities', ['shippers', 'carriers'])
async def test_noone_found(find, entities):
    shippers = await find(entities)
    assert shippers == []


@pytest.mark.parametrize('entities', ['shippers', 'carriers'])
async def test_idempotency(request_register, entities):
    for _ in range(2):
        response = await request_register(entities)
        assert response.status_code == 200


@pytest.mark.parametrize('entities', ['shippers', 'carriers'])
async def test_non_equal_refs(request_register, entities):
    response = await request_register(entities, external_ref='another_ref')
    assert response.status_code == 400
    assert response.json() == {
        'code': 'non_equal_external_refs',
        'message': 'query.external_ref != body.external_ref',
        'details': {},
    }


@pytest.mark.parametrize('entities', ['shippers', 'carriers'])
async def test_conflict(request_register, entities):
    first_response = await request_register(entities, SHIPPER)
    assert first_response.status_code == 200

    another_shipper = copy.deepcopy(SHIPPER)
    another_shipper['billing']['person_id'] = 'billing_person_id_2'
    second_response = await request_register(entities, another_shipper)
    assert second_response.status_code == 409
    assert second_response.json() == {
        'code': 'conflict',
        'message': 'Shipper has been registered with different parameters',
        'details': {},
    }


async def test_different_namespaces(request_register, find, pgsql):
    shipper_entry = SHIPPER.copy()
    shipper_entry['external_ref'] = 'shipper_id_1'
    shipper_register_response = await request_register(
        'shippers',
        shipper=shipper_entry,
        external_ref=shipper_entry['external_ref'],
    )
    assert shipper_register_response.status_code == 200

    carrier_entry = SHIPPER.copy()
    carrier_entry['external_ref'] = 'carrier_id_1'
    carrier_register_response = await request_register(
        'carriers',
        shipper=carrier_entry,
        external_ref=carrier_entry['external_ref'],
    )
    assert carrier_register_response.status_code == 200

    print('111111111111111111111111111111111111111111111111111')
    for tbl in ['carriers', 'shippers']:
        cursor = pgsql['cargo_trucks'].cursor()
        cursor.execute('SELECT * FROM cargo_trucks.{}'.format(tbl))
        print(tbl, list(cursor))

    shippers = await find(
        'shippers', external_ref=shipper_entry['external_ref'],
    )
    assert shippers == [shipper_entry]
    carriers = await find(
        'carriers', external_ref=carrier_entry['external_ref'],
    )
    assert carriers == [carrier_entry]

    no_shippers = await find(
        'shippers', external_ref=carrier_entry['external_ref'],
    )
    assert no_shippers == []
    no_carriers = await find(
        'carriers', external_ref=shipper_entry['external_ref'],
    )
    assert no_carriers == []


#  ##############################
#  Target handlers with shortcuts


@pytest.fixture(name='find')
def _find(taxi_cargo_trucks):
    url_template = '/internal/cargo-trucks/{}/find'

    async def wrapper(entities, external_ref=None):
        url = url_template.format(entities)

        if external_ref is None:
            external_ref = EXTERNAL_REF

        params = {'external_ref': external_ref}
        response = await taxi_cargo_trucks.post(url, params=params)
        assert response.status_code == 200
        return response.json()[entities]

    return wrapper


@pytest.fixture(name='request_register')
def _request_register(taxi_cargo_trucks):
    url_template = '/internal/cargo-trucks/{}/register'

    async def wrapper(entities, shipper=None, external_ref=None):
        url = url_template.format(entities)

        if shipper is None:
            shipper = SHIPPER

        if external_ref is None:
            external_ref = shipper['external_ref']

        params = {'external_ref': external_ref}
        data = shipper
        response = await taxi_cargo_trucks.post(url, params=params, json=data)
        return response

    return wrapper
