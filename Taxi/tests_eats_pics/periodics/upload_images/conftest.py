import pytest

# this path *is* whitelisted in config.json
MOCK_IMAGES_PATH = '/images/'


@pytest.fixture(name='mock_ext_image')
def _mock_ext_image(mockserver, request):
    path_prefix = MOCK_IMAGES_PATH

    class _info:
        @staticmethod
        def get_prefix():
            return path_prefix

        @staticmethod
        def generate_image_binary(url):
            idx = url.find(path_prefix)
            if idx != -1:
                url = url[idx + len(path_prefix)]
            url = url.strip('/\\')
            return bytearray(b'I\'m an image! My url is %a' % url)

    @mockserver.handler(path_prefix, prefix=True)
    def _mock_images(request):
        url_suffix = request.path[len(path_prefix) :].strip('/\\')

        if request.method in ['HEAD', 'GET']:
            return mockserver.make_response(
                _info.generate_image_binary(url_suffix),
                200,
                content_type='image/jpeg',
            )
        return mockserver.make_response('Not found or invalid method', 404)

    return _info
