# pylint: disable=W0102
async def add_tags(
        taxi_effrat_employees,
        tags=['test_taxi_tag0', 'test_taxi_tag1'],
        domain='taxi',
):
    for tag in tags:
        response = await taxi_effrat_employees.put(
            f'/admin/v1/tags?name={tag}',
            headers={'X-WFM-Domain': domain},
            json={'description': 'taxi tag'},
        )
        assert response.status_code == 200


async def check_employees_tags(taxi_effrat_employees, should_be):
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200
    response = list(
        sorted(response.json()['employees'], key=lambda x: x['login']),
    )
    assert len(response) >= len(should_be)
    for response_operator, should_be_tags in zip(response, should_be):
        assert response_operator['tags'] == should_be_tags


async def get_employee_tags(taxi_effrat_employees):
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200
    return sorted(
        [
            {
                'login': emp['login'],
                'domain': emp['source'],
                'tags': sorted(emp['tags']),
            }
            for emp in response.json()['employees']
        ],
        key=lambda x: (x['login'], x['domain'], x['tags']),
    )


async def update_employee_tags(
        taxi_effrat_employees,
        mode,
        tags=['test_taxi_tag0', 'test_taxi_tag1'],
        entities=['login0', 'login1'],
        domain='taxi',
):
    response = await taxi_effrat_employees.post(
        '/admin/v1/employee/tags/update-bulk',
        headers={'X-WFM-Domain': domain},
        json={
            'tags': [{'name': name} for name in tags],
            'entities': [{'value': value} for value in entities],
            'mode': mode,
        },
    )
    return response
