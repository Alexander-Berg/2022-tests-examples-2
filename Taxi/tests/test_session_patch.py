import aiohttp

TEST_URL = 'http://test.url'


async def test_request(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(TEST_URL, 'GET')
    def patch_request(*args, **kwargs):
        return response_mock(text='REQUEST PATCHED')

    response = await aiohttp.ClientSession().request('GET', TEST_URL)
    assert (await response.text()) == (await patch_request().text())


async def test_get(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(TEST_URL, 'GET')
    def patch_request(*args, **kwargs):
        return response_mock(text='GET PATCHED')

    response = await aiohttp.ClientSession().get(TEST_URL)
    assert (await response.text()) == (await patch_request().text())


async def test_with(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(TEST_URL, 'GET')
    def patch_request(*args, **kwargs):
        return response_mock(text='WITH PATCHED')

    async with aiohttp.ClientSession().get(TEST_URL) as response:
        assert (await response.text()) == (await patch_request().text())


async def test_same_prefix(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://test.url/_post', 'POST')
    def patch_post_request(*args, **kwargs):
        return response_mock(text='POST PATCHED')

    @patch_aiohttp_session('http://test.url', 'GET')
    def patch_get_request(*args, **kwargs):
        return response_mock(text='GET PATCHED')

    response = await aiohttp.ClientSession().get('http://test.url')
    assert (await response.text()) == (await patch_get_request().text())

    response = await aiohttp.ClientSession().post('http://test.url/_post')
    assert (await response.text()) == (await patch_post_request().text())
