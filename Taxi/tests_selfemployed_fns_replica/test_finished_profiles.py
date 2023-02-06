import pytest

CONFIG = {
    'selfemployed-fns-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('selfemployed_main', files=['initial.sql'])
async def test_retrieve(taxi_selfemployed_fns_replica):
    response = await taxi_selfemployed_fns_replica.post(
        '/v1/profiles/retrieve',
        json={'id_in_set': ['dbid1_uuid1', 'dbid2_uuid2']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'profiles': [
            {
                'data': {
                    'contractor_profile_id': 'uuid1',
                    'do_send_receipts': False,
                    'increment': 1,
                    'inn_pd_id': 'inn1_pd_id',
                    'is_own_park': False,
                    'park_id': 'dbid1',
                    'phone_pd_id': 'phone1_pd_id',
                    'updated_at': '2021-11-01T00:00:00.000',
                },
                'park_contractor_profile_id': 'dbid1_uuid1',
                'revision': '2021-11-01T00:00:00+0000_1',
            },
            {
                'data': {
                    'contractor_profile_id': 'uuid2',
                    'do_send_receipts': True,
                    'increment': 2,
                    'inn_pd_id': 'inn2_pd_id',
                    'is_own_park': True,
                    'park_id': 'dbid2',
                    'phone_pd_id': 'phone2_pd_id',
                    'updated_at': '2021-11-02T00:00:00.000',
                },
                'park_contractor_profile_id': 'dbid2_uuid2',
                'revision': '2021-11-02T00:00:00+0000_2',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('selfemployed_main', files=['initial.sql'])
async def test_updates(taxi_selfemployed_fns_replica):
    response = await taxi_selfemployed_fns_replica.post(
        '/v1/profiles/updates',
        json={'last_known_revision': '2021-11-02T12:00:00+0000_0'},
        params={'consumer': 'test'},
    )
    response_json = response.json()
    response_json.pop('cache_lag')

    assert response.status_code == 200
    assert response_json == {
        'last_modified': '2021-11-03T00:00:00Z',
        'last_revision': '2021-11-03T00:00:00+0000_3',
        'profiles': [
            {
                'data': {
                    'contractor_profile_id': 'uuid3',
                    'do_send_receipts': False,
                    'increment': 3,
                    'inn_pd_id': 'inn2_pd_id',
                    'is_own_park': False,
                    'park_id': 'dbid3',
                    'phone_pd_id': 'phone2_pd_id',
                    'updated_at': '2021-11-03T00:00:00.000',
                },
                'park_contractor_profile_id': 'dbid3_uuid3',
                'revision': '2021-11-03T00:00:00+0000_3',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('selfemployed_main', files=['initial.sql'])
async def test_retrieve_by_inn(taxi_selfemployed_fns_replica):
    response = await taxi_selfemployed_fns_replica.post(
        '/v1/bindings/retrieve-by-inn',
        json={'inn_pd_id_in_set': ['inn2_pd_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'bindings_by_inns': [
            {
                'inn_pd_id': 'inn2_pd_id',
                'bindings': [
                    {
                        'data': {
                            'increment': 2,
                            'inn_pd_id': 'inn2_pd_id',
                            'status': 'COMPLETED',
                            'exceeded_legal_income_year': 2021,
                            'updated_at': '2021-11-02T00:00:00.000',
                        },
                        'phone_pd_id': 'phone2_pd_id',
                        'revision': '2021-11-02T00:00:00+0000_2',
                    },
                ],
            },
        ],
    }
