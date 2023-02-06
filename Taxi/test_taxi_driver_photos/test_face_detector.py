import asyncio
import io

from aiohttp import web
from PIL import Image
import pytest

from taxi.models.image_typing import ImageFragment

from taxi_driver_photos.api.exceptions import NoFaceFoundError
from taxi_driver_photos.generated.web import web_context as web_context_module
from taxi_driver_photos.models.face_detector import FaceDetector


def _get_image_bytes() -> bytes:
    test_image = Image.new('RGB', (200, 400))
    fp = io.BytesIO()
    test_image.save(fp, 'JPEG')
    fp.seek(0)
    return fp.read()


async def _detect_face(
        web_context: web_context_module.Context,
) -> ImageFragment:
    face_detector = FaceDetector(
        web_context.clients.cbir_features, web_context.config,
    )
    image_bytes = _get_image_bytes()
    return await face_detector.get_largest_face(image_bytes)


def _mock_face_recognition(patch, face_recognition_faces) -> None:
    @patch('face_recognition.face_locations')
    def _patched_face_locations(*args):
        return face_recognition_faces


def _mock_cbir_response(mock_cbir_features, cbir_response) -> None:
    @mock_cbir_features('/images-apphost/cbir-features')
    async def _mock_cbir_features(*args, **kwargs):
        return cbir_response


def _mock_cbir_faces(mock_cbir_features, cbir_faces) -> None:
    cbir_response = web.json_response(
        data={
            'cbirdaemon': {
                'info_orig': '1280x720',
                'similarnn': {
                    'FaceFeatures': [
                        {
                            'Angle': 0,
                            'Confidence': 0.99,
                            'Features': [],
                            'LayerName': '',
                            **face,
                        }
                        for face in cbir_faces
                    ],
                },
            },
        },
    )
    _mock_cbir_response(mock_cbir_features, cbir_response)


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=False)
@pytest.mark.parametrize(
    ['face_recognition_faces', 'expected_face_rect'],
    [
        (
            [(400, 1200, 1000, 500)],
            ImageFragment(x=500, y=400, width=700, height=600, angle=0),
        ),
    ],
)
async def test_face_recognition(
        face_recognition_faces,
        expected_face_rect,
        web_context: web_context_module.Context,
        patch,
):
    _mock_face_recognition(patch, face_recognition_faces)

    assert await _detect_face(web_context) == expected_face_rect


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=False)
async def test_face_recognition_fails(
        web_context: web_context_module.Context, patch,
):
    _mock_face_recognition(patch, [])

    with pytest.raises(NoFaceFoundError):
        await _detect_face(web_context)


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=True)
@pytest.mark.parametrize(
    ['face_recognition_faces', 'cbir_faces', 'expected_face_rect'],
    [
        (
            [(400, 1200, 1000, 500)],
            [
                {
                    'CenterX': 0.3481233716,
                    'CenterY': 0.5577586889,
                    'Height': 0.7067925334,
                    'Width': 0.2908706665,
                },
                {
                    'CenterX': 0.6117575169,
                    'CenterY': 0.5166860819,
                    'Height': 0.06618449092,
                    'Width': 0.02901615202,
                },
            ],
            ImageFragment(x=500, y=400, width=700, height=600, angle=0),
        ),
        (
            [],
            [
                {
                    'CenterX': 0.7465394752,
                    'CenterY': 0.2837462835,
                    'Height': 0.00283465234,
                    'Width': 0.01457346583,
                },
                {
                    'CenterX': 0.3481233716,
                    'CenterY': 0.5577586889,
                    'Height': 0.7067925334,
                    'Width': 0.2908706665,
                },
                {
                    'CenterX': 0.6117575169,
                    'CenterY': 0.5166860819,
                    'Height': 0.06618449092,
                    'Width': 0.02901615202,
                },
            ],
            ImageFragment(x=259, y=147, width=372, height=508, angle=0),
        ),
    ],
)
async def test_cbir_face_detection(
        face_recognition_faces,
        cbir_faces,
        expected_face_rect,
        web_context: web_context_module.Context,
        patch,
        mock_cbir_features,
):
    _mock_face_recognition(patch, face_recognition_faces)
    _mock_cbir_faces(mock_cbir_features, cbir_faces)

    assert await _detect_face(web_context) == expected_face_rect


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=True)
@pytest.mark.parametrize(
    'cbir_response',
    [
        (
            web.json_response(
                data={
                    'cbirdaemon': {
                        'info_orig': '1280x720',
                        'similarnn': {'FaceFeatures': []},
                    },
                },
            )
        ),
        (web.json_response(data={})),
        (web.json_response(text='not json at all')),
    ],
)
async def test_cbir_face_detection_fails(
        cbir_response,
        web_context: web_context_module.Context,
        patch,
        mock_cbir_features,
):
    _mock_face_recognition(patch, [])
    _mock_cbir_response(mock_cbir_features, cbir_response)

    with pytest.raises(NoFaceFoundError):
        await _detect_face(web_context)


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=True)
async def test_cbir_face_detection_timeout(
        web_context: web_context_module.Context, patch,
):
    _mock_face_recognition(patch, [])

    @patch('generated.clients.cbir_features.CbirFeaturesClient._send')
    async def _raise_timeout(*args, **kwargs):
        raise asyncio.TimeoutError

    with pytest.raises(NoFaceFoundError):
        await _detect_face(web_context)


@pytest.mark.config(DRIVER_PHOTOS_USE_CBIR_FACE_DETECTION=True)
@pytest.mark.parametrize(
    ['landmarks', 'expected_angle'],
    [
        (
            [
                {'X': 0.0, 'Y': 1.0},
                {'X': 3.0, 'Y': 1.0},
                {'X': 1.0, 'Y': 3.0},
                {'X': 0.0, 'Y': 5.0},
                {'X': 3.0, 'Y': 5.0},
            ],
            0,
        ),
        (
            [
                {'X': 0.0, 'Y': 1.0},
                {'X': 0.0, 'Y': 3.0},
                {'X': 1.0, 'Y': 2.0},
                {'X': 3.0, 'Y': 1.0},
                {'X': 3.0, 'Y': 3.0},
            ],
            90,
        ),
        (
            [
                {'X': 3.0, 'Y': 5.0},
                {'X': 0.0, 'Y': 5.0},
                {'X': 1.0, 'Y': 3.0},
                {'X': 3.0, 'Y': 1.0},
                {'X': 0.0, 'Y': 1.0},
            ],
            180,
        ),
        (
            [
                {'X': 0.0, 'Y': 3.0},
                {'X': 0.0, 'Y': 1.0},
                {'X': 1.0, 'Y': 2.0},
                {'X': 3.0, 'Y': 3.0},
                {'X': 3.0, 'Y': 1.0},
            ],
            270,
        ),
        ([], 0),
        ([{'X': 0.0, 'Y': 3.0}], 0),
        (
            [
                {'X': 0.0, 'Y': 0.0},
                {'X': 0.0, 'Y': 0.0},
                {'X': 1.0, 'Y': 0.0},
                {'X': 3.0, 'Y': 0.0},
                {'X': 3.0, 'Y': 0.0},
            ],
            0,
        ),
    ],
)
async def test_cbir_rotation(
        landmarks,
        expected_angle,
        web_context: web_context_module.Context,
        patch,
        mock_cbir_features,
):
    _mock_face_recognition(patch, [])
    cbir_face = {
        'CenterX': 0.5,
        'CenterY': 0.5,
        'Height': 1.0,
        'Width': 1.0,
        'Landmarks': landmarks,
    }
    _mock_cbir_faces(mock_cbir_features, [cbir_face])

    expected_face_rect = ImageFragment(
        x=0, y=0, width=1280, height=720, angle=expected_angle,
    )
    assert await _detect_face(web_context) == expected_face_rect
