import aiohttp
import pytest

from taxi.clients import captcha

DEFAULT_URL = 'http://api.captcha.yandex.net'


@pytest.fixture(name='test_captcha_client')
async def captcha_client(loop, db, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    yield captcha.CaptchaClient(session=session, api_url=DEFAULT_URL)
    await session.close()


async def test_generate(
        test_captcha_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(f'{DEFAULT_URL}/generate', 'GET')
    def _captcha_api(method, url, **kwargs):
        answer = b"""<?xml version='1.0'?>
        <number url="http://u.captcha.yandex.net/image?key=10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF">10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF</number>"""  # noqa
        assert method == 'get'
        assert 'api.captcha.yandex.net/generate' in url
        return response_mock(text=answer, status=200)

    response = await test_captcha_client.generate()
    assert response == {
        'key': '10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF',
        'url': (
            'http://u.captcha.yandex.net/image?'
            'key=10pIGk1YA_uMYERwCg9Zzltn_cQ3bBOF'
        ),
    }
    assert _captcha_api.calls


@pytest.mark.parametrize(
    'answer, exc',
    [
        (
            b"""<?xml version='1.0'?>
        <image_check>ok</image_check>""",
            None,
        ),
        (
            b"""<?xml version='1.0'?>
        <image_check error="not found">failed</image_check>""",
            captcha.NotFoundError,
        ),
        (
            b"""<?xml version='1.0'?>
        <image_check>failed</image_check>""",
            captcha.DoesntMatchError,
        ),
        (
            b"""<?xml version='1.0'?>
        <image_check error="inconsistent type">failed</image_check>""",
            captcha.WrongTypeError,
        ),
    ],
)
async def test_check(
        test_captcha_client, patch_aiohttp_session, response_mock, answer, exc,
):
    @patch_aiohttp_session(f'{DEFAULT_URL}/check', 'GET')
    def _captcha_api(method, url, **kwargs):
        assert method == 'get'
        assert 'api.captcha.yandex.net/check' in url
        return response_mock(text=answer, status=200)

    try:
        await test_captcha_client.check('key', 'answer')
    except exc:
        pass
    assert _captcha_api.calls


@pytest.mark.parametrize('response_code', [400, 500])
async def test_generate_errors(
        test_captcha_client,
        patch_aiohttp_session,
        response_mock,
        response_code,
):
    @patch_aiohttp_session('http://api.captcha.yandex.net/generate', 'GET')
    def _captcha_api(*args, **kwargs):
        return response_mock(status=response_code)

    if response_code == 500:
        with pytest.raises(captcha.InternalServerError):
            await test_captcha_client.generate()
    else:
        with pytest.raises(captcha.BadRequestError):
            await test_captcha_client.generate()


@pytest.mark.parametrize(
    'response_code, exception_type',
    [(400, captcha.BadRequestError), (500, captcha.InternalServerError)],
)
async def test_request_error(
        test_captcha_client,
        patch_aiohttp_session,
        response_mock,
        response_code,
        exception_type,
):
    @patch_aiohttp_session('http://api.captcha.yandex.net/check', 'GET')
    def _captcha_api(*args, **kwargs):
        return response_mock(status=response_code)

    with pytest.raises(exception_type):
        await test_captcha_client.check('key', 'answer')
