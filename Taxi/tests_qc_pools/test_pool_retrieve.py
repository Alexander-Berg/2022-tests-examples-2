import pytest


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
)
@pytest.mark.parametrize(
    'limit,cursor,length,new_cursor',
    [(5, '0', 5, '5'), (5, '5', 2, '33'), (10, '10', 1, '33')],
)
async def test_pool_retrieve_ok_psql(
        limit, cursor, length, new_cursor, taxi_qc_pools, load_json,
):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': limit, 'cursor': cursor},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['items']) == length
    assert body['cursor'] == new_cursor


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
)
async def test_pool_retrieve_types_ok_psql(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool2'},
        json={'limit': 1, 'cursor': '0'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {
        'cursor': '34',
        'items': [
            {
                'created': '2020-01-01T00:00:33+00:00',
                'data': [
                    {'field': 'bool', 'value': True},
                    {'field': 'int', 'value': 11},
                    {'field': 'set_string', 'value': ['AAA222']},
                    {'field': 'string', 'value': 'AAA111'},
                ],
                'entity_id': 'entity_id34',
                'entity_type': 'driver',
                'exam': 'dkvu',
                'id': 'id_dkvu_34',
            },
        ],
    }


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
    QC_POOLS_PERSONAL_SETTINGS={
        'bulk_retrieve': 100,
        'bulk_store': 100,
        'pool3': {
            'retrieve': {
                'license_pd_id': {
                    'data_type': 'driver_licenses',
                    'alias': 'license',
                },
            },
        },
    },
)
async def test_pool_retrieve_pd(taxi_qc_pools, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    async def _licenses_retrieve(request):
        assert request.json == {
            'items': [{'id': 'license_pd_id3'}],
            'primary_replica': False,
        }
        return {'items': [{'id': 'license_pd_id3', 'value': 'license3'}]}

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool3'},
        json={'limit': 5, 'cursor': '1'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['items'][0]['data'] == [
        {'field': 'license', 'value': 'license3'},
    ]
