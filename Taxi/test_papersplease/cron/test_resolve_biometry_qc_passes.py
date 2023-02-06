import base64
import datetime
from typing import List

from aiohttp import web
import pytest

from papersplease.crontasks import resolve_biometry_qc_passes
from papersplease.generated.cron import run_cron
from papersplease.settings import qc_settings
from test_papersplease.cron.utils import mock
from test_papersplease.cron.utils import state


CURSOR_STATE_NAME = resolve_biometry_qc_passes.CURSOR_STATE_NAME


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

    return _get_model_without_categorial


def _mock_qc_pools_biometry_get(mock_qc_pools, response_items):
    @mock_qc_pools('/internal/qc-pools/v1/pool/retrieve')
    async def _qc_pools_biometry_get(request):
        assert request.method == 'POST'
        if request.json.get('cursor') == '666666666666666666':
            return web.json_response(
                data=dict(cursor='666666666666666666', items=[]),
            )
        return web.json_response(
            data=dict(cursor='666666666666666666', items=response_items),
        )

    return _qc_pools_biometry_get


def _mock_qc_pools_biometry_set(mock_qc_pools):
    @mock_qc_pools('/internal/qc-pools/v1/pool/push')
    async def _qc_pools_biometry_set(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    return _qc_pools_biometry_set


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
                                'LayerName': 'prod_v9_enc_toloka_96',
                                'Version': '8',
                            },
                        ],
                    },
                },
            }
        return response_mock(json=features)

    return _get_features


DEFAULT_CONFIG: dict = {
    'PPS_CRON_CURSOR_USE_PGSQL': 'enabled',
    'PPS_CRON_RESOLVE_BIOMETRY_QC_PASSES_ALL_CONFIGS': {
        'batch_size': 1,
        'cbir_face_features_max_concurrency': 1,
        'duplicates_between_selfie_and_etalons_threshold': 1,
        'empty_batches_limit': 1,
        'empty_batch_sleep_time': 0.001,
        'enabled': True,
        'etalon_is_from_screen_threshold': 0.8,
        'low_similarity_fail_threshold': 0.25,
        'high_similarity_success_threshold': 0.75,
        'max_concurrency': 1,
        'max_size_of_etalons': 10,
        'min_similarity_between_etalons_threshold': 0.6,
        'pool_name': 'biometry_verification',
        'resolution_enabled': True,
        'similarity_for_update_etalons_threshold': 0.8,
        'sleep_time_after_batch': 0.001,
    },
    'PPS_CRON_RESOLVE_QC_PASSES_CATBOOST_MODELS': {
        'selfie_from_screen_biometry': {
            'threshold': 0.8,
            'url': (
                'https://storage.yandex-team.ru/get-devtools/model_zero.bin'
            ),
        },
    },
}

DEFAULT_QC_POOLS_RESPONSE: List[dict] = [
    {
        'id': 'some_id',
        'entity_id': 'somepark_driverid',
        'created': '2020-01-01T00:00:00',
        'entity_type': 'driver',
        'exam': 'biometry',
        'media': [
            {
                'id': 'etalon_id',
                'code': 'someetalon',
                'url': 'http://example.com/file.jpg',
            },
            {
                'id': 'selfie_id',
                'code': 'selfie',
                'url': 'http://example.com/file.jpg',
            },
        ],
    },
]

DEFAULT_QC_POOLS_RESPONSE_WITH_FEATURES: List[dict] = [
    {
        'id': 'some_id',
        'entity_id': 'somepark_driverid',
        'created': '2020-01-01T00:00:00',
        'entity_type': 'driver',
        'exam': 'biometry',
        'media': [
            {
                'id': 'etalon_id_1',
                'code': 'biometry_etalons.selfie.0',
                'url': 'http://example.com/file.jpg',
            },
            {
                'id': 'selfie_id',
                'code': 'selfie',
                'url': 'http://example.com/file.jpg',
            },
            {
                'id': 'etalon_id_2',
                'code': 'biometry_etalons.selfie.1',
                'url': 'http://example.com/file.jpg',
            },
            {
                'id': 'etalon_id_3',
                'code': 'biometry_etalons.selfie.2',
                'url': 'http://example.com/file.jpg',
            },
        ],
        'data': [
            {
                'field': 'biometry_etalons.selfie.0.cbir_face_features',
                'value': ['1.0', '2.0', '3.0', '4.0', '0.5'],
            },
            {
                'field': 'biometry_etalons.selfie.2.cbir_face_features',
                'value': ['5.0', '6.0', '7.0', '8.0', '0.9'],
            },
            {'field': 'biometry_etalons.selfie.1.meta.from', 'value': 'dkvu'},
            {
                'field': 'biometry_etalons.selfie.2.meta.from',
                'value': 'identity',
            },
        ],
    },
]

DEFAULT_QC_POOL_GET_CALLS: List[dict] = [
    {
        'exam': 'biometry',
        'pass_id': 'some_id',
        'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
        'processed': datetime.datetime(2020, 9, 20, 19, 2, 15, 677000),
        'entity_id': 'somepark_driverid',
        'entity_type': 'driver',
        'additional_info': {
            'qc_pass': {
                'selfie': {
                    'id_': 'selfie_id',
                    'url': 'http://example.com/file.jpg',
                },
                'etalons_meta_data': [{}],
            },
            'etalons_info': [{'id': 'etalon_id'}, {'id': 'selfie_id'}],
            'old_etalons_info': [{'id': 'etalon_id'}],
            'catboost_features': {
                'selfie_from_screen_score': 0.46161414343735935,
            },
            'etalons_catboost_features': [{'selfie_from_screen_score': None}],
            'verdict': 'success',
            'reason': None,
            'errors': [],
            'face_similarities': [[[1.0]]],
            'picture_similarities': [],
            'etalons_min_similarity': 1.0,
        },
    },
]

DEFAULT_GET_FEATURES_CALLS = 3


@pytest.mark.now('2020-09-20T19:02:15.677Z')
@pytest.mark.parametrize(
    'comment,config,qc_pools_biometry_get_response,'
    'expected_qc_pools_biometry_get_calls,'
    'expected_qc_pools_biometry_set_calls,get_features_calls',
    [
        (
            'successful_pass',
            DEFAULT_CONFIG,
            DEFAULT_QC_POOLS_RESPONSE,
            DEFAULT_QC_POOL_GET_CALLS,
            [
                {
                    'items': [
                        {
                            'id': 'some_id',
                            'entity_id': 'somepark_driverid',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'data': [
                                {'field': 'resolution', 'value': 'success'},
                                {
                                    'field': 'good_biometry_etalons_ids',
                                    'value': [
                                        'driver-photo_etalon_id',
                                        'driver-photo_selfie_id',
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
            DEFAULT_GET_FEATURES_CALLS,
        ),
        (
            'resolution_disabled',
            {
                **DEFAULT_CONFIG,
                'PPS_CRON_RESOLVE_BIOMETRY_QC_PASSES_ALL_CONFIGS': {
                    **DEFAULT_CONFIG[
                        'PPS_CRON_RESOLVE_BIOMETRY_QC_PASSES_ALL_CONFIGS'
                    ],
                    'resolution_enabled': False,
                },
            },
            DEFAULT_QC_POOLS_RESPONSE,
            DEFAULT_QC_POOL_GET_CALLS,
            [],
            DEFAULT_GET_FEATURES_CALLS,
        ),
        (
            'with_face_features',
            DEFAULT_CONFIG,
            DEFAULT_QC_POOLS_RESPONSE_WITH_FEATURES,
            [
                {
                    'exam': 'biometry',
                    'pass_id': 'some_id',
                    'pass_modified': datetime.datetime(2020, 1, 1, 0, 0),
                    'processed': datetime.datetime(
                        2020, 9, 20, 19, 2, 15, 677000,
                    ),
                    'entity_id': 'somepark_driverid',
                    'entity_type': 'driver',
                    'additional_info': {
                        'qc_pass': {
                            'selfie': {
                                'id_': 'selfie_id',
                                'url': 'http://example.com/file.jpg',
                            },
                            'etalons_meta_data': [
                                {},
                                {'from': 'dkvu'},
                                {'from': 'identity'},
                            ],
                        },
                        'etalons_info': [
                            {'id': 'etalon_id_1'},
                            {'id': 'etalon_id_2'},
                            {'id': 'etalon_id_3'},
                        ],
                        'old_etalons_info': [
                            {'id': 'etalon_id_1'},
                            {'id': 'etalon_id_2'},
                            {'id': 'etalon_id_3'},
                        ],
                        'catboost_features': {
                            'selfie_from_screen_score': 0.46161414343735935,
                        },
                        'etalons_catboost_features': [
                            {'selfie_from_screen_score': None},
                            {'selfie_from_screen_score': None},
                            {'selfie_from_screen_score': None},
                        ],
                        'verdict': 'success',
                        'reason': None,
                        'errors': [],
                        'face_similarities': [
                            [
                                [0.6094208632140256],
                                [1.0],
                                [0.7493852589702373],
                            ],
                        ],
                        'picture_similarities': [],
                        'etalons_min_similarity': 0.6094208632140256,
                    },
                },
            ],
            [
                {
                    'items': [
                        {
                            'id': 'some_id',
                            'entity_id': 'somepark_driverid',
                            'entity_type': 'driver',
                            'exam': 'biometry',
                            'data': [
                                {'field': 'resolution', 'value': 'success'},
                                {
                                    'field': 'good_biometry_etalons_ids',
                                    'value': [
                                        'driver-photo_etalon_id_1',
                                        'driver-photo_etalon_id_2',
                                        'driver-photo_etalon_id_3',
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
            DEFAULT_GET_FEATURES_CALLS,
        ),
        (
            'successful_eda_equipment_pass',
            DEFAULT_CONFIG,
            [{**DEFAULT_QC_POOLS_RESPONSE[0], 'exam': 'eda_equipment'}],
            [{**DEFAULT_QC_POOL_GET_CALLS[0], 'exam': 'eda_equipment'}],
            [
                {
                    'items': [
                        {
                            'id': 'some_id',
                            'entity_id': 'somepark_driverid',
                            'entity_type': 'driver',
                            'exam': 'eda_equipment',
                            'data': [
                                {'field': 'resolution', 'value': 'success'},
                                {
                                    'field': 'good_biometry_etalons_ids',
                                    'value': [
                                        'driver-photo_etalon_id',
                                        'driver-photo_selfie_id',
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
            DEFAULT_GET_FEATURES_CALLS,
        ),
    ],
)
async def test_cron(
        patch_aiohttp_session,
        response_mock,
        mock_qc_pools,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        qc_pools_biometry_get_response,
        expected_qc_pools_biometry_get_calls,
        expected_qc_pools_biometry_set_calls,
        get_features_calls,
):
    taxi_config.set_values(config)
    _mock_qc_pools_biometry_get(mock_qc_pools, qc_pools_biometry_get_response)
    qc_pools_biometry_set = _mock_qc_pools_biometry_set(mock_qc_pools)
    _mock_get_model(patch_aiohttp_session, response_mock)
    get_features = _mock_get_features(patch_aiohttp_session, response_mock)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['papersplease.crontasks.resolve_biometry_qc_passes', '-t', '0'],
    )

    assert (
        await db.antifraud_iron_lady_verdicts.find({}, {'_id': False}).to_list(
            None,
        )
        == expected_qc_pools_biometry_get_calls
    )

    assert (
        mock.get_requests(qc_pools_biometry_set)
        == expected_qc_pools_biometry_set_calls
    )

    assert len(get_features.calls) == get_features_calls
