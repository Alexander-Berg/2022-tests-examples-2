# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import typing

import pytest

from taxi.clients import driver_photos
from taxi.clients.helpers import errors as client_errors

import taxi_order_performer_service.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi_order_performer_service.generated.service.pytest_plugins',
]


@pytest.fixture
def patch_driver_photos(patch):
    def helper(photos: typing.List[driver_photos.Photo] = None):
        # pylint: disable=unused-variable
        @patch('taxi.clients.driver_photos.Client.get_driver_photos')
        async def get_photos(*args, **kwargs):
            return photos if photos else []

    return helper


@pytest.fixture
def patch_driver_photos_raise(patch):
    def helper(
            exception_type: typing.Type[
                client_errors.BaseError
            ] = client_errors.BaseError,
    ):
        # pylint: disable=unused-variable
        @patch('taxi.clients.driver_photos.Client.get_driver_photos')
        async def get_photos(*args, **kwargs):
            raise exception_type()

    return helper
