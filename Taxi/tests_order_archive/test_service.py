# flake8: noqa
# pylint: disable=import-error,wildcard-import
from order_archive_plugins.generated_tests import *
from .test_order_proc_retrieve import test_service


async def test_ping(taxi_order_archive):
    response = await taxi_order_archive.get('ping')
    assert response.status_code == 200
    assert response.content == b''
