import pytest


@pytest.mark.parametrize('content_type', ['image/jpeg', 'image/png'])
async def test_basic(taxi_grocery_pics, mockserver, content_type):
    @mockserver.handler(
        '/avatars-mds/getinfo-grocery-goods/12345/imagename/orig',
    )
    def mds_mock(request):
        return mockserver.make_response(
            b'This is image', headers={'Content-Type': content_type},
        )

    response = await taxi_grocery_pics.get(
        '/v1/grocery-pics/admin/retrieve/12345/imagename/orig',
    )
    assert response.status_code == 200
    assert response.content == b'This is image'
    assert response.content_type == content_type
    assert mds_mock.times_called == 1


async def test_not_found(taxi_grocery_pics, mockserver):
    @mockserver.handler(
        '/avatars-mds/getinfo-grocery-goods/12345/imagename/orig',
    )
    def mds_mock(request):
        return mockserver.make_response('Not found', status=404)

    response = await taxi_grocery_pics.get(
        '/v1/grocery-pics/admin/retrieve/12345/imagename/orig',
    )
    assert response.status_code == 404
    assert mds_mock.times_called == 1
