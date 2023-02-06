import json

import pytest


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
)
async def test_sample_get_ok_psql(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': 100, 'cursor': '0'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('pool1_retrieve.json')


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={
        '__default__': {
            'expiration_s': 600,
            'meta_projection': [],
            'media_codes': [],
        },
        'pool1': {
            'expiration_s': 600,
            'meta_projection': ['quality-control.name'],
            'media_codes': ['dkvu_front'],
        },
    },
)
async def test_sample_get_fields_media_codes(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={
            'limit': 100,
            'cursor': '0',
            'fields': ['quality-control.name'],
            'media_codes': ['dkvu_front'],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['items'][0]['data']) == 1
    assert len(body['items'][0]['media']) == 1


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
)
async def test_retrieve_no_cursor(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': 100},
    )
    assert response.status_code == 200
    assert response.json() == load_json('pool1_retrieve.json')


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_sample_get_item_cursor(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': 100, 'cursor': '1'},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['items']) == 1
    assert body['items'][0]['id'] == 'id_dkvu_2'


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_sample_get_max_cursor(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool3'},
        json={'limit': 100, 'cursor': '1'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['cursor'] == '9223372036854775807'


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_push_pass_array_pass_data(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    assert len(response.json()['pool_states']) == 1
    assert response.json()['pool_states'][0]['pool'] == 'pool1'
    assert response.json()['pool_states'][0]['status'] == 'new'
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push_array.json'),
    )
    assert response.status_code == 200
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    new_response_states = response.json()['pool_states']
    assert len(new_response_states) == 1
    assert new_response_states[0]['pool'] == 'pool1'
    assert new_response_states[0]['status'] == 'processed'
    assert response.json()['pass']['data'] == load_json('pass_data_array.json')


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_push_one_pass(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    assert len(response.json()['pool_states']) == 1
    assert response.json()['pool_states'][0]['pool'] == 'pool1'
    assert response.json()['pool_states'][0]['status'] == 'new'
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push.json'),
    )
    assert response.status_code == 200
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    new_response_states = response.json()['pool_states']
    assert len(new_response_states) == 1
    assert new_response_states[0]['pool'] == 'pool1'
    assert new_response_states[0]['status'] == 'processed'
    assert response.json()['pass']['data'] == load_json('pass_data.json')


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
@pytest.mark.config(
    QC_POOLS_POOL_SETTINGS={'__default__': {'expiration_s': 600}},
)
async def test_retrieve_push_retrieve(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': 100, 'cursor': '0'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('pool1_retrieve.json')

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push_one.json'),
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/retrieve',
        params={'pool': 'pool1'},
        json={'limit': 100, 'cursor': '0'},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body['items']) == 1
    assert body['items'][0]['id'] == 'id_dkvu_2'

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('failed_passes.json')


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_push_info_with_media(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    assert len(response.json()['pool_states']) == 1
    assert response.json()['pool_states'][0]['pool'] == 'pool1'
    assert response.json()['pool_states'][0]['status'] == 'new'

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_2'},
    )
    assert response.status_code == 200
    assert response.json()['pass']['media'] == [
        {'code': 'dkvu_front', 'url': 'http://dkvu_2_front.jpg'},
    ]

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push_with_media.json'),
    )
    assert response.status_code == 200
    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_1'},
    )
    assert response.status_code == 200
    new_response_states = response.json()['pool_states']
    assert len(new_response_states) == 1
    assert new_response_states[0]['pool'] == 'pool1'
    assert new_response_states[0]['status'] == 'processed'
    assert response.json()['pass']['data'] == load_json('pass_data.json')

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_2'},
    )
    assert response.json()['pass']['media'] == load_json('pass_media.json')
    assert response.status_code == 200


@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_push_passdata_with_null_value(taxi_qc_pools, load_json):
    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool1'},
        json=load_json('pool1_push_with_null_value.json'),
    )
    # return 400 because one of PassData 'value' is null
    assert response.status_code == 400
    assert response.json()['code'] == 'PASSDATA VALUE IS NULL'


def make_bulk_store(request_body, make_id=lambda x: x):
    items = json.loads(request_body)['items']
    response_items = [
        {'id': 'pd_id_' + make_id(i['value']), 'value': i['value']}
        for i in items
    ]
    return {'items': response_items}


@pytest.mark.config(
    QC_POOLS_PERSONAL_SETTINGS={
        'bulk_retrieve': 100,
        'bulk_store': 100,
        'pool3': {
            'push': {
                'license': {
                    'data_type': 'driver_licenses',
                    'alias': 'license_pd_id',
                },
            },
        },
    },
)
@pytest.mark.pgsql('qc_pools', files=['fill_pool1.sql'])
async def test_push_with_pd_data(taxi_qc_pools, load_json, mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_store')
    def pd_bulk_store(request):
        return make_bulk_store(request.get_data())

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_3'},
    )
    assert response.status_code == 200
    assert response.json()['pass']['data'] == [
        {
            'field': 'quality-control.license_pd_id',
            'value': 'qc_license_pd_id',
        },
    ]

    response = await taxi_qc_pools.post(
        '/internal/qc-pools/v1/pool/push',
        params={'pool': 'pool3'},
        json=load_json('push_with_pd_data.json'),
    )
    assert response.status_code == 200
    assert pd_bulk_store.times_called == 1

    response = await taxi_qc_pools.get(
        '/internal/qc-pools/v1/pass/info', params={'id': 'id_dkvu_3'},
    )
    assert response.json()['pass']['data'] == [
        {'field': 'pool3.license_pd_id', 'value': 'pd_id_AAA333'},
        {
            'field': 'quality-control.license_pd_id',
            'value': 'qc_license_pd_id',
        },
    ]
    assert response.status_code == 200
