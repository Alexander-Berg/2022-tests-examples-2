import pytest


def add_labs(pgsql):
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
            (id, taxi_corp_id, contacts, communication_name, contact_id,
            billing_info_id)
        VALUES
            ('my_entity_lab_id', '123456', 'some contacts', 'comname',
            {l_e_contacts_id}, {l_e_billing_id})
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]

    query = """
        INSERT INTO persey_labs.addresses
            (full_text, lon, lat, locality_id, title, subtitle, comment)
        VALUES
            ('Somewhere', '37.642214', '55.734438', 213, 'some', 'where',
            'Do not enter')
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    address_id = rows[0][0]

    query = """
        INSERT INTO persey_labs.contacts
            (phone, email)
        VALUES
            ('+79998887766', 'mail@yandex.ru')
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    c_p_contacts_id = rows[0][0]

    query = f"""
        INSERT INTO persey_labs.lab_contact_persons
            ("name", contact_id)
        VALUES
            ('Ivanov Ivan', {c_p_contacts_id})
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    c_p_id = rows[0][0]

    query = """
        INSERT INTO persey_labs.contacts
            (phone, email, web_site)
        VALUES
            ('+78888887766', 'mail@yandex.ru', 'wwww.my_lab.ru')
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    contacts_id = rows[0][0]

    for i in range(3):
        query = f"""
            INSERT INTO persey_labs.labs
                 (id, lab_entity_id, is_active, "name", description,
                  tests_per_day,
                 contacts, contact_id, address_id, contact_person_id)
            VALUES
                ('my_lab_id_{i}', '{l_e_id}', 'TRUE', 'MY_LAB_{i}',
                'some description', 10,
                'some contacts', {contacts_id}, {address_id}, {c_p_id});
        """
        cursor.execute(query)

    query = f"""
        INSERT INTO persey_labs.lab_entities
            (id, taxi_corp_id, contacts, communication_name, contact_id,
            billing_info_id)
        VALUES
            ('id_for_filter', '123456', 'some contacts', 'comname',
            {l_e_contacts_id}, {l_e_billing_id})
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]

    query = """
            INSERT INTO persey_labs.addresses
                (full_text, lon, lat, locality_id, title, subtitle, comment)
            VALUES
                ('Somewhere', '37.642214', '55.734438', 2, 'some', 'where',
                'Do not enter'),
                ('Somewhere', '37.642214', '55.734438', 213, 'some', 'where',
                'Do not enter'),
                ('Somewhere', '37.642214', '55.734438', 213, 'some', 'where',
                'Do not enter')
            RETURNING id;
        """
    cursor.execute(query)
    rows = cursor.fetchall()
    address_ids = [row[0] for row in rows]

    query = f"""
            INSERT INTO persey_labs.labs
                 (id, lab_entity_id, is_active, "name", description,
                  tests_per_day,
                 contacts, contact_id, address_id, contact_person_id)
            VALUES
                ('my_lab_id_10', '{l_e_id}', 'FALSE', 'MY_LAB_10',
                'some description', 10,
                'some contacts', {contacts_id}, {address_ids[0]}, {c_p_id}),
                ('my_lab_id_11', '{l_e_id}', 'TRUE', 'MY_LAB_11',
                'some description', 10,
                'some contacts', {contacts_id}, {address_ids[1]}, {c_p_id}),
                ('my_lab_id_12', '{l_e_id}', 'TRUE', 'MY_LAB_12',
                'some description', 10,
                'some contacts', {contacts_id}, {address_ids[2]}, {c_p_id})
            RETURNING id;
        """
    cursor.execute(query)
    rows = cursor.fetchall()
    lab_ids = [row[0] for row in rows]

    query = """
            INSERT INTO persey_labs.person_infos
                (firstname, middlename, surname)
            VALUES
                ('Ivanov', 'Ivan', 'Ivanovich')
            RETURNING id;
        """
    cursor.execute(query)
    rows = cursor.fetchall()
    person_id = rows[0][0]

    query = """
            INSERT INTO persey_labs.contacts
                (phone, email)
            VALUES
                ('+79998887766', 'mail@yandex.ru')
            RETURNING id;
        """
    cursor.execute(query)
    rows = cursor.fetchall()
    contacts_id = rows[0][0]

    query = f"""
            INSERT INTO persey_labs.lab_employees
                (lab_id, yandex_login, is_active, contact_id, person_info_id,
                address_id)
            VALUES
                ('{lab_ids[0]}', 'login_test_10', TRUE, {contacts_id},
                {person_id}, {address_id}),
                ('{lab_ids[1]}', 'login_test_11', TRUE, {contacts_id},
                {person_id}, {address_id}),
                ('{lab_ids[2]}', 'login_test_12', TRUE, {contacts_id},
                {person_id}, {address_id});
        """
    cursor.execute(query)


def get_ids(response):
    return {lab['id'] for lab in response['labs']}


@pytest.mark.servicetest
async def test_admin_lab_list_simple(taxi_persey_labs, pgsql, load_json):
    add_labs(pgsql)

    response = await taxi_persey_labs.post('admin/v1/lab/list')
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')


@pytest.mark.servicetest
async def test_admin_lab_list_pagination(taxi_persey_labs, pgsql, load_json):
    add_labs(pgsql)

    response = await taxi_persey_labs.post('admin/v1/lab/list', {'results': 2})
    assert response.status_code == 200
    response_body = response.json()
    assert get_ids(response_body) == {'my_lab_id_0', 'my_lab_id_1'}

    response = await taxi_persey_labs.post(
        'admin/v1/lab/list', {'cursor': response_body['cursor']},
    )
    assert response.status_code == 200
    assert get_ids(response.json()) == {
        'my_lab_id_10',
        'my_lab_id_11',
        'my_lab_id_12',
        'my_lab_id_2',
    }


@pytest.mark.parametrize(
    'filters, exp_ids',
    [
        ({'lab_id': 'my_lab_id_10'}, {'my_lab_id_10'}),
        ({'is_active': False}, {'my_lab_id_10'}),
        ({'locality_id': 2}, {'my_lab_id_10'}),
        (
            {'lab_entity_id': 'id_for_filter'},
            {'my_lab_id_10', 'my_lab_id_11', 'my_lab_id_12'},
        ),
        ({'lab_employee_yandex_login': 'login_test_10'}, {'my_lab_id_10'}),
    ],
)
@pytest.mark.servicetest
async def test_admin_lab_list_filters(
        taxi_persey_labs, pgsql, load_json, filters, exp_ids,
):
    add_labs(pgsql)

    response = await taxi_persey_labs.post(
        'admin/v1/lab/list', {'filters': filters},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert get_ids(response_body) == exp_ids


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'lab_ids_header, filters, exp_ids, exp_resp_status',
    [
        (None, None, {'my_lab_id_10', 'my_lab_id_11', 'my_lab_id_12'}, 200),
        (
            'my_lab_id_10,my_lab_id_11',
            None,
            {'my_lab_id_10', 'my_lab_id_11'},
            200,
        ),
        ('my_lab_id_100,my_lab_id_110', None, set(), 200),
        (None, {'lab_id': 'my_lab_id_11'}, {'my_lab_id_11'}, 200),
        (None, {'lab_id': 'my_lab_id_110'}, set(), 200),
        (
            'my_lab_id_10,my_lab_id_11',
            {'lab_id': 'my_lab_id_11'},
            {'my_lab_id_11'},
            200,
        ),
        ('my_lab_id_10,my_lab_id_11', {'lab_id': 'my_lab_id_110'}, None, 400),
    ],
)
async def test_disp_lab_list_permissions(
        taxi_persey_labs,
        pgsql,
        lab_ids_header,
        filters,
        exp_ids,
        exp_resp_status,
):
    add_labs(pgsql)

    headers = {'X-YaTaxi-Lab-Entity-Id': 'id_for_filter'}
    if lab_ids_header:
        headers['X-YaTaxi-Lab-Ids'] = lab_ids_header

    response = await taxi_persey_labs.post(
        'disp/v1/lab/list', headers=headers, json={'filters': filters},
    )
    assert response.status_code == exp_resp_status

    if exp_resp_status == 200:
        assert get_ids(response.json()) == exp_ids
