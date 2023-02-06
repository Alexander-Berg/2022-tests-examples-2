# pylint: disable=too-many-lines
import base64
import datetime

from aiohttp import web
import pytest

from taxi_antifraud.crontasks import resolve_sts_qc_passes
from taxi_antifraud.generated.cron import run_cron
from taxi_antifraud.settings import qc_settings
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = resolve_sts_qc_passes.CURSOR_STATE_NAME


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['ANTIFRAUD_OCR_API_KEY'] = 'token'
    simple_secdist['settings_override'][
        'TAXIMETER_XSERVICE_NIRVANA_API_KEY'
    ] = 'another_token'
    simple_secdist['settings_override'][
        'ANTIFRAUD_AVTOCOD_API_KEY'
    ] = 'one_more_token'
    return simple_secdist


def _mock_nirvana_sts_get(mock_taximeter_xservice, response_items):
    @mock_taximeter_xservice('/utils/nirvana/sts/get')
    async def _nirvana_sts_get(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '666666666666666666':
            return web.json_response(data=dict(items=[]))
        return web.json_response(
            data=dict(cursor=666666666666666666, items=response_items),
        )

    return _nirvana_sts_get


def _mock_nirvana_sts_set(mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/nirvana/sts/set')
    async def _nirvana_sts_set(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    return _nirvana_sts_set


def _mock_avtocod(patch_aiohttp_session, response_mock, content=None):
    @patch_aiohttp_session(
        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
        'yandex_project_check_auto_report_v2@yandex_project/_make',
        'POST',
    )
    def _make_report(method, url, json, **kwargs):
        assert (
            url == 'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
            'yandex_project_check_auto_report_v2@yandex_project/_make'
        )
        return response_mock(
            json={
                'size': 1,
                'stamp': '2017-01-18T15:23:12Z',
                'state': 'ok',
                'data': [
                    {
                        'uid': 'default_uid@default',
                        'isnew': False,
                        'process_request_uid': (
                            'default_process_request_uid@default'
                        ),
                        'suggest_get': '2020-02-21T18:41:47.145Z',
                    },
                ],
            },
        )

    if content is None:
        content = {
            'identifiers': {
                'vehicle': {'vin': '5TDDKRFH80S073711', 'sts': '56778'},
            },
            'tech_data': {
                'brand': {'id': 'ID_MARK_AC', 'name': {'normalized': 'AC'}},
                'body': {
                    'color': {'name': 'Желтый', 'type': '11'},
                    'number': 'Z94СВ41ААGR323020',
                },
                'year': 2021,
                'model': {
                    'id': 'ID_MARK_AC_ZAGATO',
                    'name': {'normalized': '378 GT Zagato'},
                },
            },
        }

    @patch_aiohttp_session(
        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
        'default_uid@default',
        'GET',
    )
    def _get_report(method, url, params, **kwargs):
        assert (
            url == 'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
            'default_uid@default'
        )
        return response_mock(
            json={
                'size': 1,
                'stamp': '2017-01-18T15:23:12Z',
                'state': 'ok',
                'data': [
                    {
                        'domain_uid': 'some_domain_uid',
                        'report_type_uid': 'some_report_uid_1@some_domain_uid',
                        'vehicle_id': '5TDDKRFH80S073711',
                        'query': {
                            'type': 'VIN',
                            'body': '5TDDKRFH80S073711',
                            'data': {
                                'messageId': 703182,
                                'from': {
                                    'id': 273893635,
                                    'firstName': 'Alesha',
                                },
                                'date': 1562495577,
                                'chat': {
                                    'id': 273893635,
                                    'firstName': 'Alesha',
                                },
                                'text': '5TDDKRFH80S073711',
                            },
                        },
                        'progress_ok': 4,
                        'progress_wait': 0,
                        'progress_error': 0,
                        'state': {
                            'sources': [
                                {
                                    '_id': 'references.base',
                                    'state': 'OK',
                                    'data': {
                                        'from_cache': False,
                                        'real_status': 'OK',
                                    },
                                },
                                {
                                    '_id': 'images.avtonomer',
                                    'state': 'OK',
                                    'data': {
                                        'from_cache': False,
                                        'real_status': 'OK',
                                    },
                                },
                                {
                                    '_id': 'base',
                                    'state': 'OK',
                                    'data': {
                                        'from_cache': False,
                                        'real_status': 'OK',
                                    },
                                },
                                {
                                    '_id': 'sub.base',
                                    'state': 'OK',
                                    'data': {
                                        'from_cache': False,
                                        'real_status': 'OK',
                                    },
                                },
                            ],
                        },
                        'content': content,
                        'uid': 'report_uid_DK3711@some_domain_uid',
                        'name': 'NONAME',
                        'comment': '',
                        'tags': '',
                        'created_at': '2019-07-07T10:51:46.067Z',
                        'created_by': 'system',
                        'updated_at': '2019-07-07T10:51:55.167Z',
                        'updated_by': 'manager',
                        'active_from': '1900-01-01T00:00:00.000Z',
                        'active_to': '3000-01-01T00:00:00.000Z',
                    },
                ],
            },
        )

    @patch_aiohttp_session(
        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
        'default_uid@default/_refresh',
        'POST',
    )
    def _refresh_report(method, url, json, **kwargs):
        assert (
            url == 'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
            'default_uid@default/_refresh'
        )
        return response_mock(
            json={
                'size': 1,
                'stamp': '2017-01-18T15:23:12Z',
                'state': 'ok',
                'data': [
                    {
                        'uid': 'default_uid@default',
                        'isnew': True,
                        'process_request_uid': (
                            'default_process_request_uid@default'
                        ),
                        'suggest_get': '2021-02-21T18:41:47.151Z',
                    },
                ],
            },
        )

    return _make_report, _refresh_report, _get_report


def _mock_yavtocod(
        mock_antifraud_py,
        vin='X9FMXXEEBMCG00947',
        year='2016',
        color='КОРИЧНЕВЫЙ',
        model='ФОЛЬКСВАГЕН ПОЛО ',
):
    @mock_antifraud_py('/yavtocod/v1/get_info_by_vin')
    async def _by_vin(request):
        assert request.method == 'POST'

        return web.json_response(
            data={
                'body_number': 'XW8ZZZ61ZGG032947',
                'color': color,
                'year': year,
                'model': model,
            },
        )

    @mock_antifraud_py('/yavtocod/v1/get_info_by_car_number')
    async def _by_car_number(request):
        assert request.method == 'POST'

        return web.json_response(
            data={
                'sources': [
                    {'name': 'vin01', 'data': [{'name': 'vin', 'value': vin}]},
                    {
                        'name': 'avto_yslyga',
                        'data': [
                            {'name': 'vin', 'value': 'X9FMXXEEBMCG00947'},
                        ],
                    },
                    {
                        'name': 'mafin',
                        'data': [
                            {'name': 'brand', 'value': 'Ford'},
                            {'name': 'model', 'value': 'Focus'},
                            {'name': 'year', 'value': '2012'},
                        ],
                    },
                    {
                        'name': 'insurance_mts',
                        'data': [
                            {'name': 'brand_name', 'value': 'Ford'},
                            {'name': 'model_name', 'value': 'Focus'},
                            {'name': 'brand_code', 'value': 'Ford'},
                            {'name': 'model_code', 'value': 'Focus'},
                            {'name': 'year', 'value': '2012'},
                            {'name': 'vin', 'value': 'X9FMXXEEBMCG00947'},
                            {
                                'name': 'identity_number',
                                'value': '4853-668956',
                            },
                            {
                                'name': 'identity_issue_date',
                                'value': '2018-01-19',
                            },
                            {'name': 'identity_type', 'value': 'STS'},
                        ],
                    },
                ],
            },
        )

    return _by_vin, _by_car_number


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
        if 'VehicleCertificateRegistrationFront' in data['meta']:
            response = {
                'data': {
                    'fulltext': ocr_response['sts_front'],
                    'max_line_confidence': 1,
                },
            }
        elif 'VehicleCertificateRegistrationBack' in data['meta']:
            response = {
                'data': {
                    'fulltext': ocr_response['sts_back'],
                    'max_line_confidence': 1,
                },
            }
        elif 'PlatesOcr' in data['meta']:
            response = {
                'data': {
                    'fulltext': ocr_response['plates'],
                    'max_line_confidence': 0.9785078764,
                },
            }
        elif 'FullOcrMultihead' in data['meta']:
            response = {
                'data': {
                    'fulltext': ocr_response['full'],
                    'max_line_confidence': 0.83974534,
                },
            }
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
    def _get_model_one_categorial(method, url, **kwargs):
        b64_model = """
Q0JNMbgBAAAEAAAAYP7//wgAAABIAAAAEgAAAEZsYWJ1ZmZlcnNNb2RlbF92MQAAAAAqAEgABAAIAA
wAEAAUABgAHAAgACQAKAAsADAANAA4AAAAAAA8AEAARAAqAAAAAQAAAJAAAACEAAAAeAAAADQBAADA
AAAAlAAAAIwAAABMAAAAMAAAAHwAAAAkAAAAoAAAAJQAAAAMAAAAYAAAAIwAAAABAAAAAAAAAAAAAA
AAAAAAAgAAAAAAAAAAAPA/AAAAAAAA8D8AAAAAAgAAABQ7sRM7scM/FDuxEzuxw78AAAAAAQAAAAAA
AAABAAAAAQAAAAEAAAAAAAAAAQAAAAAA/v8AAAAAAAAAAAEAAAAEAAAAaP///wAAAAAEAAAAAQAAAL
Lv9vIAAAAAAAAAAAAAAAAEAAAAWAAAADQAAAAcAAAABAAAAMT///8DAAAABAAAAAQAAAAAAAAA2P//
/wIAAAADAAAABAAAAAAAAADs////AQAAAAIAAAAEAAAAAAAAAAwAEAAAAAQACAAMAAwAAAAAAAAAAQ
AAAAQAAAAAAAAAAQAAAAwAAAAIAAwABAAIAAgAAAAAAAAAAAAAAA==
        """
        return response_mock(read=base64.b64decode(b64_model))

    @patch_aiohttp_session(
        'https://storage.yandex-team.ru/get-devtools/model_two.bin', 'GET',
    )
    def _get_model_with_two_categorial(method, url, **kwargs):
        b64_model = """
Q0JNMcgBAAAMAAAACAAMAAQACAAIAAAACAAAAEgAAAASAAAARmxhYnVmZmVyc01vZGVsX3YxAAAAAC
oASAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAAAAAADwAQABEACoAAAABAAAAkAAAAIQAAAB4
AAAAIAEAAKgAAACUAAAAjAAAAEwAAAAwAAAAfAAAACQAAACIAAAAfAAAAAwAAABgAAAAdAAAAAEAAA
AAAAAAAAAAAAAAAAACAAAAAAAAAAAA8D8AAAAAAADwPwAAAAACAAAAFDuxEzuxw78UO7ETO7HDPwAA
AAABAAAAAAAAAAEAAAABAAAAAQAAAAAAAAABAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
QAAABYAAAANAAAABwAAAAEAAAAxP///wMAAAAFAAAABAAAAAAAAADY////AgAAAAQAAAAEAAAAAAAA
AOz///8BAAAAAwAAAAQAAAAAAAAADAAQAAAABAAIAAwADAAAAAAAAAACAAAABAAAAAEAAAAAAABAAg
AAACQAAAAEAAAA8P///wAAAAABAAAAAQAAAAwAEAAIAAwAAAAHAAwAAAAAAAAAAAAAAAAAAAA=
        """
        return response_mock(read=base64.b64decode(b64_model))

    return (
        _get_model_without_categorial,
        _get_model_one_categorial,
        _get_model_with_two_categorial,
    )


def _mock_get_features(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(qc_settings.CBIR_URL, 'POST')
    def _get_features(method, url, params, **kwargs):
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


def _mock_quality_control_history(mock_quality_control_py3, qc_history=None):
    @mock_quality_control_py3('/api/v1/pass/history')
    async def _api_v1_pass_history(request):
        assert request.method == 'POST'

        if qc_history is None:
            return web.json_response(data=dict(cursor='end', items=[]))
        return web.json_response(data=dict(cursor='end', items=qc_history))

    return _api_v1_pass_history


def _mock_qc_invites_info(mock_qc_invites):
    @mock_qc_invites('/api/qc-invites/v1/invite_info')
    async def _qc_invites_find(request):
        assert request.method == 'GET'

        return web.json_response(
            data=dict(comment='[allow auto verdict] Регулярный вызов'),
        )

    return _qc_invites_find


DEFAULT_CONFIG: dict = {
    'AFS_CRON_CURSOR_USE_PGSQL': 'enabled',
    'AFS_CRON_RESOLVE_STS_QC_PASSES_EMPTY_BATCH_SLEEP_TIME': 0.01,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_EMPTY_BATCHES_LIMIT': 3,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_ENABLED': True,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_RESOLUTION_ENABLED': True,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_BRANDS_MAP': [
        {'car_brand': 'AC', 'avtocod_brand_id': 'ID_MARK_AC'},
    ],
    'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_MODELS_MAP': [
        {
            'car_brand_model': 'AC_378 GT Zagato',
            'avtocod_model_id': 'ID_MARK_AC_ZAGATO',
        },
    ],
    'AFS_CRON_RESOLVE_STS_QC_PASSES_MISTAKES_STATUS_ENABLED': True,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_ENABLED': True,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_REPORT_ERRORS_SLEEP': 0.01,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_AFTER_MAKE_SLEEP': 0.01,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_RESOLUTION_DATA_ENABLED': True,
    'AFS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
        'is_car_color_correct_front_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
            'threshold': 0.4,
        },
        'is_car_color_correct_back_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
            'threshold': 0.4,
        },
        'is_car_color_correct_left_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
            'threshold': 0.4,
        },
        'is_car_color_correct_right_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_one.bin',
            'threshold': 0.4,
        },
        'is_car_brand_correct_front_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_two.bin',
            'threshold': 0.4,
        },
        'is_car_brand_correct_back_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_two.bin',
            'threshold': 0.4,
        },
        'is_car_brand_correct_left_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_two.bin',
            'threshold': 0.4,
        },
        'is_car_brand_correct_right_v9_rot': {
            'url': 'https://storage.yandex-team.ru/get-devtools/model_two.bin',
            'threshold': 0.4,
        },
        'is_car_photo_bad_front_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'is_car_photo_bad_back_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'is_car_photo_bad_left_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'is_car_photo_bad_right_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'is_sts_photo_bad_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'car_photo_from_screen_with_sts_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'sts_photo_from_screen_with_sts_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.6,
        },
        'front_sts_is_russian_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.4,
        },
        'back_sts_is_russian_v9_rot': {
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
            'threshold': 0.4,
        },
    },
    'AFS_CRON_RESOLVE_STS_QC_PASSES_SUCCESS_STATUS_ENABLED': True,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_COLOR_MAPPING': [],
    'AFS_CRON_RESOLVE_STS_QC_PASSES_VERDICTS_FOR_BLOCKED_ENABLED': False,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_VERDICTS_FOR_INVITED_ENABLED': False,
    'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_ENABLED': True,
    'PPS_CRON_COMMENTS_FOR_INVITES_TO_RESOLVE': [
        '[allow auto verdict] Регулярный вызов',
    ],
}


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_sts_get_response,ocr_response,'
    'expected_verdicts_db_content,'
    'expected_state_pgsql_content,expected_nirvana_sts_get_calls,'
    'expected_nirvana_sts_set_calls',
    [
        (
            'success verdict',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                    'entity_id': 'dbid_uuid',
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': '5TDDKRFH80S073711',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': 'Z94СВ41ААGR323020',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '56778',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '2021',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'СОБСТВЕННИК (владелец)',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'российская федерация',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                                'sts': '56778',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {
                                                'id': 'ID_MARK_AC',
                                                'name': {'normalized': 'AC'},
                                            },
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'year': 2021,
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                                'name': {
                                                    'normalized': (
                                                        '378 GT Zagato'
                                                    ),
                                                },
                                            },
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'yavtocod_report': {
                            'by_car_number': {
                                'sources': [
                                    {
                                        'data': [
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                        ],
                                        'name': 'vin01',
                                    },
                                    {
                                        'data': [
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                        ],
                                        'name': 'avto_yslyga',
                                    },
                                    {
                                        'data': [
                                            {'name': 'brand', 'value': 'Ford'},
                                            {
                                                'name': 'model',
                                                'value': 'Focus',
                                            },
                                            {'name': 'year', 'value': '2012'},
                                        ],
                                        'name': 'mafin',
                                    },
                                    {
                                        'data': [
                                            {
                                                'name': 'brand_name',
                                                'value': 'Ford',
                                            },
                                            {
                                                'name': 'model_name',
                                                'value': 'Focus',
                                            },
                                            {
                                                'name': 'brand_code',
                                                'value': 'Ford',
                                            },
                                            {
                                                'name': 'model_code',
                                                'value': 'Focus',
                                            },
                                            {'name': 'year', 'value': '2012'},
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                            {
                                                'name': 'identity_number',
                                                'value': '4853-668956',
                                            },
                                            {
                                                'name': 'identity_issue_date',
                                                'value': '2018-01-19',
                                            },
                                            {
                                                'name': 'identity_type',
                                                'value': 'STS',
                                            },
                                        ],
                                        'name': 'insurance_mts',
                                    },
                                ],
                            },
                            'by_vin': {
                                'body_number': 'XW8ZZZ61ZGG032947',
                                'color': 'КОРИЧНЕВЫЙ',
                                'model': 'ФОЛЬКСВАГЕН ' 'ПОЛО ',
                                'year': '2016',
                            },
                        },
                        'qc_pass': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'brand': 'AC',
                            'car_id': '642a1f0353b28c52c127975826f81ebd',
                            'color': 'Желтый',
                            'country': 'Россия',
                            'db_id': '7ad36bc7560449998acbe2c57a75c293',
                            'entity_id': 'dbid_uuid',
                            'is_invited': False,
                            'model': '378 GT Zagato',
                            'number': 'А001ВВ00',
                            'pictures_urls': {
                                'back_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'left_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'right_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'was_blocked': False,
                            'year': '2021',
                        },
                        'ocr_responses': {
                            'back_car_recognized_text': [
                                {
                                    'confidence': 0.7724065185,
                                    'text': 'А001ВВ00\n',
                                    'type': 'text',
                                },
                            ],
                            'back_sts_back_strategy': [],
                            'back_sts_front_strategy': [
                                {
                                    'confidence': 0.1494631618,
                                    'text': '5TDDKRFH80S073711',
                                    'type': 'stsfront_vin_number',
                                },
                            ],
                            'front_car_recognized_text': [
                                {
                                    'confidence': 0.7724065185,
                                    'text': 'А001ВВ00\n',
                                    'type': 'text',
                                },
                            ],
                            'front_sts_back_strategy': [],
                            'front_sts_front_strategy': [
                                {
                                    'confidence': 0.1494631618,
                                    'text': '5TDDKRFH80S073711',
                                    'type': 'stsfront_vin_number',
                                },
                            ],
                            'front_sts_full_model_text': (
                                ' 9911 725289'
                                'Z94СВ41ААGR323020567782021чные номера '
                                'автомобиля сверены, техническоеСОБСТВЕННИК'
                                ' (владелец)российская федерация'
                            ),
                            'back_sts_full_model_text': (
                                ' 9911 725289'
                                'Z94СВ41ААGR323020567782021чные номера '
                                'автомобиля сверены, техническоеСОБСТВЕННИК'
                                ' (владелец)российская федерация'
                            ),
                        },
                        'verdict': 'success',
                        'errors': [],
                        'changes': [],
                        'message_keys': [],
                        'catboost_features': {
                            'front_photo_has_correct_color': (
                                0.5383858565626407
                            ),
                            'back_photo_has_correct_color': 0.5383858565626407,
                            'left_photo_has_correct_color': 0.5383858565626407,
                            'right_photo_has_correct_color': (
                                0.5383858565626407
                            ),
                            'front_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'back_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'left_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'right_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'front_photo_has_bad_format': 0.46161414343735935,
                            'back_photo_has_bad_format': 0.46161414343735935,
                            'left_photo_has_bad_format': 0.46161414343735935,
                            'right_photo_has_bad_format': 0.46161414343735935,
                            'sts_photo_has_bad_format': 0.46161414343735935,
                            'front_car_photo_from_screen': 0.46161414343735935,
                            'back_car_photo_from_screen': 0.46161414343735935,
                            'left_car_photo_from_screen': 0.46161414343735935,
                            'right_car_photo_from_screen': 0.46161414343735935,
                            'front_sts_photo_from_screen': 0.46161414343735935,
                            'back_sts_photo_from_screen': 0.46161414343735935,
                            'front_sts_is_russian': 0.46161414343735935,
                            'back_sts_is_russian': 0.46161414343735935,
                        },
                        'reason': None,
                        'invite_comment': None,
                    },
                    'entity_id': '642a1f0353b28c52c127975826f81ebd',
                    'entity_type': 'car',
                    'exam': 'sts',
                    'pass_id': '6021b864fa207cb60a4f3498',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            {'resolve_sts_qc_passes_cursor': '666666666666666666'},
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
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'success',
                    },
                ],
            ],
        ),
        (
            'successful_pass_with_unknown_verdict',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': 'Z94CT41DAHR509509',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                                'sts': '56778',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {
                                                'id': 'ID_MARK_AC',
                                                'name': {'normalized': 'AC'},
                                            },
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'year': 2021,
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                                'name': {
                                                    'normalized': (
                                                        '378 GT Zagato'
                                                    ),
                                                },
                                            },
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'yavtocod_report': {
                            'by_car_number': {
                                'sources': [
                                    {
                                        'data': [
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                        ],
                                        'name': 'vin01',
                                    },
                                    {
                                        'data': [
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                        ],
                                        'name': 'avto_yslyga',
                                    },
                                    {
                                        'data': [
                                            {'name': 'brand', 'value': 'Ford'},
                                            {
                                                'name': 'model',
                                                'value': 'Focus',
                                            },
                                            {'name': 'year', 'value': '2012'},
                                        ],
                                        'name': 'mafin',
                                    },
                                    {
                                        'data': [
                                            {
                                                'name': 'brand_name',
                                                'value': 'Ford',
                                            },
                                            {
                                                'name': 'model_name',
                                                'value': 'Focus',
                                            },
                                            {
                                                'name': 'brand_code',
                                                'value': 'Ford',
                                            },
                                            {
                                                'name': 'model_code',
                                                'value': 'Focus',
                                            },
                                            {'name': 'year', 'value': '2012'},
                                            {
                                                'name': 'vin',
                                                'value': 'X9FMXXEEBMCG00947',
                                            },
                                            {
                                                'name': 'identity_number',
                                                'value': '4853-668956',
                                            },
                                            {
                                                'name': 'identity_issue_date',
                                                'value': '2018-01-19',
                                            },
                                            {
                                                'name': 'identity_type',
                                                'value': 'STS',
                                            },
                                        ],
                                        'name': 'insurance_mts',
                                    },
                                ],
                            },
                            'by_vin': {
                                'body_number': 'XW8ZZZ61ZGG032947',
                                'color': 'КОРИЧНЕВЫЙ',
                                'model': 'ФОЛЬКСВАГЕН ' 'ПОЛО ',
                                'year': '2016',
                            },
                        },
                        'qc_pass': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'brand': 'AC',
                            'car_id': '642a1f0353b28c52c127975826f81ebd',
                            'color': 'Желтый',
                            'country': 'Россия',
                            'db_id': '7ad36bc7560449998acbe2c57a75c293',
                            'entity_id': None,
                            'is_invited': False,
                            'model': '378 GT Zagato',
                            'number': 'А001ВВ00',
                            'pictures_urls': {
                                'back_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'left_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'right_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'was_blocked': False,
                            'year': '2021',
                        },
                        'ocr_responses': {
                            'back_car_recognized_text': [
                                {
                                    'confidence': 0.7724065185,
                                    'text': 'А001ВВ00\n',
                                    'type': 'text',
                                },
                            ],
                            'back_sts_back_strategy': [],
                            'back_sts_front_strategy': [
                                {
                                    'confidence': 0.1494631618,
                                    'text': 'Z94CT41DAHR509509',
                                    'type': 'stsfront_vin_number',
                                },
                            ],
                            'front_car_recognized_text': [
                                {
                                    'confidence': 0.7724065185,
                                    'text': 'А001ВВ00\n',
                                    'type': 'text',
                                },
                            ],
                            'front_sts_back_strategy': [],
                            'front_sts_front_strategy': [
                                {
                                    'confidence': 0.1494631618,
                                    'text': 'Z94CT41DAHR509509',
                                    'type': 'stsfront_vin_number',
                                },
                            ],
                            'front_sts_full_model_text': (
                                ' 9911 725289'
                                'чные номера автомобиля сверены, техническое'
                            ),
                            'back_sts_full_model_text': (
                                ' 9911 725289'
                                'чные номера автомобиля сверены, техническое'
                            ),
                        },
                        'verdict': 'unknown',
                        'errors': [
                            'there is no avtocod sts number in full and '
                            'specific ocr response',
                            'there is no qc pass vin in full and specific ocr',
                            'qc pass year is not found in full ocr response',
                            'keywords российская or владелец is not found'
                            ' in full ocr response',
                        ],
                        'changes': [],
                        'message_keys': [],
                        'catboost_features': {
                            'front_photo_has_correct_color': (
                                0.5383858565626407
                            ),
                            'back_photo_has_correct_color': 0.5383858565626407,
                            'left_photo_has_correct_color': 0.5383858565626407,
                            'right_photo_has_correct_color': (
                                0.5383858565626407
                            ),
                            'front_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'back_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'left_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'right_photo_has_correct_brand': (
                                0.46161414343735935
                            ),
                            'front_photo_has_bad_format': 0.46161414343735935,
                            'back_photo_has_bad_format': 0.46161414343735935,
                            'left_photo_has_bad_format': 0.46161414343735935,
                            'right_photo_has_bad_format': 0.46161414343735935,
                            'sts_photo_has_bad_format': 0.46161414343735935,
                            'front_car_photo_from_screen': 0.46161414343735935,
                            'back_car_photo_from_screen': 0.46161414343735935,
                            'left_car_photo_from_screen': 0.46161414343735935,
                            'right_car_photo_from_screen': 0.46161414343735935,
                            'front_sts_photo_from_screen': 0.46161414343735935,
                            'back_sts_photo_from_screen': 0.46161414343735935,
                            'front_sts_is_russian': 0.46161414343735935,
                            'back_sts_is_russian': 0.46161414343735935,
                        },
                        'reason': None,
                        'invite_comment': None,
                    },
                    'entity_id': '642a1f0353b28c52c127975826f81ebd',
                    'entity_type': 'car',
                    'exam': 'sts',
                    'pass_id': '6021b864fa207cb60a4f3498',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'qc_id': 'some_qc_id',
                },
            ],
            {'resolve_sts_qc_passes_cursor': '666666666666666666'},
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
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_cron_sts(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_sts_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_state_pgsql_content,
        expected_nirvana_sts_get_calls,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    nirvana_sts_get = _mock_nirvana_sts_get(
        mock_taximeter_xservice, nirvana_sts_get_response,
    )
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    _mock_avtocod(patch_aiohttp_session, response_mock)
    _mock_yavtocod(mock_antifraud_py)
    get_jpg = _mock_get_jpg(patch_aiohttp_session, response_mock)
    get_ocr_response = _mock_get_ocr_response(
        patch_aiohttp_session, response_mock, ocr_response,
    )
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_verdicts_db_content
    )

    assert [
        list(nirvana_sts_get.next_call()['request'].query.items())
        for _ in range(nirvana_sts_get.times_called)
    ] == expected_nirvana_sts_get_calls
    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls

    assert (
        await state.get_all_cron_state(master_pool)
        == expected_state_pgsql_content
    )

    assert len(get_jpg.calls) == 6
    assert len(get_ocr_response.calls) == 8


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,nirvana_sts_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_sts_set_calls',
    [
        (
            'incorrect_car_number_format',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ББ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ББ00\n',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'avtocod_verdict': 'YES_BAD_NUMBER_FORMAT',
                        'qc_pass': {'number': 'А001ББ00'},
                        'verdict': 'unknown',
                        'changes': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ББ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'change_car_number_from_ocr',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001AA00\n',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'qc_pass': {'number': 'А001АА00'},
                        'verdict': 'unknown',
                        'changes': [
                            {
                                'field_name': 'number',
                                'new_value': 'А001АА00',
                                'old_value': 'А001ВВ00',
                            },
                        ],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001АА00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'ocr_car_number_is_substring',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ0\n',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'qc_pass': {'number': 'А001ВВ00'},
                        'verdict': 'unknown',
                        'changes': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'incorrect_ocr_car_number_format',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ0O',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'qc_pass': {'number': 'А001ВВ00'},
                        'verdict': 'unknown',
                        'changes': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
        (
            'yellow number has length 8 in ocr incorrect format',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'АА11177',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'sts_front': [],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'АА111777\n',
                    },
                ],
                'full': [],
            },
            [
                {
                    'additional_info': {
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'qc_pass': {'number': 'АА11177'},
                        'verdict': 'unknown',
                        'changes': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'АА11177',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_car_number(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        cron_context,
        taxi_config,
        db,
        comment,
        nirvana_sts_get_response,
        config,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    _mock_nirvana_sts_set(mock_taximeter_xservice)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_avtocod(patch_aiohttp_session, response_mock)
    _mock_yavtocod(mock_antifraud_py)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.avtocod_verdict': True,
                'additional_info.qc_pass.number': True,
                'additional_info.verdict': True,
                'additional_info.changes': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_sts_get_response,avtocod_content,'
    'expected_verdicts_db_content,'
    'expected_nirvana_sts_set_calls,expected_make_report_calls,'
    'expected_refresh_report_calls,expected_get_report_calls',
    [
        (
            'successful_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'avtocod_disabled',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_AVTOCOD_ENABLED': False,
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': None,
                        'avtocod_verdict': 'YES_AVTOCOD_DISABLED',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
            [],
            [],
        ),
        (
            'wrong_brand',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_TOYOTA'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_TOYOTA'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'NO_AVTOCOD_BRAND',
                        'verdict': 'mistakes',
                        'message_keys': ['avtocod_error_message'],
                        'reason': 'NO_AVTOCOD_BRAND',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['avtocod_error_message'],
                        'status': 'mistakes',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'wrong_model',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_TWO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {'id': 'ID_MARK_TWO'},
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'NO_AVTOCOD_MODEL',
                        'verdict': 'mistakes',
                        'message_keys': ['avtocod_error_message'],
                        'reason': 'NO_AVTOCOD_MODEL',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['avtocod_error_message'],
                        'status': 'mistakes',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'wrong_year',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2020,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2020,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'NO_AVTOCOD_YEAR',
                        'verdict': 'mistakes',
                        'message_keys': ['avtocod_error_message'],
                        'reason': 'NO_AVTOCOD_YEAR',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['avtocod_error_message'],
                        'status': 'mistakes',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'wrong_vin',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': 'COMPLETELY_WRONG'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': 'COMPLETELY_WRONG',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'NO_AVTOCOD_VIN',
                        'verdict': 'mistakes',
                        'message_keys': ['avtocod_error_message'],
                        'reason': 'NO_AVTOCOD_VIN',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['avtocod_error_message'],
                        'status': 'mistakes',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'exception_with_wrong_vin',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'A002BB00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'NO_EXCEPTION_VIN',
                        'verdict': 'mistakes',
                        'message_keys': ['avtocod_error_message'],
                        'reason': 'NO_EXCEPTION_VIN',
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'A002BB00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'message_keys': ['avtocod_error_message'],
                        'status': 'mistakes',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'A002BB00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'exception_with_right_vin',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'A002BB00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073222',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073222'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073222',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_EXCEPTION',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'A002BB00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073222',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'A002BB00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'exception_with_unnormalized_car_number',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А002ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073222',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073222'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073222',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_EXCEPTION',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А002ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073222',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А002ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'exception_with_similar_vin',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'A002BB00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073112',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073112'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073112',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_EXCEPTION',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'A002BB00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073112',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'A002BB00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'avtocod_error',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {},
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {},
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD_ERROR',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'empty_tech_data',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'Toyota',
                        'model': 'Mark II',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {'tech_data': {'body': {}}},
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {'tech_data': {'body': {}}},
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'country_is_none',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': {
                            'data': [
                                {
                                    'active_from': '1900-01-01T00:00:00.000Z',
                                    'active_to': '3000-01-01T00:00:00.000Z',
                                    'comment': '',
                                    'content': {
                                        'identifiers': {
                                            'vehicle': {
                                                'vin': '5TDDKRFH80S073711',
                                            },
                                        },
                                        'tech_data': {
                                            'brand': {'id': 'ID_MARK_AC'},
                                            'body': {
                                                'color': {
                                                    'name': 'Желтый',
                                                    'type': '11',
                                                },
                                                'number': 'Z94СВ41ААGR323020',
                                            },
                                            'model': {
                                                'id': 'ID_MARK_AC_ZAGATO',
                                            },
                                            'year': 2021,
                                        },
                                    },
                                    'created_at': '2019-07-07T10:51:46.067Z',
                                    'created_by': 'system',
                                    'domain_uid': 'some_domain_uid',
                                    'name': 'NONAME',
                                    'progress_error': 0,
                                    'progress_ok': 4,
                                    'progress_wait': 0,
                                    'query': {
                                        'body': '5TDDKRFH80S073711',
                                        'data': {
                                            'chat': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'date': 1562495577,
                                            'from': {
                                                'firstName': 'Alesha',
                                                'id': 273893635,
                                            },
                                            'messageId': 703182,
                                            'text': '5TDDKRFH80S073711',
                                        },
                                        'type': 'VIN',
                                    },
                                    'report_type_uid': (
                                        'some_report_uid_1@some_domain_uid'
                                    ),
                                    'state': {
                                        'sources': [
                                            {
                                                '_id': 'references.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'images.avtonomer',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                            {
                                                '_id': 'sub.base',
                                                'data': {
                                                    'from_cache': False,
                                                    'real_status': 'OK',
                                                },
                                                'state': 'OK',
                                            },
                                        ],
                                    },
                                    'tags': '',
                                    'uid': 'report_uid_DK3711@some_domain_uid',
                                    'updated_at': '2019-07-07T10:51:55.167Z',
                                    'updated_by': 'manager',
                                    'vehicle_id': '5TDDKRFH80S073711',
                                },
                            ],
                            'size': 1,
                            'stamp': '2017-01-18T15:23:12Z',
                            'state': 'ok',
                        },
                        'avtocod_verdict': 'YES_AVTOCOD',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [
                {
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'yandex_project_check_auto_report_v2@yandex_project/'
                        '_make'
                    ),
                    'json': {'query': 'А001ВВ00', 'queryType': 'GRZ'},
                },
            ],
            [
                {
                    'json': {},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default/_refresh'
                    ),
                },
            ],
            [
                {
                    'params': {'_content': 'true', '_detailed': 'true'},
                    'url': (
                        'https://b2bapi.avtocod.ru/b2b/api/v1/user/reports/'
                        'default_uid@default'
                    ),
                },
            ],
        ),
        (
            'country_is_not_russia',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Намибия',
                    },
                },
            ],
            {
                'identifiers': {'vehicle': {'vin': '5TDDKRFH80S073711'}},
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'avtocod_report': None,
                        'avtocod_verdict': 'YES_NOT_VALID_COUNTRY',
                        'verdict': 'unknown',
                        'message_keys': [],
                        'reason': None,
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
            [],
            [],
            [],
        ),
    ],
)
async def test_avtocod(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_sts_get_response,
        avtocod_content,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
        expected_make_report_calls,
        expected_refresh_report_calls,
        expected_get_report_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    (
        avtocod_make_report,
        avtocod_refresh_report,
        avtocod_get_report,
    ) = _mock_avtocod(patch_aiohttp_session, response_mock, avtocod_content)
    _mock_yavtocod(mock_antifraud_py)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(
        patch_aiohttp_session,
        response_mock,
        {'sts_front': [], 'sts_back': [], 'plates': [], 'full': []},
    )

    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.avtocod_report': True,
                'additional_info.avtocod_verdict': True,
                'additional_info.verdict': True,
                'additional_info.message_keys': True,
                'additional_info.reason': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls

    assert [
        {'url': x['url'], 'json': x['json']} for x in avtocod_make_report.calls
    ] == expected_make_report_calls
    assert [
        {'url': x['url'], 'json': x['json']}
        for x in avtocod_refresh_report.calls
    ] == expected_refresh_report_calls
    assert [
        {'url': x['url'], 'params': x['params']}
        for x in avtocod_get_report.calls
    ] == expected_get_report_calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'config,nirvana_sts_get_response,avtocod_content,'
    'expected_verdicts_db_content,expected_nirvana_sts_set_calls',
    [
        (
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                    },
                },
            ],
            {
                'identifiers': {
                    'vehicle': {
                        'vin': '5TDDKRFH80S073711',
                        'sts': '9931416219',
                    },
                },
                'tech_data': {
                    'brand': {'id': 'ID_MARK_AC'},
                    'body': {
                        'color': {'name': 'Желтый', 'type': '11'},
                        'number': 'Z94СВ41ААGR323020',
                    },
                    'year': 2021,
                    'model': {'id': 'ID_MARK_AC_ZAGATO'},
                },
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'brand': 'AC',
                            'car_id': '642a1f0353b28c52c127975826f81ebd',
                            'color': 'Желтый',
                            'country': 'Россия',
                            'db_id': '7ad36bc7560449998acbe2c57a75c293',
                            'entity_id': None,
                            'is_invited': False,
                            'model': '378 GT Zagato',
                            'number': 'А001ВВ00',
                            'pictures_urls': {
                                'back_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'back_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'front_sts_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'left_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                                'right_car_picture_url': (
                                    'http://example.com/file.jpg'
                                ),
                            },
                            'registration_cert': '9931416219',
                            'vin': '5TDDKRFH80S073711',
                            'was_blocked': False,
                            'year': '2021',
                        },
                        'verdict': 'unknown',
                        'changes': [
                            {
                                'field_name': 'registration_cert',
                                'new_value': '9931416219',
                                'old_value': None,
                            },
                            {
                                'field_name': 'vin',
                                'new_value': '5TDDKRFH80S073711',
                                'old_value': None,
                            },
                        ],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '9931416219',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_change_sts_vin(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        config,
        nirvana_sts_get_response,
        avtocod_content,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    _mock_avtocod(patch_aiohttp_session, response_mock, avtocod_content)
    _mock_yavtocod(mock_antifraud_py)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(
        patch_aiohttp_session,
        response_mock,
        {'sts_front': [], 'sts_back': [], 'plates': [], 'full': []},
    )

    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass': True,
                'additional_info.verdict': True,
                'additional_info.changes': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_sts_get_response,ocr_response,'
    'expected_verdicts_db_content,expected_nirvana_sts_set_calls',
    [
        (
            'successful_invited_pass',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                        'is_invited': 'True',
                    },
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': '5TDDKRFH80S073711',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': 'Z94СВ41ААGR323020',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '56778',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '2021',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'СОБСТВЕННИК (владелец)',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'российская федерация',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {'is_invited': True, 'was_blocked': False},
                        'verdict': 'success',
                        'errors': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
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
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                        'was_blocked': 'True',
                    },
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': '5TDDKRFH80S073711',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': 'Z94СВ41ААGR323020',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '56778',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '2021',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'СОБСТВЕННИК (владелец)',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'российская федерация',
                    },
                ],
            },
            [
                {
                    'additional_info': {
                        'qc_pass': {'is_invited': False, 'was_blocked': True},
                        'verdict': 'success',
                        'errors': [],
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_invited_blocked(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_sts_get_response,
        ocr_response,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    _mock_avtocod(patch_aiohttp_session, response_mock)
    _mock_yavtocod(mock_antifraud_py)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.is_invited': True,
                'additional_info.qc_pass.was_blocked': True,
                'additional_info.verdict': True,
                'additional_info.errors': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls


@pytest.mark.now('2022-02-04T14:36:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_sts_get_response,ocr_response,yavtocod_info,'
    'expected_verdicts_db_content,expected_nirvana_sts_set_calls',
    [
        (
            'successful_pass_without_avtocod_requests',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_DO_NOT_USE_AVTOCOD_IF_NOT_NEEDED': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                        'is_invited': 'True',
                    },
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': '5TDDKRFH80S073711',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': 'Z94СВ41ААGR323020',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '56778',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '2021',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'СОБСТВЕННИК (владелец)',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'российская федерация',
                    },
                ],
            },
            {
                'vin': '5TDDKRFH80S073711',
                'year': '2021',
                'color': 'Желтый',
                'model': 'AC 378 GT Zagato',
            },
            [{'additional_info': {'verdict': 'success', 'errors': []}}],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
                        },
                        'id': 'some_qc_id',
                        'status': 'unknown',
                    },
                ],
            ],
        ),
    ],
)
async def test_not_using_avtocod(
        mock_taximeter_xservice,
        mock_antifraud_py,
        mock_quality_control_py3,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_sts_get_response,
        ocr_response,
        yavtocod_info,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    (
        avtocod_make_report,
        avtocod_refresh_report,
        avtocod_get_report,
    ) = _mock_avtocod(patch_aiohttp_session, response_mock)
    _mock_yavtocod(mock_antifraud_py, **yavtocod_info)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls

    assert not avtocod_make_report.calls
    assert not avtocod_refresh_report.calls
    assert not avtocod_get_report.calls


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,'
    'config,nirvana_sts_get_response,ocr_response,history_features,'
    'expected_verdicts_db_content,expected_nirvana_sts_set_calls',
    [
        (
            'invited_pass_with_success_resolution',
            DEFAULT_CONFIG,
            [
                {
                    'id': 'some_qc_id',
                    'pending_date': '2020-01-01T00:00:00',
                    'photos': {
                        'RegistrationCertFront': 'http://example.com/file.jpg',
                        'RegistrationCertBack': 'http://example.com/file.jpg',
                        'VehicleAuthorization': 'http://example.com/file.jpg',
                        'Front': 'http://example.com/file.jpg',
                        'Left': 'http://example.com/file.jpg',
                        'Back': 'http://example.com/file.jpg',
                        'Right': 'http://example.com/file.jpg',
                    },
                    'data': {
                        'pass_id': '6021b864fa207cb60a4f3498',
                        'db_id': '7ad36bc7560449998acbe2c57a75c293',
                        'car_id': '642a1f0353b28c52c127975826f81ebd',
                        'number': 'А001ВВ00',
                        'year': '2021',
                        'brand': 'AC',
                        'model': '378 GT Zagato',
                        'color': 'Желтый',
                        'vin': '5TDDKRFH80S073711',
                        'registration_cert': '56778',
                        'body_number': 'Z94СВ41ААGR323020',
                        'country': 'Россия',
                        'is_invited': 'True',
                    },
                    'entity_id': 'dbid_uuid',
                },
            ],
            {
                'sts_front': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.1494631618,
                        'Type': 'stsfront_vin_number',
                        'Text': '5TDDKRFH80S073711',
                    },
                ],
                'sts_back': [],
                'plates': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7724065185,
                        'Type': 'text',
                        'Text': 'А001ВВ00\n',
                    },
                ],
                'full': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'phone',
                        'Text': ' 9911 725289',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': 'Z94СВ41ААGR323020',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '56778',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8156407475,
                        'Type': 'text',
                        'Text': '2021',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'чные номера автомобиля сверены, техническое',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'СОБСТВЕННИК (владелец)',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.7567083836,
                        'Type': 'text',
                        'Text': 'российская федерация',
                    },
                ],
            },
            [
                {
                    'entity_id': 'some_entity_id',
                    'entity_type': 'driver',
                    'modified': '2020-01-01T00:00:00',
                    'exam': 'dkvu',
                    'id': '6021b864fa207cb60a4f3498',
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
                    },
                },
            ],
            [
                [
                    {
                        'data': {
                            'body_number': 'Z94СВ41ААGR323020',
                            'color': 'Желтый',
                            'number': 'А001ВВ00',
                            'registration_cert': '56778',
                            'vin': '5TDDKRFH80S073711',
                            'year': '2021',
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
        mock_antifraud_py,
        mock_quality_control_py3,
        mock_qc_invites,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        nirvana_sts_get_response,
        ocr_response,
        history_features,
        expected_verdicts_db_content,
        expected_nirvana_sts_set_calls,
):
    taxi_config.set_values(config)
    _mock_nirvana_sts_get(mock_taximeter_xservice, nirvana_sts_get_response)
    nirvana_sts_set = _mock_nirvana_sts_set(mock_taximeter_xservice)
    _mock_avtocod(patch_aiohttp_session, response_mock)
    _mock_yavtocod(mock_antifraud_py)
    _mock_get_jpg(patch_aiohttp_session, response_mock)
    _mock_get_ocr_response(patch_aiohttp_session, response_mock, ocr_response)
    _mock_get_model(patch_aiohttp_session, response_mock)
    _mock_get_features(patch_aiohttp_session, response_mock)
    _mock_quality_control_history(mock_quality_control_py3, history_features)
    _mock_qc_invites_info(mock_qc_invites)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.resolve_sts_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find(
            {},
            {
                '_id': False,
                'additional_info.qc_pass.is_invited': True,
                'additional_info.verdict': True,
                'additional_info.invite_comment': True,
            },
        ).to_list(None)
        == expected_verdicts_db_content
    )

    assert mock.get_requests(nirvana_sts_set) == expected_nirvana_sts_set_calls
