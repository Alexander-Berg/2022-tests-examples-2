import copy

import pytest

URL = '/internal/v1/labs'


@pytest.mark.config(PERSEY_LABS_USE_MANY_TESTS=True)
@pytest.mark.parametrize(
    ['locality_id', 'date', 'lab_id', 'lab_idxes', 'shift_ids'],
    [
        (2, '2020-04-16', None, [], []),  # no bucket_owners -> no labs
        (213, '2020-04-17', None, [0, 1], [2, 5]),
        (2, '2020-04-17', None, [2, 3], [8, 11]),
        (None, '2020-04-17', 'my_lab_id_1', [1], [5]),
    ],
)
async def test_get_labs_db(
        taxi_persey_labs,
        load_json,
        fill_labs,
        locality_id,
        date,
        lab_id,
        lab_idxes,
        shift_ids,
):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    lab_ids = [f'my_lab_id_{i}' for i in range(3)] + ['labka_bez_ruki']
    fill_labs.load_employees(lab_ids, load_json('employees.json'))

    expected = load_json('full_response.json')
    filtered = []
    for i, lab in enumerate(expected):
        if i in lab_idxes:
            filtered.append(lab)
    expected = filtered
    for lab in expected:
        employees_filtered = []
        for employee in lab['bucket_owners']:
            shifts_filtered = [
                shift
                for shift in employee['shifts']
                if shift['id'] in shift_ids
            ]
            shifts_filtered.sort(key=lambda x: x['id'])
            employee['shifts'] = shifts_filtered
            if shifts_filtered:
                employees_filtered.append(employee)
        employees_filtered.sort(key=lambda x: x['login'])
        lab['bucket_owners'] = employees_filtered
    expected = {lab['id']: lab for lab in expected}

    params = {'date': date}
    if locality_id is not None:
        params['locality_id'] = locality_id
    if lab_id is not None:
        params['lab_id'] = lab_id
    response = await taxi_persey_labs.get(URL, params=params)
    assert response.status_code == 200
    labs = response.json()['labs']
    labs = {lab['id']: lab for lab in labs}

    for lab in labs.values():
        lab['bucket_owners'].sort(key=lambda x: x['login'])
        for employee in lab['bucket_owners']:
            employee['shifts'].sort(key=lambda x: x['id'])
        employee_tests_threshold = lab_entities[lab['entity_id']].get(
            'employee_tests_threshold',
        )
        if employee_tests_threshold is not None:
            for test in expected[lab['id']]['tests']:
                test['tests_per_day'] = min(
                    test['tests_per_day'],
                    employee_tests_threshold * len(lab['bucket_owners']),
                )

    assert labs == expected


@pytest.mark.config(PERSEY_LABS_USE_MANY_TESTS=True)
@pytest.mark.config(
    PERSEY_LABS_TESTS_PER_HOUR={
        'enabled': True,
        'lab_tph': {'__default__': 3.4},
    },
)
async def test_get_labs_db_tph(taxi_persey_labs, load_json, fill_labs):
    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    lab_ids = [f'my_lab_id_{i}' for i in range(3)] + ['labka_bez_ruki']
    fill_labs.load_employees(lab_ids, load_json('employees.json'))

    params = {}
    params['locality_id'] = 2
    params['date'] = '2020-04-17'
    response = await taxi_persey_labs.get(URL, params=params)
    assert response.status_code == 200
    assert response.json() == load_json('response_tph.json')
