import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from contractor_orders_polling_plugins.generated_tests import *

from tests_contractor_orders_polling import utils


async def test_sdc(taxi_contractor_orders_polling):
    sdc_headers = {**utils.HEADERS}
    sdc_headers.pop('Accept-Language')
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=sdc_headers,
    )
    assert response.status_code == 200
