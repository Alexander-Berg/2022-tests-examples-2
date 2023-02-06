import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from quality_control_cpp_plugins.generated_tests import *  # noqa


@pytest.mark.servicetest
async def test_ping(taxi_quality_control_cpp, remove_trash):
    response = await taxi_quality_control_cpp.get('ping')
    assert response.status_code == 200
