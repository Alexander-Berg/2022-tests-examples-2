import base64
from typing import Optional

import aiohttp
import pytest

from taxi_antifraud.settings import qc_settings


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['ANTIFRAUD_OCR_API_KEY'] = 'token'
    return simple_secdist


def get_features(
        data: aiohttp.multipart.MultipartWriter, load,
) -> Optional[dict]:
    photo_with_response = base64.b64decode(
        load('ocr_and_cbir_responsed_photo'),
    )
    photo_no_response = base64.b64decode(load('drive_handlers_no_response'))
    photo_ocr_do_not_answered = base64.b64decode(
        load('drive_handlers_ocr_do_not_answered'),
    )
    photo = list(data)[0][0]._value  # pylint: disable=protected-access
    if photo in (photo_with_response, photo_ocr_do_not_answered):
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
    if photo == photo_no_response:
        return None
    raise Exception('Can not find photo')


@pytest.fixture
def mock_get_model(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/model_zero.bin', 'GET',
    )
    def _get_model_without_categorial(method, url, **kwargs):
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

    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/model_quasi.bin', 'GET',
    )
    def _get_quasi_model(method, url, **kwargs):
        b64_model = """
Q0JNMVgBAAAMAAAACAAMAAQACAAIAAAACAAAAEQAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAo
AEQABAAIAAwAEAAUABgAHAAgACQAKAAsADAANAA4AAAAAAA8AEAAKAAAAAEAAACMAAAAgAAAAHQA
AADoAAAAoAAAAJAAAACIAAAASAAAACwAAAB4AAAAIAAAAIAAAAB4AAAACAAAAFwAAAABAAAAAAAA
AAAAAAAAAAAAAgAAAAAAAAAAAPA/AAAAAAAA8D8AAAAAAgAAAHZiJ3ZbGbC/dmIndlsZsD8AAAAA
AQAAAAAAAAABAAAAAQAAAAEAAAAAAAAAAQAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAo
AAAABAAAAOz///8BAAAAAQAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAAAAAAABAAAAAEA
AAAAAAA/AAAAAA==
        """
        return response_mock(read=base64.b64decode(b64_model))

    return _get_model_without_categorial, _get_quasi_model


def _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response):
    @patch_aiohttp_session(qc_settings.OCR_URL, 'POST')
    def _get_ocr_response(method, url, data, **kwargs):
        if 'DriverLicenceFront' in data['meta']:
            response = {'data': {'fulltext': ocr_response['front']}}
        elif 'DriverLicenceBack' in data['meta']:
            response = {'data': {'fulltext': ocr_response['back']}}
        elif 'Passport' in data['meta']:
            response = {'data': {'fulltext': ocr_response['passport']}}
        else:
            return response_mock(status=404)
        return response_mock(json=response)

    return _get_ocr_response


def _mock_get_features(patch_aiohttp_session, response_mock, load):
    @patch_aiohttp_session(qc_settings.CBIR_URL, 'POST')
    def _get_features(method, url, params, data, **kwargs):
        features = get_features(data, load)
        return response_mock(json=features)


def _get_handle_request(photo: bytes) -> aiohttp.FormData:
    form = aiohttp.FormData()
    if photo is not None:
        file_content = base64.b64decode(photo)
        form.add_field(name='photo', value=file_content)

    return form


def _load_photo(photo_path: str, load) -> bytes:
    big_photo_size = 200 * 10 ** 6
    big_photo = 'a' * big_photo_size
    return big_photo if photo_path == 'BIG_PHOTO' else load(photo_path)


def _prepare_test(
        photo_path, patch_aiohttp_session, response_mock, ocr_response, load,
) -> aiohttp.FormData:
    photo = _load_photo(photo_path, load)

    _mock_get_features(patch_aiohttp_session, response_mock, load)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)

    return _get_handle_request(photo)


async def _check_test(
        data, url, web_app_client, expected_status, expected_handle_response,
):
    response = await web_app_client.post(url, data=data)

    assert response.status == expected_status
    if response.status != 413:
        assert await response.json() == expected_handle_response


DEFAULT_CONFIG = {
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


@pytest.mark.parametrize(
    'photo_path,ocr_response,expected_status,expected_handle_response',
    [
        pytest.param(
            'drive_handlers_no_response',
            {'front': None},
            200,
            {'ocr_answered': False, 'cbir_answered': False},
            id='No responses front',
        ),
        pytest.param(
            'ocr_and_cbir_responsed_photo',
            {
                'front': [
                    {'Confidence': 1, 'Text': 'Иван', 'Type': 'name'},
                    {
                        'Confidence': 1,
                        'Text': 'Иванович',
                        'Type': 'middle_name',
                    },
                    {'Confidence': 1, 'Text': 'Иванов', 'Type': 'surname'},
                    {
                        'Confidence': 1,
                        'Text': '13.01.2018',
                        'Type': 'issue_date',
                    },
                    {'Confidence': 1, 'Text': '0133741979', 'Type': 'number'},
                ],
            },
            200,
            {
                'ocr_answered': True,
                'recognized_text': [
                    {'confidence': 1, 'text': 'Иван', 'type': 'name'},
                    {
                        'confidence': 1,
                        'text': 'Иванович',
                        'type': 'middle_name',
                    },
                    {'confidence': 1, 'text': 'Иванов', 'type': 'surname'},
                    {
                        'confidence': 1,
                        'text': '13.01.2018',
                        'type': 'issue_date',
                    },
                    {'confidence': 1, 'text': '0133741979', 'type': 'number'},
                ],
                'cbir_answered': True,
                'quasi_gibdd_score': 0.48428344894918696,
                'from_screen_model_score': 0.46161414343735935,
                'bad_format_model_score': 0.46161414343735935,
            },
            id='ocr and cbir responsed front',
        ),
        pytest.param(
            'drive_handlers_ocr_do_not_answered',
            {'front': None},
            200,
            {
                'ocr_answered': False,
                'cbir_answered': True,
                'from_screen_model_score': 0.46161414343735935,
                'bad_format_model_score': 0.46161414343735935,
            },
            id='ocr_do_not_answered_and_cbir_answered',
        ),
        pytest.param('BIG_PHOTO', None, 413, None, id='Big photo'),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_handle_license_front(
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_get_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo_path,
        expected_status,
        expected_handle_response,
        ocr_response,
        load,
):
    data = _prepare_test(
        photo_path, patch_aiohttp_session, response_mock, ocr_response, load,
    )

    await _check_test(
        data,
        '/v1/check_driver_license_front',
        web_app_client,
        expected_status,
        expected_handle_response,
    )


@pytest.mark.parametrize(
    'photo_path,ocr_response,expected_status,expected_handle_response',
    [
        pytest.param(
            'drive_handlers_no_response',
            {'back': None},
            200,
            {'ocr_answered': False, 'cbir_answered': False},
            id='No responses back',
        ),
        pytest.param(
            'ocr_and_cbir_responsed_photo',
            {
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '13.01.2018',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '27.11.2021',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            200,
            {
                'ocr_answered': True,
                'recognized_text': [
                    {
                        'confidence': 0.4252831159,
                        'type': 'number',
                        'text': '0133741979',
                    },
                    {
                        'confidence': 0.2956020088,
                        'type': 'issue_date',
                        'text': '13.01.2018',
                    },
                    {
                        'confidence': 0.7656020088,
                        'type': 'expiration_date',
                        'text': '27.11.2021',
                    },
                    {
                        'confidence': 0.8817818761,
                        'type': 'experience_from',
                        'text': '2011',
                    },
                ],
                'cbir_answered': True,
                'quasi_gibdd_score': 0.48428344894918696,
                'from_screen_model_score': 0.46161414343735935,
                'bad_format_model_score': 0.46161414343735935,
            },
            id='ocr and cbir responsed back',
        ),
        pytest.param(
            'drive_handlers_ocr_do_not_answered',
            {'back': None},
            200,
            {
                'ocr_answered': False,
                'cbir_answered': True,
                'from_screen_model_score': 0.46161414343735935,
                'bad_format_model_score': 0.46161414343735935,
            },
            id='ocr_do_not_answered_and_cbir_answered',
        ),
        pytest.param('BIG_PHOTO', None, 413, None, id='Big photo'),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_handle_license_back(
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_get_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo_path,
        expected_status,
        expected_handle_response,
        ocr_response,
        load,
):
    data = _prepare_test(
        photo_path, patch_aiohttp_session, response_mock, ocr_response, load,
    )

    await _check_test(
        data,
        '/v1/check_driver_license_back',
        web_app_client,
        expected_status,
        expected_handle_response,
    )


@pytest.mark.parametrize(
    'photo_path,ocr_response,expected_status,expected_handle_response',
    [
        pytest.param(
            'drive_handlers_no_response',
            {'passport': None},
            200,
            {'ocr_answered': False, 'cbir_answered': False},
            id='No responses passport',
        ),
        pytest.param(
            'ocr_and_cbir_responsed_photo',
            {
                'passport': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8776330352,
                        'Type': 'name',
                        'Text': 'татьяна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8884754181,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.886099577,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8965250254,
                        'Type': 'subdivision',
                        'Text': '770-093',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8824692369,
                        'Type': 'gender',
                        'Text': 'жен',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8840693831,
                        'Type': 'citizenship',
                        'Text': 'rus',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8886011243,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8612622023,
                        'Type': 'birth_place',
                        'Text': 'москва',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8992502093,
                        'Type': 'number',
                        'Text': '0910234523',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.899061203,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8840693831,
                        'Type': 'expiration_date',
                        'Text': '-',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8734120131,
                        'Type': 'issued_by',
                        'Text': 'уфмс',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            200,
            {
                'ocr_answered': True,
                'recognized_text': [
                    {
                        'confidence': 0.8776330352,
                        'text': 'татьяна',
                        'type': 'name',
                    },
                    {
                        'confidence': 0.8884754181,
                        'text': 'николаевна',
                        'type': 'middle_name',
                    },
                    {
                        'confidence': 0.886099577,
                        'text': 'андреева',
                        'type': 'surname',
                    },
                    {
                        'confidence': 0.8965250254,
                        'text': '770-093',
                        'type': 'subdivision',
                    },
                    {
                        'confidence': 0.8824692369,
                        'text': 'жен',
                        'type': 'gender',
                    },
                    {
                        'confidence': 0.8840693831,
                        'text': 'rus',
                        'type': 'citizenship',
                    },
                    {
                        'confidence': 0.8886011243,
                        'text': '25.11.1968',
                        'type': 'birth_date',
                    },
                    {
                        'confidence': 0.8612622023,
                        'text': 'москва',
                        'type': 'birth_place',
                    },
                    {
                        'confidence': 0.8992502093,
                        'text': '0910234523',
                        'type': 'number',
                    },
                    {
                        'confidence': 0.899061203,
                        'text': '17.01.2014',
                        'type': 'issue_date',
                    },
                    {
                        'confidence': 0.8840693831,
                        'text': '-',
                        'type': 'expiration_date',
                    },
                    {
                        'confidence': 0.8734120131,
                        'text': 'уфмс',
                        'type': 'issued_by',
                    },
                ],
                'cbir_answered': True,
                'quasi_fms_score': 0.48428344894918696,
                'from_screen_model_score': 0.46161414343735935,
            },
            id='ocr and cbir responsed passport',
        ),
        pytest.param(
            'drive_handlers_ocr_do_not_answered',
            {'passport': None},
            200,
            {
                'ocr_answered': False,
                'cbir_answered': True,
                'from_screen_model_score': 0.46161414343735935,
            },
            id='ocr_do_not_answered_and_cbir_answered',
        ),
        pytest.param('BIG_PHOTO', None, 413, None, id='Big photo'),
    ],
)
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_handle_passport(
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_get_model,  # pylint: disable=redefined-outer-name
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        photo_path,
        expected_status,
        expected_handle_response,
        ocr_response,
        load,
):
    data = _prepare_test(
        photo_path, patch_aiohttp_session, response_mock, ocr_response, load,
    )

    await _check_test(
        data,
        '/v1/check_passport_title',
        web_app_client,
        expected_status,
        expected_handle_response,
    )
