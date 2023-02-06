from .utils import assert_util


class AssertUtil(assert_util.AssertUtil):
    def __init__(self, client):
        super().__init__(client, 'autogen/header-accept/openapi-3-0')

    async def _do_request(self, data):
        response = await self.client.get(self.url, headers=data)
        return response.status_code, response.text


async def test_default(taxi_userver_sample):
    helper = AssertUtil(taxi_userver_sample)
    await helper.assert_equal({}, 'my text')


async def test_text_plain(taxi_userver_sample):
    helper = AssertUtil(taxi_userver_sample)
    await helper.assert_equal({'Accept': 'text/plain'}, 'my text')


async def test_text_html(taxi_userver_sample):
    helper = AssertUtil(taxi_userver_sample)
    await helper.assert_equal({'Accept': 'text/html'}, '<html>my html</html>')


async def test_invalid(taxi_userver_sample):
    helper = AssertUtil(taxi_userver_sample)
    await helper.assert_equal({'Accept': 'Foo/Boo'}, 'my text')
