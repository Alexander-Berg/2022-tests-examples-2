import pytest

from tests_multiclass_pricing_storage import tvm_tickets

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from multiclass_pricing_storage_plugins.generated_tests import *  # noqa


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
@pytest.mark.servicetest
async def test_ping(taxi_multiclass_pricing_storage):
    response = await taxi_multiclass_pricing_storage.get(
        'ping', headers=tvm_tickets.TVM_HEADER,
    )
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
