import base64
from typing import Optional

import aiohttp
import pytest

from taxi_antifraud.settings import qc_settings


@pytest.fixture
def mock_catboost_model(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/model_zero.bin', 'GET',
    )
    def _get_model_without_categorical(method, url, **kwargs):
        b64_model = """
Q0JNMZABAAAMAAAACAAMAAQACAAIAAAACAAAAEgAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAAAC
oASAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAAAAAADwAQABEACoAAAABAAAAjAAAAIAAAAB0
AAAAHAEAAKQAAACQAAAAiAAAAEwAAAAwAAAAeAAAACQAAACEAAAAeAAAAAwAAABcAAAAcAAAAAEAAA
AAAAAAAAAAAAAAAAACAAAAAAAAAAAA8D8AAAAAAADwPwAAAAACAAAAFDuxEzuxw78UO7ETO7HDPwEA
AAAAAAAAAQAAAAEAAAABAAAAAAAAAAEAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAF
wAAAA4AAAAIAAAAAQAAADA////AwAAAAMAAAAEAAAAAQAAAAAAoEDY////AgAAAAIAAAAEAAAAAAAA
AOz///8BAAAAAQAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAAAAAAABAAAAAAAAAAAAAAA
        """
        return response_mock(read=base64.b64decode(b64_model))

    return _get_model_without_categorical


def _get_image_features(photo: str, load) -> Optional[dict]:
    photo1 = base64.b64decode(load('drive_handlers_photo1'))
    photo2 = base64.b64decode(load('drive_handlers_photo2'))
    photo3 = base64.b64decode(load('drive_handlers_photo3'))

    if photo in (photo1, photo2, photo3):
        return {
            'cbirdaemon': {
                'info_orig': '320x240',
                'similarnn': {
                    'ImageFeatures': [
                        {
                            'Dimension': [1, 96],
                            'Features': [1, 2, 3, 4, 5],
                            'LayerName': 'prod_v8_enc_toloka_96',
                            'Version': '8',
                        },
                    ],
                },
            },
        }

    return None


def _get_face_features(photo: str, load) -> Optional[dict]:
    photo1 = base64.b64decode(load('drive_handlers_photo1'))
    photo2 = base64.b64decode(load('drive_handlers_photo2'))
    photo3 = base64.b64decode(load('drive_handlers_photo3'))
    photo_strange1 = base64.b64decode(load('drive_handlers_strange1'))
    photo_strange2 = base64.b64decode(load('drive_handlers_strange2'))
    no_response_photo = base64.b64decode(load('drive_handlers_no_response'))
    if photo == photo1:
        features = {
            'cbirdaemon': {
                'info_orig': '320x240',
                'similarnn': {
                    'FaceFeatures': [
                        {
                            'Dimension': [1, 96],
                            'LayerName': 'super_face_layer',
                            'Version': '8',
                            'Features': [1, 2, 3, 4, 5],
                            'Height': 10,
                            'Width': 10,
                            'Landmarks': [
                                {'X': 1, 'Y': 2},
                                {'X': 2, 'Y': 3},
                                {'X': 3, 'Y': 4},
                                {'X': 4, 'Y': 5},
                                {'X': 5, 'Y': 1},
                            ],
                        },
                        {
                            'Dimension': [1, 96],
                            'LayerName': 'super_face_layer',
                            'Version': '8',
                            'Features': [4, 5, 6, 4, 5],
                            'Height': 7,
                            'Width': 9,
                            'Landmarks': [
                                {'X': 1, 'Y': 2},
                                {'X': 2, 'Y': 3},
                                {'X': 3, 'Y': 4},
                                {'X': 4, 'Y': 5},
                                {'X': 5, 'Y': 1},
                            ],
                        },
                    ],
                },
            },
        }
    elif photo == photo2:
        features = {
            'cbirdaemon': {
                'info_orig': '320x240',
                'similarnn': {
                    'FaceFeatures': [
                        {
                            'Dimension': [1, 96],
                            'LayerName': 'super_face_layer',
                            'Version': '8',
                            'Features': [1, 2, 3, 4, 5],
                            'Height': 5,
                            'Width': 7,
                            'Landmarks': [
                                {'X': 1, 'Y': 2},
                                {'X': 2, 'Y': 3},
                                {'X': 3, 'Y': 4},
                                {'X': 4, 'Y': 5},
                                {'X': 5, 'Y': 1},
                            ],
                        },
                        {
                            'Dimension': [1, 96],
                            'LayerName': 'super_face_layer',
                            'Version': '8',
                            'Features': [3, 2, 1, 4, 5],
                            'Height': 6,
                            'Width': 6,
                            'Landmarks': [
                                {'X': 1, 'Y': 2},
                                {'X': 2, 'Y': 3},
                                {'X': 3, 'Y': 4},
                                {'X': 4, 'Y': 5},
                                {'X': 5, 'Y': 1},
                            ],
                        },
                    ],
                },
            },
        }
    elif photo == photo3:
        features = {
            'cbirdaemon': {
                'info_orig': '320x240',
                'similarnn': {'FaceFeatures': []},
            },
        }
    elif photo in (photo_strange1, photo_strange2):
        features = {}
    elif photo == no_response_photo:
        return None
    else:
        raise Exception('Can not find photo')

    return features


def _mock_get_features(patch_aiohttp_session, response_mock, load):
    @patch_aiohttp_session(qc_settings.CBIR_URL, 'POST')
    def _get_features(method, url, params, data, **kwargs):
        photo = list(data)[0][0]._value  # pylint: disable=protected-access
        bad_response_photo = base64.b64decode(
            load('drive_handlers_response_500'),
        )
        if photo == bad_response_photo:
            return response_mock(status=500)

        if params['cbird'] == qc_settings.CBIR_ID:
            features = _get_image_features(photo, load)
        elif params['cbird'] == qc_settings.CBIR_ID_FACE_FEATURES:
            features = _get_face_features(photo, load)
        else:
            return response_mock(status=404)

        return response_mock(json=features)


def get_handle_request(photo1: str, photo2: str) -> aiohttp.FormData:
    form = aiohttp.FormData()
    if photo1 is not None:
        file1_content = base64.b64decode(photo1)
        form.add_field(name='photo1', value=file1_content)
    if photo2 is not None:
        file2_content = base64.b64decode(photo2)
        form.add_field(name='photo2', value=file2_content)

    return form


DEFAULT_CONFIG: dict = {
    'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
        'is_front_bad_format_with_rotations_v9_drive': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'is_back_bad_format_with_rotations_v9_drive': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'photo_from_screen_with_rotations_drive': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'quasi_gibdd_drive': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_quasi.bin'
            ),
        },
        'quasi_fms_drive': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_quasi.bin'
            ),
        },
    },
    'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_ENABLED': True,
}


def get_url(request_id: Optional[str]) -> str:
    url = '/v1/calculate_faces_similarity'
    if request_id is not None:
        url += f'?request_id={request_id}'
    return url


@pytest.mark.parametrize(
    'request_id,photo1_path,photo2_path,status,expected_calculate_response',
    [
        pytest.param(
            None,
            'drive_handlers_photo1',
            'drive_handlers_photo2',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': True,
                'found_face_on_photo2': True,
                'similarity': 51 / 55,
            },
            id='both_photos_exist',
        ),
        pytest.param(
            'string',
            'drive_handlers_photo1',
            'drive_handlers_photo2',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': True,
                'found_face_on_photo2': True,
                'similarity': 51 / 55,
            },
            id='both_photos_exist_with_id',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_faces_similarity(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        request_id,
        photo1_path,
        photo2_path,
        status,
        expected_calculate_response,
        load,
):
    photo1 = load(photo1_path)
    photo2 = load(photo2_path)

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)
    url = get_url(request_id)
    response = await web_app_client.post(url, data=data)
    assert response.status == status
    assert await response.json() == expected_calculate_response


@pytest.mark.parametrize(
    'request_id,photo1_path,photo2_path,status,expected_calculate_response',
    [
        pytest.param(
            '2',
            'drive_handlers_photo3',
            'drive_handlers_photo2',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': False,
                'found_face_on_photo2': True,
                'similarity': 0,
            },
            id='first_photo_is_empty',
        ),
        pytest.param(
            'some str',
            'drive_handlers_photo1',
            'drive_handlers_photo3',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': True,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='second_photo_is_empty',
        ),
        pytest.param(
            None,
            'drive_handlers_photo3',
            'drive_handlers_photo3',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': False,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='both_photos_are_empty',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_faces_similarity_no_face_on_photo(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        request_id,
        photo1_path,
        photo2_path,
        status,
        expected_calculate_response,
        load,
):
    photo1 = load(photo1_path)
    photo2 = load(photo2_path)

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)
    url = get_url(request_id)
    response = await web_app_client.post(url, data=data)
    assert response.status == status
    assert await response.json() == expected_calculate_response


@pytest.mark.parametrize(
    'photo1_path,photo2_path,status',
    [
        pytest.param(None, None, 400, id='Both_photos_do_not_exist'),
        pytest.param(
            None,
            'drive_handlers_photo2',
            400,
            id='First_photo_does_not_exist',
        ),
        pytest.param(
            'drive_handlers_photo1',
            None,
            400,
            id='Second_photo_does_not_exist',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_faces_similarity_photo_is_absent(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo1_path,
        photo2_path,
        status,
        load,
):
    photo1 = load(photo1_path) if photo1_path is not None else None
    photo2 = load(photo2_path) if photo2_path is not None else None

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)

    response = await web_app_client.post(
        '/v1/calculate_faces_similarity', data=data,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'photo1_path,photo2_path,status,expected_calculate_response',
    [
        pytest.param(
            'drive_handlers_strange1',
            'drive_handlers_strange2',
            200,
            {
                'cbir_answered_for_photo1': False,
                'cbir_answered_for_photo2': False,
                'found_face_on_photo1': False,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='Both_photos_are_strange_bytes',
        ),
        pytest.param(
            'drive_handlers_strange1',
            'drive_handlers_photo1',
            200,
            {
                'cbir_answered_for_photo1': False,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': False,
                'found_face_on_photo2': True,
                'similarity': 0,
            },
            id='First_photo_is_strange_bytes',
        ),
        pytest.param(
            'drive_handlers_photo1',
            'drive_handlers_strange2',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': False,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'found_face_on_photo1': True,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='Second_photo_is_strange_bytes',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_face_similarity_strange_bytes(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo1_path,
        photo2_path,
        status,
        expected_calculate_response,
        load,
):
    photo1 = load(photo1_path)
    photo2 = load(photo2_path)

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)

    response = await web_app_client.post(
        '/v1/calculate_faces_similarity', data=data,
    )
    assert response.status == status
    assert await response.json() == expected_calculate_response


@pytest.mark.parametrize(
    'photo1_path,photo2_path,status,expected_calculate_response',
    [
        pytest.param(
            'drive_handlers_photo1',
            'drive_handlers_no_response',
            200,
            {
                'cbir_answered_for_photo1': True,
                'cbir_answered_for_photo2': False,
                'from_screen_model_score_for_photo1': 0.46161414343735935,
                'found_face_on_photo1': True,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='Cbir_did_not_responsed_second_photo',
        ),
        pytest.param(
            'drive_handlers_no_response',
            'drive_handlers_photo1',
            200,
            {
                'cbir_answered_for_photo1': False,
                'cbir_answered_for_photo2': True,
                'from_screen_model_score_for_photo2': 0.46161414343735935,
                'found_face_on_photo1': False,
                'found_face_on_photo2': True,
                'similarity': 0,
            },
            id='Cbir_did_not_responsed_first_photo',
        ),
        pytest.param(
            'drive_handlers_no_response',
            'drive_handlers_no_response',
            200,
            {
                'cbir_answered_for_photo1': False,
                'cbir_answered_for_photo2': False,
                'found_face_on_photo1': False,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='Cbir_did_not_responsed_both_photo',
        ),
        pytest.param(
            'drive_handlers_response_500',
            'drive_handlers_response_500',
            200,
            {
                'cbir_answered_for_photo1': False,
                'cbir_answered_for_photo2': False,
                'found_face_on_photo1': False,
                'found_face_on_photo2': False,
                'similarity': 0,
            },
            id='Cbir responsed 500',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_face_similarity_no_cbir_response(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo1_path,
        photo2_path,
        status,
        expected_calculate_response,
        load,
):
    photo1 = load(photo1_path)
    photo2 = load(photo2_path)

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)

    response = await web_app_client.post(
        '/v1/calculate_faces_similarity', data=data,
    )
    assert response.status == status
    assert await response.json() == expected_calculate_response


def get_bytes_if_big_photo_possible(photo_path: str, load) -> bytes:
    big_photo_size = 200 * 10 ** 6
    big_photo = 'a' * big_photo_size
    return big_photo if photo_path == 'BIG_PHOTO' else load(photo_path)


@pytest.mark.parametrize(
    'photo1_path,photo2_path,status',
    [
        pytest.param(
            'BIG_PHOTO', 'BIG_PHOTO', 413, id='Both_photos_are_too_large',
        ),
        pytest.param(
            'BIG_PHOTO',
            'drive_handlers_photo1',
            413,
            id='First_photo_is_too_large',
        ),
        pytest.param(
            'drive_handlers_photo1',
            'BIG_PHOTO',
            413,
            id='Second_photo_is_too_large',
        ),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_faces_similarity_large_photo(
        mock_catboost_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo1_path,
        photo2_path,
        status,
        load,
):
    photo1 = get_bytes_if_big_photo_possible(photo1_path, load)
    photo2 = get_bytes_if_big_photo_possible(photo2_path, load)

    _mock_get_features(patch_aiohttp_session, response_mock, load)

    data = get_handle_request(photo1, photo2)

    response = await web_app_client.post(
        '/v1/calculate_faces_similarity', data=data,
    )
    assert response.status == status
