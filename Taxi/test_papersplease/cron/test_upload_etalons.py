from aiohttp import web
import pytest

from papersplease.crontasks import upload_etalons
from papersplease.generated.cron import run_cron
from test_papersplease.cron.utils import state

CURSOR_STATE_NAME = upload_etalons.CURSOR_STATE_NAME


RIGHT_ETALONS = {
    'parkid_driverid': {
        'provider': 'taxi',
        'profile': {'id': 'some_id', 'type': 'some_type'},
        'profile_media': {
            'photo': [
                {
                    'media_id': 'etalon_id_1',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_2',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_3',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_4',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_5',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_6',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_7',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_8',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_9',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_10',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'meta': {'exam': 'dkvu'},
                },
            ],
        },
    },
    'parkid_driverid_1': {
        'provider': 'taxi',
        'profile': {'id': 'some_id', 'type': 'some_type'},
        'profile_media': None,
    },
    'parkid_driverid_3': {
        'provider': 'taxi',
        'profile': {'id': 'some_id', 'type': 'some_type'},
        'profile_media': {
            'photo': [
                {
                    'media_id': 'etalon_id_1',
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
                {
                    'media_id': 'etalon_id_2',
                    'storage_id': 'duplicated_id',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                },
            ],
        },
    },
}

RIGHT_STORE_REQUEST = {
    'parkid_driverid': {
        'provider': 'taxi',
        'profile': {'id': 'parkid_driverid', 'type': 'park_driver_profile_id'},
        'media': {
            'photo': [
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'storage_id',
                    'storage_bucket': 'storage_bucket',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {'exam': 'identity'},
                },
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {'exam': 'dkvu'},
                },
            ],
        },
    },
    'parkid_driverid_1': {
        'provider': 'taxi',
        'profile': {
            'id': 'parkid_driverid_1',
            'type': 'park_driver_profile_id',
        },
        'media': {
            'photo': [
                {
                    'storage_id': 'storage_id',
                    'storage_bucket': 'storage_bucket',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {'exam': 'identity'},
                },
            ],
        },
    },
    'parkid_driverid_2': {
        'provider': 'taxi',
        'profile': {
            'id': 'parkid_driverid_2',
            'type': 'park_driver_profile_id',
        },
        'media': {
            'photo': [
                {
                    'storage_id': 'storage_id',
                    'storage_bucket': 'storage_bucket',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {'exam': 'identity'},
                },
            ],
        },
    },
    'parkid_driverid_3': {
        'provider': 'taxi',
        'profile': {
            'id': 'parkid_driverid_2',
            'type': 'park_driver_profile_id',
        },
        'media': {
            'photo': [
                {
                    'storage_id': 'some_storage',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
                {
                    'storage_id': 'duplicated_id',
                    'storage_bucket': 'driver_photo',
                    'storage_type': 'media-storage',
                    'calculate_cbir_features': True,
                    'meta': {},
                },
            ],
        },
    },
}


@pytest.mark.config(
    PPS_CRON_UPLOAD_ETALONS_BATCH_SIZE=1,
    PPS_CRON_UPLOAD_ETALONS_ENABLED=True,
    PPS_CRON_UPLOAD_ETALONS_EXAMS_FOR_UPDATING=['dkvu', 'identity'],
    PPS_CRON_UPLOAD_ETALONS_MAX_BIOMETRY_PHOTO=3,
    PPS_CRON_UPLOAD_ETALONS_SLEEP_TIME=0.01,
    PPS_CRON_UPLOAD_ETALONS_UPDATING_ENABLED=True,
)
async def test_cron(
        mock_quality_control_py3,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        cron_context,
):
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    @mock_quality_control_py3('/api/v1/pass/list')
    async def _api_v1_pass_list(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == 'end':
            return web.json_response(
                data=dict(
                    modified='2020-01-01T00:00:00', cursor='end', items=[],
                ),
            )
        return web.json_response(
            data=dict(
                modified='2020-01-01T00:00:00',
                cursor='end',
                items=[
                    {
                        'id': '',
                        'status': 'NEW',
                        'entity_id': '',
                        'exam': 'dkk',
                        'entity_type': '',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'url': '', 'code': '', 'required': True}],
                    },
                    {
                        'id': '',
                        'status': 'RESOLVED',
                        'entity_id': '',
                        'exam': 'dkk',
                        'entity_type': '',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'url': '', 'code': '', 'required': True}],
                    },
                    {
                        'id': 'some_id_1',
                        'status': 'RESOLVED',
                        'entity_id': 'parkid_driverid',
                        'exam': 'identity',
                        'entity_type': 'driver',
                        'modified': '2020-01-01T00:00:00',
                        'media': [
                            {
                                'code': 'selfie',
                                'storage': {
                                    'id': 'storage_id',
                                    'bucket': 'storage_bucket',
                                    'type': 'media-storage',
                                },
                                'required': True,
                            },
                        ],
                        'resolution': {'status': 'SUCCESS'},
                    },
                    {
                        'id': 'some_id_1',
                        'status': 'RESOLVED',
                        'entity_id': 'parkid_driverid_1',
                        'exam': 'identity',
                        'entity_type': 'driver',
                        'modified': '2020-01-01T00:00:00',
                        'media': [
                            {
                                'code': 'selfie',
                                'storage': {
                                    'id': 'storage_id',
                                    'bucket': 'storage_bucket',
                                    'type': 'media-storage',
                                },
                                'required': True,
                            },
                        ],
                        'resolution': {'status': 'SUCCESS'},
                    },
                    {
                        'id': 'some_id_2',
                        'status': 'RESOLVED',
                        'entity_id': 'parkid_driverid_2',
                        'exam': 'identity',
                        'entity_type': 'driver',
                        'modified': '2020-01-01T00:00:00',
                        'media': [
                            {
                                'code': 'selfie',
                                'storage': {
                                    'id': 'storage_id',
                                    'bucket': 'storage_bucket',
                                    'type': 'media-storage',
                                },
                                'required': True,
                            },
                        ],
                        'resolution': {'status': 'SUCCESS'},
                    },
                    {
                        'id': 'some_id_3',
                        'status': 'RESOLVED',
                        'entity_id': 'parkid_driverid_3',
                        'exam': 'identity',
                        'entity_type': 'driver',
                        'modified': '2020-01-01T00:00:00',
                        'media': [
                            {
                                'code': 'selfie',
                                'storage': {
                                    'id': 'duplicated_id',
                                    'bucket': 'storage_bucket',
                                    'type': 'media-storage',
                                },
                                'required': True,
                            },
                        ],
                        'resolution': {'status': 'SUCCESS'},
                    },
                ],
            ),
        )

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _biometry_etalons_profiles_retrieve(request):
        assert request.method == 'POST'

        if request.json['profile_ids'][0] == 'parkid_driverid_2':
            return mockserver.make_response(json={'profiles': []})
        return mockserver.make_response(
            json={
                'profiles': [
                    RIGHT_ETALONS[profile_id]
                    for profile_id in request.json['profile_ids']
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profile/store',
    )
    async def _biometry_etalons_profile_store(request):
        assert request.method == 'POST'
        assert (
            request.json == RIGHT_STORE_REQUEST[request.json['profile']['id']]
        )

        return mockserver.make_response(
            json={'profile': {'id': 'some_id', 'type': 'some_type'}},
            status=200,
        )

    await run_cron.main(['papersplease.crontasks.upload_etalons', '-t', '0'])

    assert _api_v1_pass_list.times_called == 2
    assert _biometry_etalons_profiles_retrieve.times_called == 4
    assert _biometry_etalons_profile_store.times_called == 3
