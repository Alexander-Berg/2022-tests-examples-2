from .utils import assert_util


class PostJsonAssertUtil(assert_util.PostJsonAssertUtil):
    def __init__(self, client):
        super().__init__(client, 'autogen/x-taxi-cpp-type-with-oneof')


async def test_success(taxi_userver_sample, mockserver):
    @mockserver.json_handler(
        '/userver-sample/autogen/x-taxi-cpp-type-with-oneof',
    )
    def _handler(request):
        return mockserver.make_response(json=request.json)

    helper = PostJsonAssertUtil(taxi_userver_sample)
    await helper.assert_equal(47)
