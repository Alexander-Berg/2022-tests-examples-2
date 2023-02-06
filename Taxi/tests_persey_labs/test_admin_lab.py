import pytest

ADMIN_URL_PREFIX = 'admin/v1'
DISP_URL_PREFIX = 'disp/v1'


def add_entity_lab(pgsql):
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
    return l_e_id


def add_lab(pgsql):
    cursor = pgsql['persey_labs'].cursor()

    l_e_id = add_entity_lab(pgsql)

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
            ('my_lab_id', '{l_e_id}', TRUE, 'MY_LAB', 'some description', 10,
            'some contacts', {contacts_id}, {address_id}, {c_p_id})
            RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    lab_id = rows[0][0]

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
                    ('{lab_id}', 'login', TRUE, NULL, NULL, {address_id})
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
async def test_admin_lab_get_simple(
        taxi_persey_labs, pgsql, load_json, url_prefix,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab?id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'labs_header, exp_resp_code', [('my_lab_id', 200), ('nonexistent', 403)],
)
async def test_disp_lab_get_forbidden(
        taxi_persey_labs, pgsql, labs_header, exp_resp_code,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.get(
        'disp/v1/lab?id=my_lab_id',
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
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_post_simple(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_entity_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.labs;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 'my_lab_id'


@pytest.mark.parametrize(
    'labs_header, exp_resp_code', [(None, 200), ('any', 403)],
)
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_disp_lab_post_forbidden(
        taxi_persey_labs, pgsql, load_json, labs_header, exp_resp_code,
):
    add_entity_lab(pgsql)

    headers = {'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'}
    if labs_header is not None:
        headers['X-YaTaxi-Lab-Ids'] = labs_header

    response = await taxi_persey_labs.post(
        'disp/v1/lab', load_json('request_post_simple.json'), headers=headers,
    )

    assert response.status_code == exp_resp_code

    if exp_resp_code == 403:
        assert response.json() == {
            'code': 'lab_entity_forbidden',
            'message': 'Insufficient permissions for lab_entity',
        }


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_post_generated_id(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_entity_lab(pgsql)

    request = load_json('request_post_simple.json')
    request.pop('id')
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    exp_response = load_json('exp_response_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = 'SELECT nextval(\'labs_ids\');'
    cursor.execute(query)
    rows = cursor.fetchall()
    lab_id_num = rows[0][0]

    exp_response['id'] = 'my_entity_lab_id_' + str(lab_id_num - 1)
    assert response.json() == exp_response


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_post_conflict(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_entity_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')

    cursor = pgsql['persey_labs'].cursor()
    query = """
        SELECT id
        FROM persey_labs.labs;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]
    assert l_e_id == 'my_lab_id'

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 409


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_post_not_found(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_post_invalid(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_entity_lab(pgsql)

    request = load_json('request_post_simple.json')
    request['id'] = (
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        'aaaaaaaaaaaa > 120 aaaaaa'
    )
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_person']['contact_detailed']['phone'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    request = load_json('request_post_simple.json')
    request['contact_person']['contact_detailed']['email'] = 'invalid'
    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        request,
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('url_prefix', [ADMIN_URL_PREFIX, DISP_URL_PREFIX])
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_put_simple(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    add_entity_lab(pgsql)

    response = await taxi_persey_labs.post(
        f'{url_prefix}/lab',
        load_json('request_post_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_simple.json')

    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab?id=my_lab_id',
        load_json('request_put_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_put_response_simple.json')

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab?id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_put_response_simple.json')


@pytest.mark.parametrize(
    'labs_header, exp_resp_code', [('my_lab_id', 200), ('nonexistent', 403)],
)
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_disp_lab_put_forbidden(
        taxi_persey_labs, pgsql, load_json, labs_header, exp_resp_code,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.put(
        'disp/v1/lab?id=my_lab_id',
        load_json('request_put_simple.json'),
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
@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.servicetest
async def test_admin_lab_put_not_found(
        taxi_persey_labs, pgsql, load_json, mockserver, url_prefix,
):
    response = await taxi_persey_labs.put(
        f'{url_prefix}/lab?id=my_lab_id',
        load_json('request_put_simple.json'),
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('url_prefix', [DISP_URL_PREFIX])
@pytest.mark.servicetest
async def test_admin_lab_delete_simple(
        taxi_persey_labs, pgsql, load_json, url_prefix,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab?id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.delete(
        f'{url_prefix}/lab?id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.get(
        f'{url_prefix}/lab?id=my_lab_id',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404

    cursor = pgsql['persey_labs'].cursor()
    query = f"""
                SELECT s.id FROM persey_labs.lab_employee_shifts AS s
                INNER JOIN persey_labs.lab_employees AS e
                    ON e.id = s.lab_employee_id
                WHERE e.lab_id = 'my_lab_id';
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    assert not rows

    query = f"""
                SELECT id FROM persey_labs.lab_employees
                WHERE lab_id = 'my_lab_id';
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    assert not rows


@pytest.mark.parametrize(
    'labs_header, exp_resp_code', [('my_lab_id', 200), ('nonexistent', 403)],
)
@pytest.mark.servicetest
async def test_disp_lab_delete_forbidden(
        taxi_persey_labs, pgsql, labs_header, exp_resp_code,
):
    add_lab(pgsql)

    response = await taxi_persey_labs.delete(
        'disp/v1/lab?id=my_lab_id',
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
