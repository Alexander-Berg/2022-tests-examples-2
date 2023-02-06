# pylint: disable=W0622,C0103
import dataclasses
import datetime
from typing import Any
from typing import List
from typing import Optional

from tests_effrat_employees import department
from tests_effrat_employees import personal
from tests_effrat_employees import time_utils

_FIELDS_TO_INSERT = [
    'yandex_uid',
    'login',
    'domain',
    'full_name',
    'employment_status',
    'phone_pd_id',
    'telegram_login_pd_id',
    'email_pd_id',
    'timezone',
    'id',
    'supervisor_id',
    'mentor_id',
    'updated_at',
    'employment_datetime',
]


@dataclasses.dataclass
class Supervisor:
    login: str
    name: Optional[str]


@dataclasses.dataclass
class Mentor:
    login: str
    name: Optional[str]


@dataclasses.dataclass
class Tag:
    name: str
    color: Optional[str]
    description: Optional[str]


def supervisor_from_ee_response(response) -> Supervisor:
    return Supervisor(response['login'], response.get('full_name', None))


def mentor_from_ee_response(response) -> Mentor:
    return Mentor(response['login'], response.get('full_name', None))


@dataclasses.dataclass
class EmployeeModel:
    yandex_uid: str
    login: str
    domain: str
    full_name: str
    employment_status: str
    phone_pd_id: Optional[str]
    telegram_login_pd_id: Optional[str]
    email_pd_id: Optional[str]
    timezone: Optional[str]
    staff_login: str
    employment_datetime: datetime.datetime
    supervisor: Optional[Supervisor]
    mentor_login: Optional[str]
    departments: List[department.Department]
    positions: List[str]
    tags: List[str]
    employee_uid: Optional[str]

    @property
    def supervisor_login(self) -> Optional[str]:
        if self.supervisor is None:
            return None
        return self.supervisor.login

    def to_staff_response(self, modified_at: datetime.datetime):
        name_split = self.full_name.split(' ')
        if self.supervisor is None or self.supervisor.name is None:
            supervisor_name = None
        else:
            supervisor_name_split = self.supervisor.name.split(' ')
            supervisor_name = {
                'last': {'ru': supervisor_name_split[0]},
                'first': {'ru': ' '.join(supervisor_name_split[1:])},
            }
        return {
            'name': {
                'last': {'ru': name_split[0]},
                'first': {'ru': ' '.join(name_split[1:])},
            },
            'department_group': department.department_to_staff_response(
                self.departments[0], self.departments[1:],
            ),
            'phones': [
                {
                    'type': 'mobile',
                    'number': personal.decode_entity(self.phone_pd_id),
                    'is_main': True,
                },
            ],
            'official': {
                'position': {'ru': self.positions[0]},
                'is_dismissed': (self.employment_status == 'fired'),
            },
            'environment': {'timezone': self.timezone},
            'chief': {'login': self.supervisor_login, 'name': supervisor_name},
            'accounts': [
                {
                    'type': 'telegram',
                    'private': False,
                    'value': personal.decode_entity(self.telegram_login_pd_id),
                },
            ],
            'login': self.login,
            'uid': self.yandex_uid,
            '_meta': {'modified_at': modified_at.isoformat()},
            'created_at': self.employment_datetime.isoformat(),
        }

    def to_callcenter_response(
            self,
            created_at: datetime.datetime = time_utils.EPOCH,
            updated_at: datetime.datetime = time_utils.EPOCH,
            timezone: Optional[str] = 'Europe/Moscow',
    ):
        name_split = self.full_name.split(' ')
        timezone_dict = {}
        if timezone is not None:
            timezone_dict['timezone'] = timezone
        response = {
            'id': 5553535,
            'login': self.login,
            'yandex_uid': self.yandex_uid,
            'agent_id': '3222281488',
            'state': (
                'ready' if self.employment_status == 'in_staff' else 'deleted'
            ),
            'last_name': name_split[0],
            'first_name': name_split[1],
            'middle_name': name_split[2] if len(name_split) > 2 else None,
            'callcenter_id': self.departments[0].external_id,
            'roles': self.positions,
            'name_in_telephony': 'unused',
            'phone_number': personal.decode_entity(self.phone_pd_id),
            'supervisor_login': self.supervisor_login,
            'mentor_login': self.mentor_login,
            # callcenter employee might have different login and staff login
            'staff_login': f'staff_{self.login}',
            'created_at': created_at.isoformat(),
            'updated_at': updated_at.isoformat(),
            'employment_date': (self.employment_datetime.date().isoformat()),
            'telegram_login': personal.decode_entity(
                self.telegram_login_pd_id,
            ),
            'roles_info': [
                {'role': position, 'source': 'idm'}
                for position in self.positions
            ],
        }
        response.update(timezone_dict)
        return response


def _create_full_name(index: int) -> str:
    return f'surname{index} name{index} fathername{index} '


def create_supervisor(index: int, **kwargs) -> Optional[Supervisor]:
    if index == -1:
        return None
    res = Supervisor(f'login{index}', _create_full_name(index))
    for k, v in kwargs.items():
        if hasattr(res, k):
            setattr(res, k, v)
    return res


def create_mentor(index: int, **kwargs) -> Mentor:
    res = Mentor(f'login{index}', _create_full_name(index))
    for k, v in kwargs.items():
        if hasattr(res, k):
            setattr(res, k, v)
    return res


def create_employee(index: int, **kwargs) -> EmployeeModel:
    login = f'login{index}'
    res = EmployeeModel(
        supervisor=create_supervisor(index - 1),
        mentor_login=None,
        departments=department.generate_departments(index),
        positions=['software engineer'],
        yandex_uid=f'uid{index}',
        login=login,
        domain='taxi',
        full_name=_create_full_name(index),
        employment_status='in_staff',
        phone_pd_id=personal.encode_entity(f'phone{index}'),
        telegram_login_pd_id=personal.encode_entity(f'telegram{index}'),
        email_pd_id=personal.encode_entity(f'{login}@yandex-team.ru'),
        timezone='Europe/Moscow',
        staff_login=login,
        employment_datetime=datetime.datetime(
            year=1970 + index, month=1, day=1, tzinfo=datetime.timezone.utc,
        ),
        tags=[],
        employee_uid=None,
    )
    for k, v in kwargs.items():
        if hasattr(res, k):
            setattr(res, k, v)
    return res


_FIELDS_TO_FILL = [
    'yandex_uid',
    'login',
    'domain',
    'full_name',
    'employment_status',
    'phone_pd_id',
    'telegram_login_pd_id',
    'email_pd_id',
    'timezone',
    'supervisor',
    'departments',
    'positions',
    'tags',
    'employee_uid',
]


def employee_from_ee_response(response) -> EmployeeModel:
    def _value_to_field(name: str, response) -> Any:
        value = response.get(name, None)
        if name == 'departments':
            departments = []
            for dpt in value:
                _, dpt_name, dpt_index = dpt.split('_')
                departments.append(
                    department.Department(dpt, f'{dpt_name} {dpt_index}'),
                )
            return departments
        if name == 'supervisor':
            if 'supervisor_login' not in response:
                return None
            return Supervisor(response['supervisor_login'], None)
        if name == 'domain':
            return response['source']
        return value

    return create_employee(
        0, **{x: _value_to_field(x, response) for x in _FIELDS_TO_FILL},
    )


def compare_employees(lhs: EmployeeModel, rhs: EmployeeModel):
    def _cmp_fields(name: str):
        nonlocal lhs
        nonlocal rhs
        if name == 'supervisor':
            return lhs.supervisor_login == rhs.supervisor_login
        if name == 'departments':
            lhs_deps = lhs.departments
            rhs_deps = rhs.departments
            for rhs_dep, lhs_dep in zip(lhs_deps, rhs_deps):
                if lhs_dep.external_id != rhs_dep.external_id:
                    return False
                if lhs_dep.name != rhs_dep.name:
                    return False
            return True
        return getattr(lhs, name) == getattr(rhs, name)

    equal = [_cmp_fields(x) for x in _FIELDS_TO_FILL]
    assert all(equal)


@dataclasses.dataclass
class StaffEmployee:
    login: str
    domain: str

    def to_config_value(self):
        return {'login': self.login, 'domain': self.domain}


def generate_login(index: int) -> str:
    return f'login{index}'


def generate_staff_logins(index: int) -> StaffEmployee:
    return StaffEmployee(generate_login(index), 'taxi')


def set_staff_logins_config(taxi_config, logins: List[StaffEmployee]):
    taxi_config.set_values(
        dict(
            EFFRAT_EMPLOYEES_EMPLOYEES_LOGINS={
                'employees': [x.to_config_value() for x in logins],
            },
        ),
    )


def gen_staff_logins_config(taxi_config, number: int):
    logins = [generate_staff_logins(i) for i in range(number)]
    set_staff_logins_config(taxi_config, logins)
