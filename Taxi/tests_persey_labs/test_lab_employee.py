import copy

import pytest

RESPONSE_EMPL = {
    'id': 1,
    'lab_id': 'labka_bez_ruki',
    'yandex_login': 'employee',
    'taxi_corp_id': '123456',
    'is_active': True,
    'contact_detailed': {
        'phone': '+79998887766',
        'email': 'employee@yandex.ru',
    },
    'address': {
        'position': [21.0, 21.0],
        'text': 'Vykhino',
        'locality_id': 2,
        'locality_name': 'Санкт-Петербург',
        'title': 'rayon',
        'subtitle': 'where',
        'comment': 'Do not enter',
    },
    'person_info': {
        'firstname': 'Кек',
        'middlename': 'Кекович',
        'surname': 'Кеков',
    },
}


@pytest.mark.parametrize(
    'login, exp_code, exp_response',
    [
        ('employee', 200, {'phone': '+79998887766'}),
        ('no_phone', 200, {}),
        ('not_exists', 404, None),
    ],
)
async def test_lab_employee_phone_simple(
        taxi_persey_labs, load_json, fill_labs, login, exp_code, exp_response,
):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('labka_bez_ruki', load_json('employees.json'))

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab-employee/phone?login={login}',
    )
    assert response.status_code == exp_code
    if exp_response is not None:
        assert response.json() == exp_response


async def test_lab_employee_address_simple(
        taxi_persey_labs, load_json, fill_labs, pgsql,
):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('labka_bez_ruki', load_json('employees.json'))

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab-employee/address?login=employee',
    )
    assert response.status_code == 200
    assert response.json() == {
        'address': {
            'position': [21.0, 21.0],
            'text': 'Vykhino',
            'locality_id': 2,
            'title': 'rayon',
            'subtitle': 'where',
            'comment': 'Do not enter',
        },
    }

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab-employee/address?login=not_exist',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'lab_employee_not_found',
        'message': 'Lab employee not found in db',
    }


async def test_lab_employee_by_login(taxi_persey_labs, load_json, fill_labs):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('labka_bez_ruki', load_json('employees.json'))

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab-employee?login=employee',
    )
    assert response.status_code == 200
    assert response.json() == RESPONSE_EMPL


async def test_lab_employee_by_shift_id(
        taxi_persey_labs, load_json, fill_labs,
):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('labka_bez_ruki', load_json('employees.json'))

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab-employee?shift_id=1',
    )
    assert response.status_code == 200
    assert response.json() == RESPONSE_EMPL


@pytest.mark.parametrize(
    'login, code, exp_response',
    [
        (
            'employee',
            200,
            {
                'shifts': [
                    {
                        'id': 2,
                        'start_time': '2020-04-17T05:00:00+0000',
                        'finish_time': '2020-04-17T09:00:00+0000',
                    },
                ],
            },
        ),
        ('no_phone', 200, {'shifts': []}),
        ('not_exists', 404, None),
    ],
)
async def test_lab_employee_shifts(
        taxi_persey_labs, load_json, fill_labs, login, code, exp_response,
):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('labka_bez_ruki', load_json('employees.json'))

    params = {'date': '2020-04-17', 'login': login}
    response = await taxi_persey_labs.get(
        '/internal/v1/lab-employee/shifts', params=params,
    )

    assert response.status_code == code
    if code == 200:
        assert response.json() == exp_response
