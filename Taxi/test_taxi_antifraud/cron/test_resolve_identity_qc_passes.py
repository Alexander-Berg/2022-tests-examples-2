# pylint: disable=too-many-lines
import base64
import datetime

from aiohttp import web
import pytest
from yt import yson

from taxi_antifraud.crontasks import resolve_identity_qc_passes
from taxi_antifraud.generated.cron import run_cron
from taxi_antifraud.settings import qc_settings
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = resolve_identity_qc_passes.CURSOR_STATE_NAME


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['ANTIFRAUD_OCR_API_KEY'] = 'token'
    simple_secdist['settings_override'][
        'TAXIMETER_XSERVICE_NIRVANA_API_KEY'
    ] = 'another_token'
    return simple_secdist


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        assert request_id.endswith('_pd_id')
        return {'license': request_id[:-6]}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, number, *args, **kwargs):
        return {'id': number + '_pd_id'}


def _mock_nirvana_identity_get(mock_taximeter_xservice, response_items):
    @mock_taximeter_xservice('/utils/nirvana/identity/get')
    async def _nirvana_identity_get(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '666666666666666666':
            return web.json_response(data=dict(items=[]))
        return web.json_response(
            data=dict(cursor=666666666666666666, items=response_items),
        )

    return _nirvana_identity_get


def _mock_nirvana_identity_set(mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/nirvana/identity/set')
    async def _nirvana_identity_set(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    return _nirvana_identity_set


def _mock_get_jpg(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://example.com/file.jpg', 'GET')
    def _get_jpg(method, url, **kwargs):
        if (
                url.startswith('http://example.com/file')
                and method.upper() == 'GET'
        ):
            return response_mock(read=bytes())
        return response_mock(status=404)

    return _get_jpg


def _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response):
    @patch_aiohttp_session(qc_settings.OCR_URL, 'POST')
    def _get_ocr_response(method, url, data, **kwargs):
        if 'PassportKaz' in data['meta']:
            response = {'data': {'fulltext': ocr_response['passport_kaz']}}
        elif 'Passport' in data['meta']:
            response = {'data': {'fulltext': ocr_response['passport']}}
        else:
            return response_mock(status=404)
        return response_mock(json=response)

    return _get_ocr_response


def _mock_get_model(patch_aiohttp_session, response_mock):
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
        'https://storage.yandex-team.ru/get-devtools/model_one.bin', 'GET',
    )
    def _get_model_with_one_categorial(method, url, **kwargs):
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

    return (
        _get_model_without_categorial,
        _get_model_with_one_categorial,
        _get_regressor_model,
    )


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
                                'Features': [0.736, 0.928, 0.1111, 0.3, 0.4],
                                'Height': 0.1342742741,
                                'Width': 0.15700639635,
                                'Confidence': 0.99,
                            },
                            {
                                'LayerName': 'super_face_layer',
                                'Features': [0.572, 0.374, 0.2222, 0.4, 0.1],
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
                                'Features': [0.123, 0.546, 0.234, 0.765],
                                'LayerName': 'prod_v8_enc_toloka_96',
                                'Version': '8',
                            },
                        ],
                    },
                },
            }
        return response_mock(json=features)

    return _get_features


def _mock_driver_profile(mock_driver_profiles, driver_profile):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def get_profile(request):
        assert request.method == 'POST'
        return web.json_response(data=dict(profiles=[driver_profile]))

    return get_profile


def _mock_selfemployed(mock_selfemployed, passport_is_valid=True):
    @mock_selfemployed('/admin/selfemployed-check-passport/')
    async def check_passport(request):
        assert request.method == 'POST'
        if not passport_is_valid:
            return web.json_response(
                status=404,
                data={'code': '404', 'text': 'Passport is not valid'},
            )
        return web.json_response(data={'message': 'Passport is valid'})

    return check_passport


def _mock_get_saas_response(
        patch_aiohttp_session, response_mock, response_json,
):
    @patch_aiohttp_session(qc_settings.SAAS_URL, 'GET')
    def _get_saas_response(method, url, **kwargs):
        return response_mock(
            json={'response': {'results': [{'groups': response_json}]}},
        )

    return _get_saas_response


def _mock_qc_invites(mock_qc_invites):
    @mock_qc_invites('/admin/qc-invites/v1/dkvu/invite')
    async def _qc_invite_dkvu(request):
        assert request.method == 'POST'

        return web.json_response(data=dict(invite_id='invite_id'))

    @mock_qc_invites('/admin/qc-invites/v1/identity/invite')
    async def _qc_invite_identity(request):
        assert request.method == 'POST'

        return web.json_response(data=dict(invite_id='invite_id'))

    return _qc_invite_dkvu, _qc_invite_identity


def _mock_qc_invites_info(mock_qc_invites):
    @mock_qc_invites('/api/qc-invites/v1/invite_info')
    async def _qc_invites_find(request):
        assert request.method == 'GET'

        return web.json_response(
            data=dict(comment='[allow auto verdict] Регулярный вызов'),
        )

    return _qc_invites_find


def _mock_quality_control_history(mock_quality_control_py3, qc_history=None):
    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'

        if qc_history is None:
            return web.json_response(data=dict(cursor='end', items=[]))
        return web.json_response(data=dict(cursor='end', items=qc_history))

    return _api_v1_pass_history


DEFAULT_CONFIG: dict = {
    'AFS_CRON_CURSOR_USE_PGSQL': 'enabled',
    'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
        'photo_from_screen_v2': {
            'threshold': 0.2,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'printed_photo': {
            'threshold': 0.9,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'passport_selfie_bad_format': {
            'threshold': 0.2,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'passport_title_is_russian': {
            'threshold': 0.2,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'passport_registration_is_russian': {
            'threshold': 0.2,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
        'face_age': {
            'url': 'https://storage.yandex-team.ru/get-devtools/regressor_model.bin',  # noqa: E501 pylint: disable=line-too-long
            'is_regressor': True,
        },
        'quasi_fms': {
            'threshold': 0.2,
            'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
        },
    },
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_AGE_MODEL_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_CHECK_PASSPORT_IN_FNS_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_EMPTY_BATCH_SLEEP_TIME': 0.01,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_EMPTY_BATCHES_LIMIT': 3,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_FACE_AGE_THRESHOLD': 50,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_MISTAKES_SELFIE_FORMAT_THRESHOLD': (
        0.5
    ),
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_MISTAKES_SELFIE_SAAS_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_CONFIDENCE_THRESHOLD': 0.3,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_PART_OF_PASSES_TO_RESOLVE': 1,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_RESOLUTION_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_INVITED_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_COURIERS_ENABLED': True,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_STRATEGY': [
        {
            'identity_type': 'id_kaz_stripped',
            'ocr_strategy': 'PassportKaz',
            'confidence_threshold': 0.6,
        },
    ],
    'PPS_CRON_COMMENTS_FOR_INVITES_TO_RESOLVE': [
        '[allow auto verdict] Регулярный вызов',
    ],
}

SUCCESSFUL_CATBOOST_MODELS: dict = {
    'photo_from_screen_v2': {
        'threshold': 0.7,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_zero.bin',
    },
    'printed_photo': {
        'threshold': 0.9,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_zero.bin',
    },
    'passport_selfie_bad_format': {
        'threshold': 0.7,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_zero.bin',
    },
    'passport_title_is_russian': {
        'threshold': 0.2,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_zero.bin',
    },
    'passport_registration_is_russian': {
        'threshold': 0.2,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_zero.bin',
    },
    'face_age': {
        'url': (
            'https://storage.yandex-team.ru/get-devtools/regressor_model.bin'
        ),
        'is_regressor': True,
    },
    'quasi_fms': {
        'threshold': 0.2,
        'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
    },
}

DEFAULT_FACE_SAAS_FEATURES = [
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
]

DEFAULT_CATBOOST_FEATURES: dict = {
    'face_age_prediction': 24.375,
    'printed_selfie_score': 0.46161414343735935,
    'quasi_fms_score': 0.48428344894918696,
    'registration_from_screen_score': 0.46161414343735935,
    'registration_is_russian_score': 0.46161414343735935,
    'selfie_bad_format_score': 0.46161414343735935,
    'selfie_from_screen_score': 0.46161414343735935,
    'title_from_screen_score': 0.46161414343735935,
    'title_is_russian_score': 0.46161414343735935,
}


def _build_saas_body(body: dict) -> str:
    return base64.b64encode(bytes([0]) + yson.dumps(body)).decode()


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'saas_response,expected_verdicts_db_content,'
    'expected_state_pgsql_content,expected_nirvana_identity_get_calls,'
    'expected_nirvana_identity_set_calls',
    [
        (
            'successful_pass',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
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
                                        'exam': 'identity',
                                        'uberdriver_driver_id': None,
                                        'width': 0.2446286529,
                                    },
                                ),
                            },
                            'relevance': '842027688',
                        },
                    ],
                },
            ],
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'text': (
                                        'с.бичурча '
                                        'бантево '
                                        'шемуршинского '
                                        'р-на '
                                        'чувашской '
                                        'асср'
                                    ),
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
                                    'text': (
                                        'отделом '
                                        'уфмс '
                                        'россии '
                                        'по '
                                        'г. '
                                        'москве '
                                        'по '
                                        'району '
                                        'митино'
                                    ),
                                    'type': 'issued_by',
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
                                            'confidence': 0.98,
                                            'driver_id': (
                                                'some_other_driver_id'
                                            ),
                                            'driver_license': '9568746539',
                                            'exam': 'identity',
                                            'height': 0.5797693729,
                                            'pass_id': (
                                                '603a74ad9ed31f2bb89c9de4'
                                            ),
                                            'pass_modified': 1514616129.840873,
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'uberdriver_driver_id': None,
                                            'width': 0.2446286529,
                                        },
                                        'similarity': 0.842027688,
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
                                            'confidence': 0.98,
                                            'driver_id': (
                                                'some_other_driver_id'
                                            ),
                                            'driver_license': '9568746539',
                                            'exam': 'identity',
                                            'height': 0.5797693729,
                                            'pass_id': (
                                                '603a74ad9ed31f2bb89c9de4'
                                            ),
                                            'pass_modified': 1514616129.840873,
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'uberdriver_driver_id': None,
                                            'width': 0.2446286529,
                                        },
                                        'similarity': 0.842027688,
                                    },
                                ],
                                'width': 0.15700639635,
                            },
                        ],
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '*****34523',
                            'patronymic': 'николаевна',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'success',
                        'errors': [],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234523,
                                -184523,
                                -134523,
                                -84523,
                                -34523,
                                65477,
                                165477,
                                265477,
                                365477,
                                465477,
                                2088,
                                2088,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                -0.008903177939903549,
                                -0.011315662546132461,
                                -0.015528943006028709,
                                -0.02471516628609964,
                                -0.06051038438142688,
                                0.031904332819157874,
                                0.012624110903630113,
                                0.007868854929052234,
                                0.005715817958448822,
                                0.004487869432861344,
                                '0910',
                                234523,
                                4764,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'last_name': 'Андреева',
                                'first_name': 'Татьяна',
                                'middle_name': 'Николаевна',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '0910234523_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': 'Брюс',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': 'Мефодиевич',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': 'Иванов',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                            {
                                'field_name': 'issuer',
                                'new_value': '770-093',
                                'old_value': 'УВД Первоуральска',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            {'resolve_identity_qc_passes_cursor': '666666666666666666'},
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
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'unknown_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [],
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'text': (
                                        'с.бичурча '
                                        'бантево '
                                        'шемуршинского '
                                        'р-на '
                                        'чувашской '
                                        'асср'
                                    ),
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
                                    'text': (
                                        'отделом '
                                        'уфмс '
                                        'россии '
                                        'по '
                                        'г. '
                                        'москве '
                                        'по '
                                        'району '
                                        'митино'
                                    ),
                                    'type': 'issued_by',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '*****34523',
                            'patronymic': 'николаевна',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score '
                            'reached threshold',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234523,
                                -184523,
                                -134523,
                                -84523,
                                -34523,
                                65477,
                                165477,
                                265477,
                                365477,
                                465477,
                                2088,
                                2088,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                -0.008903177939903549,
                                -0.011315662546132461,
                                -0.015528943006028709,
                                -0.02471516628609964,
                                -0.06051038438142688,
                                0.031904332819157874,
                                0.012624110903630113,
                                0.007868854929052234,
                                0.005715817958448822,
                                0.004487869432861344,
                                '0910',
                                234523,
                                4764,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'last_name': 'Андреева',
                                'first_name': 'Татьяна',
                                'middle_name': 'Николаевна',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '0910234523_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': 'Брюс',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': 'Мефодиевич',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': 'Иванов',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                            {
                                'field_name': 'issuer',
                                'new_value': '770-093',
                                'old_value': 'УВД Первоуральска',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            {'resolve_identity_qc_passes_cursor': '666666666666666666'},
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
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_cron(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_quality_control_py3,
        mock_qc_invites,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        saas_response,
        expected_verdicts_db_content,
        expected_state_pgsql_content,
        expected_nirvana_identity_get_calls,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    nirvana_identity_get = _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    get_jpg = _mock_get_jpg(patch_aiohttp_session, response_mock)
    get_ocr_response = _mock_get_ocr_response(
        patch_aiohttp_session, response_mock, ocr_response,
    )
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, saas_response,
    )
    _mock_selfemployed(mock_selfemployed)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_verdicts_db_content
    )

    assert [
        list(nirvana_identity_get.next_call()['request'].query.items())
        for _ in range(nirvana_identity_get.times_called)
    ] == expected_nirvana_identity_get_calls
    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )

    assert (
        await state.get_all_cron_state(master_pool)
        == expected_state_pgsql_content
    )

    assert len(get_jpg.calls) == 3
    assert len(get_ocr_response.calls) == 1


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'expected_verdicts_db_content,expected_nirvana_identity_set_calls',
    [
        (
            'unknown_pass_is_invited',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_INVITED_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'is_invited': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'text': (
                                        'с.бичурча '
                                        'бантево '
                                        'шемуршинского '
                                        'р-на '
                                        'чувашской '
                                        'асср'
                                    ),
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
                                    'text': (
                                        'отделом '
                                        'уфмс '
                                        'россии '
                                        'по '
                                        'г. '
                                        'москве '
                                        'по '
                                        'району '
                                        'митино'
                                    ),
                                    'type': 'issued_by',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '*****34523',
                            'patronymic': 'николаевна',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': True,
                            'was_blocked': False,
                        },
                        'verdict': 'success',
                        'errors': [],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234523,
                                -184523,
                                -134523,
                                -84523,
                                -34523,
                                65477,
                                165477,
                                265477,
                                365477,
                                465477,
                                2088,
                                2088,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                -0.008903177939903549,
                                -0.011315662546132461,
                                -0.015528943006028709,
                                -0.02471516628609964,
                                -0.06051038438142688,
                                0.031904332819157874,
                                0.012624110903630113,
                                0.007868854929052234,
                                0.005715817958448822,
                                0.004487869432861344,
                                '0910',
                                234523,
                                4764,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'last_name': 'Андреева',
                                'first_name': 'Татьяна',
                                'middle_name': 'Николаевна',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '0910234523_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': 'Брюс',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': 'Мефодиевич',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': 'Иванов',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                            {
                                'field_name': 'issuer',
                                'new_value': '770-093',
                                'old_value': 'УВД Первоуральска',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'unknown_pass_was_blocked',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'was_blocked': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'text': (
                                        'с.бичурча '
                                        'бантево '
                                        'шемуршинского '
                                        'р-на '
                                        'чувашской '
                                        'асср'
                                    ),
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
                                    'text': (
                                        'отделом '
                                        'уфмс '
                                        'россии '
                                        'по '
                                        'г. '
                                        'москве '
                                        'по '
                                        'району '
                                        'митино'
                                    ),
                                    'type': 'issued_by',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '*****34523',
                            'patronymic': 'николаевна',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': True,
                        },
                        'verdict': 'success',
                        'errors': [],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234523,
                                -184523,
                                -134523,
                                -84523,
                                -34523,
                                65477,
                                165477,
                                265477,
                                365477,
                                465477,
                                2088,
                                2088,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                -0.008903177939903549,
                                -0.011315662546132461,
                                -0.015528943006028709,
                                -0.02471516628609964,
                                -0.06051038438142688,
                                0.031904332819157874,
                                0.012624110903630113,
                                0.007868854929052234,
                                0.005715817958448822,
                                0.004487869432861344,
                                '0910',
                                234523,
                                4764,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'last_name': 'Андреева',
                                'first_name': 'Татьяна',
                                'middle_name': 'Николаевна',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '0910234523_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': 'Брюс',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': 'Мефодиевич',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': 'Иванов',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                            {
                                'field_name': 'issuer',
                                'new_value': '770-093',
                                'old_value': 'УВД Первоуральска',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'unknown_pass_success_config_is_disabled',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_PART_OF_PASSES_TO_RESOLVE': (  # noqa: E501 pylint: disable=line-too-long
                    0
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'text': (
                                        'с.бичурча '
                                        'бантево '
                                        'шемуршинского '
                                        'р-на '
                                        'чувашской '
                                        'асср'
                                    ),
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
                                    'text': (
                                        'отделом '
                                        'уфмс '
                                        'россии '
                                        'по '
                                        'г. '
                                        'москве '
                                        'по '
                                        'району '
                                        'митино'
                                    ),
                                    'type': 'issued_by',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '*****34523',
                            'patronymic': 'николаевна',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'success',
                        'errors': [],
                        'skip_verdict_because_of_percent': True,
                        'quasi_fms_features': {
                            'features': [
                                -234523,
                                -184523,
                                -134523,
                                -84523,
                                -34523,
                                65477,
                                165477,
                                265477,
                                365477,
                                465477,
                                2088,
                                2088,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                2089,
                                -0.008903177939903549,
                                -0.011315662546132461,
                                -0.015528943006028709,
                                -0.02471516628609964,
                                -0.06051038438142688,
                                0.031904332819157874,
                                0.012624110903630113,
                                0.007868854929052234,
                                0.005715817958448822,
                                0.004487869432861344,
                                '0910',
                                234523,
                                4764,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'last_name': 'Андреева',
                                'first_name': 'Татьяна',
                                'middle_name': 'Николаевна',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '0910234523_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': 'Брюс',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': 'Мефодиевич',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': 'Иванов',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                            {
                                'field_name': 'issuer',
                                'new_value': '770-093',
                                'old_value': 'УВД Первоуральска',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            [
                [
                    {
                        'id': 'some_qc_id',
                        'status': 'unknown',
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                    },
                ],
            ],
        ),
    ],
)
async def test_config(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_quality_control_py3,
        mock_qc_invites,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_selfemployed(mock_selfemployed)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'history_features,expected_verdicts_db_content,'
    'expected_nirvana_identity_set_calls',
    [
        (
            'successful_pass_is_invited',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_INVITED_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'is_invited': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Confidence': 0.8884754181,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.886099577,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8965250254,
                        'Type': 'subdivision',
                        'Text': '770-093',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8886011243,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8992502093,
                        'Type': 'number',
                        'Text': '0910234523',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.899061203,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8734120131,
                        'Type': 'issued_by',
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
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
                        'verdict': 'success',
                        'invite_comment': (
                            '[allow auto verdict] Регулярный вызов'
                        ),
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
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
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_quality_control_py3,
        mock_qc_invites,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        history_features,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_selfemployed(mock_selfemployed)
    _mock_quality_control_history(mock_quality_control_py3, history_features)
    _mock_qc_invites_info(mock_qc_invites)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.invite_comment': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'expected_verdicts_db_content,expected_nirvana_identity_set_calls',
    [
        (
            'incorrect_date',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/0204 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {'passport': []},
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'first_name': 'Брюс',
                        'last_name': 'Иванов',
                        'middle_name': 'Мефодиевич',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '0204-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '*****34522',
                            'patronymic': 'Мефодиевич',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': None,
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'field first_name is not recognized in title',
                            'field patronymic is not recognized in title',
                            'field last_name is not recognized in title',
                            'field date_of_birth is not recognized in title',
                            'field number is not recognized in title',
                            'field issue_date is not recognized in title',
                            'field issuer is not recognized in title',
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score is None',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'catboost registration_is_russian_score is None',
                            'birthday is unknown',
                            'qc_pass birthday is not equal to driver '
                            'profile birthday',
                            'passport is not valid according to FNS',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234522,
                                -184522,
                                -134522,
                                -84522,
                                -34522,
                                65478,
                                165478,
                                265478,
                                365478,
                                465478,
                                663073,
                                663073,
                                663074,
                                663074,
                                663074,
                                663074,
                                663074,
                                663074,
                                663074,
                                663074,
                                -2.8273381601726064,
                                -3.593463110089854,
                                -4.929111966815837,
                                -7.844987103949268,
                                -19.20728810613522,
                                10.12666849934329,
                                4.007022081485152,
                                2.497660823119053,
                                1.8142651541269241,
                                1.424501265365925,
                                '0910',
                                234522,
                                -656221,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'registration_from_screen_score': None,
                            'registration_is_russian_score': None,
                        },
                        'driver_profile': {
                            'full_name': {
                                'first_name': 'Брюс',
                                'last_name': 'Иванов',
                                'middle_name': 'Мефодиевич',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': None,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id2',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '0204-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'without_title',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'someparkid_somedriverid',
                },
            ],
            {'passport': []},
            {},
            [],
            [
                [
                    {
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                    },
                ],
            ],
        ),
        (
            'without_ocr',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {'passport': []},
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'first_name': 'Брюс',
                        'last_name': 'Иванов',
                        'middle_name': 'Мефодиевич',
                    },
                    'license_driver_birth_date': None,
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '*****34522',
                            'patronymic': 'Мефодиевич',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'field first_name is not recognized in title',
                            'field patronymic is not recognized in title',
                            'field last_name is not recognized in title',
                            'field date_of_birth is not recognized in title',
                            'field number is not recognized in title',
                            'field issue_date is not recognized in title',
                            'field issuer is not recognized in title',
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score '
                            'reached threshold',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'birthday is unknown',
                            'passport is not valid according to FNS',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'is_valid_by_real_fms': None,
                            'features': [
                                -234522,
                                -184522,
                                -134522,
                                -84522,
                                -34522,
                                65478,
                                165478,
                                265478,
                                365478,
                                465478,
                                5636,
                                5636,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                -0.024031860550396123,
                                -0.0305437833971017,
                                -0.04190392649529445,
                                -0.06669269539291546,
                                -0.16328717919008168,
                                0.08608998442224869,
                                0.034064951232187966,
                                0.021233397871010026,
                                0.015423636990461806,
                                0.012110131950382188,
                                '0910',
                                234522,
                                1216,
                            ],
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'first_name': 'Брюс',
                                'last_name': 'Иванов',
                                'middle_name': 'Мефодиевич',
                            },
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': None,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id2',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'without_registration',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': '',
                        'first_name': '',
                        'patronymic': '',
                        'date_of_birth': '',
                        'number': '',
                        'issuer': '',
                        'issue_date': '',
                        'permanent_address': '',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Confidence': 0.8884754181,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.886099577,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8886011243,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8992502093,
                        'Type': 'number',
                        'Text': '3949857363',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.899061203,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'first_name': 'Брюс',
                        'last_name': 'Иванов',
                        'middle_name': 'Мефодиевич',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
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
                                    'confidence': 0.8886011243,
                                    'text': '25.11.1968',
                                    'type': 'birth_date',
                                },
                                {
                                    'confidence': 0.8992502093,
                                    'text': '3949857363',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.899061203,
                                    'text': '17.01.2014',
                                    'type': 'issue_date',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '',
                            'last_name': 'андреева',
                            'number': '*****57363',
                            'patronymic': 'николаевна',
                            'permanent_address': '',
                            'pictures_urls': {
                                'registration_picture_url': None,
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'field issuer is not recognized in title',
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score is '
                            'None',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'catboost registration_is_russian_score is '
                            'None',
                            'catboost quasi_fms_score is None',
                            'qc_pass first name is not equal to driver '
                            'profile first name',
                            'qc_pass last name is not equal to driver '
                            'profile last name',
                            'qc_pass middle name is not equal to driver '
                            'profile middle name',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': None,
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_fms_score': None,
                            'registration_from_screen_score': None,
                            'registration_is_russian_score': None,
                        },
                        'driver_profile': {
                            'full_name': {
                                'first_name': 'Брюс',
                                'last_name': 'Иванов',
                                'middle_name': 'Мефодиевич',
                            },
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '3949857363_pd_id',
                                'old_value': None,
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'татьяна',
                                'old_value': '',
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'николаевна',
                                'old_value': '',
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'андреева',
                                'old_value': '',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id2',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '',
                            'last_name': 'андреева',
                            'number': '3949857363',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'with_small_confidence',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '1970-04-01',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {
                'passport': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'name',
                        'Text': 'татьяна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'number',
                        'Text': '3949857363',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'first_name': 'Брюс',
                        'last_name': 'Иванов',
                        'middle_name': 'Мефодиевич',
                    },
                    'license_driver_birth_date': '1970-04-01T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
                                {
                                    'confidence': 0.1,
                                    'text': 'татьяна',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.1,
                                    'text': 'николаевна',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.1,
                                    'text': 'андреева',
                                    'type': 'surname',
                                },
                                {
                                    'confidence': 0.1,
                                    'text': '25.11.1968',
                                    'type': 'birth_date',
                                },
                                {
                                    'confidence': 0.1,
                                    'text': '3949857363',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.1,
                                    'text': '17.01.2014',
                                    'type': 'issue_date',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1970-04-01',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '*****34522',
                            'patronymic': 'Мефодиевич',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'field first_name is not recognized in title',
                            'field patronymic is not recognized in title',
                            'field last_name is not recognized in title',
                            'field date_of_birth is not recognized in title',
                            'field number is not recognized in title',
                            'field issue_date is not recognized in title',
                            'field issuer is not recognized in title',
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score '
                            'reached threshold',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'passport obtained before 45, driver is older '
                            'than 45 now',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': {
                            'features': [
                                -234522,
                                -184522,
                                -134522,
                                -84522,
                                -34522,
                                65478,
                                165478,
                                265478,
                                365478,
                                465478,
                                5636,
                                5636,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                5637,
                                -0.024031860550396123,
                                -0.0305437833971017,
                                -0.04190392649529445,
                                -0.06669269539291546,
                                -0.16328717919008168,
                                0.08608998442224869,
                                0.034064951232187966,
                                0.021233397871010026,
                                0.015423636990461806,
                                0.012110131950382188,
                                '0910',
                                234522,
                                1216,
                            ],
                            'is_valid_by_real_fms': None,
                        },
                        'catboost_features': DEFAULT_CATBOOST_FEATURES,
                        'driver_profile': {
                            'full_name': {
                                'first_name': 'Брюс',
                                'last_name': 'Иванов',
                                'middle_name': 'Мефодиевич',
                            },
                            'license_driver_birth_date': (
                                '1970-04-01T00:00:00.000'
                            ),
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id2',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1970-04-01',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'with_some_none_from_ocr',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id2',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {
                'passport': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.9,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.9,
                        'Type': 'number',
                        'Text': '3949857363',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.9,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'first_name': 'Брюс',
                        'last_name': 'Иванов',
                        'middle_name': 'Мефодиевич',
                    },
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                },
            },
            [
                {
                    'additional_info': {
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
                                {
                                    'confidence': 0.9,
                                    'text': '25.11.1968',
                                    'type': 'birth_date',
                                },
                                {
                                    'confidence': 0.9,
                                    'text': '3949857363',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.9,
                                    'text': '17.01.2014',
                                    'type': 'issue_date',
                                },
                            ],
                        },
                        'face_saas_features': DEFAULT_FACE_SAAS_FEATURES,
                        'qc_pass': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'Брюс',
                            'issue_date': '2014-01-17',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '*****57363',
                            'patronymic': 'Мефодиевич',
                            'permanent_address': 'ул. Пушкина, д. 17',
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_picture_url': None,
                            },
                            'type': 'passport_rus',
                            'is_invited': False,
                            'was_blocked': False,
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'field first_name is not recognized in title',
                            'field patronymic is not recognized in title',
                            'field last_name is not recognized in title',
                            'field issuer is not recognized in title',
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score '
                            'reached threshold',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'catboost quasi_fms_score is None',
                        ],
                        'skip_verdict_because_of_percent': False,
                        'quasi_fms_features': None,
                        'catboost_features': {
                            **DEFAULT_CATBOOST_FEATURES,
                            'quasi_fms_score': None,
                        },
                        'driver_profile': {
                            'license_driver_birth_date': (
                                '1968-11-25T00:00:00.000'
                            ),
                            'full_name': {
                                'first_name': 'Брюс',
                                'last_name': 'Иванов',
                                'middle_name': 'Мефодиевич',
                            },
                            'license': {'pd_id': 'SomeNumber_pd_id'},
                        },
                        'has_inn_in_fns': True,
                        'license_number_pd_id': 'SomeNumber_pd_id',
                        'message_keys': [],
                        'reason': None,
                        'verdict_info': None,
                        'invite_exam_request': None,
                        'invite_comment': None,
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '3949857363_pd_id',
                                'old_value': '0910234522_pd_id',
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1968-11-25',
                                'old_value': '01.04.1970',
                            },
                            {
                                'field_name': 'issue_date',
                                'new_value': '2014-01-17',
                                'old_value': '2004-05-01',
                            },
                        ],
                        'history_features': [],
                        'is_courier': False,
                    },
                    'entity_id': 'somepark_somedriver',
                    'entity_type': 'driver',
                    'exam': 'identity',
                    'pass_id': 'some_pass_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id2',
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'Брюс',
                            'issue_date': '2014-01-17',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '3949857363',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id2',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_resolution_data(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_quality_control_py3,
        mock_qc_invites,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_selfemployed(mock_selfemployed)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'passport_is_valid_in_fns,expected_verdicts_db_content,'
    'expected_nirvana_identity_set_calls',
    [
        (
            'passport_is_not_valid',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
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
                        'Text': (
                            'с.бичурча бантево шемуршинского '
                            'р-на чувашской асср'
                        ),
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
                        'Text': (
                            'отделом уфмс россии по г. москве по району митино'
                        ),
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                },
            },
            False,
            [
                {
                    'additional_info': {
                        'verdict': 'unknown',
                        'errors': [
                            'catboost title_from_screen_score reached '
                            'threshold',
                            'catboost selfie_from_screen_score reached '
                            'threshold',
                            'catboost registration_from_screen_score '
                            'reached threshold',
                            'catboost selfie_bad_format_score reached '
                            'threshold',
                            'passport is not valid according to FNS',
                        ],
                        'has_inn_in_fns': False,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_fns(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_quality_control_py3,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        passport_is_valid_in_fns,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_selfemployed(mock_selfemployed, passport_is_valid_in_fns)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.has_inn_in_fns': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'face_saas_features,expected_verdicts_db_content,'
    'expected_nirvana_identity_set_calls',
    [
        (
            'mistakes pass selfie duplicates',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {'passport': []},
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
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
                                        'exam': 'identity',
                                        'confidence': 0.99,
                                        'photo_number_by_size': 1,
                                        'picture_type': 'selfie',
                                    },
                                ),
                            },
                            'relevance': '995027688',
                        },
                    ],
                },
            ],
            [
                {
                    'additional_info': {
                        'face_saas_features': [
                            {
                                'confidence': 0.9,
                                'height': 0.7678670883,
                                'layer_name': 'super_face_layer',
                                'saas_info': [
                                    {
                                        'metainfo': {
                                            'confidence': 0.99,
                                            'driver_id': 'some_driver_id',
                                            'driver_license': '0133741979',
                                            'exam': 'identity',
                                            'pass_modified': 1514616129.840873,
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'uberdriver_driver_id': None,
                                        },
                                        'similarity': 0.995027688,
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
                                            'confidence': 0.99,
                                            'driver_id': 'some_driver_id',
                                            'driver_license': '0133741979',
                                            'exam': 'identity',
                                            'pass_modified': 1514616129.840873,
                                            'photo_number_by_size': 1,
                                            'picture_type': 'selfie',
                                            'uberdriver_driver_id': None,
                                        },
                                        'similarity': 0.995027688,
                                    },
                                ],
                                'width': 0.15700639635,
                            },
                        ],
                        'verdict': 'mistakes',
                        'errors': [],
                        'message_keys': ['identity_fake_document'],
                        'reason': 'selfie_duplicates',
                        'verdict_info': {
                            'selfie_duplicate': {
                                'driver_id': 'some_driver_id',
                                'driver_license': '0133741979',
                                'exam': 'identity',
                                'park_id': None,
                                'pass_id': None,
                                'picture_type': 'selfie',
                            },
                        },
                        'invite_exam_request': {
                            'license_pd_id': 'SomeNumber_pd_id',
                            'park_id': 'somepark',
                            'comment_for_assessors': (
                                'Подозрение на дубли по '
                                'лицу: 0133741979;some_driver_id.'
                            ),
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id',
                        'status': 'mistakes',
                        'message_keys': ['identity_fake_document'],
                    },
                ],
            ],
        ),
    ],
)
async def test_selfie_duplicates(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_qc_invites,
        mock_quality_control_py3,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        face_saas_features,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_get_saas_response(
        patch_aiohttp_session, response_mock, face_saas_features,
    )
    _mock_selfemployed(mock_selfemployed)
    _mock_qc_invites(mock_qc_invites)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.message_keys': True,
                'additional_info.invite_exam_request': True,
                'additional_info.face_saas_features': True,
                'additional_info.reason': True,
                'additional_info.verdict_info': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'expected_verdicts_db_content,expected_nirvana_identity_set_calls',
    [
        (
            'mistakes pass selfie duplicates',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_MISTAKES_SELFIE_FORMAT_THRESHOLD': (  # noqa: E501 pylint: disable=line-too-long
                    0.3
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {'passport': []},
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'SomeNumber_pd_id'},
                },
            },
            [
                {
                    'additional_info': {
                        'verdict': 'mistakes',
                        'errors': [],
                        'message_keys': ['identity_not_able_to_compare_faces'],
                        'reason': 'photo_quality',
                        'verdict_info': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id',
                        'status': 'mistakes',
                        'message_keys': ['identity_not_able_to_compare_faces'],
                    },
                ],
            ],
        ),
    ],
)
async def test_bad_selfie_format(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_qc_invites,
        mock_quality_control_py3,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_selfemployed(mock_selfemployed)
    _mock_qc_invites(mock_qc_invites)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.errors': True,
                'additional_info.message_keys': True,
                'additional_info.reason': True,
                'additional_info.verdict_info': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_identity_get_response,ocr_response,driver_profile,'
    'history_features,expected_verdicts_db_content,'
    'expected_nirvana_identity_set_calls',
    [
        (
            'first courier pass',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'was_blocked': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {
                'passport': [
                    {
                        'Confidence': 0.8776330352,
                        'Type': 'name',
                        'Text': 'татьяна',
                    },
                    {
                        'Confidence': 0.8884754181,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'Confidence': 0.886099577,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'Confidence': 0.8965250254,
                        'Type': 'subdivision',
                        'Text': '770-093',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8886011243,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8992502093,
                        'Type': 'number',
                        'Text': '0910234523',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.899061203,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'COURIER_pd_id'},
                },
            },
            [],
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'history_features': [],
                        'is_courier': True,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'not first courier pass',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': (
                    SUCCESSFUL_CATBOOST_MODELS
                ),
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    False
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityTitle': 'http://example.com/file.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'was_blocked': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {
                'passport': [
                    {
                        'Confidence': 0.8776330352,
                        'Type': 'name',
                        'Text': 'татьяна',
                    },
                    {
                        'Confidence': 0.8884754181,
                        'Type': 'middle_name',
                        'Text': 'николаевна',
                    },
                    {
                        'Confidence': 0.886099577,
                        'Type': 'surname',
                        'Text': 'андреева',
                    },
                    {
                        'Confidence': 0.8965250254,
                        'Type': 'subdivision',
                        'Text': '770-093',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8886011243,
                        'Type': 'birth_date',
                        'Text': '25.11.1968',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8992502093,
                        'Type': 'number',
                        'Text': '0910234523',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.899061203,
                        'Type': 'issue_date',
                        'Text': '17.01.2014',
                    },
                ],
            },
            {
                'park_driver_profile_id': 'somepark_somedriver',
                'data': {
                    'full_name': {
                        'last_name': 'Андреева',
                        'first_name': 'Татьяна',
                        'middle_name': 'Николаевна',
                    },
                    'license_driver_birth_date': '1968-11-25T00:00:00.000',
                    'license': {'pd_id': 'COURIER_pd_id'},
                },
            },
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'identity',
                    'id': 'some_pass_id',
                    'status': 'NEW',
                },
                {
                    'assessor': 'someone',
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'identity',
                    'id': 'some_pass_id',
                    'status': 'RESOLVED',
                },
            ],
            [
                {
                    'additional_info': {
                        'verdict': 'success',
                        'history_features': [
                            {
                                'entity_id': 'some_entity_id',
                                'modified': '2020-01-01T00:00:00',
                                'pass_id': 'some_pass_id',
                            },
                            {
                                'entity_id': 'some_entity_id',
                                'modified': '2020-01-01T00:00:00',
                                'pass_id': 'some_pass_id',
                            },
                        ],
                        'is_courier': True,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '1968-11-25',
                            'first_name': 'татьяна',
                            'issue_date': '2014-01-17',
                            'issuer': '770-093',
                            'last_name': 'андреева',
                            'number': '0910234523',
                            'patronymic': 'николаевна',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_courier(
        mock_taximeter_xservice,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_selfemployed,
        mock_qc_invites,
        mock_quality_control_py3,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        driver_profile,
        history_features,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, driver_profile)
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_selfemployed(mock_selfemployed)
    _mock_qc_invites(mock_qc_invites)
    _mock_quality_control_history(mock_quality_control_py3, history_features)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.verdict': True,
                'additional_info.history_features': True,
                'additional_info.is_courier': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_identity_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_identity_set_calls',
    [
        (
            'front instead of title',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityFront': 'http://example.com/file_front.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'last_name': 'Иванов',
                        'first_name': 'Брюс',
                        'patronymic': 'Мефодиевич',
                        'date_of_birth': '01.04.1970',
                        'number': '0910234522',
                        'issuer': 'УВД Первоуральска',
                        'issue_date': '05/01/2004 00:00:00',
                        'permanent_address': 'ул. Пушкина, д. 17',
                        'type': 'passport_rus',
                        'was_blocked': 'True',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {'passport': []},
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'pictures_urls': {
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file_front.jpg'
                                ),
                                'back_picture_url': None,
                            },
                        },
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'date_of_birth': '01.04.1970',
                            'first_name': 'Брюс',
                            'issue_date': '2004-05-01',
                            'issuer': 'УВД Первоуральска',
                            'last_name': 'Иванов',
                            'number': '0910234522',
                            'patronymic': 'Мефодиевич',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_front_instead_of_title(
        mock_taximeter_xservice,
        patch_aiohttp_session,
        response_mock,
        taxi_config,
        cron_context,
        db,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_qc_invites,
        mock_quality_control_py3,
        mock_selfemployed,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, {})
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_selfemployed(mock_selfemployed)
    _mock_qc_invites(mock_qc_invites)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {}, {'_id': False, 'additional_info.qc_pass.pictures_urls': True},
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_identity_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_identity_set_calls',
    [
        (
            'pass with type id_kaz_stripped',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'IdentityFront': 'http://example.com/file_front.jpg',
                        'IdentityRegistration': 'http://example.com/file.jpg',
                        'IdentitySelfie': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'type': 'id_kaz_stripped',
                        'was_blocked': 'False',
                    },
                    'pass_id': 'some_pass_id',
                    'entity_id': 'somepark_somedriver',
                },
            ],
            {
                'passport_kaz': [
                    {'Type': 'name', 'Text': 'атабек', 'Confidence': 0.7},
                    {'Type': 'surname', 'Text': 'атабеков', 'Confidence': 0.7},
                    {
                        'Type': 'middle_name',
                        'Text': 'атабекулы',
                        'Confidence': 0.7,
                    },
                    {
                        'Type': 'number',
                        'Text': '111222333444',
                        'Confidence': 0.7,
                    },
                    {
                        'Type': 'birth_date',
                        'Text': '01-02-1993',
                        'Confidence': 0.7,
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'date_of_birth': '1993-02-01',
                            'first_name': 'атабек',
                            'is_invited': False,
                            'issue_date': None,
                            'issuer': None,
                            'last_name': 'атабеков',
                            'number': '******333444',
                            'patronymic': 'атабекулы',
                            'permanent_address': None,
                            'pictures_urls': {
                                'back_picture_url': None,
                                'registration_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'selfie_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'title_picture_url': (
                                    'http://example.com/file_front.jpg'
                                ),
                            },
                            'type': 'id_kaz_stripped',
                            'was_blocked': False,
                        },
                        'changes': [
                            {
                                'field_name': 'number_pd_id',
                                'new_value': '111222333444_pd_id',
                                'old_value': None,
                            },
                            {
                                'field_name': 'firstname',
                                'new_value': 'атабек',
                                'old_value': None,
                            },
                            {
                                'field_name': 'middlename',
                                'new_value': 'атабекулы',
                                'old_value': None,
                            },
                            {
                                'field_name': 'lastname',
                                'new_value': 'атабеков',
                                'old_value': None,
                            },
                            {
                                'field_name': 'date_of_birth',
                                'new_value': '1993-02-01',
                                'old_value': None,
                            },
                        ],
                        'ocr_responses': {
                            'back_recognized_text_by_dkvu_front_model': None,
                            'title_recognized_text': [
                                {
                                    'confidence': 0.7,
                                    'text': 'атабек',
                                    'type': 'name',
                                },
                                {
                                    'confidence': 0.7,
                                    'text': 'атабеков',
                                    'type': 'surname',
                                },
                                {
                                    'confidence': 0.7,
                                    'text': 'атабекулы',
                                    'type': 'middle_name',
                                },
                                {
                                    'confidence': 0.7,
                                    'text': '111222333444',
                                    'type': 'number',
                                },
                                {
                                    'confidence': 0.7,
                                    'text': '01-02-1993',
                                    'type': 'birth_date',
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
                            'date_of_birth': '1993-02-01',
                            'first_name': 'атабек',
                            'last_name': 'атабеков',
                            'number': '111222333444',
                            'patronymic': 'атабекулы',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_id_kaz_stripped_identies(
        mock_taximeter_xservice,
        patch_aiohttp_session,
        response_mock,
        taxi_config,
        cron_context,
        db,
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_driver_profiles,
        mock_qc_invites,
        mock_quality_control_py3,
        mock_selfemployed,
        comment,
        config,
        nirvana_identity_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_identity_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_identity_get(
        mock_taximeter_xservice, nirvana_identity_get_response,
    )
    nirvana_identity_set = _mock_nirvana_identity_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_driver_profile(mock_driver_profiles, {})
    _mock_get_saas_response(patch_aiohttp_session, response_mock, [])
    _mock_selfemployed(mock_selfemployed)
    _mock_qc_invites(mock_qc_invites)
    _mock_quality_control_history(mock_quality_control_py3)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_identity_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass': True,
                'additional_info.changes': True,
                'additional_info.ocr_responses': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert (
        mock.get_requests(nirvana_identity_set)
        == expected_nirvana_identity_set_calls
    )
