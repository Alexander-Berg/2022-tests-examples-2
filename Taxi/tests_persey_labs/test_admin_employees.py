import pytest

from tests_persey_labs import utils


ADMIN_URL_PREFIX = 'admin/v1'
DISP_URL_PREFIX = 'disp/v1'


def add_lab(pgsql):
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
            {l_e_contacts_id}, {l_e_billing_id}),
            ('other_entity_lab_id', '123456', 'some contacts', 'comname',
            {l_e_contacts_id}, {l_e_billing_id})
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_ids = [row[0] for row in rows]

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

    query = f"""
        INSERT INTO persey_labs.labs
             (id, lab_entity_id, is_active, "name", description,
            tests_per_day,
             contacts, contact_id, address_id, contact_person_id)
        VALUES
            ('my_lab_id', '{l_e_ids[0]}', TRUE, 'MY_LAB',
            'some description', 10,
            'some contacts', {contacts_id}, {address_id}, {c_p_id}),
            ('other_lab_id', '{l_e_ids[1]}', TRUE, 'OTHER_LAB',
            'some description', 10,
            'some contacts', {contacts_id}, {address_id}, {c_p_id})
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    lab_id = rows[0][0]
    return lab_id


def add_lab_employees(pgsql):
    cursor = pgsql['persey_labs'].cursor()

    lab_id = add_lab(pgsql)

    for i in range(3):
        person_id = 'NULL'
        contacts_id = 'NULL'
        yandex_login = 'NULL'

        if i % 2 == 0:
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

            yandex_login = f'\'login_{i}\''

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

        query = f"""
                INSERT INTO persey_labs.lab_employees
                    (lab_id, yandex_login, is_active, contact_id,
                    person_info_id, address_id)
                VALUES
                    ('{lab_id}', {yandex_login}, TRUE, {contacts_id},
                    {person_id}, {address_id})
                RETURNING id;
            """
        cursor.execute(query)
        rows = cursor.fetchall()
        employee_id = rows[0][0]

        query = f"""
                    INSERT INTO persey_labs.lab_employee_shifts
                        (lab_employee_id, start_time, finish_time)
                    VALUES
                        ('{employee_id}', '2013-01-01 01:45:00 UTC',
                        '2013-01-01 02:45:00 UTC');
                """
        cursor.execute(query)


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.servicetest
async def test_admin_lab_employee_list_simple(
        taxi_persey_labs, pgsql, load_json, url_prefix,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee/list?lab_id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'labs_header, exp_resp_code', [('my_lab_id', 200), ('nonexistent', 403)],
)
async def test_admin_lab_employee_list_forbidden(
        taxi_persey_labs, pgsql, labs_header, exp_resp_code,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.get(
        'disp/v1/lab/employee/list?lab_id=my_lab_id',
        headers={
            'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
            'X-YaTaxi-Lab-Ids': labs_header,
        },
    )
    assert response.status_code == exp_resp_code
    if exp_resp_code == 403:
        assert response.json() == {
            'code': 'lab_forbidden',
            'message': 'Insufficient permissions for lab',
        }


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.servicetest
async def test_admin_lab_employee_get_simple(
        taxi_persey_labs, pgsql, load_json, url_prefix,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_get_simple.json')


@pytest.mark.servicetest
@utils.permission_variants()
async def test_admin_lab_employee_get_forbidden(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.get(
        'disp/v1/lab/employee?id=1', headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.servicetest
async def test_admin_lab_employee_get_not_found(
        taxi_persey_labs, load_json, url_prefix,
):
    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_post_simple(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_post_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.lab_employees;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 1


@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.parametrize(
    'headers, lab_id, exp_resp_code, exp_error_code',
    [
        (
            {'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
            'my_lab_id',
            200,
            None,
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'my_lab_id,nonexistent',
            },
            'my_lab_id',
            200,
            None,
        ),
        (
            {'X-YaTaxi-Lab-Entity-Id': 'nonexistent'},
            'my_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'nonexistent',
                'X-YaTaxi-Lab-Ids': 'my_lab_id',
            },
            'my_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'non_employee_lab',
            },
            'non_employee_lab',
            404,
            'lab_not_in_lab_entity',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'nonexistent',
            },
            'my_lab_id',
            403,
            'lab_forbidden',
        ),
        (
            {'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
            'other_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
    ],
)
@pytest.mark.servicetest
async def test_admin_lab_employee_post_forbidden(
        taxi_persey_labs,
        pgsql,
        load_json,
        headers,
        lab_id,
        exp_resp_code,
        exp_error_code,
):
    add_lab(pgsql)

    post_request_json = load_json('request_put_simple.json')
    post_request_json['lab_id'] = lab_id

    response = await taxi_persey_labs.post(
        'disp/v1/lab/employee', post_request_json, headers=headers,
    )
    assert response.status_code == exp_resp_code

    if exp_error_code is not None:
        assert response.json()['code'] == exp_error_code


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_post_not_found(
        taxi_persey_labs, load_json, mockserver, url_prefix,
):
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.parametrize(
    'phone_add_status_code',
    [
        pytest.param(409),
        pytest.param(
            200,
            marks=pytest.mark.config(
                PERSEY_LABS_ALLOW_DUPLICATE_EMPLOYEE_PHONES=True,
            ),
        ),
    ],
)
async def test_admin_lab_employee_post_conflict(
        taxi_persey_labs,
        pgsql,
        load_json,
        mockserver,
        url_prefix,
        phone_add_status_code,
):
    add_lab(pgsql)

    request = load_json('request_post_simple.json')

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_post_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.lab_employees;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 1

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 409

    request['yandex_login'] = 'nonconflict_login'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == phone_add_status_code


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_post_invalid(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_lab(pgsql)

    request = load_json('request_post_simple.json')
    request['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_put_simple(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_post_simple.json')

    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        load_json('request_put_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_put_simple.json')

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_put_simple.json')


@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.parametrize(
    'headers, lab_id, exp_resp_code, exp_error_code',
    [
        (
            {'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
            'my_lab_id',
            200,
            None,
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'my_lab_id,nonexistent',
            },
            'my_lab_id',
            200,
            None,
        ),
        (
            {'X-YaTaxi-Lab-Entity-Id': 'nonexistent'},
            'my_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'nonexistent',
                'X-YaTaxi-Lab-Ids': 'my_lab_id',
            },
            'my_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'other_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'other_lab_id',
            },
            'other_lab_id',
            404,
            'lab_employee_not_found',
        ),
        (
            {
                'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
                'X-YaTaxi-Lab-Ids': 'nonexistent',
            },
            'my_lab_id',
            403,
            'lab_forbidden',
        ),
        (
            {'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
            'other_lab_id',
            404,
            'lab_not_in_lab_entity',
        ),
    ],
)
@pytest.mark.servicetest
async def test_admin_lab_employee_put_forbidden(
        taxi_persey_labs,
        pgsql,
        load_json,
        headers,
        lab_id,
        exp_resp_code,
        exp_error_code,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        'disp/v1/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    put_request_json = load_json('request_put_simple.json')
    put_request_json['lab_id'] = lab_id

    response = await taxi_persey_labs.put(
        'disp/v1/lab/employee?id=1', put_request_json, headers=headers,
    )
    assert response.status_code == exp_resp_code

    if exp_error_code is not None:
        assert response.json()['code'] == exp_error_code


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_put_not_found(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        load_json('request_put_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404

    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_post_simple.json')

    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        load_json('request_put_not_found.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.parametrize(
    'phone_add_status_code',
    [
        pytest.param(409),
        pytest.param(
            200,
            marks=pytest.mark.config(
                PERSEY_LABS_ALLOW_DUPLICATE_EMPLOYEE_PHONES=True,
            ),
        ),
    ],
)
async def test_admin_lab_employee_put_conflict(
        taxi_persey_labs,
        pgsql,
        load_json,
        mockserver,
        url_prefix,
        phone_add_status_code,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_for_conflict.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        load_json('request_put_conflict.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 409

    request = load_json('request_put_conflict.json')
    request['yandex_login'] = 'non_conflict_login'
    request['contact_detailed']['phone'] = '+79999997766'
    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == phone_add_status_code


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_employee_put_invalid(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab/employee',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    request = load_json('request_put_simple.json')
    request['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_put_simple.json')
    request['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab/employee?id=1',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('url_prefix', [DISP_URL_PREFIX])
@pytest.mark.servicetest
async def test_admin_lab_employee_delete_simple(
        taxi_persey_labs, pgsql, load_json, url_prefix,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.delete(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab/employee?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404

    cursor = pgsql['persey_labs'].cursor()
    query = f"""
                SELECT id FROM persey_labs.lab_employee_shifts
                WHERE lab_employee_id = 1;
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    assert not rows


@pytest.mark.servicetest
@utils.permission_variants()
async def test_admin_lab_employee_delete_forbidden(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees(pgsql)

    response = await taxi_persey_labs.delete(
        'disp/v1/lab/employee?id=1', headers=headers,
    )
    assert response.status_code == exp_resp_code
