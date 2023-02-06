import aiohttp
import pytest

from . import common


class HappyPathForm:
    name = 'Quentin'
    age = 56
    response = len(name) + age

    @classmethod
    def as_multipart_form(cls) -> aiohttp.FormData:
        form_data = aiohttp.FormData()
        form_data.add_field(
            name='name',
            value=cls.name,
            content_type='text/plain; charset=utf-8',
        )
        form_data.add_field(
            name='age',
            value=str(cls.age),
            content_type='text/plain; charset=utf-8',
        )
        return form_data

    @classmethod
    def as_dict(cls) -> dict:
        return {'name': cls.name, 'age': cls.age}


@pytest.mark.parametrize(
    'url', ['/forms/happy-multipart', '/forms/openapi/happy-multipart'],
)
async def test_multipart_happy_path(web_app_client, url):
    response = await web_app_client.post(
        url, data=HappyPathForm.as_multipart_form(),
    )
    assert response.status == 200
    assert int(await response.text()) == HappyPathForm.response


@pytest.mark.parametrize(
    'url', ['/forms/happy-urlencoded', '/forms/openapi/happy-urlencoded'],
)
async def test_urlencoded_happy_path(web_app_client, url):
    response = await web_app_client.post(url, data=HappyPathForm.as_dict())
    assert response.status == 200
    assert int(await response.text()) == HappyPathForm.response


@pytest.mark.parametrize(
    'url', ['/forms/happy-urlencoded', '/forms/openapi/happy-urlencoded'],
)
async def test_urlencoded_wrong_content_type(web_app_client, url):
    response = await web_app_client.post(
        url, data=HappyPathForm.as_multipart_form(),
    )
    assert response.status == 400
    assert await response.json() == common.make_request_error(
        'Invalid Content-Type: multipart/form-data; expected one of '
        '[\'application/x-www-form-urlencoded\']',
    )


@pytest.mark.parametrize(
    'url', ['/forms/happy-multipart', '/forms/openapi/happy-multipart'],
)
async def test_multipart_wrong_content_type(web_app_client, url):
    response = await web_app_client.post(url, data=HappyPathForm.as_dict())
    assert response.status == 400
    assert await response.json() == common.make_request_error(
        'Invalid Content-Type: application/x-www-form-urlencoded; '
        'expected one of [\'multipart/form-data\']',
    )


@pytest.mark.parametrize(
    'url', ['/forms/save-file-report', '/forms/openapi/save-file-report'],
)
async def test_post_file(web_app_client, url):
    filename = 'report.csv'
    file_content = b'aba\xFFaba'
    form = aiohttp.FormData()
    form.add_field(name='report', value=file_content, filename=filename)
    response = await web_app_client.post('/forms/save-file-report', data=form)

    assert response.status == 200
    assert await response.json() == {
        'filename': filename,
        'size': len(file_content),
    }


async def test_binary_multipart(web_app_client):
    form = aiohttp.FormData()
    form.add_field(
        name='binary_data',
        value=b'ab\xFF',
        content_type='application/octet-stream',
    )
    response = await web_app_client.post('/forms/binary-multipart', data=form)
    assert response.status == 200
    assert await response.read() == b'ab\xFFab\xFF'


@pytest.mark.parametrize(
    'url,content_type',
    [
        ('/forms/openapi/raw-urlencoded', 'application/x-www-form-urlencoded'),
        ('/forms/openapi/raw-form-data', 'multipart/form-data'),
    ],
)
async def test_raw_strings(web_app_client, url, content_type):
    response = await web_app_client.post(
        url, data='abacaba', headers={'Content-Type': content_type},
    )

    assert response.status == 200
    assert await response.json() == {'size': 7}
