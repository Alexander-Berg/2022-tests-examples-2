from .utils import assert_util


class GetSwaggerAssertUtil(assert_util.GetJsonAssertUtil):
    def __init__(self, client):
        super().__init__(client, 'autogen/allof-inline/swagger-2-0')


class GetOpenapiAssertUtil(assert_util.GetJsonAssertUtil):
    def __init__(self, client):
        super().__init__(client, 'autogen/allof-inline/openapi-3-0')


async def test_get_swagger_2_0(taxi_userver_sample):
    helper = GetSwaggerAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'x': 53, 'z': 'some string'})


async def test_get_openapi_3_0(taxi_userver_sample):
    helper = GetOpenapiAssertUtil(taxi_userver_sample)
    await helper.assert_equal({'x': 42, 'w': 'my string'})
