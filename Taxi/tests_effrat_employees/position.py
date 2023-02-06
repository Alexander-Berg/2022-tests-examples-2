import dataclasses
from typing import List


def insert_positions_query(position_name: List[str]) -> str:
    return (
        'insert into effrat_employees.position (name) values (\''
        + '\'), (\''.join(position_name)
        + '\')'
    )


@dataclasses.dataclass
class EmployeePosition:
    employee_login: str
    position_name: str
