# pylint: disable=too-many-lines
import asyncio
import base64
import copy
import datetime
from typing import Callable

from aiohttp import web
import pandas  # noqa: fixes freezegun import
import pytest
from yt import yson

from taxi_antifraud.crontasks import resolve_qc_passes
from taxi_antifraud.generated.cron import run_cron
from taxi_antifraud.settings import qc_settings
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = resolve_qc_passes.CURSOR_STATE_NAME


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['ANTIFRAUD_OCR_API_KEY'] = 'token'
    simple_secdist['settings_override'][
        'TAXIMETER_XSERVICE_NIRVANA_API_KEY'
    ] = 'another_token'
    simple_secdist['settings_override'][
        'ANTIFRAUD_SANDBOX_OAUTH_TOKEN'
    ] = 'token2'
    return simple_secdist


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        assert request_id.endswith('_pd_id')
        return {'license': request_id[:-6]}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, driver_license, *args, **kwargs):
        return {'id': driver_license + '_pd_id'}


def _mock_nirvana_dkvu_get(mock_taximeter_xservice, response_items):
    @mock_taximeter_xservice('/utils/nirvana/dkvu/get')
    async def _nirvana_dkvu_get(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '666666666666666666':
            return web.json_response(data=dict(items=[]))
        return web.json_response(
            data=dict(cursor=666666666666666666, items=response_items),
        )

    return _nirvana_dkvu_get


def _mock_qc_invites(mock_qc_invites):
    @mock_qc_invites('/admin/qc-invites/v1/dkvu/invite')
    async def _qc_invite_dkvu(request):
        assert request.method == 'POST'

        return web.json_response(data=dict(invite_id='invite_id'))

    return _qc_invite_dkvu


def _mock_qc_invites_info(mock_qc_invites):
    @mock_qc_invites('/api/qc-invites/v1/invite_info')
    async def _qc_invites_find(request):
        assert request.method == 'GET'

        return web.json_response(
            data=dict(comment='[allow auto verdict] Регулярный вызов'),
        )

    return _qc_invites_find


def _mock_nirvana_dkvu_set(mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/nirvana/dkvu/set')
    async def _nirvana_dkvu_set(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    return _nirvana_dkvu_set


def _mock_get_jpg(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://example.com/file.jpg', 'GET')
    def _get_jpg(method, url, **kwargs):
        if url == 'http://example.com/file.jpg' and method.upper() == 'GET':
            return response_mock(read=bytes())
        return response_mock(status=404)

    return _get_jpg


def _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response):
    @patch_aiohttp_session(qc_settings.OCR_URL, 'POST')
    def _get_ocr_response(method, url, data, **kwargs):
        if 'DriverLicenceFront' in data['meta']:
            response = {'data': {'fulltext': ocr_response['front']}}
        elif 'DriverLicenceBack' in data['meta']:
            response = {'data': {'fulltext': ocr_response['back']}}
        elif 'FullOcrMultihead' in data['meta']:
            response = {'data': {'fulltext': ocr_response['full']}}
        else:
            return response_mock(status=404)
        return response_mock(json=response)

    return _get_ocr_response


def _mock_get_model(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/model.bin', 'GET',
    )
    def _get_model(method, url, **kwargs):
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

    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/regressor_model.bin',
        'GET',
    )
    def _get_regressor_model(method, url, **kwargs):
        b64_model = """
Q0JNMZABAAAMAAAACAAMAAQACAAIAAAACAAAAEgAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAAAC
oASAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAAAAAADwAQABEACoAAAABAAAAjAAAAIAAAAB0
AAAAHAEAAKQAAACQAAAAiAAAAEwAAAAwAAAAeAAAACQAAACEAAAAeAAAAAwAAABcAAAAcAAAAAEAAA
AAAAAAAAA5QAAAAAACAAAAAAAAAAAA8D8AAAAAAADwPwAAAAACAAAAAAAAAAAA5L8AAAAAAADkPwEA
AAAAAAAAAQAAAAEAAAABAAAAAAAAAAEAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAF
wAAAA4AAAAIAAAAAQAAADA////AwAAAAMAAAAEAAAAAQAAAAAANELY////AgAAAAIAAAAEAAAAAAAA
AOz///8BAAAAAQAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAAAAAAABAAAAAAAAAAAAAAA
        """
        return response_mock(read=base64.b64decode(b64_model))

    return _get_model, _get_regressor_model


def _mock_get_features(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(qc_settings.CBIR_URL, 'POST')
    def _get_features(method, url, params, **kwargs):
        if params['cbird'] == qc_settings.CBIR_ID_FACE_FEATURES:
            features = {
                'cbirdaemon': {
                    'info_orig': '320x240',
                    'similarnn': {
                        'FaceFeatures': [
                            {
                                'LayerName': 'super_face_layer',
                                'Features': [0.736, 0.928, 0.1111, 3.9, 5.6],
                                'Height': 0.1342742741,
                                'Width': 0.15700639635,
                                'Confidence': 0.99,
                            },
                            {
                                'LayerName': 'super_face_layer',
                                'Features': [0.572, 0.374, 0.2222, 3.9, 5.6],
                                'Height': 0.7678670883,
                                'Width': 0.3513435721,
                                'Confidence': 0.9,
                            },
                        ],
                    },
                },
            }
        else:
            features = {
                'cbirdaemon': {
                    'info_orig': '320x240',
                    'similarnn': {
                        'ImageFeatures': [
                            {
                                'Dimension': [1, 96],
                                'Features': [0.123, 0.546],
                                'LayerName': 'prod_v8_enc_toloka_96',
                                'Version': '8',
                            },
                        ],
                    },
                },
            }
        return response_mock(json=features)

    return _get_features


def _mock_get_saas_response(
        patch_aiohttp_session, response_mock, response_json,
):
    @patch_aiohttp_session(qc_settings.SAAS_URL, 'GET')
    def _get_saas_response(method, url, **kwargs):
        return response_mock(
            json={'response': {'results': [{'groups': response_json}]}},
        )

    return _get_saas_response


QC_HISTORY_DEFAULT = [
    {
        'entity_id': 'some_entity_id',
        'entity_type': 'driver',
        'modified': '2020-01-01T00:00:00',
        'exam': 'dkvu',
        'id': 'some_pass_id',
        'status': 'NEW',
    },
    {
        'entity_id': 'some_entity_id',
        'entity_type': 'driver',
        'modified': '2019-01-01T00:00:00',
        'exam': 'dkvu',
        'id': 'some_pass_id_2',
        'status': 'RESOLVED',
        'resolution': {'status': 'FAIL'},
    },
    {
        'entity_id': 'some_entity_id',
        'entity_type': 'driver',
        'modified': '2018-01-01T00:00:00',
        'exam': 'dkvu',
        'id': 'some_pass_id_3',
        'status': 'RESOLVED',
        'resolution': {'status': 'SUCCESS', 'identity': {}},
    },
    {
        'entity_id': 'some_entity_id',
        'entity_type': 'driver',
        'modified': '2017-01-01T00:00:00',
        'exam': 'dkvu',
        'id': 'some_pass_id_4',
        'status': 'RESOLVED',
        'resolution': {'status': 'CANCEL', 'identity': {'yandex_team': {}}},
    },
    {
        'entity_id': 'some_entity_id',
        'entity_type': 'driver',
        'modified': '2016-01-01T00:00:00',
        'exam': 'dkvu',
        'id': 'some_pass_id_5',
        'status': 'RESOLVED',
        'resolution': {
            'status': 'SUCCESS',
            'identity': {'yandex_team': {'yandex_login': 'toropov'}},
        },
    },
]


def _mock_quality_control_history(mock_quality_control_py3, qc_history=None):
    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'

        if qc_history is None:
            return web.json_response(
                data=dict(cursor='end', items=QC_HISTORY_DEFAULT),
            )
        return web.json_response(data=dict(cursor='end', items=qc_history))

    return _api_v1_pass_history


def _mock_blocklist_find_info(mock_blocklist, blocklist_info=None):
    @mock_blocklist('/internal/blocklist/v1/find')
    async def _internal_blocklist_v1_find(request):
        assert request.method == 'POST'

        if blocklist_info is None:
            return web.json_response(data=dict(history={}, blocks=[]))
        return web.json_response(data=dict(history={}, blocks=blocklist_info))

    return _internal_blocklist_v1_find


def _mock_driver_profile(mock_driver_profiles, driver_profile):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def get_profile(request):
        assert request.method == 'POST'
        return web.json_response(data=dict(profiles=[driver_profile]))

    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _get_app_profile(request):
        assert request.method == 'POST'
        return web.json_response(data=dict(profiles=[driver_profile]))

    return get_profile


def _mock_geolocation(mock_driver_trackstory, geolocation):
    @mock_driver_trackstory('/position')
    async def _position_post(request):
        assert request.method == 'POST'
        return web.json_response(data={'position': geolocation, 'type': 'raw'})


def _mock_telesign(mock_uantifraud, score):
    @mock_uantifraud('/v2/phone_scoring/sync/score')
    async def get_score(request):
        assert request.method == 'POST'
        return web.json_response(
            data={
                'report': {
                    'score': score,
                    'recommendation': 'dunno',
                    'full_report': '',
                },
            },
        )

    return get_score


def _build_saas_body(body: dict) -> str:
    return base64.b64encode(bytes([0]) + yson.dumps(body)).decode()


def _assert_unordered_equality(
        actual: list, expected: list, key: Callable,
) -> None:
    assert sorted(actual, key=key) == sorted(expected, key=key)


DEFAULT_CONFIG: dict = {
    'AFS_CRON_CURSOR_USE_PGSQL': 'enabled',
    'AFS_CRON_RESOLVE_QC_PASSES_AGE_MODEL_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
        'is_front_bad_format_with_rotations_v9': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'is_back_bad_format_with_rotations_v9': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'is_selfie_bad_format': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'photo_from_screen_with_rotations': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'printed_photo': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'faceapp_selfie': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.9,
        },
        'isRUS_license_with_rotations_v9': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.1,
        },
        'face_age': {
            'url': 'https://storage.yandex-team.ru/get-devtools/regressor_model.bin',  # noqa: E501 pylint: disable=line-too-long
            'is_regressor': True,
        },
        'quasi_gibdd': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model.bin',
            'threshold': 0.1,
        },
    },
    'AFS_CRON_RESOLVE_QC_PASSES_DKVU_SAAS_THRESHOLDS': {
        'min_similarity_front': 0.975,
        'min_similarity_back': 0.984,
        'min_similarity_selfie': 0.960,
    },
    'AFS_CRON_RESOLVE_QC_PASSES_EMPTY_BATCH_SLEEP_TIME': 0.01,
    'AFS_CRON_RESOLVE_QC_PASSES_EMPTY_BATCHES_LIMIT': 3,
    'AFS_CRON_RESOLVE_QC_PASSES_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_EXAM_TO_FEATURES_NAME_MAPPING': [
        {'exam': 'dkvu', 'features_name': 'Feat8_tlk'},
    ],
    'AFS_CRON_RESOLVE_QC_PASSES_PART_OF_PASSES_TO_RESOLVE': 1.0,
    'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_RESOLUTION_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_OCR_CONFIDENCE_EXPERIENCE_THRESHOLD': 0.5,
    'AFS_CRON_RESOLVE_QC_PASSES_RESOLUTION_DATA_ON_UNKNOWN_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_HISTORY_FEATURES_LENGTH': 5,
    'AFS_CRON_RESOLVE_QC_PASSES_MISTAKES_STATUS_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_MAX_MISTAKES_VERDICTS_IN_ROW': 1,
    'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_BLACKLIST_THRESHOLD': 0.1,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_STATUS_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_QUASI_GIBDD_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_FIO_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATE_FIO_MAX_LICENSE_DISTANCE': 4,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_INVALID_SYMBOLS_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_BAD_FORMAT_THRESHOLD': 0.5,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_MIN_DAYS_DELTA': 1,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_MIN_SIMILARITY_BACK': 0.99,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_MIN_SIMILARITY_FRONT': 0.982,
    'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_MIN_SIMILARITY_SAME_DRIVER': (
        0.995
    ),
    'AFS_CRON_RESOLVE_QC_PASSES_BANNED_SELFIES_CONFIDENCE_THRESHOLD': 0.889,
    'AFS_CRON_RESOLVE_QC_PASSES_BANNED_SELFIES_COUNT_OF_FACES': 1,
    'AFS_CRON_RESOLVE_QC_PASSES_BANNED_SELFIES_FACE_SIZE_THRESHOLD': 0.0,
    'AFS_CRON_RESOLVE_QC_PASSES_BANNED_SELFIES_SIMILARITY_THRESHOLD': 0.8797,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_BANNED_SELFIES_SAAS_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_FIO_AND_BIRTHDAY_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
        True
    ),
    'AFS_CRON_RESOLVE_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': False,
    'AFS_CRON_RESOLVE_QC_PASSES_VERDICTS_FOR_INVITED_ENABLED': False,
    'AFS_CRON_RESOLVE_QC_PASSES_BLOCK_SUCCESS_VERDICTS_AFTER_BLACKLIST': True,
    'AFS_CRON_RESOLVE_QC_PASSES_DRIVER_LICENSE_YEARS_THRESHOLD': 18,
    'AFS_CRON_RESOLVE_QC_PASSES_DRIVER_YEARS_THRESHOLD': {
        'min_years': 18,
        'max_years': 100,
    },
    'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_REAL_GIBDD_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_ISSUE_DATE_AND_LAST_CHECK_DIFFERENCE_THRESHOLD': (  # noqa: E501 pylint: disable=line-too-long
        30
    ),
    'AFS_CRON_RESOLVE_QC_PASSES_FACE_AGE_THRESHOLD': 20,
    'AFS_CRON_RESOLVE_QC_PASSES_SAAS_SEARCH_SIZE': 10,
    'AFS_CRON_RESOLVE_QC_PASSES_SAAS_TOP_SIZE': 50,
    'AFS_CRON_RESOLVE_QC_PASSES_SUSPICIOUS_DEVICES_TO_UNKNOWN_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_SUSPICIOUS_PARKS_TO_UNKNOWN_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_SUSPICIOUS_GEOHASHES_TO_UNKNOWN_ENABLED': True,
    'PPS_CRON_COMMENTS_FOR_INVITES_TO_RESOLVE': [
        '[allow auto verdict] Регулярный вызов',
    ],
    'AFS_CRON_RESOLVE_QC_PASSES_VALID_LICENSE_FORMAT': '[\\wА-я\\-–/\']*',
}

DEFAULT_CONFIG_WITHOUT_QUASI_GIBDD = DEFAULT_CONFIG.copy()
DEFAULT_CONFIG_WITHOUT_QUASI_GIBDD[
    'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_ENABLED'
] = False

DEFAULT_CATBOOST_FEATURES: dict = {
    'back_is_rus_license_probability': 0.48428344894918696,
    'back_photo_from_screen_probability': 0.48428344894918696,
    'front_is_rus_license_probability': 0.48428344894918696,
    'front_photo_from_screen_probability': 0.48428344894918696,
    'is_front_bad_format_probability': 0.48428344894918696,
    'is_back_bad_format_probability': 0.48428344894918696,
    'is_selfie_bad_format_probability': 0.48428344894918696,
    'selfie_photo_from_screen_probability': 0.48428344894918696,
    'printed_selfie_probability': 0.48428344894918696,
    'faceapp_selfie_probability': 0.48428344894918696,
    'face_age_prediction': 24.375,
    'quasi_gibdd_score': 0.48428344894918696,
}

DEFAULT_GET_MODEL_CALLS = {
    'classifier_model_calls': 8,
    'regressor_model_calls': 1,
}

DEFAULT_QUASI_GIBDD_FEATURES = {
    'features': [
        -70,
        -45,
        -37,
        -33,
        -27,
        3,
        12,
        22,
        46,
        48,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        -2,
        1,
        0,
        0.014285714285714285,
        -0.0,
        -0.0,
        -0.0,
        -0.0,
        0.0,
        0.0,
        -0.09090909090909091,
        0.021739130434782608,
        0.0,
        '0133',
        741979,
        6853,
    ],
    'is_valid_by_real_gibdd': None,
    'last_check_date': None,
}

DEFAULT_DRIVER_PROFILE = {
    'created_date': '2020-10-09T10:29:15.695',
    'device_model': 'GOOGLE PIXEL 4A (5G)',
    'imei': 'fn-UjinhSRmNhhvGTP6lFN',
    'locale': 'ru',
    'metrica_device_id': 'd01c68c2e786f543c8c52a2f6329cfbb',
    'metrica_uuid': 'dba479fb9d834be095069c27d2f9a91a',
    'network_operator': 'MTS RUS',
    'phone_pd_ids': [{'pd_id': 'some_pd_id'}],
    'taximeter_platform': 'android',
    'taximeter_version': '10.07 ' '(1074054729)',
}

DEFAULT_GEOLOCATION = {
    'lat': 55.75017,
    'lon': 37.534206,
    'speed': 0.024069087579846382,
    'accuracy': 20,
    'direction': 20,
    'timestamp': 1650904279,
    'geohash': 'ucftnj5862',
}


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content,'
    'expected_state_pgsql_content,expected_nirvana_dkvu_get_calls,'
    'expected_nirvana_dkvu_set_calls,expected_get_jpg_calls,'
    'expected_get_ocr_response_calls,expected_get_model_calls,'
    'expected_get_features_calls,expected_get_saas_response_calls,'
    'expected_get_quality_control_history',
    [
        (
            'failed_passes_with_lots_of_fails',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'isRUS_license_with_rotations_v9': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['isRUS_license_with_rotations_v9'],
                        'threshold': 0.9,
                    },
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 0.9,
                    },
                },
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1910-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2019-10-07',
                    },
                },
                {
                    'id': 'some_qc_id_2',
                    'pending_date': '2020-02-02T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id_2',
                        'db_id': 'some_db_id_2',
                        'driver_id': 'some_driver_id_2',
                    },
                },
                {
                    'id': 'some_qc_id_3',
                    'pending_date': '2020-03-03T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id_3',
                        'db_id': 'some_db_id_3',
                        'driver_id': 'some_driver_id_3',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979A',
                        'number_pd_id': '0133741979A_pd_id',
                        'issue_date': 'not a date',
                        'expire_date': 'not a date',
                    },
                },
                {
                    'id': 'some_qc_id_4',
                    'pending_date': '2020-04-04T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id_4',
                        'db_id': 'some_db_id_4',
                        'driver_id': 'some_driver_id_4',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '000011110A',
                        'number_pd_id': '000011110A_pd_id',
                        'issue_date': '2000-01-01',
                        'expire_date': '2010-01-01',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'вася',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'андреич',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0000111102',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '03.07.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '17.07.2023',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0000222201',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
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
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0000222201',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
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
                    {
                        'Confidence': 0.3875634563,
                        'Type': 'some_random_field',
                        'Text': 'ВАСИЛИЙ!',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'ocr_features': {
                            'back': [
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.2956020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.6,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.7656020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.09999999999999998
                                    ),
                                    'name': 'license_number',
                                    'ocr_confidence': 0.4252831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'back_experience_from': '2011',
                            'back_experience_from_ocr_confidence': (
                                0.8817818761
                            ),
                            'back_expiration_date': '27.11.2021',
                            'back_issue_date': '07.10.2019',
                            'back_license_number_pd_id': '0000222201_pd_id',
                            'back_full_model_text_contains_firstname': True,
                            'back_recognized_text': [
                                {
                                    'confidence': 0.4252831159,
                                    'pd_id': '0000222201_pd_id',
                                    'text': '*****22201',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.2956020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.7656020088,
                                    'text': '27.11.2021',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8817818761,
                                    'text': '2011',
                                    'type': 'experience_from',
                                },
                            ],
                            'front': [
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.4285714285714286
                                    ),
                                    'name': 'firstname',
                                    'ocr_confidence': 0.8776331544,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'middlename',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 0.7,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.7566020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.5,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.8986020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.19999999999999996
                                    ),
                                    'name': 'license_number',
                                    'ocr_confidence': 0.8942831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'front_expiration_date': '17.07.2023',
                            'front_issue_date': '03.07.2019',
                            'front_license_number_pd_id': '0000111102_pd_id',
                            'front_birth_date': None,
                            'front_birth_date_ocr_confidence': None,
                            'front_recognized_text': [
                                {
                                    'confidence': 0.8776331544,
                                    'text': 'вася',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'андреич',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.8942831159,
                                    'pd_id': '0000111102_pd_id',
                                    'text': '*****11102',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7566020088,
                                    'text': '03.07.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.8986020088,
                                    'text': '17.07.2023',
                                    'type': 'expiration_date',
                                },
                            ],
                            'probable_experience_date': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'saas_features': {
                            'back': [],
                            'front': [],
                            'selfie': [],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.15700639635,
                            },
                        ],
                        'quasi_gibdd_features': DEFAULT_QUASI_GIBDD_FEATURES,
                        'duplicate_by_fio_license_pd_ids': [],
                        'duplicate_by_fio_birthday_pd_ids': [],
                        'qc_pass': {
                            'birthday': '1910-01-01',
                            'country': None,
                            'db_id': 'some_db_id',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id',
                            'expire_date': '2019-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': None,
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'blacklist_features': {'parks_where_blacklisted': []},
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                            'by_driver_license': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                        },
                        'changes': [],
                        'verdict': 'unknown',
                        'skip_verdict_because_of_percent': False,
                        'errors': [
                            'ocr field lastname is missing from ocr '
                            'response for front picture',
                            'ocr field firstname on front picture is '
                            'different from the field in driver profile',
                            'ocr field license_expire_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue and expire dates in driver '
                            'profile are not exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is different from the field on back '
                            'picture',
                            'license numbers on front and back pictures '
                            'are different',
                            'ocr field license_number on front picture is '
                            'different from the field in driver profile',
                            'catboost front_is_rus_license_probability '
                            'reached threshold',
                            'catboost back_is_rus_license_probability '
                            'reached threshold',
                            'face age prediction is not close to driver age',
                            'firstname is found in full model text for '
                            'back picture',
                            'license is expired',
                            'quasi-gibdd score is too low',
                        ],
                        'message_keys': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                        'invite_dkvu_request': None,
                        'photo_signatures': {
                            'front': None,
                            'back': None,
                            'selfie': None,
                        },
                        'vm_detects': None,
                        'protector_aux_data': None,
                        'telesign_score': None,
                        'suspicion_info': {
                            'by_device_id': [],
                            'by_park_id': [],
                            'by_geohash': [],
                        },
                        'invite_comment': None,
                        'driver_profile': DEFAULT_DRIVER_PROFILE,
                        'geolocation': DEFAULT_GEOLOCATION,
                    },
                    'entity_id': 'some_db_id_some_driver_id',
                    'entity_type': 'driver',
                    'exam': 'dkvu',
                    'pass_id': 'some_pass_id',
                    'qc_id': 'some_qc_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                },
                {
                    'additional_info': {
                        'ocr_features': {
                            'back': [
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.2956020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.7656020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.4252831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                            ],
                            'back_experience_from': '2011',
                            'back_experience_from_ocr_confidence': (
                                0.8817818761
                            ),
                            'back_expiration_date': '27.11.2021',
                            'back_issue_date': '07.10.2019',
                            'back_license_number_pd_id': '0000222201_pd_id',
                            'back_full_model_text_contains_firstname': False,
                            'back_recognized_text': [
                                {
                                    'confidence': 0.4252831159,
                                    'pd_id': '0000222201_pd_id',
                                    'text': '*****22201',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.2956020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.7656020088,
                                    'text': '27.11.2021',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8817818761,
                                    'text': '2011',
                                    'type': 'experience_from',
                                },
                            ],
                            'front': [
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'firstname',
                                    'ocr_confidence': 0.8776331544,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'middlename',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.7566020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.8986020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.8942831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                            ],
                            'front_expiration_date': '17.07.2023',
                            'front_issue_date': '03.07.2019',
                            'front_license_number_pd_id': '0000111102_pd_id',
                            'front_birth_date': None,
                            'front_birth_date_ocr_confidence': None,
                            'front_recognized_text': [
                                {
                                    'confidence': 0.8776331544,
                                    'text': 'вася',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'андреич',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.8942831159,
                                    'pd_id': '0000111102_pd_id',
                                    'text': '*****11102',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7566020088,
                                    'text': '03.07.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.8986020088,
                                    'text': '17.07.2023',
                                    'type': 'expiration_date',
                                },
                            ],
                            'probable_experience_date': None,
                        },
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'saas_features': {
                            'back': [],
                            'front': [],
                            'selfie': [],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.15700639635,
                            },
                        ],
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': None,
                        'duplicate_by_fio_birthday_pd_ids': None,
                        'qc_pass': {
                            'birthday': None,
                            'country': None,
                            'db_id': 'some_db_id_2',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id_2',
                            'expire_date': None,
                            'first_name': None,
                            'issue_date': None,
                            'last_name': None,
                            'middle_name': None,
                            'number': None,
                            'number_pd_id': None,
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'blacklist_features': None,
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                            'by_driver_license': None,
                        },
                        'changes': [],
                        'verdict': 'unknown',
                        'skip_verdict_because_of_percent': False,
                        'errors': [
                            'ocr field lastname is missing from ocr '
                            'response for front picture',
                            'field firstname is missing from driver '
                            'profile',
                            'ocr field license_expire_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_issue_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue and expire dates in driver '
                            'profile are not exactly ten years apart',
                            'ocr field license_expire_date on back '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue date on front picture and '
                            'expire date in driver profile are not '
                            'exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is different from the field on back '
                            'picture',
                            'license issue and expire dates on front '
                            'picture are not exactly ten years apart',
                            'field license_issue_date is missing from '
                            'driver profile',
                            'license number is not present',
                            'license numbers on front and back pictures '
                            'are different',
                            'ocr field license_number on front picture is '
                            'different from the field in driver profile',
                            'catboost front_is_rus_license_probability '
                            'reached threshold',
                            'catboost back_is_rus_license_probability '
                            'reached threshold',
                            'birthday is unknown',
                            'license expire date is not present',
                            'blacklist features are None',
                            'quasi-gibdd score is not calculated',
                        ],
                        'message_keys': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                        'invite_dkvu_request': None,
                        'photo_signatures': {
                            'front': None,
                            'back': None,
                            'selfie': None,
                        },
                        'vm_detects': None,
                        'protector_aux_data': None,
                        'telesign_score': None,
                        'suspicion_info': {
                            'by_device_id': [],
                            'by_park_id': [],
                            'by_geohash': [],
                        },
                        'invite_comment': None,
                        'driver_profile': DEFAULT_DRIVER_PROFILE,
                        'geolocation': DEFAULT_GEOLOCATION,
                    },
                    'entity_id': 'some_db_id_2_some_driver_id_2',
                    'entity_type': 'driver',
                    'exam': 'dkvu',
                    'pass_id': 'some_pass_id_2',
                    'qc_id': 'some_qc_id_2',
                    'pass_modified': datetime.datetime(2020, 2, 2, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                },
                {
                    'additional_info': {
                        'ocr_features': {
                            'back': [
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.2956020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.7656020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.09090909090909094
                                    ),
                                    'name': 'license_number',
                                    'ocr_confidence': 0.4252831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'back_experience_from': '2011',
                            'back_experience_from_ocr_confidence': (
                                0.8817818761
                            ),
                            'back_expiration_date': '27.11.2021',
                            'back_issue_date': '07.10.2019',
                            'back_license_number_pd_id': '0000222201_pd_id',
                            'back_full_model_text_contains_firstname': True,
                            'back_recognized_text': [
                                {
                                    'confidence': 0.4252831159,
                                    'pd_id': '0000222201_pd_id',
                                    'text': '*****22201',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.2956020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.7656020088,
                                    'text': '27.11.2021',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8817818761,
                                    'text': '2011',
                                    'type': 'experience_from',
                                },
                            ],
                            'front': [
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.4285714285714286
                                    ),
                                    'name': 'firstname',
                                    'ocr_confidence': 0.8776331544,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'middlename',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.7566020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.8986020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.18181818181818177
                                    ),
                                    'name': 'license_number',
                                    'ocr_confidence': 0.8942831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'front_expiration_date': '17.07.2023',
                            'front_issue_date': '03.07.2019',
                            'front_license_number_pd_id': '0000111102_pd_id',
                            'front_birth_date': None,
                            'front_birth_date_ocr_confidence': None,
                            'front_recognized_text': [
                                {
                                    'confidence': 0.8776331544,
                                    'text': 'вася',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'андреич',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.8942831159,
                                    'pd_id': '0000111102_pd_id',
                                    'text': '*****11102',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7566020088,
                                    'text': '03.07.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.8986020088,
                                    'text': '17.07.2023',
                                    'type': 'expiration_date',
                                },
                            ],
                            'probable_experience_date': None,
                        },
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'saas_features': {
                            'back': [],
                            'front': [],
                            'selfie': [],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.15700639635,
                            },
                        ],
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'duplicate_by_fio_birthday_pd_ids': None,
                        'qc_pass': {
                            'birthday': None,
                            'country': None,
                            'db_id': 'some_db_id_3',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id_3',
                            'expire_date': 'not a date',
                            'first_name': 'Василий',
                            'issue_date': 'not a date',
                            'last_name': 'Иванов',
                            'middle_name': None,
                            'number': '*****41979A',
                            'number_pd_id': '0133741979A_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'blacklist_features': {'parks_where_blacklisted': []},
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                            'by_driver_license': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                        },
                        'changes': [],
                        'verdict': 'unknown',
                        'skip_verdict_because_of_percent': False,
                        'errors': [
                            'ocr field lastname is missing from ocr '
                            'response for front picture',
                            'ocr field firstname on front picture is '
                            'different from the field in driver profile',
                            'ocr field license_expire_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_issue_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue and expire dates in driver '
                            'profile are not exactly ten years apart',
                            'ocr field license_expire_date on back '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue date on front picture and '
                            'expire date in driver profile are not '
                            'exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is different from the field on back '
                            'picture',
                            'license issue and expire dates on front '
                            'picture are not exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is less than or equal to the field '
                            'license_issue_date in driver profile',
                            'issue_date_plus_ten_years is None, should '
                            'never fire. so it\'s either a bug or '
                            'issue_date is not an iso date string',
                            'license number has wrong length',
                            'license numbers on front and back pictures '
                            'are different',
                            'ocr field license_number on front picture is '
                            'different from the field in driver profile',
                            'catboost front_is_rus_license_probability '
                            'reached threshold',
                            'catboost back_is_rus_license_probability '
                            'reached threshold',
                            'birthday is unknown',
                            'firstname is found in full model text for '
                            'back picture',
                            'license expire date is not present',
                            'quasi-gibdd score is not calculated',
                        ],
                        'message_keys': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                        'invite_dkvu_request': None,
                        'photo_signatures': {
                            'front': None,
                            'back': None,
                            'selfie': None,
                        },
                        'vm_detects': None,
                        'protector_aux_data': None,
                        'telesign_score': None,
                        'suspicion_info': {
                            'by_device_id': [],
                            'by_park_id': [],
                            'by_geohash': [],
                        },
                        'invite_comment': None,
                        'driver_profile': DEFAULT_DRIVER_PROFILE,
                        'geolocation': DEFAULT_GEOLOCATION,
                    },
                    'entity_id': 'some_db_id_3_some_driver_id_3',
                    'entity_type': 'driver',
                    'exam': 'dkvu',
                    'pass_id': 'some_pass_id_3',
                    'qc_id': 'some_qc_id_3',
                    'pass_modified': datetime.datetime(2020, 3, 3, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                },
                {
                    'additional_info': {
                        'ocr_features': {
                            'back': [
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.5,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.2956020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.5,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.7656020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.5,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.4252831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'back_experience_from': '2011',
                            'back_experience_from_ocr_confidence': (
                                0.8817818761
                            ),
                            'back_expiration_date': '27.11.2021',
                            'back_issue_date': '07.10.2019',
                            'back_license_number_pd_id': '0000222201_pd_id',
                            'back_full_model_text_contains_firstname': True,
                            'back_recognized_text': [
                                {
                                    'confidence': 0.4252831159,
                                    'pd_id': '0000222201_pd_id',
                                    'text': '*****22201',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.2956020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.7656020088,
                                    'text': '27.11.2021',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8817818761,
                                    'text': '2011',
                                    'type': 'experience_from',
                                },
                            ],
                            'front': [
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': (
                                        0.4285714285714286
                                    ),
                                    'name': 'firstname',
                                    'ocr_confidence': 0.8776331544,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': None,
                                    'levenshtein_similarity': None,
                                    'name': 'middlename',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': False,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.6,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.7566020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.5,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.8986020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 0.9,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.8942831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'front_expiration_date': '17.07.2023',
                            'front_issue_date': '03.07.2019',
                            'front_license_number_pd_id': '0000111102_pd_id',
                            'front_birth_date': None,
                            'front_birth_date_ocr_confidence': None,
                            'front_recognized_text': [
                                {
                                    'confidence': 0.8776331544,
                                    'text': 'вася',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'андреич',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.8942831159,
                                    'pd_id': '0000111102_pd_id',
                                    'text': '*****11102',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7566020088,
                                    'text': '03.07.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.8986020088,
                                    'text': '17.07.2023',
                                    'type': 'expiration_date',
                                },
                            ],
                            'probable_experience_date': None,
                        },
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'saas_features': {
                            'back': [],
                            'front': [],
                            'selfie': [],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.15700639635,
                            },
                        ],
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'duplicate_by_fio_birthday_pd_ids': None,
                        'qc_pass': {
                            'birthday': None,
                            'country': None,
                            'db_id': 'some_db_id_4',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id_4',
                            'expire_date': '2010-01-01',
                            'first_name': 'Василий',
                            'issue_date': '2000-01-01',
                            'last_name': 'Иванов',
                            'middle_name': None,
                            'number': '*****1110A',
                            'number_pd_id': '000011110A_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'blacklist_features': {'parks_where_blacklisted': []},
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                            'by_driver_license': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                        },
                        'changes': [],
                        'verdict': 'unknown',
                        'skip_verdict_because_of_percent': False,
                        'errors': [
                            'ocr field lastname is missing from ocr '
                            'response for front picture',
                            'ocr field firstname on front picture is '
                            'different from the field in driver profile',
                            'ocr field license_expire_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_issue_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_expire_date on back '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue date on front picture and '
                            'expire date in driver profile are not '
                            'exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is different from the field on back '
                            'picture',
                            'license issue and expire dates on front '
                            'picture are not exactly ten years apart',
                            'ocr field license_expire_date on front '
                            'picture is more than ten years greater than '
                            'the field license_issue_date in driver '
                            'profile',
                            'license number has invalid characters',
                            'license numbers on front and back pictures '
                            'are different',
                            'ocr field license_number on front picture is '
                            'different from the field in driver profile',
                            'catboost front_is_rus_license_probability '
                            'reached threshold',
                            'catboost back_is_rus_license_probability '
                            'reached threshold',
                            'birthday is unknown',
                            'firstname is found in full model text for '
                            'back picture',
                            'license is expired',
                            'quasi-gibdd score is not calculated',
                        ],
                        'message_keys': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                        'invite_dkvu_request': None,
                        'photo_signatures': {
                            'front': None,
                            'back': None,
                            'selfie': None,
                        },
                        'vm_detects': None,
                        'protector_aux_data': None,
                        'telesign_score': None,
                        'suspicion_info': {
                            'by_device_id': [],
                            'by_park_id': [],
                            'by_geohash': [],
                        },
                        'invite_comment': None,
                        'driver_profile': DEFAULT_DRIVER_PROFILE,
                        'geolocation': DEFAULT_GEOLOCATION,
                    },
                    'entity_id': 'some_db_id_4_some_driver_id_4',
                    'entity_type': 'driver',
                    'exam': 'dkvu',
                    'pass_id': 'some_pass_id_4',
                    'qc_id': 'some_qc_id_4',
                    'pass_modified': datetime.datetime(2020, 4, 4, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                },
            ],
            {'resolve_qc_passes_cursor': '666666666666666666'},
            [
                [('cursor', '0'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1910-01-01',
                            'expire_date': '2019-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                    {'data': {}, 'id': 'some_qc_id_2', 'status': 'unknown'},
                    {
                        'data': {
                            'expire_date': 'not a date',
                            'first_name': 'Василий',
                            'issue_date': 'not a date',
                            'last_name': 'Иванов',
                            'number': '0133741979A',
                        },
                        'id': 'some_qc_id_3',
                        'status': 'unknown',
                    },
                    {
                        'data': {
                            'expire_date': '2010-01-01',
                            'first_name': 'Василий',
                            'issue_date': '2000-01-01',
                            'last_name': 'Иванов',
                            'number': '000011110A',
                        },
                        'id': 'some_qc_id_4',
                        'status': 'unknown',
                    },
                ],
            ],
            12,
            16,
            DEFAULT_GET_MODEL_CALLS,
            16,
            20,
            [
                {
                    'direction': 'desc',
                    'filter': {'id': 'some_db_id_2_some_driver_id_2'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'id': 'some_db_id_3_some_driver_id_3'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'id': 'some_db_id_4_some_driver_id_4'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'driver_license_pd_id': '0133741979A_pd_id'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'driver_license_pd_id': '000011110A_pd_id'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'id': 'some_db_id_some_driver_id'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'driver_license_pd_id': '0133741979_pd_id'},
                    'limit': 5,
                },
            ],
        ),
        (
            'successful_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'ocr_features': {
                            'back': [
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.2956020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.7656020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.4252831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'back_experience_from': '2011',
                            'back_experience_from_ocr_confidence': (
                                0.8817818761
                            ),
                            'back_expiration_date': '07.10.2029',
                            'back_issue_date': '07.10.2019',
                            'back_license_number_pd_id': '0133741979_pd_id',
                            'back_full_model_text_contains_firstname': False,
                            'back_recognized_text': [
                                {
                                    'confidence': 0.4252831159,
                                    'pd_id': '0133741979_pd_id',
                                    'text': '*****41979',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.2956020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.7656020088,
                                    'text': '07.10.2029',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8817818761,
                                    'text': '2011',
                                    'type': 'experience_from',
                                },
                            ],
                            'front': [
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'lastname',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'firstname',
                                    'ocr_confidence': 0.8776331544,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': False,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'middlename',
                                    'ocr_confidence': 0.8884754777,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_issue_date',
                                    'ocr_confidence': 0.7566020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_expire_date',
                                    'ocr_confidence': 0.8986020088,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                                {
                                    'is_in_full_model_text': True,
                                    'levenshtein_similarity': 1.0,
                                    'name': 'license_number',
                                    'ocr_confidence': 0.8942831159,
                                    'ocr_info_is_present': True,
                                    'profile_info_is_present': True,
                                },
                            ],
                            'front_expiration_date': '07.10.2029',
                            'front_issue_date': '07.10.2019',
                            'front_license_number_pd_id': '0133741979_pd_id',
                            'front_birth_date': '24.08.1993',
                            'front_birth_date_ocr_confidence': 0.8920281529,
                            'front_recognized_text': [
                                {
                                    'confidence': 0.8776331544,
                                    'text': 'василий',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'аристархович',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.8884754777,
                                    'text': 'иванов',
                                    'type': 'surname',
                                },
                                {
                                    'confidence': 0.8942831159,
                                    'pd_id': '0133741979_pd_id',
                                    'text': '*****41979',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7566020088,
                                    'text': '07.10.2019',
                                    'type': 'issue_date',
                                },
                                {
                                    'confidence': 0.8986020088,
                                    'text': '07.10.2029',
                                    'type': 'expiration_date',
                                },
                                {
                                    'confidence': 0.8920281529,
                                    'text': '24.08.1993',
                                    'type': 'birth_date',
                                },
                            ],
                            'probable_experience_date': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'saas_features': {
                            'back': [],
                            'front': [],
                            'selfie': [],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [],
                                'width': 0.15700639635,
                            },
                        ],
                        'quasi_gibdd_features': DEFAULT_QUASI_GIBDD_FEATURES,
                        'duplicate_by_fio_license_pd_ids': [],
                        'duplicate_by_fio_birthday_pd_ids': [],
                        'qc_pass': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'db_id': 'some_db_id',
                            'driver_experience': '2019-10-07',
                            'driver_id': 'some_driver_id',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'blacklist_features': {'parks_where_blacklisted': []},
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                            'by_driver_license': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2019-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_2',
                                    'status': 'FAIL',
                                },
                                {
                                    'entity_id': 'some_entity_id',
                                    'modified': '2018-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_3',
                                    'status': 'SUCCESS',
                                },
                                {
                                    'assessor': None,
                                    'entity_id': 'some_entity_id',
                                    'modified': '2017-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_4',
                                    'status': 'CANCEL',
                                },
                                {
                                    'assessor': 'toropov',
                                    'entity_id': 'some_entity_id',
                                    'modified': '2016-01-01T00:00:00',
                                    'pass_id': 'some_pass_id_5',
                                    'status': 'SUCCESS',
                                },
                            ],
                        },
                        'changes': [
                            {
                                'field_name': 'birthday',
                                'new_value': '1993-08-24',
                                'old_value': None,
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'Иванов',
                                'old_value': ' Иванов ',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'Василий',
                                'old_value': 'Василий  ',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'Аристархович',
                                'old_value': 'Аристархович   ',
                            },
                            {
                                'field_name': 'country',
                                'new_value': 'rus',
                                'old_value': None,
                            },
                            {
                                'field_name': 'driver_experience',
                                'new_value': '2019-10-07',
                                'old_value': None,
                            },
                        ],
                        'verdict': 'success',
                        'skip_verdict_because_of_percent': False,
                        'errors': [],
                        'message_keys': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                        'invite_dkvu_request': None,
                        'photo_signatures': {
                            'front': None,
                            'back': None,
                            'selfie': None,
                        },
                        'vm_detects': None,
                        'protector_aux_data': None,
                        'telesign_score': None,
                        'suspicion_info': {
                            'by_device_id': [],
                            'by_park_id': [],
                            'by_geohash': [],
                        },
                        'invite_comment': None,
                        'driver_profile': DEFAULT_DRIVER_PROFILE,
                        'geolocation': DEFAULT_GEOLOCATION,
                    },
                    'entity_id': 'some_db_id_some_driver_id',
                    'entity_type': 'driver',
                    'exam': 'dkvu',
                    'pass_id': 'some_pass_id',
                    'qc_id': 'some_qc_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                },
            ],
            {'resolve_qc_passes_cursor': '666666666666666666'},
            [
                [('cursor', '0'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
            3,
            4,
            DEFAULT_GET_MODEL_CALLS,
            4,
            5,
            [
                {
                    'direction': 'desc',
                    'filter': {'id': 'some_db_id_some_driver_id'},
                    'limit': 5,
                },
                {
                    'direction': 'desc',
                    'filter': {'driver_license_pd_id': '0133741979_pd_id'},
                    'limit': 5,
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_driver_profiles,
        mock_driver_trackstory,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_state_pgsql_content,
        expected_nirvana_dkvu_get_calls,
        expected_nirvana_dkvu_set_calls,
        expected_get_jpg_calls,
        expected_get_ocr_response_calls,
        expected_get_model_calls,
        expected_get_features_calls,
        expected_get_saas_response_calls,
        expected_get_quality_control_history,
):
    taxi_config.set_values(config)
    nirvana_dkvu_get = _mock_nirvana_dkvu_get(
        mock_taximeter_xservice, nirvana_dkvu_get_response,
    )
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    get_jpg = _mock_get_jpg(patch_aiohttp_session, response_mock)
    get_ocr_response = _mock_get_ocr_response(
        patch_aiohttp_session, response_mock, ocr_response,
    )
    get_classifier_model, get_regressor_model = _mock_get_model(
        patch_aiohttp_session, response_mock,
    )
    get_features = _mock_get_features(patch_aiohttp_session, response_mock)
    get_saas_response = _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    get_quality_control_history = _mock_quality_control_history(
        mock_quality_control_py3,
    )
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    _mock_blocklist_find_info(mock_blocklist)
    _mock_driver_profile(
        mock_driver_profiles,
        {'data': DEFAULT_DRIVER_PROFILE, 'park_driver_profile_id': 'some_id'},
    )
    _mock_geolocation(mock_driver_trackstory, DEFAULT_GEOLOCATION)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_verdicts_db_content
    )

    assert [
        list(nirvana_dkvu_get.next_call()['request'].query.items())
        for _ in range(nirvana_dkvu_get.times_called)
    ] == expected_nirvana_dkvu_get_calls
    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )
    assert len(get_jpg.calls) == expected_get_jpg_calls
    assert len(get_ocr_response.calls) == expected_get_ocr_response_calls
    assert {
        'classifier_model_calls': len(get_classifier_model.calls),
        'regressor_model_calls': len(get_regressor_model.calls),
    } == expected_get_model_calls
    assert len(get_features.calls) == expected_get_features_calls
    assert len(get_saas_response.calls) == expected_get_saas_response_calls
    _assert_unordered_equality(
        mock.get_requests(get_quality_control_history),
        expected_get_quality_control_history,
        lambda x: list(x['filter'].values()),
    )

    assert (
        await state.get_all_cron_state(master_pool)
        == expected_state_pgsql_content
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'blocklist_find_history,expected_verdicts_db_content',
    [
        (
            'unknown_pass_because_of_blacklist_history',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'block_id': 'some_block_id',
                    'kwargs': {},
                    'predicate_id': 'some_redicate_id',
                    'status': 'active',
                },
            ],
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'errors': ['has blacklist verdict in some parks'],
                        'blacklist_features': {
                            'parks_where_blacklisted': ['some'],
                        },
                    },
                },
            ],
        ),
        (
            'successful_pass_config_is_disabled',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLOCK_SUCCESS_VERDICTS_AFTER_BLACKLIST': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'block_id': 'some_block_id',
                    'kwargs': {},
                    'predicate_id': 'some_redicate_id',
                    'status': 'active',
                },
            ],
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'errors': [],
                        'blacklist_features': {
                            'parks_where_blacklisted': ['some'],
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_history_features(
        mock_taximeter_xservice,
        patch_aiohttp_session,
        response_mock,
        mock_quality_control_py3,
        mock_blocklist,
        mock_qc_invites,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        blocklist_find_history,
        expected_verdicts_db_content,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)

    _mock_blocklist_find_info(mock_blocklist, blocklist_find_history)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.blacklist_features': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content',
    [
        (
            'successful pass because of timeout',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'errors': [],
                        'blacklist_features': {'parks_where_blacklisted': []},
                    },
                },
            ],
        ),
    ],
)
async def test_timeout(
        mock_taximeter_xservice,
        patch_aiohttp_session,
        response_mock,
        mock_quality_control_py3,
        patch,
        mock_blocklist,
        mock_qc_invites,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    @patch('generated.clients.blocklist.BlocklistClient._send')
    async def raise_timeout(*args, **kwargs):
        raise asyncio.TimeoutError

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert len(raise_timeout.calls) == 1

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.blacklist_features': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content,'
    'expected_get_saas_response_calls',
    [
        (
            'test_saas',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 137.07627735443532,
                                        'car_id': (
                                            '478f147a532441d7982af8a6020a2011'
                                        ),
                                        'car_numbers': 'X675MC178',
                                        'city': 'Санкт-Петербург',
                                        'db': (
                                            '3c9ceaabb3024732a250d163c10157f8'
                                        ),
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'driver_name': 'Сидоров Довлет',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'КР Транспорт',
                                        'qc_date': '2018-10-30',
                                        'qc_id': (
                                            'a8f509f1a91141a3b96d51a78495f593'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2018-10-30T11:40:21Z',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                        'url': '1328725/b7a6d1d92301932d.jpg',
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '2948531856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                ),
                            },
                            'relevance': '937016308',
                        },
                    ],
                },
                {
                    'documents': [
                        {
                            'properties': {
                                # It has YsonEntity
                                '_Body': 'AXsiYnJpZ2h0bmVzc19sZXZlbCI9OTguODk0MTY3NjQzNjEwNzk7ImNhcl9pZCI9IjZjM2NmYTY4YjM5MTQwODJiMmFhNWJiMzBiNGE0YTI1IjsiY2FyX251bWJlcnMiPSJBODQ4Q1A3NTAiOyJjaXR5Ij0iXHhkMFx4OWNceGQwXHhiZVx4ZDFceDgxXHhkMFx4YmFceGQwXHhiMlx4ZDBceGIwIjsiZGIiPSJlY2ViMDE2OGY4ZTY0NDVlYmQ0OGFjZmIyZDBlNTcxNyI7ImRyaXZlcl9pZCI9IjVmMDQ5MTQxOGYyYjQ0OTk4MjEwNWJiMDc3NGI5Y2Y5IjsiZHJpdmVyX2xpY2Vuc2UiPSJNTTAwOTg0NCI7ImRyaXZlcl9uYW1lIj0iUGhpbGlwcGUgU2hleW11ciBBeml6YWdhIjsiaW1hZ2VfdHlwZSI9IkRyaXZlckxpY2Vuc2UiOyJwYXJrX25hbWUiPSJceGQwXHhiMVx4ZDBceGI4XHhkMFx4YjdceGQwXHhiZFx4ZDBceGI1XHhkMVx4ODEiOyJxY19kYXRlIj0iMjAxOS0wMS0zMCI7InFjX2lkIj0iNmRiY2E3NjAxMjM4NDYyMDg5ZjE4NGVjMTI0ODBiYmYiOyJleGFtIj0iZGt2dSI7InJlc29sdXRpb24iPSM7InRpbWVzdGFtcCI9IjIwMTktMDEtMzBUMTE6NDc6MDlaIjsidXJsIj0iMTEwMDg5NS9jNzMzMDU2YmE2NzZhOTZjYWUyLmpwZyI7fQ==',  # noqa: E501 pylint: disable=line-too-long
                            },
                            'relevance': '931299209',
                        },
                    ],
                },
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '2948531856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                        'pass_id': 'some_pass_id',
                                    },
                                ),
                            },
                            'relevance': '937016308',
                        },
                    ],
                },
            ],
            {'front': [], 'back': [], 'full': []},
            [
                {
                    'additional_info': {
                        'saas_features': {
                            'back': [
                                {
                                    'metainfo': {
                                        'brightness_level': 137.07627735443532,
                                        'car_id': (
                                            '478f147a532441d7982af8a6020a2011'
                                        ),
                                        'car_numbers': 'X675MC178',
                                        'city': 'Санкт-Петербург',
                                        'db': (
                                            '3c9ceaabb3024732a250d163c10157f8'
                                        ),
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '*****69214',
                                        'driver_name': 'Сидоров Довлет',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'КР Транспорт',
                                        'pass_modified': 1514616129.840873,
                                        'qc_date': '2018-10-30',
                                        'qc_id': (
                                            'a8f509f1a91141a3b96d51a78495f593'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2018-10-30T11:40:21Z',
                                        'uberdriver_driver_id': None,
                                        'url': '1328725/b7a6d1d92301932d.jpg',
                                    },
                                    'similarity': 0.942027688,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.937016308,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 98.89416764361079,
                                        'car_id': (
                                            '6c3cfa68b3914082b2aa5bb30b4a4a25'
                                        ),
                                        'car_numbers': 'A848CP750',
                                        'city': 'Москва',
                                        'db': (
                                            'eceb0168f8e6445ebd48acfb2d0e5717'
                                        ),
                                        'driver_id': (
                                            '5f0491418f2b449982105bb0774b9cf9'
                                        ),
                                        'driver_license': '****9844',
                                        'driver_name': (
                                            'Philippe Sheymur Azizaga'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'бизнес',
                                        'qc_date': '2019-01-30',
                                        'qc_id': (
                                            '6dbca7601238462089f184ec12480bbf'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': None,
                                        'timestamp': '2019-01-30T11:47:09Z',
                                        'url': (
                                            '1100895/c733056ba676a96cae2.jpg'
                                        ),
                                    },
                                    'similarity': 0.931299209,
                                },
                            ],
                            'front': [
                                {
                                    'metainfo': {
                                        'brightness_level': 137.07627735443532,
                                        'car_id': (
                                            '478f147a532441d7982af8a6020a2011'
                                        ),
                                        'car_numbers': 'X675MC178',
                                        'city': 'Санкт-Петербург',
                                        'db': (
                                            '3c9ceaabb3024732a250d163c10157f8'
                                        ),
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '*****69214',
                                        'driver_name': 'Сидоров Довлет',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'КР Транспорт',
                                        'pass_modified': 1514616129.840873,
                                        'qc_date': '2018-10-30',
                                        'qc_id': (
                                            'a8f509f1a91141a3b96d51a78495f593'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2018-10-30T11:40:21Z',
                                        'uberdriver_driver_id': None,
                                        'url': '1328725/b7a6d1d92301932d.jpg',
                                    },
                                    'similarity': 0.942027688,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.937016308,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 98.89416764361079,
                                        'car_id': (
                                            '6c3cfa68b3914082b2aa5bb30b4a4a25'
                                        ),
                                        'car_numbers': 'A848CP750',
                                        'city': 'Москва',
                                        'db': (
                                            'eceb0168f8e6445ebd48acfb2d0e5717'
                                        ),
                                        'driver_id': (
                                            '5f0491418f2b449982105bb0774b9cf9'
                                        ),
                                        'driver_license': '****9844',
                                        'driver_name': (
                                            'Philippe Sheymur Azizaga'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'бизнес',
                                        'qc_date': '2019-01-30',
                                        'qc_id': (
                                            '6dbca7601238462089f184ec12480bbf'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': None,
                                        'timestamp': '2019-01-30T11:47:09Z',
                                        'url': (
                                            '1100895/c733056ba676a96cae2.jpg'
                                        ),
                                    },
                                    'similarity': 0.931299209,
                                },
                            ],
                            'selfie': [
                                {
                                    'metainfo': {
                                        'brightness_level': 137.07627735443532,
                                        'car_id': (
                                            '478f147a532441d7982af8a6020a2011'
                                        ),
                                        'car_numbers': 'X675MC178',
                                        'city': 'Санкт-Петербург',
                                        'db': (
                                            '3c9ceaabb3024732a250d163c10157f8'
                                        ),
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '*****69214',
                                        'driver_name': 'Сидоров Довлет',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'КР Транспорт',
                                        'pass_modified': 1514616129.840873,
                                        'qc_date': '2018-10-30',
                                        'qc_id': (
                                            'a8f509f1a91141a3b96d51a78495f593'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2018-10-30T11:40:21Z',
                                        'uberdriver_driver_id': None,
                                        'url': '1328725/b7a6d1d92301932d.jpg',
                                    },
                                    'similarity': 0.942027688,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.937016308,
                                },
                                {
                                    'metainfo': {
                                        'brightness_level': 98.89416764361079,
                                        'car_id': (
                                            '6c3cfa68b3914082b2aa5bb30b4a4a25'
                                        ),
                                        'car_numbers': 'A848CP750',
                                        'city': 'Москва',
                                        'db': (
                                            'eceb0168f8e6445ebd48acfb2d0e5717'
                                        ),
                                        'driver_id': (
                                            '5f0491418f2b449982105bb0774b9cf9'
                                        ),
                                        'driver_license': '****9844',
                                        'driver_name': (
                                            'Philippe Sheymur Azizaga'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'бизнес',
                                        'qc_date': '2019-01-30',
                                        'qc_id': (
                                            '6dbca7601238462089f184ec12480bbf'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': None,
                                        'timestamp': '2019-01-30T11:47:09Z',
                                        'url': (
                                            '1100895/c733056ba676a96cae2.jpg'
                                        ),
                                    },
                                    'similarity': 0.931299209,
                                },
                            ],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                137.07627735443532
                                            ),
                                            'car_id': '478f147a532441d7982af8a6020a2011',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': 'X675MC178',
                                            'city': 'Санкт-Петербург',
                                            'db': '3c9ceaabb3024732a250d163c10157f8',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': '241d732cca194fffad2380dc0bb9fe77',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****69214',
                                            'driver_name': 'Сидоров Довлет',
                                            'image_type': 'DriverLicense',
                                            'park_name': 'КР Транспорт',
                                            'pass_modified': 1514616129.840873,
                                            'qc_date': '2018-10-30',
                                            'qc_id': 'a8f509f1a91141a3b96d51a78495f593',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2018-10-30T11:40:21Z'
                                            ),
                                            'uberdriver_driver_id': None,
                                            'url': (
                                                '1328725/b7a6d1d92301932d.jpg'
                                            ),
                                        },
                                        'similarity': 0.942027688,
                                    },
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                115.39172284095349
                                            ),
                                            'car_id': 'eef410b521d845a681c948d888982c56',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': '0336HX40',
                                            'city': 'Калуга',
                                            'db': '3e0920e77b27469e9ac502ee3c4f4f93',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': 'a5d2a6ebf1dc4eb8b5d1a98b0994cb09',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****31856',
                                            'driver_name': (
                                                'Барабов Андрей Юрьевич'
                                            ),
                                            'image_type': 'DriverLicense',
                                            'park_name': 'Аренда Авто +',
                                            'qc_date': '2019-02-25',
                                            'qc_id': '21f807b8aeb64c9790ff3854809c45bc',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2019-02-25T05:35:17Z'
                                            ),
                                            'url': (
                                                '1575887/6a06af11ecac3a1d7.jpg'
                                            ),
                                        },
                                        'similarity': 0.937016308,
                                    },
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                98.89416764361079
                                            ),
                                            'car_id': '6c3cfa68b3914082b2aa5bb30b4a4a25',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': 'A848CP750',
                                            'city': 'Москва',
                                            'db': 'eceb0168f8e6445ebd48acfb2d0e5717',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': '5f0491418f2b449982105bb0774b9cf9',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '****9844',
                                            'driver_name': (
                                                'Philippe '
                                                'Sheymur '
                                                'Azizaga'
                                            ),
                                            'image_type': 'DriverLicense',
                                            'park_name': 'бизнес',
                                            'qc_date': '2019-01-30',
                                            'qc_id': '6dbca7601238462089f184ec12480bbf',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': None,
                                            'timestamp': (
                                                '2019-01-30T11:47:09Z'
                                            ),
                                            'url': '1100895/c733056ba676a96cae2.jpg',  # noqa: E501 pylint: disable=line-too-long
                                        },
                                        'similarity': 0.931299209,
                                    },
                                ],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                137.07627735443532
                                            ),
                                            'car_id': '478f147a532441d7982af8a6020a2011',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': 'X675MC178',
                                            'city': 'Санкт-Петербург',
                                            'db': '3c9ceaabb3024732a250d163c10157f8',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': '241d732cca194fffad2380dc0bb9fe77',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****69214',
                                            'driver_name': 'Сидоров Довлет',
                                            'image_type': 'DriverLicense',
                                            'park_name': 'КР Транспорт',
                                            'pass_modified': 1514616129.840873,
                                            'qc_date': '2018-10-30',
                                            'qc_id': 'a8f509f1a91141a3b96d51a78495f593',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2018-10-30T11:40:21Z'
                                            ),
                                            'uberdriver_driver_id': None,
                                            'url': (
                                                '1328725/b7a6d1d92301932d.jpg'
                                            ),
                                        },
                                        'similarity': 0.942027688,
                                    },
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                115.39172284095349
                                            ),
                                            'car_id': 'eef410b521d845a681c948d888982c56',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': '0336HX40',
                                            'city': 'Калуга',
                                            'db': '3e0920e77b27469e9ac502ee3c4f4f93',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': 'a5d2a6ebf1dc4eb8b5d1a98b0994cb09',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****31856',
                                            'driver_name': (
                                                'Барабов Андрей Юрьевич'
                                            ),
                                            'image_type': 'DriverLicense',
                                            'park_name': 'Аренда Авто +',
                                            'qc_date': '2019-02-25',
                                            'qc_id': '21f807b8aeb64c9790ff3854809c45bc',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2019-02-25T05:35:17Z'
                                            ),
                                            'url': (
                                                '1575887/6a06af11ecac3a1d7.jpg'
                                            ),
                                        },
                                        'similarity': 0.937016308,
                                    },
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                98.89416764361079
                                            ),
                                            'car_id': '6c3cfa68b3914082b2aa5bb30b4a4a25',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': 'A848CP750',
                                            'city': 'Москва',
                                            'db': 'eceb0168f8e6445ebd48acfb2d0e5717',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': '5f0491418f2b449982105bb0774b9cf9',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '****9844',
                                            'driver_name': (
                                                'Philippe '
                                                'Sheymur '
                                                'Azizaga'
                                            ),
                                            'image_type': 'DriverLicense',
                                            'park_name': 'бизнес',
                                            'qc_date': '2019-01-30',
                                            'qc_id': '6dbca7601238462089f184ec12480bbf',  # noqa: E501 pylint: disable=line-too-long
                                            'exam': 'dkvu',
                                            'resolution': None,
                                            'timestamp': (
                                                '2019-01-30T11:47:09Z'
                                            ),
                                            'url': '1100895/c733056ba676a96cae2.jpg',  # noqa: E501 pylint: disable=line-too-long
                                        },
                                        'similarity': 0.931299209,
                                    },
                                ],
                                'width': 0.15700639635,
                            },
                        ],
                        'verdict': 'mistakes',
                    },
                },
            ],
            5,
        ),
        (
            'successful_pass saas has only identity',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '2948531856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'identity',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                        'confidence': 0.9,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                    },
                                ),
                            },
                            'relevance': '999999999',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'saas_features': {
                            'back': [
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'confidence': 0.9,
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'exam': 'identity',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.999999999,
                                },
                            ],
                            'front': [
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'confidence': 0.9,
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'exam': 'identity',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.999999999,
                                },
                            ],
                            'selfie': [
                                {
                                    'metainfo': {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'confidence': 0.9,
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '*****31856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'exam': 'identity',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                    'similarity': 0.999999999,
                                },
                            ],
                        },
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                115.39172284095349
                                            ),
                                            'car_id': 'eef410b521d845a681c948d888982c56',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': '0336HX40',
                                            'city': 'Калуга',
                                            'confidence': 0.9,
                                            'db': '3e0920e77b27469e9ac502ee3c4f4f93',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': 'a5d2a6ebf1dc4eb8b5d1a98b0994cb09',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****31856',
                                            'driver_name': (
                                                'Барабов Андрей Юрьевич'
                                            ),
                                            'exam': 'identity',
                                            'image_type': 'DriverLicense',
                                            'park_name': 'Аренда Авто +',
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'qc_date': '2019-02-25',
                                            'qc_id': '21f807b8aeb64c9790ff3854809c45bc',  # noqa: E501 pylint: disable=line-too-long
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2019-02-25T05:35:17Z'
                                            ),
                                            'url': (
                                                '1575887/6a06af11ecac3a1d7.jpg'
                                            ),
                                        },
                                        'similarity': 0.999999999,
                                    },
                                ],
                                'width': 0.3513435721,
                            },
                            {
                                'confidence': 0.99,
                                'height': 0.1342742741,
                                'layer_name': 'super_face_layer',
                                'saas_info': [
                                    {
                                        'metainfo': {
                                            'brightness_level': (
                                                115.39172284095349
                                            ),
                                            'car_id': 'eef410b521d845a681c948d888982c56',  # noqa: E501 pylint: disable=line-too-long
                                            'car_numbers': '0336HX40',
                                            'city': 'Калуга',
                                            'confidence': 0.9,
                                            'db': '3e0920e77b27469e9ac502ee3c4f4f93',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_id': 'a5d2a6ebf1dc4eb8b5d1a98b0994cb09',  # noqa: E501 pylint: disable=line-too-long
                                            'driver_license': '*****31856',
                                            'driver_name': (
                                                'Барабов Андрей Юрьевич'
                                            ),
                                            'exam': 'identity',
                                            'image_type': 'DriverLicense',
                                            'park_name': 'Аренда Авто +',
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'qc_date': '2019-02-25',
                                            'qc_id': '21f807b8aeb64c9790ff3854809c45bc',  # noqa: E501 pylint: disable=line-too-long
                                            'resolution': 'mistakes',
                                            'timestamp': (
                                                '2019-02-25T05:35:17Z'
                                            ),
                                            'url': (
                                                '1575887/6a06af11ecac3a1d7.jpg'
                                            ),
                                        },
                                        'similarity': 0.999999999,
                                    },
                                ],
                                'width': 0.15700639635,
                            },
                        ],
                        'verdict': 'unknown',
                    },
                },
            ],
            5,
        ),
    ],
)
async def test_saas_response(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_qc_invites,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_get_saas_response_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    get_saas_response = _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    _mock_qc_invites(mock_qc_invites)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.saas_features': True,
                'additional_info.face_saas_features': True,
                'additional_info.verdict': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )
    assert len(get_saas_response.calls) == expected_get_saas_response_calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content,expected_invite_request',
    [
        (
            'successful_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 137.07627735443532,
                                        'car_id': (
                                            '478f147a532441d7982af8a6020a2011'
                                        ),
                                        'car_numbers': 'X675MC178',
                                        'city': 'Санкт-Петербург',
                                        'db': (
                                            '3c9ceaabb3024732a250d163c10157f8'
                                        ),
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'driver_name': 'Сидоров Довлет',
                                        'image_type': 'DriverLicense',
                                        'park_name': 'КР Транспорт',
                                        'qc_date': '2018-10-30',
                                        'qc_id': (
                                            'a8f509f1a91141a3b96d51a78495f593'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2018-10-30T11:40:21Z',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                        'url': '1328725/b7a6d1d92301932d.jpg',
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '2948531856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                    },
                                ),
                            },
                            'relevance': '937016308',
                        },
                    ],
                },
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'brightness_level': 115.39172284095349,
                                        'car_id': (
                                            'eef410b521d845a681c948d888982c56'
                                        ),
                                        'car_numbers': '0336HX40',
                                        'city': 'Калуга',
                                        'db': (
                                            '3e0920e77b27469e9ac502ee3c4f4f93'
                                        ),
                                        'driver_id': (
                                            'a5d2a6ebf1dc4eb8b5d1a98b0994cb09'
                                        ),
                                        'driver_license': '2948531856',
                                        'driver_name': (
                                            'Барабов Андрей Юрьевич'
                                        ),
                                        'image_type': 'DriverLicense',
                                        'park_name': 'Аренда Авто +',
                                        'qc_date': '2019-02-25',
                                        'qc_id': (
                                            '21f807b8aeb64c9790ff3854809c45bc'
                                        ),
                                        'exam': 'dkvu',
                                        'resolution': 'mistakes',
                                        'timestamp': '2019-02-25T05:35:17Z',
                                        'url': '1575887/6a06af11ecac3a1d7.jpg',
                                        'pass_id': 'some_pass_id',
                                    },
                                ),
                            },
                            'relevance': '937016308',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
        ),
        (
            'blacklist_different_driver',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0134741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                    },
                                ),
                            },
                            'relevance': '983927688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'blacklist',
                        'blacklist_reason': 'saas_duplicate',
                        'reason': 'saas_duplicate',
                        'verdict_info': {
                            'saas_duplicate': {
                                'driver_license': '1234569214',
                                'driver_id': (
                                    '241d732cca194fffad2380dc0bb9fe77'
                                ),
                                'exam': None,
                                'park_id': None,
                                'pass_id': None,
                                'picture_type': None,
                            },
                        },
                    },
                },
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '0134741979_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': 'Подозрение на дубли по фото: 1234569214.',
                    'identity_type': 'service',
                },
            ],
        ),
        (
            'blacklist_same_driver',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0134741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'driver_id': 'some_driver_id',
                                        'driver_license': '0134741979',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                    },
                                ),
                            },
                            'relevance': '995027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'blacklist',
                        'blacklist_reason': 'saas_duplicate',
                        'reason': 'saas_duplicate',
                        'verdict_info': {
                            'saas_duplicate': {
                                'driver_license': '0134741979',
                                'driver_id': 'some_driver_id',
                                'exam': None,
                                'park_id': None,
                                'pass_id': None,
                                'picture_type': None,
                            },
                        },
                    },
                },
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '0134741979_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': 'Подозрение на дубли по фото: 0134741979.',
                    'identity_type': 'service',
                },
            ],
        ),
        (
            'success_same_driver',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_DKVU_SAAS_THRESHOLDS': {
                    'min_similarity_front': 1.1,
                    'min_similarity_back': 1.1,
                    'min_similarity_selfie': 1.1,
                },
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'driver_id': 'driver_id',
                                        'driver_license': '0134741979',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                    },
                                ),
                            },
                            'relevance': '994927688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
        ),
        (
            'success_same_driver_close_passes',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_DKVU_SAAS_THRESHOLDS': {
                    'min_similarity_front': 1.1,
                    'min_similarity_back': 1.1,
                    'min_similarity_selfie': 1.1,
                },
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2017-12-30T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'driver_id': 'some_driver_id',
                                        'driver_license': '0133741979',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                    },
                                ),
                            },
                            'relevance': '995027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
        ),
        (
            'success_bad_format',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_DUPLICATES_SAAS_BAD_FORMAT_THRESHOLD': (  # noqa: E501 pylint: disable=line-too-long
                    0.1
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_DKVU_SAAS_THRESHOLDS': {
                    'min_similarity_front': 1.1,
                    'min_similarity_back': 1.1,
                    'min_similarity_selfie': 1.1,
                },
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'pass_modified': 1514616129.840873,
                                        'uberdriver_driver_id': None,
                                    },
                                ),
                            },
                            'relevance': '983927688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
        ),
    ],
)
async def test_saas_duplicate(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_invite_request,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert mock.get_requests(get_mock_qc_invites) == expected_invite_request

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.blacklist_reason': True,
                'additional_info.verdict_info': True,
                'additional_info.reason': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content,expected_invite_request,'
    'expected_nirvana_dkvu_set_calls',
    [
        (
            'successful_pass-low_neighbour_confidence',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.2,
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'qc_tags': [],
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'successful_pass-little_neighbour_face_size',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_BANNED_SELFIES_FACE_SIZE_THRESHOLD': (  # noqa: E501 pylint: disable=line-too-long
                    0.5
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.98,
                                        'driver_id': (
                                            '241d732cca194fffad2380dc0bb9fe77'
                                        ),
                                        'driver_license': '1234569214',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'qc_tags': [],
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'successful_pass-same_driver_id',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.98,
                                        'driver_id': 'some_driver_id',
                                        'driver_license': '1234569214',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'qc_tags': [],
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'successful_pass-same_driver_license',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0134741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.98,
                                        'driver_id': 'some_other_driver_id',
                                        'driver_license': '0134741979',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'qc_tags': [],
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'successful_pass-low_similarity',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.98,
                                        'driver_id': 'some_other_driver_id',
                                        'driver_license': '9568746539',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '542027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'blacklist_reason': None,
                        'qc_tags': [],
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'blacklist',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_BLACKLIST_DUPLICATES_SAAS_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий',
                        'last_name': 'Иванов',
                        'number': '0133741979',
                        'nunmber_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2023-06-16',
                    },
                },
            ],
            [
                {
                    'documents': [
                        {
                            'properties': {
                                '_Body': _build_saas_body(
                                    {
                                        'confidence': 0.98,
                                        'driver_id': 'some_other_driver_id',
                                        'driver_license': '9568746539',
                                        'height': 0.5797693729,
                                        'pass_id': '603a74ad9ed31f2bb89c9de4',
                                        'pass_modified': 1514616129.840873,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                        'exam': 'dkvu',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '942027688',
                        },
                    ],
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'blacklist',
                        'blacklist_reason': 'selfie_duplicates',
                        'qc_tags': ['blacklist_selfie_duplicates'],
                        'reason': 'selfie_duplicates',
                        'verdict_info': {
                            'selfie_duplicate': {
                                'driver_license': '9568746539',
                                'driver_id': 'some_other_driver_id',
                                'exam': 'dkvu',
                                'park_id': None,
                                'pass_id': '603a74ad9ed31f2bb89c9de4',
                                'picture_type': 'selfie',
                            },
                        },
                    },
                },
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '0133741979_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': (
                        'Подозрение на заблокированного двойника (по лицу): '
                        '9568746539;some_other_driver_id.'
                    ),
                    'identity_type': 'service',
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'message_keys': [
                            'dkvu_block_reason_blocked_on_another_account',
                        ],
                        'qc_tags': ['blacklist_selfie_duplicates'],
                        'status': 'blacklist',
                    },
                ],
            ],
        ),
    ],
)
async def test_banned_selfie_duplicate(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_invite_request,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert mock.get_requests(get_mock_qc_invites) == expected_invite_request

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.blacklist_reason': True,
                'additional_info.qc_tags': True,
                'additional_info.verdict_info': True,
                'additional_info.reason': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,saas_response,ocr_response,'
    'expected_verdicts_db_content,expected_state_pgsql_content,'
    'expected_nirvana_dkvu_get_calls,expected_nirvana_dkvu_set_calls,',
    [
        (
            'successful_pass_skipped_by_config',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_PART_OF_PASSES_TO_RESOLVE': 0.0,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'skip_verdict_because_of_percent': True,
                        'errors': [],
                    },
                },
            ],
            {'resolve_qc_passes_cursor': '666666666666666666'},
            [
                [('cursor', '0'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
            ],
            [[{'id': 'some_qc_id', 'status': 'unknown'}]],
        ),
        (
            'successful_pass_disabled_resolution',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_RESOLUTION_ENABLED': False,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            [],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'skip_verdict_because_of_percent': False,
                        'errors': [],
                    },
                },
            ],
            {'resolve_qc_passes_cursor': '666666666666666666'},
            [
                [('cursor', '0'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
                [('cursor', '666666666666666666'), ('limit', '100')],
            ],
            [],
        ),
        (
            'disabled_by_config',
            {**DEFAULT_CONFIG, 'AFS_CRON_RESOLVE_QC_PASSES_ENABLED': False},
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {},
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                    },
                },
            ],
            [],
            {'front': [], 'back': []},
            [],
            {'resolve_qc_passes_cursor': '0'},
            [],
            [],
        ),
    ],
)
async def test_config(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        saas_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_state_pgsql_content,
        expected_nirvana_dkvu_get_calls,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    nirvana_dkvu_get = _mock_nirvana_dkvu_get(
        mock_taximeter_xservice, nirvana_dkvu_get_response,
    )
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.skip_verdict_because_of_percent': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )
    assert [
        list(nirvana_dkvu_get.next_call()['request'].query.items())
        for _ in range(nirvana_dkvu_get.times_called)
    ] == expected_nirvana_dkvu_get_calls
    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )
    assert (
        await state.get_all_cron_state(master_pool)
        == expected_state_pgsql_content
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,qc_history,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls,'
    'expected_invite_request',
    [
        (
            'successful_pass_is_valid_by_real_gibdd',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 1.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0134741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0134741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -1,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                -2,
                                1,
                                0,
                                0.014285714285714285,
                                -0.0,
                                -0.0,
                                -0.0,
                                -0.0,
                                0.0,
                                0.0,
                                -0.09090909090909091,
                                0.021739130434782608,
                                0.0,
                                '0134',
                                741979,
                                6853,
                            ],
                            'is_valid_by_real_gibdd': True,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'success',
                        'errors': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
            [],
        ),
        (
            'failed_pass_is_not_valid_by_real_gibdd',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': -0.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0135741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0135741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0135741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0135741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -1,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                -2,
                                1,
                                0,
                                0.014285714285714285,
                                -0.0,
                                -0.0,
                                -0.0,
                                -0.0,
                                0.0,
                                0.0,
                                -0.09090909090909091,
                                0.021739130434782608,
                                0.0,
                                '0135',
                                741979,
                                6853,
                            ],
                            'is_valid_by_real_gibdd': False,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'unknown',
                        'errors': [
                            'driver license is not valid by real gibdd',
                        ],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0135741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
        ),
        (
            'blacklist_pass_with_too_little_score',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 1.1,
                    },
                },
                'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_BLACKLIST_THRESHOLD': (
                    1.1
                ),
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -1,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                -2,
                                1,
                                0,
                                0.014285714285714285,
                                -0.0,
                                -0.0,
                                -0.0,
                                -0.0,
                                0.0,
                                0.0,
                                -0.09090909090909091,
                                0.021739130434782608,
                                0.0,
                                '0133',
                                741979,
                                6853,
                            ],
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'verdict': 'blacklist',
                        'duplicate_by_fio_license_pd_ids': [],
                        'errors': ['quasi-gibdd score is too low'],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': 'quasi_gibdd',
                        'reason': 'quasi_gibdd',
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'blacklist',
                        'message_keys': ['dkvu_blacklist_reason_fake_license'],
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '0133741979_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': (
                        'Есть сомнения в подлинности ВУ. '
                        'Нужно проверить данные на сайте ГИБДД.'
                    ),
                    'identity_type': 'service',
                },
            ],
        ),
        (
            'successful_pass_with_initial_number_fio_duplicate',
            DEFAULT_CONFIG,
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Петр',
                        'last_name': 'Петров',
                        'middle_name': 'Петрович',
                        'number': '1243741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'петр',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'петрович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'петров',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -1,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                -2,
                                1,
                                0,
                                0.014285714285714285,
                                -0.0,
                                -0.0,
                                -0.0,
                                -0.0,
                                0.0,
                                0.0,
                                -0.09090909090909091,
                                0.021739130434782608,
                                0.0,
                                '0133',
                                741979,
                                6853,
                            ],
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [
                            {
                                'dbid_uuid': 'dbid_driver3',
                                'first_name': 'петр',
                                'issue_date': '2019-10-07',
                                'last_name': 'петров',
                                'license_pd_id': '1243741979_pd_id',
                                'middle_name': 'петрович',
                            },
                        ],
                        'verdict': 'success',
                        'errors': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Петр',
                            'issue_date': '2019-10-07',
                            'last_name': 'Петров',
                            'middle_name': 'Петрович',
                            'number': '0133741979',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
            [],
        ),
        (
            'unknown_pass_with_from_blocklist_info',
            DEFAULT_CONFIG_WITHOUT_QUASI_GIBDD,
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'dkvu',
                    'id': 'some_pass_id',
                    'status': 'RESOLVED',
                    'resolution': {
                        'status': 'FAIL',
                        'identity': {
                            'yandex_team': {
                                'yandex_login': 'robot-afs-papers',
                            },
                        },
                    },
                },
            ],
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Петр',
                        'last_name': 'Петров',
                        'middle_name': 'Петрович',
                        'number': '1243741983',
                        'number_pd_id': '1243741983_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'петр',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'петрович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'петров',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '1243741983',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '1243741983',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '1243741983',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [
                            {
                                'dbid_uuid': 'dbid_driver3',
                                'first_name': 'петр',
                                'issue_date': '2019-10-07',
                                'last_name': 'петров',
                                'license_pd_id': '1243741979_pd_id',
                                'middle_name': 'петрович',
                            },
                        ],
                        'verdict': 'unknown',
                        'errors': [],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Петр',
                            'issue_date': '2019-10-07',
                            'last_name': 'Петров',
                            'middle_name': 'Петрович',
                            'number': '1243741983',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
            [],
        ),
        (
            'successful_pass_with_too_different_number_fio_duplicate',
            DEFAULT_CONFIG,
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Сидор',
                        'last_name': 'Сидоров',
                        'middle_name': 'Сидорович',
                        'number': '0133741979',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'сидор',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'сидорович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'сидоров',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': DEFAULT_QUASI_GIBDD_FEATURES,
                        'duplicate_by_fio_license_pd_ids': [
                            {
                                'dbid_uuid': 'dbid_driver4',
                                'first_name': 'сидор',
                                'issue_date': '2019-10-07',
                                'last_name': 'сидоров',
                                'license_pd_id': 'YK3333333333_pd_id',
                                'middle_name': 'сидорович',
                            },
                        ],
                        'verdict': 'success',
                        'errors': [],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Сидор',
                            'issue_date': '2019-10-07',
                            'last_name': 'Сидоров',
                            'middle_name': 'Сидорович',
                            'number': '0133741979',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
            [],
        ),
        (
            'blacklist_pass_is_not_valid_by_real_gibdd',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': -0.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'birthday': '1995-01-01',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '3434343434',
                        'issue_date': '2020-01-01',
                        'expire_date': '2030-01-01',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '3434343434',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '3434343434',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '3434343434',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': False,
                            'last_check_date': '2020-02-15',
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'blacklist',
                        'errors': [
                            'driver license is not valid by real gibdd',
                        ],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': 'real_gibdd',
                        'reason': 'real_gibdd',
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1995-01-01',
                            'expire_date': '2030-01-01',
                            'first_name': 'Василий',
                            'issue_date': '2020-01-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '3434343434',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['dkvu_blacklist_reason_fake_license'],
                        'qc_tags': ['gibdd_check_required'],
                        'status': 'blacklist',
                    },
                ],
            ],
            [
                {
                    'comment': (
                        'Есть сомнения в подлинности ВУ. '
                        'Нужно проверить данные на сайте ГИБДД.'
                    ),
                    'filters': {
                        'license_pd_id': '3434343434_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'identity_type': 'service',
                },
            ],
        ),
        (
            'unknown_pass_last_check_date_close_to_issue_date',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': -0.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'birthday': '1995-01-01',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '4545454545',
                        'issue_date': '2020-01-01',
                        'expire_date': '2030-01-01',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '4545454545',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '4545454545',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '4545454545',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.01.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.01.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': False,
                            'last_check_date': '2020-01-15',
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'unknown',
                        'errors': [
                            'driver license is not valid by real gibdd',
                        ],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1995-01-01',
                            'expire_date': '2030-01-01',
                            'first_name': 'Василий',
                            'issue_date': '2020-01-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '4545454545',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
        ),
        (
            'unknown_pass_issue_date_is_close_to_today_date',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_BLACKLIST_THRESHOLD': (
                    1
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 1.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'birthday': '1995-01-01',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0133741979',
                        'issue_date': '2020-09-01',
                        'expire_date': '2030-09-01',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2020',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2030',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2020',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2030',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -331,
                                -330,
                                -330,
                                -330,
                                -330,
                                -330,
                                -330,
                                -332,
                                -329,
                                -330,
                                4.728571428571429,
                                7.333333333333333,
                                8.91891891891892,
                                10.0,
                                12.222222222222221,
                                -110.0,
                                -27.5,
                                -15.090909090909092,
                                -7.1521739130434785,
                                -6.875,
                                '0133',
                                741979,
                                7183,
                            ],
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'unknown',
                        'errors': ['quasi-gibdd score is too low'],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1995-01-01',
                            'expire_date': '2030-09-01',
                            'first_name': 'Василий',
                            'issue_date': '2020-09-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
        ),
        (
            'unknown_pass_license_is_overdue',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_BLACKLIST_THRESHOLD': (
                    1
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 1.1,
                    },
                },
            },
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'birthday': '1995-01-01',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': 'Иванов',
                        'middle_name': 'Аристархович',
                        'number': '0133741979',
                        'issue_date': '2010-09-01',
                        'expire_date': '2021-09-01',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2010',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2021',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2010',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2021',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2010',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.09.2010',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.09.2021',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2010',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                3322,
                                3323,
                                3323,
                                3323,
                                3323,
                                3323,
                                3323,
                                3321,
                                3324,
                                3323,
                                -47.457142857142856,
                                -73.84444444444445,
                                -89.8108108108108,
                                -100.6969696969697,
                                -123.07407407407408,
                                1107.6666666666667,
                                276.9166666666667,
                                150.95454545454547,
                                72.26086956521739,
                                69.22916666666667,
                                '0133',
                                741979,
                                3530,
                            ],
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [],
                        'verdict': 'unknown',
                        'errors': ['quasi-gibdd score is too low'],
                        'qc_tags': [],
                        'blacklist_reason': None,
                        'reason': None,
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1995-01-01',
                            'expire_date': '2021-09-01',
                            'first_name': 'Василий',
                            'issue_date': '2010-09-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
        ),
    ],
)
async def test_gibdd(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        qc_history,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
        expected_invite_request,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3, qc_history)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.catboost_features': True,
                'additional_info.quasi_gibdd_features': True,
                'additional_info.duplicate_by_fio_license_pd_ids': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.qc_tags': True,
                'additional_info.blacklist_reason': True,
                'additional_info.verdict_info': True,
                'additional_info.reason': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )

    assert mock.get_requests(get_mock_qc_invites) == expected_invite_request


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,qc_history,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls,'
    'expected_invite_request',
    (
        (
            'mistake_verdict_pass_with_fio_duplicate',
            DEFAULT_CONFIG,
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Иван',
                        'last_name': 'Иванов',
                        'middle_name': 'Иванович',
                        'number': 'YK1111111111',
                        'number_pd_id': 'YK1111111111_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'иван',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'иванович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': 'YK1111111111',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': 'YK1111111111',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': 'YK1111111111',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_gibdd_score': None,
                        },
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [
                            {
                                'dbid_uuid': 'dbid_driver2',
                                'first_name': 'иван',
                                'issue_date': '2019-10-07',
                                'last_name': 'иванов',
                                'license_pd_id': 'YK1111111122_pd_id',
                                'middle_name': 'иванович',
                            },
                        ],
                        'verdict': 'mistakes',
                        'errors': [
                            'license number has wrong length',
                            'quasi-gibdd score is not calculated',
                        ],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': None,
                        'reason': 'fio_duplicate',
                        'verdict_info': {'driver_licenses': ['YK1111111122']},
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Иван',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                            'number': 'YK1111111111',
                        },
                        'id': 'some_qc_id',
                        'status': 'mistakes',
                        'message_keys': ['dkvu_blacklist_reason_fake_license'],
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
            [
                {
                    'filters': {
                        'license_pd_id': 'YK1111111111_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': (
                        'Подозрение на двойника по ФИО: YK1111111122. '
                        'Нужно проверить данные на сайте ГИБДД'
                    ),
                    'identity_type': 'service',
                },
            ],
        ),
        (
            'mistake_verdict_with_similar_number_fio_duplicate',
            DEFAULT_CONFIG,
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '1988-01-01',
                        'first_name': 'Петр',
                        'last_name': 'Петров',
                        'middle_name': 'Петрович',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'петр',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'петрович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'петров',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'quasi_gibdd_features': {
                            'features': [
                                -70,
                                -45,
                                -37,
                                -33,
                                -27,
                                3,
                                12,
                                22,
                                46,
                                48,
                                -1,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                -2,
                                1,
                                0,
                                0.014285714285714285,
                                -0.0,
                                -0.0,
                                -0.0,
                                -0.0,
                                0.0,
                                0.0,
                                -0.09090909090909091,
                                0.021739130434782608,
                                0.0,
                                '0133',
                                741979,
                                6853,
                            ],
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                        'duplicate_by_fio_license_pd_ids': [
                            {
                                'dbid_uuid': 'dbid_driver3',
                                'first_name': 'петр',
                                'issue_date': '2019-10-07',
                                'last_name': 'петров',
                                'license_pd_id': '1243741979_pd_id',
                                'middle_name': 'петрович',
                            },
                        ],
                        'verdict': 'mistakes',
                        'errors': [],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': None,
                        'reason': 'fio_duplicate',
                        'verdict_info': {'driver_licenses': ['1243741979']},
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Петр',
                            'issue_date': '2019-10-07',
                            'last_name': 'Петров',
                            'middle_name': 'Петрович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'mistakes',
                        'message_keys': ['dkvu_blacklist_reason_fake_license'],
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '0133741979_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': (
                        'Подозрение на двойника по ФИО: 1243741979. '
                        'Нужно проверить данные на сайте ГИБДД'
                    ),
                    'identity_type': 'service',
                },
            ],
        ),
    ),
)
async def test_mistakes_after_fio_duplicates(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        qc_history,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
        expected_invite_request,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3, qc_history)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.catboost_features': True,
                'additional_info.quasi_gibdd_features': True,
                'additional_info.duplicate_by_fio_license_pd_ids': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.qc_tags': True,
                'additional_info.blacklist_reason': True,
                'additional_info.verdict_info': True,
                'additional_info.reason': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )

    assert mock.get_requests(get_mock_qc_invites) == expected_invite_request


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,qc_history,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls,'
    'expected_invite_request',
    [
        (
            'blacklist_fio_and_birthday_duplicate',
            DEFAULT_CONFIG,
            QC_HISTORY_DEFAULT,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'birthday': '2000-01-01',
                        'first_name': 'Иван',
                        'last_name': 'Иванов',
                        'middle_name': 'Иванович',
                        'number': '1234567890',
                        'number_pd_id': '1234567890_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'иван',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'иванович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '1234567890',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '1234567890',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '1234567890',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'duplicate_by_fio_birthday_pd_ids': [
                            {
                                'birth_date': '2000-01-01',
                                'dbid_uuid': 'dbid_driver8',
                                'first_name': 'иван',
                                'is_blocked': True,
                                'last_name': 'иванов',
                                'license_pd_id': '1234567893_pd_id',
                                'middle_name': 'иванович',
                            },
                        ],
                        'verdict': 'mistakes',
                        'errors': [
                            'ocr field license_expire_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_issue_date on front '
                            'picture is different from the field in '
                            'driver profile',
                            'ocr field license_expire_date on back '
                            'picture is different from the field in '
                            'driver profile',
                            'license issue date on front picture and '
                            'expire date in driver profile are not '
                            'exactly ten years apart',
                            'ocr field license_expire_date is not present '
                            'in front picture',
                            'ocr field license_expire_date is not present '
                            'in back picture',
                            'license issue and expire dates on front '
                            'picture are not exactly ten years apart',
                        ],
                        'qc_tags': ['gibdd_check_required'],
                        'blacklist_reason': None,
                        'reason': 'fio_and_birthday_duplicates',
                        'verdict_info': {
                            'all_duplicates': [
                                {
                                    'birth_date': '2000-01-01',
                                    'dbid_uuid': 'dbid_driver8',
                                    'driver_license': '1234567893',
                                    'first_name': 'иван',
                                    'is_blocked': True,
                                    'last_name': 'иванов',
                                    'middle_name': 'иванович',
                                },
                            ],
                        },
                        'quasi_gibdd_features': {
                            'is_valid_by_real_gibdd': True,
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '2000-01-01',
                            'expire_date': '2029-10-07',
                            'first_name': 'Иван',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                            'number': '1234567890',
                        },
                        'id': 'some_qc_id',
                        'status': 'mistakes',
                        'message_keys': ['dkvu_block_reason_no_quality'],
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
            [
                {
                    'filters': {
                        'license_pd_id': '1234567890_pd_id',
                        'park_id': 'some_db_id',
                    },
                    'comment': (
                        'Подозрение на заблокированного двойника'
                        ' (по ФИО+ДР): 1234567893;driver8'
                    ),
                    'identity_type': 'service',
                },
            ],
        ),
    ],
)
async def test_banned_fio_and_birthday_duplicates(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        qc_history,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
        expected_invite_request,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3, qc_history)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.duplicate_by_fio_birthday_pd_ids': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.qc_tags': True,
                'additional_info.blacklist_reason': True,
                'additional_info.verdict_info': True,
                'additional_info.reason': True,
                'additional_info.quasi_gibdd_features.'
                'is_valid_by_real_gibdd': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )

    assert mock.get_requests(get_mock_qc_invites) == expected_invite_request


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'ocr_issue_date_front,ocr_expire_date_front,ocr_issue_date_back,'
    'ocr_expire_date_back,profile_issue_date,profile_expire_date,'
    'expected_verdict,expected_errors,expected_changes,'
    'expected_profile_issue_date,expected_profile_expire_date,'
    'expected_nirvana_dkvu_set_calls',
    [
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2019-10-07',
            '2029-10-07',
            'success',
            [],
            [
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-10-07',
                    'old_value': None,
                },
            ],
            '2019-10-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '18.11.2020',
            '18.11.2030',
            'whatever',
            '18.11.2020',
            '2020-11-18',
            '2030-11-18',
            'success',
            [],
            [
                {
                    'field_name': 'driver_experience',
                    'new_value': '2020-11-18',
                    'old_value': None,
                },
            ],
            '2020-11-18',
            '2030-11-18',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2020-11-18',
                            'expire_date': '2030-11-18',
                            'first_name': 'Василий',
                            'issue_date': '2020-11-18',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '20.11.2012',
            '20.11.2022',
            'whatever',
            '20.11.2021',
            '2012-11-20',
            '2022-11-20',
            'success',
            [],
            [
                {
                    'field_name': 'driver_experience',
                    'new_value': '2012-11-20',
                    'old_value': None,
                },
            ],
            '2012-11-20',
            '2022-11-20',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2012-11-20',
                            'expire_date': '2022-11-20',
                            'first_name': 'Василий',
                            'issue_date': '2012-11-20',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '03.10.2014',
            '03.10.2024',
            'whatever',
            '03.10.2024',
            '2014-10-03',
            '2014-10-03',
            'success',
            [],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2024-10-03',
                    'old_value': '2014-10-03',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2014-10-03',
                    'old_value': None,
                },
            ],
            '2014-10-03',
            '2024-10-03',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2014-10-03',
                            'expire_date': '2024-10-03',
                            'first_name': 'Василий',
                            'issue_date': '2014-10-03',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '28.02.2015',
            '17.06.2021',
            'whatever',
            '17.06.2025',
            '2015-02-28',
            '2021-06-17',
            'unknown',
            [
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
            ],
            [],
            '2015-02-28',
            '2021-06-17',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2021-06-17',
                            'first_name': 'Василий',
                            'issue_date': '2015-02-28',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '28.04.2020',
            '15.11.2022',
            'whatever',
            '03.11.2022',
            '2020-04-28',
            '2022-11-15',
            'unknown',
            [
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
            ],
            [],
            '2020-04-28',
            '2022-11-15',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2022-11-15',
                            'first_name': 'Василий',
                            'issue_date': '2020-04-28',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '30.08.2013',
            '30.08.2023',
            'whatever',
            '30.08.2023',
            '1999-05-19',
            '2023-08-30',
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2013-08-30',
                    'old_value': '1999-05-19',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2013-08-30',
                    'old_value': None,
                },
            ],
            '2013-08-30',
            '2023-08-30',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2013-08-30',
                            'expire_date': '2023-08-30',
                            'first_name': 'Василий',
                            'issue_date': '2013-08-30',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '22.11.2011',
            '22.11.2021',
            'whatever',
            '22.11.2021',
            '2011-03-10',
            '2021-11-22',
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2011-11-22',
                    'old_value': '2011-03-10',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2011-11-22',
                    'old_value': None,
                },
            ],
            '2011-11-22',
            '2021-11-22',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2011-11-22',
                            'expire_date': '2021-11-22',
                            'first_name': 'Василий',
                            'issue_date': '2011-11-22',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '30.07.2019',
            '30.07.2029',
            'whatever',
            '30.07.2029',
            '2019-07-29',
            '2029-07-29',
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2019-07-30',
                    'old_value': '2019-07-29',
                },
                {
                    'field_name': 'expire_date',
                    'new_value': '2029-07-30',
                    'old_value': '2029-07-29',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-07-30',
                    'old_value': None,
                },
            ],
            '2019-07-30',
            '2029-07-30',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-07-30',
                            'expire_date': '2029-07-30',
                            'first_name': 'Василий',
                            'issue_date': '2019-07-30',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '10.08.2012',
            '10.08.2022',
            'whatever',
            '10.08.2022',
            '2012-08-08',
            '2022-08-08',
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2012-08-10',
                    'old_value': '2012-08-08',
                },
                {
                    'field_name': 'expire_date',
                    'new_value': '2022-08-10',
                    'old_value': '2022-08-08',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2012-08-10',
                    'old_value': None,
                },
            ],
            '2012-08-10',
            '2022-08-10',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2012-08-10',
                            'expire_date': '2022-08-10',
                            'first_name': 'Василий',
                            'issue_date': '2012-08-10',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '20.04.2017',
            '20.04.2027',
            'whatever',
            '20.04.2027',
            '2017-04-19',
            None,
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2017-04-20',
                    'old_value': '2017-04-19',
                },
                {
                    'field_name': 'expire_date',
                    'new_value': '2027-04-20',
                    'old_value': None,
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2017-04-20',
                    'old_value': None,
                },
            ],
            '2017-04-20',
            '2027-04-20',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2017-04-20',
                            'expire_date': '2027-04-20',
                            'first_name': 'Василий',
                            'issue_date': '2017-04-20',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '09.08.2019',
            '18.01.2023',
            'whatever',
            '18.01.2023',
            '2019-08-08',
            '2023-01-17',
            'unknown',
            [
                'license issue date on front picture and '
                'expire date in driver profile are not '
                'exactly ten years apart',
            ],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2023-01-18',
                    'old_value': '2023-01-17',
                },
            ],
            '2019-08-08',
            '2023-01-18',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2023-01-18',
                            'first_name': 'Василий',
                            'issue_date': '2019-08-08',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '10.05.2018',
            '10.05.2028',
            'whatever',
            '',
            '2018-05-09',
            '2028-05-09',
            'unknown',
            [
                'ocr field license_expire_date on front '
                'picture is different from the field in '
                'driver profile',
                'ocr field license_issue_date on front '
                'picture is different from the field in '
                'driver profile',
                'ocr field license_expire_date on back '
                'picture is different from the field in '
                'driver profile',
                'license issue date on front picture and '
                'expire date in driver profile are not '
                'exactly ten years apart',
                'ocr field license_expire_date on front '
                'picture is different from the field on back '
                'picture',
                'ocr field license_expire_date on front '
                'picture is more than ten years greater than '
                'the field license_issue_date in driver '
                'profile',
            ],
            [],
            '2018-05-09',
            '2028-05-09',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2028-05-09',
                            'first_name': 'Василий',
                            'issue_date': '2018-05-09',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '25.11.2015',
            '25.11.2025',
            'whatever',
            '15.11.2025',
            '2005-11-25',
            '2025-11-25',
            'unknown',
            [
                'ocr field license_issue_date on front '
                'picture is different from the field in '
                'driver profile',
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
                'ocr field license_expire_date on back '
                'picture is different from the field in '
                'driver profile',
            ],
            [],
            '2005-11-25',
            '2025-11-25',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2025-11-25',
                            'first_name': 'Василий',
                            'issue_date': '2005-11-25',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '30.05.2010',
            '30.05.2030',
            'whatever',
            '30.05.2020',
            '2010-06-08',
            '2030-05-30',
            'unknown',
            [
                'ocr field license_issue_date on front '
                'picture is different from the field in '
                'driver profile',
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
                'ocr field license_expire_date on back '
                'picture is different from the field in '
                'driver profile',
                'license issue date on front picture and '
                'expire date in driver profile are not '
                'exactly ten years apart',
            ],
            [],
            '2010-06-08',
            '2030-05-30',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2030-05-30',
                            'first_name': 'Василий',
                            'issue_date': '2010-06-08',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '04.11.2021',
            '2019-10-07',
            '2029-10-07',
            'success',
            [],
            [
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-10-07',
                    'old_value': None,
                },
            ],
            '2019-10-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2019-10-07',
            '2021-04-11',
            'success',
            [],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2029-10-07',
                    'old_value': '2021-04-11',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-10-07',
                    'old_value': None,
                },
            ],
            '2019-10-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '04.11.2021',
            '2019-05-01',
            '2029-10-07',
            'unknown',
            [
                'ocr field license_issue_date on front '
                'picture is different from the field in '
                'driver profile',
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
                'ocr field license_expire_date on back '
                'picture is different from the field in '
                'driver profile',
            ],
            [],
            '2019-05-01',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-05-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '01.05.2019',
            '07.10.2029',
            '01.05.2019',
            '04.11.2021',
            '2019-05-01',
            '2029-10-07',
            'unknown',
            [
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
            ],
            [],
            '2019-05-01',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-05-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '01.05.2019',
            '07.10.2029',
            '01.05.2019',
            '04.11.2021',
            '2019-05-01',
            '2029-10-07',
            'unknown',
            [
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
            ],
            [],
            '2019-05-01',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-05-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2011-11-07',
            '2029-10-07',
            'success',
            [],
            [
                {
                    'field_name': 'issue_date',
                    'new_value': '2019-10-07',
                    'old_value': '2011-11-07',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-10-07',
                    'old_value': None,
                },
            ],
            '2019-10-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '01.05.2029',
            '2011-11-07',
            '2029-10-07',
            'unknown',
            [
                'ocr field license_issue_date on front '
                'picture is different from the field in '
                'driver profile',
                'license issue and expire dates in driver '
                'profile are not exactly ten years apart',
                'ocr field license_expire_date on back '
                'picture is different from the field in '
                'driver profile',
            ],
            [],
            '2011-11-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2011-11-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '01.05.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2011-11-07',
            '2029-10-07',
            'unknown',
            [
                'license issue date on front picture and '
                'expire date in driver profile are not '
                'exactly ten years apart',
            ],
            [],
            '2011-11-07',
            '2029-10-07',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2011-11-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '15.02.2020',
            '28.10.2021',
            'whatever',
            '28.10.2021',
            '2020-02-15',
            '2030-02-15',
            'success',
            [],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2021-10-28',
                    'old_value': '2030-02-15',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2020-02-15',
                    'old_value': None,
                },
            ],
            '2020-02-15',
            '2021-10-28',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2020-02-15',
                            'expire_date': '2021-10-28',
                            'first_name': 'Василий',
                            'issue_date': '2020-02-15',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '18.09.2020',
            '17.12.2023',
            'whatever',
            '17.12.2023',
            '2020-09-18',
            '2030-09-18',
            'success',
            [],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2023-12-17',
                    'old_value': '2030-09-18',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2020-09-18',
                    'old_value': None,
                },
            ],
            '2020-09-18',
            '2023-12-17',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2020-09-18',
                            'expire_date': '2023-12-17',
                            'first_name': 'Василий',
                            'issue_date': '2020-09-18',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '05.10.2019',
            '05.10.2029',
            'whatever',
            '05.10.2029',
            '2019-10-05',
            '2029-12-05',
            'success',
            [],
            [
                {
                    'field_name': 'expire_date',
                    'new_value': '2029-10-05',
                    'old_value': '2029-12-05',
                },
                {
                    'field_name': 'driver_experience',
                    'new_value': '2019-10-05',
                    'old_value': None,
                },
            ],
            '2019-10-05',
            '2029-10-05',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-05',
                            'expire_date': '2029-10-05',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-05',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '09.12.2020',
            '09.12.2020',
            'whatever',
            '09.12.2020',
            '2020-12-09',
            '2030-12-09',
            'unknown',
            [
                'ocr field license_expire_date on front '
                'picture is different from the field in '
                'driver profile',
                'ocr field license_expire_date on front '
                'picture is less than or equal to the field '
                'license_issue_date in driver profile',
            ],
            [],
            '2020-12-09',
            '2030-12-09',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2030-12-09',
                            'first_name': 'Василий',
                            'issue_date': '2020-12-09',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '16.12.2010',
            '16.12.2030',
            'whatever',
            '16.12.2030',
            '2010-12-16',
            '2020-12-16',
            'unknown',
            [
                'ocr field license_expire_date on front '
                'picture is different from the field in '
                'driver profile',
                'ocr field license_expire_date on front '
                'picture is more than ten years greater than '
                'the field license_issue_date in driver '
                'profile',
            ],
            [],
            '2010-12-16',
            '2020-12-16',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2020-12-16',
                            'first_name': 'Василий',
                            'issue_date': '2010-12-16',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '08.02.2017',
            '03.02.2027',
            'whatever',
            '08.02.2027',
            '2017-02-08',
            '2027-02-08',
            'unknown',
            [
                'ocr field license_expire_date on front '
                'picture is different from the field in '
                'driver profile',
                'ocr field license_expire_date on front '
                'picture is different from the field on back '
                'picture',
            ],
            [],
            '2017-02-08',
            '2027-02-08',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'expire_date': '2027-02-08',
                            'first_name': 'Василий',
                            'issue_date': '2017-02-08',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_dates_changing(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        ocr_issue_date_front,
        ocr_expire_date_front,
        ocr_issue_date_back,
        ocr_expire_date_back,
        profile_issue_date,
        profile_expire_date,
        expected_verdict,
        expected_errors,
        expected_changes,
        expected_profile_issue_date,
        expected_profile_expire_date,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(DEFAULT_CONFIG)
    nirvana_dkvu_get_response = [
        {
            'id': 'some_qc_id',
            'pending_date': '2020-01-01T00:00:00',
            'photos': {
                'DriverLicense': 'http://example.com/file.jpg',
                'DriverLicenseBack': 'http://example.com/file.jpg',
                'Selfie': 'http://example.com/file.jpg',
            },
            'data': {
                'pass_id': 'some_pass_id',
                'db_id': 'some_db_id',
                'driver_id': 'some_driver_id',
                'birthday': '1988-01-01',
                'first_name': 'Василий',
                'last_name': 'Иванов',
                'middle_name': 'Аристархович',
                'number': '0133741979',
                'number_pd_id': '0133741979_pd_id',
                'country': 'rus',
            },
        },
    ]
    if profile_issue_date is not None:
        nirvana_dkvu_get_response[0]['data']['issue_date'] = profile_issue_date
    if profile_expire_date is not None:
        nirvana_dkvu_get_response[0]['data'][
            'expire_date'
        ] = profile_expire_date
    ocr_response = {
        'front': [
            {'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'},
            {
                'Confidence': 0.8884754777,
                'Type': 'middle_name',
                'Text': 'аристархович',
            },
            {'Confidence': 0.8884754777, 'Type': 'surname', 'Text': 'иванов'},
            {
                'Confidence': 0.8942831159,
                'Type': 'number',
                'Text': '0133741979',
            },
            {
                'Confidence': 0.7566020088,
                'Type': 'issue_date',
                'Text': ocr_issue_date_front,
            },
            {
                'Confidence': 0.8986020088,
                'Type': 'expiration_date',
                'Text': ocr_expire_date_front,
            },
        ],
        'back': [
            {
                'Confidence': 0.4252831159,
                'Type': 'number',
                'Text': '0133741979',
            },
            {
                'Confidence': 0.2956020088,
                'Type': 'issue_date',
                'Text': ocr_issue_date_back,
            },
            {
                'Confidence': 0.7656020088,
                'Type': 'expiration_date',
                'Text': ocr_expire_date_back,
            },
        ],
        'full': [],
    }
    expected_verdicts_db_content = [
        {
            'additional_info': {
                'qc_pass': {
                    'expire_date': expected_profile_expire_date,
                    'issue_date': expected_profile_issue_date,
                },
                'changes': expected_changes,
                'verdict': expected_verdict,
                'errors': expected_errors,
            },
        },
    ]
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.expire_date': True,
                'additional_info.qc_pass.issue_date': True,
                'additional_info.changes': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'ocr_license_number_front,ocr_license_number_back,profile_license_number,'
    'expected_verdict,expected_errors,expected_changes,'
    'expected_profile_license_number,expected_nirvana_dkvu_set_calls',
    [
        (
            '0133741979',
            '0133741979',
            '0133741979',
            'success',
            [],
            [],
            '*****41979',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            '0134741979',
            '0134741979',
            '0133741979',
            'success',
            [],
            [
                {
                    'field_name': 'license_number_pd_id',
                    'new_value': '0134741979_pd_id',
                    'old_value': '0133741979_pd_id',
                },
            ],
            '*****41979',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0134741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
async def test_license_changing(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        ocr_license_number_front,
        ocr_license_number_back,
        profile_license_number,
        expected_verdict,
        expected_errors,
        expected_changes,
        expected_profile_license_number,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(DEFAULT_CONFIG)
    nirvana_dkvu_get_response = [
        {
            'id': 'some_qc_id',
            'pending_date': '2020-01-01T00:00:00',
            'photos': {
                'DriverLicense': 'http://example.com/file.jpg',
                'DriverLicenseBack': 'http://example.com/file.jpg',
                'Selfie': 'http://example.com/file.jpg',
            },
            'data': {
                'pass_id': 'some_pass_id',
                'db_id': 'some_db_id',
                'driver_id': 'some_driver_id',
                'birthday': '1988-01-01',
                'first_name': 'Василий',
                'last_name': 'Иванов',
                'middle_name': 'Аристархович',
                'issue_date': '2019-10-07',
                'expire_date': '2029-10-07',
                'country': 'rus',
                'driver_experience': '2019-10-07',
            },
        },
    ]
    if profile_license_number is not None:
        nirvana_dkvu_get_response[0]['data']['number'] = profile_license_number
        nirvana_dkvu_get_response[0]['data']['number_pd_id'] = (
            nirvana_dkvu_get_response[0]['data']['number'] + '_pd_id'
        )

    ocr_response = {
        'front': [
            {'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'},
            {
                'Confidence': 0.8884754777,
                'Type': 'middle_name',
                'Text': 'аристархович',
            },
            {'Confidence': 0.8884754777, 'Type': 'surname', 'Text': 'иванов'},
            {
                'Confidence': 0.8942831159,
                'Type': 'number',
                'Text': ocr_license_number_front,
            },
            {
                'Confidence': 0.7566020088,
                'Type': 'issue_date',
                'Text': '07.10.2019',
            },
            {
                'Confidence': 0.8986020088,
                'Type': 'expiration_date',
                'Text': '07.10.2029',
            },
        ],
        'back': [
            {
                'Confidence': 0.4252831159,
                'Type': 'number',
                'Text': ocr_license_number_back,
            },
            {
                'Confidence': 0.2956020088,
                'Type': 'issue_date',
                'Text': '07.10.2019',
            },
            {
                'Confidence': 0.7656020088,
                'Type': 'expiration_date',
                'Text': '07.10.2029',
            },
            {
                'Confidence': 0.8817818761,
                'Type': 'experience_from',
                'Text': '2011',
            },
        ],
        'full': [],
    }
    expected_verdicts_db_content = [
        {
            'additional_info': {
                'qc_pass': {'number': expected_profile_license_number},
                'changes': expected_changes,
                'verdict': expected_verdict,
                'skip_verdict_because_of_percent': False,
                'errors': expected_errors,
            },
        },
    ]
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.number': True,
                'additional_info.changes': True,
                'additional_info.verdict': True,
                'additional_info.skip_verdict_because_of_percent': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'ocr_middlename,profile_middlename,'
    'expected_verdict,expected_errors,expected_changes,'
    'expected_profile_middlename,expected_nirvana_dkvu_set_calls',
    [
        (
            'Петрович',
            '',
            'success',
            [],
            [
                {
                    'field_name': 'middlename',
                    'new_value': 'Петрович',
                    'old_value': '',
                },
            ],
            'Петрович',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Петрович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            ' ПЕТРОВИЧ ',
            ' ',
            'success',
            [],
            [
                {
                    'field_name': 'middlename',
                    'new_value': 'Петрович',
                    'old_value': ' ',
                },
            ],
            'Петрович',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Петрович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'Петрович',
            'Аристархович',
            'unknown',
            [
                'ocr field middlename on front picture is '
                'different from the field in driver profile',
            ],
            [],
            'Аристархович',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '',
            None,
            'unknown',
            ['ocr field middlename is not present in front picture'],
            [{'field_name': 'middlename', 'new_value': '', 'old_value': None}],
            '',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': '',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '-',
            '',
            'unknown',
            ['ocr field middlename is not present in front picture'],
            [],
            '',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': '',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            None,
            None,
            'unknown',
            [
                'ocr field middlename is missing from ocr response '
                'for front picture',
            ],
            [],
            None,
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            None,
            'Аристархович',
            'unknown',
            [
                'ocr field middlename is missing from ocr response '
                'for front picture',
            ],
            [],
            'Аристархович',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            '-',
            'Аристархович',
            'unknown',
            ['ocr field middlename is not present in front picture'],
            [],
            'Аристархович',
            [
                [
                    {
                        'data': {
                            'birthday': '1988-01-01',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_middlename_changing(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        ocr_middlename,
        profile_middlename,
        expected_verdict,
        expected_errors,
        expected_changes,
        expected_profile_middlename,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(DEFAULT_CONFIG)
    nirvana_dkvu_get_response = [
        {
            'id': 'some_qc_id',
            'pending_date': '2020-01-01T00:00:00',
            'photos': {
                'DriverLicense': 'http://example.com/file.jpg',
                'DriverLicenseBack': 'http://example.com/file.jpg',
                'Selfie': 'http://example.com/file.jpg',
            },
            'data': {
                'pass_id': 'some_pass_id',
                'db_id': 'some_db_id',
                'driver_id': 'some_driver_id',
                'birthday': '1988-01-01',
                'first_name': 'Василий',
                'last_name': 'Иванов',
                'number': '0133741979',
                'number_pd_id': '0133741979_pd_id',
                'issue_date': '2019-10-07',
                'expire_date': '2029-10-07',
                'country': 'rus',
                'driver_experience': '2019-10-07',
            },
        },
    ]
    if profile_middlename is not None:
        nirvana_dkvu_get_response[0]['data'][
            'middle_name'
        ] = profile_middlename

    ocr_response = {
        'front': [
            {'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'},
            {'Confidence': 0.8884754777, 'Type': 'surname', 'Text': 'иванов'},
            {
                'Confidence': 0.8942831159,
                'Type': 'number',
                'Text': '0133741979',
            },
            {
                'Confidence': 0.7566020088,
                'Type': 'issue_date',
                'Text': '07.10.2019',
            },
            {
                'Confidence': 0.8986020088,
                'Type': 'expiration_date',
                'Text': '07.10.2029',
            },
        ],
        'back': [
            {
                'Confidence': 0.4252831159,
                'Type': 'number',
                'Text': '0133741979',
            },
            {
                'Confidence': 0.2956020088,
                'Type': 'issue_date',
                'Text': '07.10.2019',
            },
            {
                'Confidence': 0.7656020088,
                'Type': 'expiration_date',
                'Text': '07.10.2029',
            },
            {
                'Confidence': 0.8817818761,
                'Type': 'experience_from',
                'Text': '2011',
            },
        ],
        'full': [],
    }

    if ocr_middlename is not None:
        ocr_response['front'].append(
            {
                'Confidence': 0.8884754777,
                'Type': 'middle_name',
                'Text': ocr_middlename,
            },
        )
    expected_verdicts_db_content = [
        {
            'additional_info': {
                'qc_pass': {'middle_name': expected_profile_middlename},
                'changes': expected_changes,
                'verdict': expected_verdict,
                'skip_verdict_because_of_percent': False,
                'errors': expected_errors,
            },
        },
    ]
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.middle_name': True,
                'additional_info.changes': True,
                'additional_info.verdict': True,
                'additional_info.skip_verdict_because_of_percent': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-03-11T00:00:00.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'unknown pass without middle_name',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'errors': [
                            'ocr field middlename is missing from ocr '
                            'response for front picture',
                        ],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_without_middle_name_in_ocr(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'ocr_issue_date_front,ocr_expire_date_front,ocr_issue_date_back,'
    'ocr_expire_date_back,ocr_experience_from,ocr_experience_from_confidence,'
    'profile_issue_date,profile_expire_date,profile_driver_experience,'
    'expected_probable_experience_date,expected_driver_experience',
    [
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2019',
            0.9,
            '2019-10-07',
            '2029-10-07',
            '1917-10-03',
            '2019-10-07',
            '1917-10-03',
        ),
        (
            '07.10.2019',
            '07.10.2029',
            '07.10.2019',
            '07.10.2029',
            '2019',
            0.9,
            '2019-10-07',
            '2029-10-07',
            None,
            '2019-10-07',
            '2019-10-07',
        ),
        (
            '07.10.2019',
            '07.10.2029',
            None,
            '07.10.2029',
            '2011',
            0.4,
            '2019-10-07',
            '2029-10-07',
            None,
            '2011-01-01',
            '2019-10-07',
        ),
        (
            '07.10.2019',
            '07.10.2029',
            None,
            '07.10.2029',
            '2011',
            0.9,
            '2019-10-07',
            '2029-10-07',
            None,
            '2011-01-01',
            '2011-01-01',
        ),
        (
            '07.10.2019',
            '07.10.2029',
            None,
            '07.10.2029',
            '2019',
            0.9,
            '2019-10-07',
            '2029-10-07',
            None,
            '2019-10-07',
            '2019-10-07',
        ),
        (
            '07.10.1917',
            '07.10.2027',
            '07.10.1917',
            '07.10.2027',
            '1917',
            0.9,
            '1917-10-07',
            '2027-10-07',
            None,
            None,
            '1917-10-07',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            None,
            '07.10.2030',
            '2010',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            '2010-01-01',
            '2010-01-01',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            '07.10.2010',
            '07.10.2030',
            '2010',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            None,
            '2020-10-07',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            '07.10.2011',
            '07.10.2030',
            '2011',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            '2011-10-07',
            '2011-10-07',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            None,
            '07.10.2030',
            '2011',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            '2011-01-01',
            '2011-01-01',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            '07.10.2020',
            '07.10.2030',
            '2000',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            None,
            '2020-10-07',
        ),
        (
            '07.10.2020',
            '07.10.2030',
            '07.10.2030',
            '07.10.2030',
            '2030',
            0.9,
            '2020-10-07',
            '2030-10-07',
            None,
            None,
            '2020-10-07',
        ),
    ],
)
async def test_driver_experience(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        ocr_issue_date_front,
        ocr_expire_date_front,
        ocr_issue_date_back,
        ocr_expire_date_back,
        ocr_experience_from,
        ocr_experience_from_confidence,
        profile_issue_date,
        profile_expire_date,
        profile_driver_experience,
        expected_probable_experience_date,
        expected_driver_experience,
):
    taxi_config.set_values(DEFAULT_CONFIG)
    nirvana_dkvu_get_response = [
        {
            'id': 'some_qc_id',
            'pending_date': '2020-01-01T00:00:00',
            'photos': {
                'DriverLicense': 'http://example.com/file.jpg',
                'DriverLicenseBack': 'http://example.com/file.jpg',
                'Selfie': 'http://example.com/file.jpg',
            },
            'data': {
                'pass_id': 'some_pass_id',
                'db_id': 'some_db_id',
                'driver_id': 'some_driver_id',
                'first_name': 'Василий  ',
                'last_name': 'Иванов',
                'middle_name': 'Аристархович',
                'number': '0133741979',
                'birthday': '1998-01-01',
            },
        },
    ]
    if profile_issue_date is not None:
        nirvana_dkvu_get_response[0]['data']['issue_date'] = profile_issue_date
    if profile_expire_date is not None:
        nirvana_dkvu_get_response[0]['data'][
            'expire_date'
        ] = profile_expire_date
    if profile_driver_experience is not None:
        nirvana_dkvu_get_response[0]['data'][
            'driver_experience'
        ] = profile_driver_experience

    ocr_response = {
        'front': [
            {'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'},
            {'Confidence': 0.8884754777, 'Type': 'surname', 'Text': 'иванов'},
            {
                'Confidence': 0.8884754777,
                'Type': 'birth_date',
                'Text': '01.01.1998',
            },
            {
                'Confidence': 0.8884754777,
                'Type': 'middle_name',
                'Text': 'аристархович',
            },
            {
                'Confidence': 0.8942831159,
                'Type': 'number',
                'Text': '0133741979',
            },
        ],
        'back': [
            {
                'Confidence': 0.4252831159,
                'Type': 'number',
                'Text': '0133741979',
            },
        ],
        'full': [],
    }

    if ocr_issue_date_front is not None:
        ocr_response['front'].append(
            {
                'Confidence': 0.7566020088,
                'Type': 'issue_date',
                'Text': ocr_issue_date_front,
            },
        )

    if ocr_expire_date_front is not None:
        ocr_response['front'].append(
            {
                'Confidence': 0.8986020088,
                'Type': 'expiration_date',
                'Text': ocr_expire_date_front,
            },
        )

    if ocr_issue_date_back is not None:
        ocr_response['back'].append(
            {
                'Confidence': 0.8884754777,
                'Type': 'issue_date',
                'Text': ocr_issue_date_back,
            },
        )

    if ocr_expire_date_back is not None:
        ocr_response['back'].append(
            {
                'Confidence': 0.7656020088,
                'Type': 'expiration_date',
                'Text': ocr_expire_date_back,
            },
        )

    if ocr_experience_from is not None:
        ocr_response['back'].append(
            {
                'Confidence': ocr_experience_from_confidence,
                'Type': 'experience_from',
                'Text': ocr_experience_from,
            },
        )

    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert await db.antifraud_iron_lady_verdicts.find(
        {}, {'_id': False, 'additional_info.errors': True},
    ).to_list(None) == [{'additional_info': {'errors': []}}]

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.ocr_features.probable_experience_date': True,
            },
        ).to_list(None)
        == [
            {
                'additional_info': {
                    'ocr_features': {
                        'probable_experience_date': (
                            expected_probable_experience_date
                        ),
                    },
                },
            },
        ]
    )

    assert [
        x.get('data', {}).get('driver_experience')
        for request in mock.get_requests(nirvana_dkvu_set)
        for x in request
    ] == [expected_driver_experience]


@pytest.mark.now('2022-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'successful pass expired license',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'False',
                        'was_blocked': 'False',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '01.03.2012',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '01.03.2022',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.03.2012',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.03.2022',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '01.03.2012',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '01.03.2022',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'db_id': 'some_db_id',
                            'driver_experience': '2012-03-01',
                            'driver_id': 'some_driver_id',
                            'expire_date': '2022-03-01',
                            'first_name': 'Василий',
                            'issue_date': '2012-03-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'success',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2012-03-01',
                            'expire_date': '2022-03-01',
                            'first_name': 'Василий',
                            'issue_date': '2012-03-01',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
async def test_license_expire_date(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass': True,
                'additional_info.verdict': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'ocr_response_front,ocr_response_back,ocr_response_full,'
    'catboost_thresholds,profile_license_number,config_enabled,'
    'qc_history,'
    'expected_verdict,expected_status,expected_message_keys_log,'
    'expected_message_keys_request,expected_reason,expected_verdict_info',
    [
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'is_back_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '0133741979',
                },
            ],
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '1111111111',
                },
            ],
            [],
            {
                'is_front_bad_format_with_rotations_v9': 0.0,
                'is_back_bad_format_with_rotations_v9': 0.0,
            },
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '0133741979',
                },
            ],
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '0133741979',
                },
            ],
            [],
            {'is_selfie_bad_format': 0.0},
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_license_quality'],
            ['dkvu_block_reason_license_quality'],
            'photo_quality',
            None,
        ),
        (
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '1111111111',
                },
            ],
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '2222222222',
                },
            ],
            [],
            {
                'is_front_bad_format_with_rotations_v9': 0.0,
                'is_back_bad_format_with_rotations_v9': 0.0,
            },
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '0133741979',
                },
            ],
            [
                {
                    'Confidence': 0.8776331544,
                    'Type': 'name',
                    'Text': 'василий',
                },
                {
                    'Confidence': 0.8884754777,
                    'Type': 'surname',
                    'Text': 'иванов',
                },
                {
                    'Confidence': 0.8942831159,
                    'Type': 'number',
                    'Text': '0133741979',
                },
            ],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            {},
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'photo_from_screen_with_rotations': 0.0},
            '0133741979',
            True,
            None,
            'unknown',
            'unknown',
            [],
            None,
            None,
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {},
            'LM0573840',
            True,
            None,
            'unknown',
            'unknown',
            [],
            None,
            None,
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {
                'is_front_bad_format_with_rotations_v9': 0.0,
                'is_back_bad_format_with_rotations_v9': 0.0,
            },
            '0133741979',
            False,
            None,
            'mistakes',
            'unknown',
            ['dkvu_block_reason_no_quality'],
            None,
            'photo_quality',
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            [],
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'dkvu',
                    'id': 'some_pass_id',
                    'status': 'NEW',
                },
            ],
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
        (
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [{'Confidence': 0.8776331544, 'Type': 'name', 'Text': 'василий'}],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'dkvu',
                    'id': 'some_pass_id',
                    'status': 'NEW',
                    'resolution': {
                        'status': 'FAIL',
                        'identity': {
                            'yandex_team': {
                                'yandex_login': 'robot-afs-papers',
                            },
                        },
                    },
                },
            ],
            'unknown',
            'unknown',
            [],
            None,
            None,
            None,
        ),
        (
            None,
            [],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            None,
            'unknown',
            'unknown',
            [],
            None,
            None,
            None,
        ),
        (
            [],
            None,
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            None,
            'unknown',
            'unknown',
            [],
            None,
            None,
            None,
        ),
        (
            [],
            [],
            [],
            {'is_front_bad_format_with_rotations_v9': 0.0},
            '0133741979',
            True,
            None,
            'mistakes',
            'mistakes',
            ['dkvu_block_reason_no_quality'],
            ['dkvu_block_reason_no_quality'],
            'photo_quality',
            None,
        ),
    ],
)
async def test_mistakes_status(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        ocr_response_front,
        ocr_response_back,
        ocr_response_full,
        catboost_thresholds,
        profile_license_number,
        config_enabled,
        qc_history,
        expected_verdict,
        expected_status,
        expected_message_keys_log,
        expected_message_keys_request,
        expected_reason,
        expected_verdict_info,
):
    config = copy.deepcopy(DEFAULT_CONFIG)
    config[
        'AFS_CRON_RESOLVE_QC_PASSES_MISTAKES_STATUS_ENABLED'
    ] = config_enabled
    for formula, threshold in catboost_thresholds.items():
        config['AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'][formula][
            'threshold'
        ] = threshold
    taxi_config.set_values(config)
    nirvana_dkvu_get_response = [
        {
            'id': 'some_qc_id',
            'pending_date': '2020-01-01T00:00:00',
            'photos': {
                'DriverLicense': 'http://example.com/file.jpg',
                'DriverLicenseBack': 'http://example.com/file.jpg',
                'Selfie': 'http://example.com/file.jpg',
            },
            'data': {
                'pass_id': 'some_pass_id',
                'db_id': 'some_db_id',
                'driver_id': 'some_driver_id',
                'first_name': 'Василий',
                'last_name': 'Иванов',
                'number': profile_license_number,
                'number_pd_id': profile_license_number + '_pd_id',
                'issue_date': '2019-10-07',
                'expire_date': '2029-10-07',
            },
        },
    ]

    ocr_response = {
        'front': ocr_response_front,
        'back': ocr_response_back,
        'full': ocr_response_full,
    }

    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3, qc_history)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.message_keys': True,
                'additional_info.reason': True,
                'additional_info.verdict_info': True,
            },
        ).to_list(None)
        == [
            {
                'additional_info': {
                    'verdict': expected_verdict,
                    'message_keys': expected_message_keys_log,
                    'reason': expected_reason,
                    'verdict_info': expected_verdict_info,
                },
            },
        ]
    )

    nirvana_dkvu_set_calls = mock.get_requests(nirvana_dkvu_set)

    assert [
        x.get('status') for request in nirvana_dkvu_set_calls for x in request
    ] == [expected_status]

    assert [
        x.get('message_keys')
        for request in nirvana_dkvu_set_calls
        for x in request
    ] == [expected_message_keys_request]


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'successful_invited_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'True',
                        'was_blocked': 'False',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'db_id': 'some_db_id',
                            'driver_experience': '2019-10-07',
                            'driver_id': 'some_driver_id',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': True,
                            'was_blocked': False,
                        },
                        'verdict': 'success',
                        'invite_dkvu_request': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'successful_blocked_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'False',
                        'was_blocked': 'True',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'db_id': 'some_db_id',
                            'driver_experience': '2019-10-07',
                            'driver_id': 'some_driver_id',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': True,
                        },
                        'verdict': 'success',
                        'invite_dkvu_request': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'blacklisted_blocked_pass',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['quasi_gibdd'],
                        'threshold': 1.1,
                    },
                },
                'AFS_CRON_RESOLVE_QC_PASSES_QUASI_GIBDD_BLACKLIST_THRESHOLD': (
                    1.1
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'False',
                        'was_blocked': 'True',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'birthday': '1993-08-24',
                            'country': None,
                            'db_id': 'some_db_id',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '*****41979',
                            'number_pd_id': '0133741979_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'is_invited': False,
                            'was_blocked': True,
                        },
                        'verdict': 'blacklist',
                        'invite_dkvu_request': {
                            'comment_for_assessors': (
                                'Есть сомнения в подлинности ВУ. '
                                'Нужно проверить данные на '
                                'сайте ГИБДД.'
                            ),
                            'license_pd_id': '0133741979_pd_id',
                            'park_id': 'some_db_id',
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                        'message_keys': ['dkvu_blacklist_reason_fake_license'],
                        'qc_tags': ['gibdd_check_required'],
                    },
                ],
            ],
        ),
    ],
)
async def test_invited_and_blocked(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    get_mock_qc_invites = _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass': True,
                'additional_info.verdict': True,
                'additional_info.invite_dkvu_request': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )

    assert mock.get_requests(get_mock_qc_invites) == []


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,history_features,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'success resolution',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'True',
                        'was_blocked': 'False',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'dkvu',
                    'id': 'some_pass_id',
                    'status': 'NEW',
                    'reason': {'invite_id': 'some_invite_id'},
                },
            ],
            [
                {
                    'additional_info': {
                        'qc_pass': {'is_invited': True},
                        'verdict': 'success',
                        'invite_comment': (
                            '[allow auto verdict] Регулярный вызов'
                        ),
                        'history_features': {
                            'by_driver_id': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'invite_id': 'some_invite_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                            ],
                            'by_driver_license': [
                                {
                                    'entity_id': 'some_entity_id',
                                    'invite_id': 'some_invite_id',
                                    'modified': '2020-01-01T00:00:00',
                                    'pass_id': 'some_pass_id',
                                },
                            ],
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
async def test_invite_comment(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        ocr_response,
        history_features,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3, history_features)
    _mock_blocklist_find_info(mock_blocklist)
    _mock_qc_invites_info(mock_qc_invites)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.is_invited': True,
                'additional_info.history_features': True,
                'additional_info.verdict': True,
                'additional_info.invite_comment': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.parametrize(
    'comment,config',
    [
        (
            'testing_authentification',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'quasi_gibdd': {'sandbox_id': 70707070, 'threshold': 0.1},
                },
            },
        ),
    ],
)
async def test_authentication(
        mock_taximeter_xservice,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        comment,
        config,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, [])
    get_classifier_model, get_regressor_model = _mock_get_model(
        patch_aiohttp_session, response_mock,
    )

    @patch_aiohttp_session('http://proxy.sandbox.yandex-team.ru/', 'GET')
    def get_sandbox_model(method, url, **kwargs):
        b64_model = """
Q0JNMZABAAAMAAAACAAMAAQACAAIAAAACAAAAEgAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAAAC
oASAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAAAAAADwAQABEACoAAAABAAAAjAAAAIAAAAB0
AAAAHAEAAKQAAACQAAAAiAAAAEwAAAAwAAAAeAAAACQAAACEAAAAeAAAAAwAAABcAAAAcAAAAAEAAA
AAAAAAAAA5QAAAAAACAAAAAAAAAAAA8D8AAAAAAADwPwAAAAACAAAAAAAAAAAA5L8AAAAAAADkPwEA
AAAAAAAAAQAAAAEAAAABAAAAAAAAAAEAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAF
wAAAA4AAAAIAAAAAQAAADA////AwAAAAMAAAAEAAAAAQAAAAAANELY////AgAAAAIAAAAEAAAAAAAA
AOz///8BAAAAAQAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAAAAAAABAAAAAAAAAAAAAAA
        """
        return response_mock(read=base64.b64decode(b64_model))

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    usual_calls = get_classifier_model.calls + get_regressor_model.calls
    assert all([query['kwargs']['headers'] is None for query in usual_calls])

    sandbox_calls = get_sandbox_model.calls
    assert len(sandbox_calls) >= 1
    assert all(
        [
            query['kwargs']['headers']['Authorization'] == 'OAuth token2'
            for query in sandbox_calls
        ],
    )


@pytest.mark.parametrize(
    'config,expected_calls',
    [
        (
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'is_front_bad_format_with_rotations_v9': {
                        's3_file': (
                            'dkvu_is_front_bad_format_with_rotations_v9.bin'
                        ),
                        'threshold': 0.9,
                    },
                    'is_back_bad_format_with_rotations_v9': {
                        's3_file': (
                            'dkvu_is_back_bad_format_with_rotations_v9.bin'
                        ),
                        'threshold': 0.9,
                    },
                    'is_selfie_bad_format': {
                        's3_file': (
                            'dkvu_is_selfie_bad_format_with_rotations_v9.bin'
                        ),
                        'threshold': 0.9,
                    },
                    'photo_from_screen_with_rotations': {
                        's3_file': 'photo_from_screen_v9.bin',
                        'threshold': 0.9,
                    },
                    'printed_photo': {
                        's3_file': 'printed_photo.bin',
                        'threshold': 0.9,
                    },
                    'isRUS_license_with_rotations_v9': {
                        's3_file': 'isRUS_license_with_rotations_v9.bin',
                        'threshold': 0.1,
                    },
                    'face_age': {
                        's3_file': 'face_age.bin',
                        'is_regressor': True,
                    },
                    'quasi_gibdd': {
                        's3_file': 'quasi_gibdd_model.bin',
                        'threshold': 0.1,
                    },
                },
            },
            [
                {'key': 'dkvu_is_front_bad_format_with_rotations_v9.bin'},
                {'key': 'dkvu_is_back_bad_format_with_rotations_v9.bin'},
                {'key': 'dkvu_is_selfie_bad_format_with_rotations_v9.bin'},
                {'key': 'photo_from_screen_v9.bin'},
                {'key': 'printed_photo.bin'},
                {'key': 'isRUS_license_with_rotations_v9.bin'},
                {'key': 'face_age.bin'},
                {'key': 'quasi_gibdd_model.bin'},
            ],
        ),
    ],
)
async def test_mds_s3(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        taxi_config,
        cron_context,
        db,
        config,
        expected_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, [])
    _mock_get_model(patch_aiohttp_session, response_mock)

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(key):
        model_content = """
Q0JNMVgBAAAMAAAACAAMAAQACAAIAAAACAAAAEQAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAo
AEQABAAIAAwAEAAUABgAHAAgACQAKAAsADAANAA4AAAAAAA8AEAAKAAAAAEAAACMAAAAgAAAAHQA
AADoAAAAoAAAAJAAAACIAAAASAAAACwAAAB4AAAAIAAAAIAAAAB4AAAACAAAAFwAAAABAAAAAAAA
AAAAAAAAAAAAAgAAAAAAAAAAAPA/AAAAAAAA8D8AAAAAAgAAAHZiJ3ZbGbC/dmIndlsZsD8AAAAA
AQAAAAAAAAABAAAAAQAAAAEAAAAAAAAAAQAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAo
AAAABAAAAOz///8BAAAAAQAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAAAAAAABAAAAAEA
AAAAAAA/AAAAAA==
        """

        return base64.b64decode(model_content)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    get_model = _download_content
    calls = get_model.calls

    assert calls == expected_calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'strange_digits_in_license',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_VALID_LICENSE_FORMAT': '.*',
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Иван',
                        'last_name': ' Иванов ',
                        'middle_name': 'Иванович',
                        'number': '013374197¹',
                        'number_pd_id': '013374197¹_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'False',
                        'was_blocked': 'False',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Type': 'name',
                        'Confidence': 0.8310127854,
                        'Text': 'ilgiz',
                    },
                    {
                        'Type': 'middle_name',
                        'Confidence': 0.7861754298,
                        'Text': '-',
                    },
                    {
                        'Type': 'surname',
                        'Confidence': 0.6807793975,
                        'Text': 'makeev',
                    },
                    {
                        'Type': 'birth_date',
                        'Confidence': 0.8866220713,
                        'Text': '26.03.1996',
                    },
                    {
                        'Type': 'number',
                        'Confidence': 0.8746417761,
                        'Text': '013374197',
                    },
                    {
                        'Type': 'issue_date',
                        'Confidence': 0.8912211061,
                        'Text': '01.07.2014',
                    },
                    {
                        'Type': 'expiration_date',
                        'Confidence': 0.8599180579,
                        'Text': '-',
                    },
                ],
                'back': [
                    {
                        'Type': 'issue_date',
                        'Confidence': 0.878357172,
                        'Text': '01.07.2014',
                    },
                    {
                        'Type': 'expiration_date',
                        'Confidence': 0.8420349956,
                        'Text': '-',
                    },
                    {
                        'Type': 'experience_from',
                        'Confidence': 0.8528244495,
                        'Text': '2014',
                    },
                    {
                        'Type': 'number',
                        'Confidence': 0.7131332755,
                        'Text': '-',
                    },
                    {
                        'Type': 'prev_number',
                        'Confidence': 0.9040181041,
                        'Text': '-',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'birthday': '1996-03-26',
                            'country': None,
                            'db_id': 'some_db_id',
                            'driver_experience': None,
                            'driver_id': 'some_driver_id',
                            'expire_date': '2029-10-07',
                            'first_name': 'Иван',
                            'is_invited': False,
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                            'number': '*****4197¹',
                            'number_pd_id': '013374197¹_pd_id',
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'was_blocked': False,
                        },
                        'quasi_gibdd_features': {
                            'features': None,
                            'is_valid_by_real_gibdd': None,
                            'last_check_date': None,
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1996-03-26',
                            'expire_date': '2029-10-07',
                            'first_name': 'Иван',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                            'number': '013374197¹',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_strange_symbols(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass': True,
                'additional_info.quasi_gibdd_features': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'check_experience',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Иван',
                        'last_name': ' Иванов ',
                        'middle_name': 'Иванович',
                        'number': '0133741971',
                        'number_pd_id': '0133741971_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                        'is_invited': 'False',
                        'was_blocked': 'False',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Type': 'name',
                        'Confidence': 0.8310127854,
                        'Text': 'ilgiz',
                    },
                    {
                        'Type': 'middle_name',
                        'Confidence': 0.7861754298,
                        'Text': '-',
                    },
                    {
                        'Type': 'surname',
                        'Confidence': 0.6807793975,
                        'Text': 'makeev',
                    },
                    {
                        'Type': 'birth_date',
                        'Confidence': 0.8866220713,
                        'Text': '26.03.1996',
                    },
                    {
                        'Type': 'number',
                        'Confidence': 0.8746417761,
                        'Text': '013374197',
                    },
                    {
                        'Type': 'issue_date',
                        'Confidence': 0.8912211061,
                        'Text': '01.07.2014',
                    },
                    {
                        'Type': 'expiration_date',
                        'Confidence': 0.8599180579,
                        'Text': '-',
                    },
                ],
                'back': [
                    {
                        'Type': 'issue_date',
                        'Confidence': 0.878357172,
                        'Text': '01.07.2014',
                    },
                    {
                        'Type': 'expiration_date',
                        'Confidence': 0.8420349956,
                        'Text': '-',
                    },
                    {
                        'Type': 'experience_from',
                        'Confidence': 0.8528244495,
                        'Text': '2014',
                    },
                    {
                        'Type': 'number',
                        'Confidence': 0.7131332755,
                        'Text': '-',
                    },
                    {
                        'Type': 'prev_number',
                        'Confidence': 0.9040181041,
                        'Text': '-',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'pictures_urls': {
                                'back_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': None,
                            },
                        },
                        'catboost_features': {
                            'is_selfie_bad_format_probability': None,
                            'selfie_photo_from_screen_probability': None,
                        },
                        'saas_features': {'back': [], 'front': []},
                        'face_saas_features': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1996-03-26',
                            'expire_date': '2029-10-07',
                            'first_name': 'Иван',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Иванович',
                            'number': '0133741971',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_without_selfie(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.pictures_urls': True,
                'additional_info.catboost_features.is_selfie_bad_format_probability': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'additional_info.catboost_features.selfie_photo_from_screen_probability': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'additional_info.saas_features': True,
                'additional_info.face_saas_features': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'has bad detects',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_VM_DETECTS_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_VM_DETECTS_TO_UNKNOWN': [
                    {'type': 1, 'id': 1},
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_bad_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'vm_detects': [
                            {'id': 1, 'type': 1},
                            {'id': 2, 'type': 2},
                        ],
                        'errors': ['has not ok detects from Protector SDK'],
                        'verdict': 'unknown',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'does not have bad detects',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_VM_DETECTS_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_VM_DETECTS_TO_UNKNOWN': [
                    {'type': 1, 'id': 1},
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_so_so_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'vm_detects': [{'id': 2, 'type': 2}],
                        'errors': [],
                        'verdict': 'success',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
async def test_vm_detects(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.vm_detects': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'has bad aux-data',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_PSDK_AUX_DATA_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_PSDK_AUX_DATA_TO_UNKNOWN': [
                    {'type': 1, 'value': '1'},
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_bad_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'protector_aux_data': [
                            {'type': 1, 'value': '1'},
                            {'type': 2, 'value': '2'},
                        ],
                        'errors': ['has not ok aux-data from Protector SDK'],
                        'verdict': 'unknown',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'does not have bad aux-data',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_PSDK_AUX_DATA_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_PSDK_AUX_DATA_TO_UNKNOWN': [
                    {'type': 1, 'value': '1'},
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_so_so_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'protector_aux_data': [{'type': 2, 'value': '2'}],
                        'errors': [],
                        'verdict': 'success',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
async def test_aux_data(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.protector_aux_data': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_dkvu_get_response,ocr_response,telesign_score,'
    'created_date,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'newbie_ok_with_score',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_REQUESTS_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_THRESHOLD': 1000,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_bad_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            111,
            '2022-03-10T00:00:00.000',
            [
                {
                    'additional_info': {
                        'telesign_score': 111,
                        'errors': [],
                        'verdict': 'success',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'newbie_not_ok_with_score',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_REQUESTS_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_THRESHOLD': 100,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_bad_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            111,
            '2022-03-10T00:00:00.000',
            [
                {
                    'additional_info': {
                        'telesign_score': 111,
                        'errors': ['Telesign score is too bad'],
                        'verdict': 'unknown',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'not_newbie_ok_without_score',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_REQUESTS_ENABLED': True,
                'AFS_CRON_RESOLVE_QC_PASSES_TELESIGN_THRESHOLD': 1000,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_bad_by_protector_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            111,
            '2022-01-01T00:00:00.000',
            [
                {
                    'additional_info': {
                        'telesign_score': None,
                        'errors': [],
                        'verdict': 'success',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
    ],
)
@pytest.mark.now('2022-03-11T00:00:00.000Z')
async def test_telesign(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_driver_profiles,
        mock_uantifraud,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        telesign_score,
        created_date,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    _mock_driver_profile(
        mock_driver_profiles,
        {
            'data': {
                'created_date': created_date,
                'phone_pd_ids': [{'pd_id': 'some_pd_id'}],
            },
            'park_driver_profile_id': 'some_id',
        },
    )
    _mock_telesign(mock_uantifraud, telesign_score)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.telesign_score': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-05-05T17:00:15.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'unknown pass because of suspicious device',
            {**DEFAULT_CONFIG},
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'driver_profile': {
                            'metrica_device_id': 'device_with_cab',
                        },
                        'suspicion_info': {
                            'by_device_id': [{'detect_type': 'cab_installed'}],
                            'by_park_id': [],
                            'by_geohash': None,
                        },
                        'errors': ['device_id is suspicious'],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_suspicious_devices(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_driver_profiles,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    _mock_driver_profile(
        mock_driver_profiles,
        {
            'data': {'metrica_device_id': 'device_with_cab'},
            'park_driver_profile_id': 'some_id',
        },
    )
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.driver_profile': True,
                'additional_info.suspicion_info': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-05-05T17:00:15.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'unknown pass because of suspicious park',
            {**DEFAULT_CONFIG},
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'suspicious_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'suspicion_info': {
                            'by_device_id': None,
                            'by_park_id': [
                                {
                                    'detect_type': 'fake_dkvu',
                                    'fake_drivers': 9,
                                    'total_drivers': 10,
                                },
                            ],
                            'by_geohash': None,
                        },
                        'errors': ['park_id is suspicious'],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_suspicious_parks(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_driver_profiles,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.suspicion_info': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-03-11T00:00:00.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'unknown pass because of faceApp',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
                    **DEFAULT_CONFIG[
                        'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                    ],
                    'faceapp_selfie': {
                        **DEFAULT_CONFIG[
                            'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS'
                        ]['faceapp_selfie'],
                        'threshold': 0.3,
                    },
                },
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'catboost_features': {
                            'faceapp_selfie_probability': 0.48428344894918696,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'catboost faceapp_selfie_probability reached '
                            'threshold',
                        ],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_faceapp(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.catboost_features.faceapp_selfie_probability': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-03-11T00:00:00.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'blacklist pass invalid symbols',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': 'DL0302664⁣⁣⁣⁣⁣',
                        'number_pd_id': 'DL0302664⁣⁣⁣⁣⁣_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': 'ŚC000833634',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': 'DL0302664⁣⁣⁣⁣⁣',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': 'DL0302664⁣⁣⁣⁣⁣',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {'number_pd_id': 'DL0302664⁣⁣⁣⁣⁣_pd_id'},
                        'verdict': 'blacklist',
                        'reason': 'invalid_symbols',
                        'message_keys': ['dkvu_block_reason_invalid_symbols'],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': 'DL0302664⁣⁣⁣⁣⁣',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['dkvu_block_reason_invalid_symbols'],
                        'status': 'blacklist',
                    },
                ],
            ],
        ),
    ],
)
async def test_invalid_symbols_in_license(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.number_pd_id': True,
                'additional_info.verdict': True,
                'additional_info.reason': True,
                'additional_info.message_keys': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-03-11T00:00:00.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'name is whitelisted',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_SUCCESS_WHITELISTED_NAMES_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_WHITELISTED_NAMES': [
                    'иван',
                    'василий',
                    'сергей',
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {'first_name': 'Василий'},
                        'verdict': 'success',
                        'errors': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'country': 'rus',
                            'driver_experience': '2019-10-07',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'name is not whitelisted',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_SUCCESS_WHITELISTED_NAMES_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'AFS_CRON_RESOLVE_QC_PASSES_WHITELISTED_NAMES': [
                    'иван',
                    'андрей',
                    'сергей',
                ],
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {'first_name': 'Василий'},
                        'verdict': 'unknown',
                        'errors': ['name is not whitelisted'],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_whitelisted_names(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.first_name': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )


@pytest.mark.now('2022-03-11T00:00:00.000Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_dkvu_get_response,ocr_response,geolocation,'
    'expected_verdicts_db_content,expected_nirvana_dkvu_set_calls',
    [
        (
            'send to assessors because of suspicious geohash',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            {
                'lat': 12.345678,
                'lon': 34.567891,
                'speed': 0.024069087579846382,
                'accuracy': 20,
                'direction': 20,
                'timestamp': 1650904279,
                'geohash': 'sf0w4x7wf1',
            },
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'errors': ['geohash is suspicious'],
                        'suspicion_info': {
                            'by_device_id': None,
                            'by_park_id': [],
                            'by_geohash': [
                                {
                                    'detect_type': 'fake_dkvu',
                                    'fake_drivers': 5,
                                    'total_drivers': 7,
                                },
                            ],
                        },
                        'geolocation': {'geohash': 'sf0w4x7wf1'},
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'send to assessors because of suspicious prefix in geohash',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'DriverLicense': 'http://example.com/file.jpg',
                        'DriverLicenseBack': 'http://example.com/file.jpg',
                        'Selfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': 'some_pass_id',
                        'db_id': 'some_db_id',
                        'driver_id': 'some_driver_id',
                        'first_name': 'Василий  ',
                        'last_name': ' Иванов ',
                        'middle_name': 'Аристархович   ',
                        'number': '0133741979',
                        'number_pd_id': '0133741979_pd_id',
                        'issue_date': '2019-10-07',
                        'expire_date': '2029-10-07',
                    },
                },
            ],
            {
                'front': [
                    {
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'василий',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'аристархович',
                    },
                    {
                        'Confidence': 0.8884754777,
                        'Type': 'surname',
                        'Text': 'иванов',
                    },
                    {
                        'Confidence': 0.8942831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.7566020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.8986020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8920281529,
                        'Type': 'birth_date',
                        'Text': '24.08.1993',
                    },
                ],
                'back': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
                'full': [
                    {
                        'Confidence': 0.4252831159,
                        'Type': 'number',
                        'Text': '0133741979',
                    },
                    {
                        'Confidence': 0.2956020088,
                        'Type': 'issue_date',
                        'Text': '07.10.2019',
                    },
                    {
                        'Confidence': 0.7656020088,
                        'Type': 'expiration_date',
                        'Text': '07.10.2029',
                    },
                    {
                        'Confidence': 0.8817818761,
                        'Type': 'experience_from',
                        'Text': '2011',
                    },
                ],
            },
            {
                'lat': 44.444444,
                'lon': 55.555555,
                'speed': 0.024069087579846382,
                'accuracy': 20,
                'direction': 20,
                'timestamp': 1650904279,
                'geohash': 'tpzsb4y7dk',
            },
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'errors': ['geohash is suspicious'],
                        'suspicion_info': {
                            'by_device_id': None,
                            'by_park_id': [],
                            'by_geohash': [
                                {
                                    'detect_type': 'fake_dkvu',
                                    'fake_drivers': 2,
                                    'total_drivers': 3,
                                },
                            ],
                        },
                        'geolocation': {'geohash': 'tpzsb4y7dk'},
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'birthday': '1993-08-24',
                            'expire_date': '2029-10-07',
                            'first_name': 'Василий',
                            'issue_date': '2019-10-07',
                            'last_name': 'Иванов',
                            'middle_name': 'Аристархович',
                            'number': '0133741979',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_suspicious_geohashes(
        mock_taximeter_xservice,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_quality_control_py3,
        mock_blocklist,
        mock_driver_trackstory,
        taxi_config,
        cron_context,
        db,
        config,
        comment,
        nirvana_dkvu_get_response,
        ocr_response,
        geolocation,
        expected_verdicts_db_content,
        expected_nirvana_dkvu_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_dkvu_get(mock_taximeter_xservice, nirvana_dkvu_get_response)
    nirvana_dkvu_set = _mock_nirvana_dkvu_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_quality_control_history(mock_quality_control_py3)
    _mock_qc_invites(mock_qc_invites)
    _mock_blocklist_find_info(mock_blocklist)
    _mock_geolocation(mock_driver_trackstory, geolocation)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.suspicion_info': True,
                'additional_info.geolocation.geohash': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_dkvu_set) == expected_nirvana_dkvu_set_calls
    )
