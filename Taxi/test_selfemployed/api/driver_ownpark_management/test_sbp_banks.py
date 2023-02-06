import pytest

from testsuite.utils import http

from test_selfemployed import conftest


HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'newcontractorid',
    'X-YaTaxi-Park-Id': 'newparkid',
    'User-Agent': (
        'app:pro brand:yandex version:10.12 '
        'platform:ios platform_version:15.0.1'
    ),
}
CONFIG_PARAMS = dict(
    SELFEMPLOYED_REQUISITES_SETTINGS={
        'bank': {
            'sf_subject': 'Self-Employed Change Payment Details',
            'resident_account_prefixes': ['40817'],
            'bik_prefixes': ['04'],
        },
        'sbp': {
            'sf_subject': 'Self-Employed FPS Change Payment Details',
            'banks': [
                {'id': 'test_bank', 'name': 'sbp_bank_name.test_bank'},
                {
                    'id': 'bad_bank',
                    'name': 'sbp_bank_name.bad_bank',
                    'disabled': True,
                },
            ],
        },
    },
)


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
async def test_sbp_banks(
        se_client, mock_personal, mock_yb_balalayka, mock_driver_profiles,
):
    phone = '+70001234567'

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_yb_balalayka('/api/payments/probation/')
    async def _mock_balalayka(request: http.Request):
        assert len(request.json['payments']) == 1
        if request.json['payments'][0]['params']['bank_alias'] == 'test_bank':
            return {
                'meta': {'built': '0000-00-00T00:00:00'},
                'data': {
                    'items': [
                        {
                            'id': request.json['payments'][0]['id'],
                            'status_bcl': 2,
                            'status_remote': 'WAITING_CONFIRMATION',
                        },
                    ],
                },
                'errors': [],
            }
        return {
            'meta': {'built': '0000-00-00T00:00:00'},
            'data': {},
            'errors': [],
        }

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['newparkid_newcontractorid'],
            'projection': ['data.park_id', 'data.uuid', 'data.full_name'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'newparkid_newcontractorid',
                    'data': {
                        'park_id': 'newparkid',
                        'uuid': 'newcontractorid',
                        'full_name': {
                            'first_name': 'Имя',
                            'last_name': 'Фамилия',
                            'middle_name': 'Отчество',
                        },
                    },
                },
            ],
        }

    response = await se_client.get(
        '/driver/v1/selfemployed/ownpark/management/sbp-banks',
        headers=HEADERS,
        params={'current_phone': phone},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'banks': ['test_bank']}


@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(**CONFIG_PARAMS)
async def test_sbp_banks_retry(
        se_client, mock_personal, mock_yb_balalayka, mock_driver_profiles,
):
    phone = '+70001234567'
    calls = []

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        assert request.json == {'id': 'INN_PD_ID', 'primary_replica': False}
        return {'value': '000000', 'id': 'INN_PD_ID'}

    @mock_yb_balalayka('/api/payments/probation/')
    async def _mock_balalayka(request: http.Request):
        assert len(request.json['payments']) == 1
        if request.json['payments'][0]['params']['bank_alias'] != 'test_bank':
            return {
                'meta': {'built': '0000-00-00T00:00:00'},
                'data': {},
                'errors': [],
            }
        data = {
            'meta': {'built': '0000-00-00T00:00:00'},
            'data': {
                'items': [
                    {
                        'id': request.json['payments'][0]['id'],
                        'status_bcl': 2,
                        'status_remote': 'PENDING',
                    },
                ],
            },
            'errors': [],
        }
        if calls:
            data = {
                'meta': {'built': '0000-00-00T00:00:00'},
                'data': {
                    'items': [
                        {
                            'id': request.json['payments'][0]['id'],
                            'status_bcl': 2,
                            'status_remote': 'WAITING_CONFIRMATION',
                        },
                    ],
                },
                'errors': [],
            }
        calls.append(request.json)
        return data

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _retrieve_profile(request: http.Request):
        assert request.json == {
            'id_in_set': ['newparkid_newcontractorid'],
            'projection': ['data.park_id', 'data.uuid', 'data.full_name'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'newparkid_newcontractorid',
                    'data': {
                        'park_id': 'newparkid',
                        'uuid': 'newcontractorid',
                        'full_name': {
                            'first_name': 'Имя',
                            'last_name': 'Фамилия',
                            'middle_name': 'Отчество',
                        },
                    },
                },
            ],
        }

    response = await se_client.get(
        '/driver/v1/selfemployed/ownpark/management/sbp-banks',
        headers=HEADERS,
        params={'current_phone': phone},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'banks': ['test_bank']}
