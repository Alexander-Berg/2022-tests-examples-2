import pytest

from dmp_suite.domain import ValidationError
from dmp_suite.staff.users import User
from .common import TestDomain, common_params


def test_domain_validate_without_error():
    domain = TestDomain(
        same_field='1',
        **common_params
    )
    assert domain.responsibles == [User('VP')]

    # проверим, что при передаче одно пользователя  в параметре, data_owners - возвращает список
    assert domain.data_owners == [User('VP1'), User('VP2')]


def test_domain_validate_error():
    with pytest.raises(ValidationError):
        TestDomain(
            same_field='1 1',
            **common_params
        )
