import pytest

from testsuite.utils import matching


async def test_photos_200(taxi_cargo_photofixation):
    metas = {
        'cargo_order_id': '6f18c706-1b78-490a-b67e-a11e1fed8c63',
        'claim_point_id': 2524342,
        'photos': [
            {'name': 'photo1.jpg', 'size': 548576},
            {'name': 'photo2.jpg', 'size': 548576},
        ],
    }
    response = await taxi_cargo_photofixation.post(
        '/v1/photos/init-uploading', metas,
    )
    assert response.status_code == 200
    assert response.json() == {
        'photos': [
            {'photo_id': matching.AnyString(), 'status': 'initiated'},
            {'photo_id': matching.AnyString(), 'status': 'initiated'},
        ],
    }


@pytest.mark.translations(
    cargo={
        'photofixation.error.no_photos_to_upload': {
            'ru': 'payload_too_large_place_holder',
        },
    },
)
async def test_photos_400(taxi_cargo_photofixation):
    metas = {
        'cargo_order_id': '6f18c706-1b78-490a-b67e-a11e1fed8c63',
        'claim_point_id': 2524342,
        'photos': [],
    }
    response = await taxi_cargo_photofixation.post(
        '/v1/photos/init-uploading', metas,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'payload_too_large_place_holder',
    }


@pytest.mark.translations(
    cargo={
        'photofixation.error.payload_too_large': {
            'ru': 'payload_too_large_place_holder',
        },
    },
)
@pytest.mark.config(
    CARGO_PHOTOFIXATION_SETTINGS={
        'mds': {'upload_url': 'test', 'download_url': 'test'},
        'max_file_size': 1500,
    },
)
async def test_photos_413(taxi_cargo_photofixation):
    metas = {
        'cargo_order_id': '6f18c706-1b78-490a-b67e-a11e1fed8c63',
        'claim_point_id': 524342,
        'photos': [
            {'name': 'photo1.jpg', 'size': 1000},
            {'name': 'photo2.jpg', 'size': 2000},
            {'name': 'photo4.jpg', 'size': 3000},
        ],
    }
    response = await taxi_cargo_photofixation.post(
        '/v1/photos/init-uploading', metas,
    )
    assert response.status_code == 413
    assert response.json() == {
        'message': 'payload_too_large_place_holder',
        'photos': [
            {'name': 'photo2.jpg', 'size': 2000},
            {'name': 'photo4.jpg', 'size': 3000},
        ],
    }
