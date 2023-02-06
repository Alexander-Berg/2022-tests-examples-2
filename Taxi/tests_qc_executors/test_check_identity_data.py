import pytest

from tests_qc_executors import utils

COUNTRIES_FROM_PARKS: dict = {
    'park1': 'rus',
    'park2': 'rus',
    'park3': 'blr',
    'park4': 'uzb',
}

DEFAULT_PASS: dict = {
    'entity_type': 'driver',
    'exam': 'identity',
    'modified': '2020-05-12T16:30:00.000Z',
    'status': 'PENDING',
    'media': [],
}

DATA_FROM_ID: dict = {
    'id1': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {
            'field': 'identity_verification.identity_data',
            'value': 'personal_id_1',
        },
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_1'},
    ],
    'id2': [
        {'field': 'identity_id', 'value': 'illegal_identity'},
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'incorrect_identity_country'},
    ],
    'id4': [
        {'field': 'identity_id', 'value': 'transborder_passport_uzb'},
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'incorrect_identity_country'},
    ],
    'id5': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {
            'field': 'identity_verification.identity_data',
            'value': 'personal_id_2',
        },
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'identity_not_yet_sixteen'},
    ],
    'id6': [
        {'field': 'identity_id', 'value': 'permanent_residency_blr'},
        {
            'field': 'identity_verification.identity_data',
            'value': 'personal_id_3',
        },
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'identity_not_yet_eighteen'},
    ],
    'id7': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_1'},
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_1'},
    ],
    'id8': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_4'},
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'identity_is_expired'},
    ],
    'id9': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_5'},
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_5'},
    ],
    'id10': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_6'},
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'identity_is_expired'},
    ],
    'id11': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {
            'field': 'identity_verification.identity_data',
            'value': 'personal_id_7',
        },
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_7'},
    ],
    'id12': [
        {'field': 'identity_id', 'value': 'passport_kaz'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_8'},
        {'field': 'resolution', 'value': 'FAIL'},
        {'field': 'reason', 'value': 'identity_is_expired'},
    ],
    'id13': [
        {'field': 'identity_id', 'value': 'passport_kaz'},
        {'field': 'identity_yang.identity_data', 'value': 'personal_id_9'},
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_9'},
    ],
    'id15': [
        {'field': 'identity_id', 'value': 'passport_rus'},
        {
            'field': 'identity_verification.identity_data',
            'value': 'personal_id_1',
        },
        {
            'field': 'identity_verification.identity_number',
            'value': 'some_number_pd_id',
        },
        {'field': 'resolution', 'value': 'SUCCESS'},
        {'field': 'identity_data', 'value': 'personal_id_1'},
        {'field': 'identity_number', 'value': 'some_number_pd_id'},
    ],
}

FROM_PD_ID_TO_VALUE: dict = {
    'personal_id_1': (
        '{"date_of_birth": "1998-01-04", "issue_date": "2018-02-01"}'
    ),
    'personal_id_2': (
        '{"date_of_birth": "2006-08-01", "issue_date": "2018-02-01"}'
    ),
    'personal_id_3': (
        '{"date_of_birth": "2005-01-01", "issue_date": "2018-02-01"}'
    ),
    'personal_id_4': (
        '{"date_of_birth": "1998-01-04", "issue_date": "2018-01-01"}'
    ),
    'personal_id_5': (
        '{"date_of_birth": "2002-05-01", "issue_date": "2018-01-01"}'
    ),
    'personal_id_6': (
        '{"date_of_birth": "1975-01-01", "issue_date": "1995-04-01"}'
    ),
    'personal_id_7': (
        '{"date_of_birth": "1977-06-01", "issue_date": "1997-07-01"}'
    ),
    'personal_id_8': '{"date_of_birth": "1977-06-01", "issue_date": "2012-06-30", "expire_date": "2022-06-30"}',
    'personal_id_9': '{"date_of_birth": "1977-06-01", "issue_date": "2012-07-02", "expire_date": "2022-07-02"}',
}


@pytest.mark.config(
    QC_EXECUTORS_CHECK_IDENTITY_DATA_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_personal_requests_count': 1,
    },
    QC_IDENTITY_RULES={
        'rus': ['passport_rus', 'passport_kaz', 'transborder_passport_uzb'],
        'blr': ['permanent_residency_blr'],
    },
    QC_EXECUTORS_CHECK_IDENTITY_DATA_AGE_RULES={
        '__default__': {'age': 18, 'reason': 'identity_not_yet_eighteen'},
        'rus': {'age': 16, 'reason': 'identity_not_yet_sixteen'},
    },
    QC_EXECUTORS_CHECK_IDENTITY_DATA_POOLS_NAMES_FOR_IDENTITY_FIELDS=[
        'identity_yang',
        'identity_verification',
    ],
    QC_EXECUTORS_CHECK_IDENTITY_DATA_RUSSIAN_IDENTITIES=['passport_rus'],
)
@pytest.mark.now('2022-07-01T19:02:15.677Z')
@pytest.mark.parametrize(
    'passes_',
    [
        (
            [
                {
                    **DEFAULT_PASS,
                    'id': 'id1',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_verification.identity_data',
                            'value': 'personal_id_1',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id2',
                    'entity_id': 'park2_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'illegal_identity'},
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id3',
                    'entity_id': 'park3_driver',
                    'data': [],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id4',
                    'entity_id': 'park4_driver',
                    'data': [
                        {
                            'field': 'identity_id',
                            'value': 'transborder_passport_uzb',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id5',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_verification.identity_data',
                            'value': 'personal_id_2',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id6',
                    'entity_id': 'park3_driver',
                    'data': [
                        {
                            'field': 'identity_id',
                            'value': 'permanent_residency_blr',
                        },
                        {
                            'field': 'identity_verification.identity_data',
                            'value': 'personal_id_3',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id7',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_1',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id8',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_4',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id9',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_5',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id10',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_6',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id11',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_verification.identity_data',
                            'value': 'personal_id_7',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id12',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_kaz'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_8',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id13',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_kaz'},
                        {
                            'field': 'identity_yang.identity_data',
                            'value': 'personal_id_9',
                        },
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id14',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                    ],
                },
                {
                    **DEFAULT_PASS,
                    'id': 'id15',
                    'entity_id': 'park1_driver',
                    'data': [
                        {'field': 'identity_id', 'value': 'passport_rus'},
                        {
                            'field': 'identity_verification.identity_data',
                            'value': 'personal_id_1',
                        },
                        {
                            'field': 'identity_verification.identity_number',
                            'value': 'some_number_pd_id',
                        },
                    ],
                },
            ]
        ),
    ],
)
async def test_check_identity_data(
        taxi_qc_executors, testpoint, mockserver, passes_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _v1_parks_list(request):
        assert request.method == 'POST'
        parks_ids = request.json['query']['park']['ids']
        return mockserver.make_response(
            json={
                'parks': [
                    {
                        'id': id_,
                        'login': 'some_login',
                        'name': 'some_name',
                        'is_active': True,
                        'city_id': 'some_city_id',
                        'locale': 'some_locale',
                        'is_billing_enabled': True,
                        'is_franchising_enabled': True,
                        'demo_mode': False,
                        'geodata': {'lat': 1, 'lon': 1, 'zoom': 1},
                        'country_id': COUNTRIES_FROM_PARKS[id_],
                    }
                    for id_ in parks_ids
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _personal_v1_identifications_retrieve(request):
        assert request.method == 'POST'
        id_ = request.json['id']
        return mockserver.make_response(
            json={'id': id_, 'value': FROM_PD_ID_TO_VALUE[id_]}, status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        items = request.json['items']
        assert len(items) == 13
        for item in items:
            assert item['data'] == DATA_FROM_ID[item['id']]
        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('check-identity-data'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _v1_parks_list.times_called == 1
    assert _personal_v1_identifications_retrieve.times_called == 11
    assert _internal_qc_pools_v1_pool_push.times_called == 1
