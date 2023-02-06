import io
import re

import pytest


RE_MULTIPART = re.compile(r'^multipart/form-data; boundary=(.*)$')


@pytest.mark.parametrize(
    'handler', ['/v2/images/upload', '/v1/grocery-pics/admin/upload'],
)
async def test_basic(taxi_grocery_pics, mockserver, handler):
    image_body = b'JPEG123, image body'

    @mockserver.json_handler('/avatars-mds/put-grocery-goods/', prefix=True)
    def avatar(request):
        content_type = request.headers['content-type']
        match = RE_MULTIPART.match(content_type)
        assert match is not None
        boundary = match.group(1)
        assert _build_multipart(image_body, boundary) == request.get_data()
        image_id = 'exampleid'
        group_id = 603
        return {
            'imagename': image_id,
            'group-id': group_id,
            'meta': {'orig-format': 'JPEG'},
            'sizes': {
                'orig': {
                    'height': 640,
                    'path': f'/get-grocery-pics/{group_id}/{image_id}/orig',
                    'width': 1024,
                },
                'sizename': {
                    'height': 200,
                    'path': (
                        f'/get-grocery-pics/{group_id}/{image_id}/sizename'
                    ),
                    'width': 200,
                },
            },
        }

    response = await taxi_grocery_pics.post(
        handler, data=image_body, headers={'Content-Type': 'image/png'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '603/exampleid',
        'path': '603/exampleid.jpeg',
        'thumbnails_template': '603/exampleid/{w}x{h}.jpeg',
        'thumbnails': [
            {'name': 'sizename', 'path': '603/exampleid/sizename.jpeg'},
            {'name': 'orig', 'path': '603/exampleid/orig.jpeg'},
        ],
    }
    assert avatar.times_called == 1


def _build_multipart(body, boundary):
    fp = io.BytesIO()
    fp.write(bytes(f'--{boundary}\r\n', 'ascii'))
    fp.write(
        b'Content-Disposition: form-data; name="file"; '
        b'filename="image"\r\n\r\n',
    )
    fp.write(body)
    fp.write(bytes(f'\r\n--{boundary}\r\n', 'ascii'))
    return fp.getvalue()
