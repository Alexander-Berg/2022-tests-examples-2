import pytest


def add_lab_entity(pgsql):
    cursor = pgsql['persey_labs'].cursor()

    query = """
        INSERT INTO persey_labs.contacts
            (phone, email, web_site)
        VALUES
            ('+77778887766', 'entity_lab@yandex.ru',
            'www.my_main_lab@yandex.ru')
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_contacts_id = rows[0][0]

    query = """
        INSERT INTO persey_labs.billing_infos
            (legal_name_short, legal_name_full, OGRN,
            legal_address, postal_address, web_license_resource,
            BIK, settlement_account, contract_start_dt, partner_uid,
            partner_commission, contract_id)
        VALUES
            ('my_entity_lab', 'my_awesome_entity_lab',
            'ogrn', 'there', 'right there', 'www.license.com',
            'bik', 'what is that', 'date', 'uid', '2.73', '321')
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_billing_id = rows[0][0]

    query = f"""
        INSERT INTO persey_labs.lab_entities
            (id, taxi_corp_id, is_active, contacts, test_kind,
            employee_tests_threshold,
            custom_employee_address, custom_lab_id, communication_name,
            contact_id, billing_info_id)
        VALUES
            ('my_lab_entity', '123456', TRUE, 'some contacts', 'simple', 10,
            TRUE, TRUE, 'comname', {l_e_contacts_id}, {l_e_billing_id});
    """
    cursor.execute(query)

    query = f"""
        INSERT INTO persey_labs.lab_entity_tests
            (lab_entity_id, test_id)
        VALUES
            ('my_lab_entity', 'covid_fast'),
            ('my_lab_entity', 'covid_slow');
    """
    cursor.execute(query)


@pytest.mark.servicetest
async def test_admin_lab_entity_get_simple(taxi_persey_labs, pgsql, load_json):
    add_lab_entity(pgsql)

    response = await taxi_persey_labs.get(
        'admin/v1/lab-entity?id=my_lab_entity',
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['contract_id'] = 'n/a'
    exp_response = load_json('exp_response_simple.json')
    exp_response['entity_tests_per_day'] = 0
    assert response_json == exp_response


@pytest.mark.servicetest
async def test_admin_lab_entity_post_simple(
        taxi_persey_labs, pgsql, load_json,
):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.lab_entities;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 'my_lab_entity'


@pytest.mark.servicetest
async def test_admin_lab_entity_post_conflict(
        taxi_persey_labs, pgsql, load_json,
):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.lab_entities;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 'my_lab_entity'

    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )
    assert response.status_code == 409

    request = load_json('request_post_simple.json')
    request['test_kinds'] = ['test_not_in_cfg']
    response = await taxi_persey_labs.post('admin/v1/lab-entity', request)
    assert response.status_code == 409


@pytest.mark.servicetest
async def test_admin_lab_entity_post_invalid(
        taxi_persey_labs, pgsql, load_json,
):
    request = load_json('request_post_simple.json')
    request['id'] = (
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aaaaaaaaaaaa > 120 aaaaaa'
    )
    response = await taxi_persey_labs.post('admin/v1/lab-entity', request)
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.post('admin/v1/lab-entity', request)
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.post('admin/v1/lab-entity', request)
    assert response.status_code == 400


@pytest.mark.servicetest
async def test_admin_lab_entity_put_simple(taxi_persey_labs, pgsql, load_json):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )
    response = await taxi_persey_labs.put(
        'admin/v1/lab-entity?id=my_lab_entity',
        load_json('request_put_simple.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_put_response_simple.json')

    response = await taxi_persey_labs.get(
        'admin/v1/lab-entity?id=my_lab_entity',
    )
    assert response.status_code == 200
    exp_response = load_json('exp_put_response_simple.json')
    exp_response['entity_tests_per_day'] = 0
    assert response.json() == exp_response


@pytest.mark.servicetest
async def test_admin_lab_entity_put_not_found(
        taxi_persey_labs, pgsql, load_json,
):
    response = await taxi_persey_labs.put(
        'admin/v1/lab-entity?id=my_lab_entity',
        load_json('request_put_simple.json'),
    )
    assert response.status_code == 404


@pytest.mark.servicetest
async def test_admin_lab_entity_put_conflict(
        taxi_persey_labs, pgsql, load_json,
):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )

    request = load_json('request_put_simple.json')
    request['test_kinds'] = ['test_not_in_cfg']
    response = await taxi_persey_labs.put(
        'admin/v1/lab-entity?id=my_lab_entity', request,
    )
    assert response.status_code == 409


@pytest.mark.servicetest
async def test_admin_lab_entity_put_invalid(
        taxi_persey_labs, pgsql, load_json,
):
    response = await taxi_persey_labs.post(
        'admin/v1/lab-entity', load_json('request_post_simple.json'),
    )

    request = load_json('request_put_simple.json')
    request['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.put(
        'admin/v1/lab-entity?id=my_lab_entity', request,
    )
    assert response.status_code == 400

    request = load_json('request_put_simple.json')
    request['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.put(
        'admin/v1/lab-entity?id=my_lab_entity', request,
    )
    assert response.status_code == 400
