import pytest


class MdsContext:
    def __init__(self):
        self.images = {}

    def add_image(self, image_key, image_bin):
        self.images[image_key] = image_bin


@pytest.fixture(autouse=True)
def mds(mockserver):
    mds_context = MdsContext()

    @mockserver.handler('/static/images/', True)
    def get_image(request):
        key = request.path.split('/')[-1]
        if key in mds_context.images:
            return mockserver.make_response(
                mds_context.images[key], content_type='image/png',
            )
        return mockserver.make_response('Not Found', status=404)
