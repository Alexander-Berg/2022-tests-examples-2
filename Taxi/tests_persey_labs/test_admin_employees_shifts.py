from typing import Any
from typing import Dict

import pytest

from tests_persey_labs import utils


DISP_URL_PREFIX = 'disp/v1'
PERSEY_TAXI_MAESTRO_BASE: Dict[str, Any] = {
    'check_period': 60,
    'enabled': True,
    'search_period': 9 * 60 * 60,
    'available_manual_search_taxi_order_statuses': ['cancelled'],
}

COMMON_ACTION_HEADERS = {
    'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
    'X-Yandex-Login': 'some-staff-login',
}


def add_lab_employees_shifts(pgsql):
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
            billing_info_id, is_active)
        VALUES
            ('my_entity_lab_id', '123456', 'some contacts', 'comname',
            {l_e_contacts_id}, {l_e_billing_id}, TRUE)
        RETURNING id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    l_e_id = rows[0][0]

    query = f"""
        INSERT INTO persey_labs.lab_entity_tests
            (lab_entity_id, test_id)
        VALUES
            ('my_entity_lab_id', 'covid_fast'),
            ('my_entity_lab_id', 'covid_slow');
    """
    cursor.execute(query)

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

    employees_ids = []

    for i in range(3):
        query = f"""
                INSERT INTO persey_labs.lab_employees
                    (lab_id, yandex_login, is_active, contact_id,
                    person_info_id, address_id)
                VALUES
                    ('{lab_id}', 'login_{i}', TRUE, NULL, NULL, {address_id})
                RETURNING id;
            """
        cursor.execute(query)
        rows = cursor.fetchall()
        employee_id = rows[0][0]

        employees_ids.append(employee_id)

        for j in range(i + 1):
            query = f"""
                    INSERT INTO persey_labs.lab_employee_shifts
                        (lab_employee_id, start_time, finish_time)
                    VALUES
                        ('{employee_id}', '2013-01-01 0{j}:45:00 UTC',
                        '2013-01-01 0{j + 1}:45:00 UTC')
                    RETURNING id;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            shift_id = rows[0][0]

            query = f"""
                INSERT INTO persey_labs.shift_tests
                    (shift_id, test_id)
                VALUES
                    ('{shift_id}', 'covid_fast'),
                    ('{shift_id}', 'covid_slow');
            """
            cursor.execute(query)

    return employees_ids


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'show_manual_taxi_order_button',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                PERSEY_TAXI_MAESTRO={
                    'available_manual_search_states': ['planned', 'planned'],
                    **PERSEY_TAXI_MAESTRO_BASE,
                },
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                PERSEY_TAXI_MAESTRO={
                    'available_manual_search_states': ['incomplete'],
                    **PERSEY_TAXI_MAESTRO_BASE,
                },
            ),
        ),
        False,
    ],
)
async def test_admin_lab_employees_shifts_list_simple(
        taxi_persey_labs, pgsql, load_json, show_manual_taxi_order_button,
):
    employees_ids = add_lab_employees_shifts(pgsql)

    query_str = ','.join(str(id) for id in employees_ids)
    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200

    exp_json = load_json('exp_response_simple.json')
    for item in exp_json['shifts']:
        item['show_manual_taxi_order_button'] = show_manual_taxi_order_button
    assert response.json() == exp_json


@pytest.mark.servicetest
async def test_admin_lab_employees_shifts_list_paging(
        taxi_persey_labs, pgsql, load_json,
):
    employees_ids = add_lab_employees_shifts(pgsql)

    query_str = ','.join(str(id) for id in employees_ids)
    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}&'
        'from=2013-01-01T01:45:00Z&to=2013-01-01T02:45:00Z',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_paging.json')


@pytest.mark.servicetest
async def test_admin_lab_employees_shifts_list_bad_intervals(
        taxi_persey_labs, pgsql, load_json,
):
    employees_ids = add_lab_employees_shifts(pgsql)

    query_str = ','.join(str(id) for id in employees_ids)
    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}&'
        'to=2013-01-01T01:45:00Z',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}&'
        'from=2013-01-01T02:45:00Z&to=2013-01-01T01:45:00Z',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400

    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}&'
        'from=2013-01-01T02:45:00Z',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 400


@utils.permission_variants()
async def test_admin_lab_employees_shifts_list_permissions(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    employees_ids = add_lab_employees_shifts(pgsql)

    query_str = ','.join(str(id) for id in employees_ids)
    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift/list?'
        f'lab_employees_ids={query_str}',
        headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.servicetest
async def test_admin_lab_employees_shifts_get_simple(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('exp_response_get_simple.json')


@pytest.mark.servicetest
@utils.permission_variants()
async def test_admin_lab_employees_shifts_get_not_found(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1', headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_post_simple(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    body = {
        'finish_time': '2013-01-01T05:45:00Z',
        'lab_employee_id': 1,
        'start_time': '2013-01-01T04:45:00Z',
        'selected_tests': ['covid_fast'],
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        body,
        headers=COMMON_ACTION_HEADERS,
    )

    cursor = pgsql['persey_labs'].cursor()

    query = (
        """
        SELECT * FROM persey_labs.lab_employee_shift_history
        WHERE lab_employee_id = {id} AND action = 'insert';
    """.format(
            id=body['lab_employee_id'],
        )
    )
    cursor.execute(query)
    history_rows = cursor.fetchall()
    history_item = history_rows[0]

    assert response.status_code == 200
    assert response.json() == {**body, 'id': 7}

    assert len(history_rows) == 1
    assert history_item[3] == 'insert'
    assert history_item[4] == COMMON_ACTION_HEADERS['X-Yandex-Login']


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_post_bad_request(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T04:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T05:45:00Z',
        },
        headers={
            'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id',
        },  # Также ошибка X-Yandex-Login
    )
    assert response.status_code == 400


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_post_intersect(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T06:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T01:45:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409


@pytest.mark.servicetest
@pytest.mark.now('1980-01-01T00:13:37Z')
@utils.permission_variants()
async def test_admin_lab_employee_shift_post_not_found(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees_shifts(pgsql)

    headers['X-Yandex-Login'] = 'some-staff-login'

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
        },
        headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T04:45:37Z')
async def test_admin_lab_employee_shift_post_forbidden(
        taxi_persey_labs, load_json, pgsql,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',  # starts earlier
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'shift_addition_forbidden',
        'message': 'Shift addition forbidden by settings',
    }


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_put_simple(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
            'selected_tests': ['covid_fast'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'finish_time': '2013-01-01T05:45:00Z',
        'lab_employee_id': 1,
        'id': 7,
        'start_time': '2013-01-01T04:45:00Z',
        'selected_tests': ['covid_fast'],
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }

    update_body = {
        'lab_employee_id': 1,
        'finish_time': '2015-01-01T21:45:00Z',
        'start_time': '2015-01-01T09:45:00Z',
        'selected_tests': ['covid_slow'],
    }

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        update_body,
        headers=COMMON_ACTION_HEADERS,
    )

    cursor = pgsql['persey_labs'].cursor()

    query = """
        SELECT * FROM persey_labs.lab_employee_shift_history
        WHERE action = 'update';
    """
    cursor.execute(query)
    history_rows = cursor.fetchall()
    history_item = history_rows[0]

    assert len(history_rows) == 1
    assert history_item[3] == 'update'
    assert history_item[4] == COMMON_ACTION_HEADERS['X-Yandex-Login']

    assert response.status_code == 200
    assert response.json() == {
        **update_body,
        'id': 7,
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_put_bad_request(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
            'selected_tests': ['covid_fast'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'finish_time': '2013-01-01T05:45:00Z',
        'lab_employee_id': 1,
        'id': 7,
        'start_time': '2013-01-01T04:45:00Z',
        'selected_tests': ['covid_fast'],
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        {
            'lab_employee_id': 1,
            'finish_time': '2015-01-01T09:45:00Z',
            'start_time': '2015-01-01T21:45:00Z',
            'selected_tests': ['covid_slow'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_put_intersect(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-02-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-02-01T04:45:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        {
            'lab_employee_id': 1,
            'finish_time': '2013-02-01T05:00:00Z',
            'start_time': '2013-02-01T04:35:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409


@pytest.mark.servicetest
@pytest.mark.now('1980-01-01T00:13:37Z')
@utils.permission_variants()
async def test_admin_lab_employee_shift_put_not_found(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees_shifts(pgsql)

    headers['X-Yandex-Login'] = 'some-staff-login'

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1',
        {
            'lab_employee_id': 1,
            'finish_time': '2015-01-01T21:45:00Z',
            'start_time': '2015-01-01T09:45:00Z',
        },
        headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_put_change_employee(
        taxi_persey_labs, pgsql, load_json, mockserver,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
            'selected_tests': ['covid_fast'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'finish_time': '2013-01-01T05:45:00Z',
        'lab_employee_id': 1,
        'id': 7,
        'start_time': '2013-01-01T04:45:00Z',
        'selected_tests': ['covid_fast'],
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        {
            'lab_employee_id': 2,
            'finish_time': '2013-01-01T05:45:00Z',
            'start_time': '2013-01-01T04:45:00Z',
            'selected_tests': ['covid_fast'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'finish_time': '2013-01-01T05:45:00Z',
        'id': 7,
        'lab_employee_id': 2,
        'start_time': '2013-01-01T04:45:00Z',
        'selected_tests': ['covid_fast'],
        'taxi_order_state': 'planned',
        'show_manual_taxi_order_button': False,
    }


@pytest.mark.servicetest
@pytest.mark.now('2014-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_update_forbidden(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.put(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1',
        {
            'lab_employee_id': 3,
            'finish_time': '2013-02-01T05:00:00Z',
            'start_time': '2013-02-01T04:35:00Z',
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'employee_swap_forbidden',
        'message': 'Shift already finished',
    }


@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213})
@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_delete_simple(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.post(
        f'{DISP_URL_PREFIX}/lab/employee/shift/',
        {
            'finish_time': '2013-01-01T05:45:00Z',
            'lab_employee_id': 1,
            'start_time': '2013-01-01T04:45:00Z',
            'selected_tests': ['covid_fast'],
        },
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_persey_labs.delete(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        headers=COMMON_ACTION_HEADERS,
    )

    assert response.status_code == 200

    cursor = pgsql['persey_labs'].cursor()

    query = """
        SELECT * FROM persey_labs.lab_employee_shift_history
        WHERE action = 'delete';
    """
    cursor.execute(query)
    history_rows = cursor.fetchall()
    history_item = history_rows[0]

    assert len(history_rows) == 1
    assert history_item[3] == 'delete'
    assert history_item[4] == COMMON_ACTION_HEADERS['X-Yandex-Login']

    response = await taxi_persey_labs.get(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=7',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_lab_id'},
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.now('1980-01-01T00:13:37Z')
@utils.permission_variants()
async def test_admin_lab_employee_shift_delete_not_found(
        taxi_persey_labs, pgsql, headers, exp_resp_code,
):
    add_lab_employees_shifts(pgsql)

    headers['X-Yandex-Login'] = 'some-staff-login'

    response = await taxi_persey_labs.delete(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1', headers=headers,
    )
    assert response.status_code == exp_resp_code


@pytest.mark.servicetest
@pytest.mark.now('2014-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_delete_forbidden_already_finished(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)

    response = await taxi_persey_labs.delete(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1',
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'shift_deleting_forbidden',
        'message': 'Shift already finished',
    }


@pytest.mark.servicetest
@pytest.mark.now('2013-01-01T00:13:37Z')
async def test_admin_lab_employee_shift_delete_forbidden_taxi_ordered(
        taxi_persey_labs, pgsql, load_json,
):
    add_lab_employees_shifts(pgsql)
    pgsql['persey_labs'].cursor().execute(
        """
        UPDATE persey_labs.lab_employee_shifts
        SET taxi_order_state = 'committed'
        WHERE id = 1;
    """,
    )

    response = await taxi_persey_labs.delete(
        f'{DISP_URL_PREFIX}/lab/employee/shift?id=1',
        headers=COMMON_ACTION_HEADERS,
    )
    assert response.status_code == 409


async def test_admin_shifts_dump(taxi_persey_labs, load_json, pgsql):
    add_lab_employees_shifts(pgsql)

    expected_lines = [
        [
            'city',
            'shift_id',
            'lab_id',
            'lab_name',
            'lab_entity_id',
            'employee_login',
            'employee_full_name',
            'shift_date',
            'start_time_local',
            'finish_time_local',
        ],
        [
            '213',
            '1',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_0',
            '',
            '2013-01-01',
            '04:45',
            '05:45',
        ],
        [
            '213',
            '2',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_1',
            '',
            '2013-01-01',
            '04:45',
            '05:45',
        ],
        [
            '213',
            '3',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_1',
            '',
            '2013-01-01',
            '05:45',
            '06:45',
        ],
        [
            '213',
            '4',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_2',
            '',
            '2013-01-01',
            '04:45',
            '05:45',
        ],
        [
            '213',
            '5',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_2',
            '',
            '2013-01-01',
            '05:45',
            '06:45',
        ],
        [
            '213',
            '6',
            'my_lab_id',
            'MY_LAB',
            'my_entity_lab_id',
            'login_2',
            '',
            '2013-01-01',
            '06:45',
            '07:45',
        ],
    ]
    expected_lines = ['\t'.join(line) for line in expected_lines]

    response = await taxi_persey_labs.get(
        'admin/v1/lab/employee/shift/dump',
        params={'date': '2013-01-01', 'locality_id': 213},
    )
    assert response.status_code == 200
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename="shifts_213_2013-01-01.csv"'
    )
    assert set(response.text.strip().split('\n')) == set(expected_lines)
