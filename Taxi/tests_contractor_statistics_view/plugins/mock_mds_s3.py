import io

from PIL import Image
import pytest


def _create_background(shape):
    background = Image.new('RGBA', shape)
    pixel = background.load()
    for x in range(background.width):
        for y in range(background.height):
            pixel[x, y] = (x, y, x + y, y)
    return background


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    """
    Copy-paste from media-storage service
    """

    class FakeMdsClient:
        storage = {}

        def put_object(self, key, body):
            self.storage[key] = bytearray(body)

        def get_object(self, key) -> bytearray:
            return self.storage.get(key)

    def _serialize_pil_image(image):
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='PNG')
        return byte_arr.getvalue()

    client = FakeMdsClient()

    # Background image
    background = _create_background((600, 200))
    client.put_object('/mds-s3/background_0', _serialize_pil_image(background))

    # Symbols to write
    symbols = [
        Image.new('RGBA', (30, 40), (255, 0, 0, 105)),
        Image.new('RGBA', (32, 44), (0, 255, 0, 125)),
        Image.new('RGBA', (34, 40), (0, 0, 0, 135)),
    ]
    for idx, sym in enumerate(symbols):
        client.put_object(f'/mds-s3/sym_{idx}', _serialize_pil_image(sym))

    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_all(request):
        if request.method == 'PUT':
            mds_s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = mds_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)
