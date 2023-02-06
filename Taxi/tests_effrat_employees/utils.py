from typing import List

from tests_effrat_employees import employee


def extended_index_response(base, generated_uuids):
    for employee_item in base['employees']:
        uuid = generated_uuids.get_uuid_by_identifier(
            employee_item['login'], employee_item['source'],
        )
        if uuid is not None:
            employee_item['employee_uid'] = uuid
    return base


def extended_employee_models(employees, generated_uuids):
    for employee_item in employees:
        uuid = generated_uuids.get_uuid_by_identifier(
            employee_item.login, employee_item.domain,
        )
        if uuid is not None:
            employee_item.employee_uid = uuid
    return employees


def verify_response(
        response, employees: List[employee.EmployeeModel], generated_uuids,
) -> str:
    assert response.status_code == 200
    response = response.json()
    cursor = response['cursor']
    assert len(response['employees']) == len(
        employees,
    ), f'Unexpected response {response}\nand\nExpected {employees}'

    response = extended_index_response(response, generated_uuids)
    employees = extended_employee_models(employees, generated_uuids)

    for (response_employee, should_be_employee) in zip(
            response['employees'], employees,
    ):
        response_employee = employee.employee_from_ee_response(
            response_employee,
        )
        employee.compare_employees(response_employee, should_be_employee)
    return cursor
