import pytest

from testsuite.utils import matching


async def test_photos_200(taxi_cargo_photofixation, build_photo_file_request):
    metas = {
        'cargo_order_id': '6f18c706-1b78-490a-b67e-a11e1fed8c63',
        'claim_point_id': 2524342,
        'photos': [
            {'name': 'photo1.jpg', 'size': 548576},
            {'name': 'photo2.jpg', 'size': 548576},
        ],
    }
    photos_response = await taxi_cargo_photofixation.post(
        '/v1/photos/init-uploading', metas,
    )
    assert photos_response.status_code == 200
    photos_json = photos_response.json()
    assert photos_json == {
        'photos': [
            {'photo_id': matching.AnyString(), 'status': 'initiated'},
            {'photo_id': matching.AnyString(), 'status': 'initiated'},
        ],
    }
    for item in photos_json['photos']:
        file_request = build_photo_file_request(
            item['photo_id'], b'IMAGE FILE MOCK',
        )
        file_response = await taxi_cargo_photofixation.post(
            '/v1/photos/file',
            data=file_request.data,
            headers=file_request.headers,
        )
        assert file_response.status_code == 200
        assert file_response.json() == {
            'photo_id': item['photo_id'],
            'status': 'uploaded',
        }


@pytest.mark.translations(
    cargo={
        'photofixation.file_upload.error.file_not_found': {
            'ru': 'файл не найден',
        },
    },
)
async def test_photos_404(taxi_cargo_photofixation, build_photo_file_request):
    file_request = build_photo_file_request(
        'ffffffff-1b78-490a-b67e-a11e1fed8c63', b'IMAGE FILE MOCK',
    )
    response = await taxi_cargo_photofixation.post(
        '/v1/photos/file',
        data=file_request.data,
        headers=file_request.headers,
    )
    assert response.status_code == 404
    assert response.json()['message'] == 'файл не найден'


@pytest.mark.translations(
    cargo={
        'photofixation.file_upload.error.payload_too_large': {
            'ru': 'payload_too_large_place_holder',
        },
    },
)
@pytest.mark.config(
    CARGO_PHOTOFIXATION_SETTINGS={
        'mds': {'upload_url': 'test', 'download_url': 'test'},
        'max_file_size': 10,
    },
)
async def test_photos_413(
        taxi_cargo_photofixation,
        build_photo_file_request,
        default_image_file_mock,
):
    metas = {
        'cargo_order_id': '6f18c706-1b78-490a-b67e-a11e1fed8c63',
        'claim_point_id': 2524342,
        'photos': [{'name': 'photo1.jpg', 'size': 3}],
    }
    photos_response = await taxi_cargo_photofixation.post(
        '/v1/photos/init-uploading', metas,
    )
    assert photos_response.status_code == 200
    photos_json = photos_response.json()
    assert photos_json == {
        'photos': [{'photo_id': matching.AnyString(), 'status': 'initiated'}],
    }
    for item in photos_json['photos']:
        file_request = build_photo_file_request(
            item['photo_id'], default_image_file_mock(),
        )
        file_response = await taxi_cargo_photofixation.post(
            '/v1/photos/file',
            data=file_request.data,
            headers=file_request.headers,
        )
        assert file_response.status_code == 413
        assert (
            file_response.json()['message'] == 'payload_too_large_place_holder'
        )
