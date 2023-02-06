# encoding=utf-8
import pytest


# There are unreal path in mocks - only for convenience.
# /internal prefix is needed for validation of using internal s3 client
@pytest.fixture(name='mock_s3', autouse=True)
def _mock_s3(mockserver):
    def _make_response(request, is_200: bool):
        if request.method == 'HEAD':
            if is_200:
                return mockserver.make_response('OK', 200)
            return mockserver.make_response('Not Found', 404)

        return mockserver.make_response('Internal Server Error', 500)

    # videos
    @mockserver.handler('/internal/v1/video/v1', prefix=True)
    def _mock_v1(request):
        return _make_response(request=request, is_200=True)

    @mockserver.handler('/internal/v1/video/nonexisting_v1', prefix=True)
    def _mock_nonexisting_v1(request):
        return _make_response(request=request, is_200=False)

    # external videos
    @mockserver.handler('/internal/v1/external_video/v1', prefix=True)
    def _mock_external_v1(request):
        return _make_response(request=request, is_200=True)

    @mockserver.handler(
        '/internal/v1/external_video/nonexisting_v1', prefix=True,
    )
    def _mock_external_nonexisting_v1(request):
        return _make_response(request=request, is_200=False)

    # photos
    @mockserver.handler('/internal/v1/photo/p1', prefix=True)
    def _mock_p1(request):
        return _make_response(request=request, is_200=True)

    @mockserver.handler('/internal/v1/photo/nonexisting_p1', prefix=True)
    def _mock_nonexisting_p1(request):
        return _make_response(request=request, is_200=False)

    # external photos
    @mockserver.handler('/internal/v1/external_photo/p1', prefix=True)
    def _mock_external_p1(request):
        return _make_response(request=request, is_200=True)

    @mockserver.handler(
        '/internal/v1/external_photo/nonexisting_p1', prefix=True,
    )
    def _mock_external_nonexisting_p1(request):
        return _make_response(request=request, is_200=False)
