# pylint: disable=redefined-outer-name
import io
import typing
import uuid

import PIL.Image as PilImage
import pytest

import taxi_admin_images.const as const
import taxi_admin_images.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
import test_taxi_admin_images.helpers as helpers

pytest_plugins = ['taxi_admin_images.generated.service.pytest_plugins']


@pytest.fixture
def mock_mds(patch, load_binary):
    client_prefix = 'client_mds.components.MDSClient'

    @patch(f'{client_prefix}.upload')
    async def upload(file_obj, ttl=None):  # pylint: disable=W0612
        return uuid.uuid4().hex

    @patch(f'{client_prefix}.remove')
    async def remove(file_obj, ttl=None):  # pylint: disable=W0612
        pass

    @patch(f'{client_prefix}.download')
    async def download(file_key):  # pylint: disable=W0612
        return load_binary('test.png')

    @patch(f'{client_prefix}.exists')
    async def exists(file_key):  # pylint: disable=W0612
        return True


@pytest.fixture
def get_image(load_binary):
    def _get_image(
            img_params: typing.Union[helpers.RealImage, io.BytesIO],
    ) -> io.BytesIO:
        if isinstance(img_params, io.BytesIO):
            return img_params

        if img_params.format == const.PNG_FORMAT:
            img = PilImage.open(io.BytesIO(load_binary('test.png')))
        elif img_params.format == const.JPEG_FORMAT:
            img = PilImage.open(io.BytesIO(load_binary('test.jpeg')))
        else:
            raise RuntimeError('Unknown img format')
        if img_params.size:
            img = img.resize(img_params.size)

        in_memory_file = io.BytesIO()
        img.save(in_memory_file, format=img_params.format)
        return in_memory_file

    return _get_image
