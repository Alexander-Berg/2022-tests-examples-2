import pytest

from testsuite.utils import matching


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.parametrize(
        'handler', ['/v1/order/photos', '/v1/admin/order/photos'],
    ),
]


@pytest.mark.config(
    CARGO_PHOTOFIXATION_SETTINGS={
        'max_file_size': 1048576,
        'mds': {
            'download_url': 'http://cargo-photofixation.s3.mdst.yandex.net',
        },
    },
)
async def test_order_photos_200(
        handler,
        taxi_cargo_photofixation,
        create_default_photos,
        cargo_order_id='bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
):
    response = await taxi_cargo_photofixation.post(
        handler, params={'cargo_order_id': cargo_order_id},
    )
    assert response.status_code == 200
    order_photos = response.json()
    assert order_photos['cargo_order_id'] == cargo_order_id
    first_photo = order_photos['photos'][0]
    assert first_photo == {
        'id': matching.AnyString(),
        'claim_point_id': 1,
        'status': 'uploaded',
        'url': matching.AnyString(),
    }
    assert (
        first_photo['url']
        == 'http://cargo-photofixation.s3.mdst.yandex.net/photos/{}_{}'.format(
            first_photo['id'], 'photo1.jpg',
        )
    )


@pytest.mark.translations(
    cargo={
        'photofixation.file_upload.error.file_not_found': {
            'ru': 'payload_too_large_place_holder',
        },
    },
)
async def test_order_photos_404(
        handler,
        taxi_cargo_photofixation,
        create_default_photos,
        cargo_order_id='aaaaaaaa-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
):
    response = await taxi_cargo_photofixation.post(
        handler, params={'cargo_order_id': cargo_order_id},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'payload_too_large_place_holder',
    }
