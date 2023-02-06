# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_pics_plugins import *  # noqa: F403 F401
import pytest

from tests_grocery_pics import models


@pytest.fixture(name='avatar_mds')
def mock_avatars(mockserver):
    mocks = {}
    namespace = 'grocery-goods'

    class Context:
        def mock_image(self, *, image: models.Image):
            @mockserver.json_handler(
                f'/{image.group_id}/{image.name}/{image.width}x{image.height}'
                f'.jpg',
            )
            def _mock_image(request):
                return mockserver.make_response(
                    status=200,
                    headers={'Content-Length': str(image.base64_size_bytes)},
                )

            mocks[image.name + 'size'] = _mock_image

            @mockserver.json_handler(
                f'/avatars-mds-get/get-{namespace}/{image.group_id}/'
                f'{image.name}/{image.width}x{image.height}',
            )
            def _mock_base64(request):
                return mockserver.make_response(image.raw_base64, 200)

            mocks[image.name + 'base64'] = _mock_base64

        def times_called(self, *, handler, image):
            return mocks[image.name + handler].times_called

        def flush(self, *, image):
            mocks[image.name + 'size'].flush()
            mocks[image.name + 'base64'].flush()

    context = Context()
    return context
