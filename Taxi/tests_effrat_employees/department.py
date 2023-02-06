import dataclasses
import datetime
from typing import Dict
from typing import List
from typing import Optional


DEFAULT_DOMAIN = 'taxi'


@dataclasses.dataclass
class Department:
    external_id: str
    name: str


@dataclasses.dataclass
class StaffDepartment:
    department: Department
    domain: str
    employee_values_modified_at: Optional[datetime.datetime] = None

    def to_config_value(self):
        return {'url': self.department.external_id, 'domain': self.domain}


def _department_to_staff_without_ancestors(
        department: Department, level: Optional[int],
) -> Dict:
    res: Dict = {
        'department': {
            'name': {'full': {'ru': department.name}},
            'url': department.external_id,
        },
    }
    if level is not None:
        res['department']['level'] = level
    return res


def department_to_staff_response(
        department: Department, ancestors: List[Department],
) -> Dict:
    main_dep = _department_to_staff_without_ancestors(department, None)
    main_dep['ancestors'] = [
        _department_to_staff_without_ancestors(ancestor, index)
        for (index, ancestor) in enumerate(ancestors)
    ]
    return main_dep


def generate_department(index: int, name: str = 'division') -> Department:
    return Department(f'url_{name}_{index}', f'{name} {index}')


def generate_departments(index: int) -> List[Department]:
    return [
        generate_department(index, 'subdivision'),
        generate_department(index, 'division'),
    ]


def generate_staff_departments(
        index: int, domain: Optional[str] = None,
) -> StaffDepartment:
    return StaffDepartment(
        generate_department(index, 'division'), domain or DEFAULT_DOMAIN,
    )


def set_staff_departments_config(
        taxi_config, departments: List[StaffDepartment],
):
    taxi_config.set_values(
        dict(
            EFFRAT_EMPLOYEES_STAFF_DEPARTMENTS={
                'departments': [x.to_config_value() for x in departments],
            },
        ),
    )


def gen_staff_departments_config(
        taxi_config, number: int, domain: Optional[str] = None,
):
    departments = [
        generate_staff_departments(i, domain or DEFAULT_DOMAIN)
        for i in range(number)
    ]
    set_staff_departments_config(taxi_config, departments)
