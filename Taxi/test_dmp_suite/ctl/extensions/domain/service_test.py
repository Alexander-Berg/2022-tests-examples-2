import pytest

from dmp_suite.ctl.core import StorageEntity
from dmp_suite.ctl.exceptions import CtlError
from dmp_suite.ctl.extensions.domain.service import (
    SERVICE_DOMAIN,
    to_storage_entity
)


def test_to_storage_entity():
    expected = StorageEntity(SERVICE_DOMAIN, 'my_entity_name')

    entity = to_storage_entity('my_entity_name')
    entity2 = to_storage_entity(entity)

    assert entity == expected
    assert entity2 == expected

    with pytest.raises(CtlError):
        to_storage_entity('')
