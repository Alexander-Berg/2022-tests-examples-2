from dataclasses import dataclass

from dmp_suite.domain import DomainBase, DomainType, domain_field
from dmp_suite.staff.users import User

common_params = {
    'doc': '1'*25,
    'responsible': User('VP'),
    'data_owner': [User('VP1'), User('VP2')],
    'code': 'test_domain_code',
    'prefix_key': 'grp',
}


@dataclass(frozen=True, eq=False)
class TestDomain(DomainBase):
    type = DomainType(
        code='test',
        description='for tests'
    )
    same_field: str = domain_field(
        title='поле',
        help='текстовое поле без пробелов',
        validators=[lambda v: 'Есть пробелы!' if ' ' in v else None],
        default=None,
    )


test_domain = TestDomain(
    same_field='1234',
    **common_params
)

