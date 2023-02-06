# pylint: disable=import-only-modules
import pytest

import tests_cctv_admin.utils as utils


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_insert_1.json', id='conventional insertion'),
        pytest.param(
            'test_insert_2.json', id='error: camera is already inserted',
        ),
        pytest.param('test_update_1.json', id='conventional update'),
        pytest.param('test_update_2.json', id='newer updated_ts in db'),
        pytest.param(
            'test_update_3.json',
            id='no update; can\'t update an absent camera',
        ),
        pytest.param(
            'test_update_4.json',
            id='no update; prev_updated_ts differs from updated_ts in db',
        ),
    ],
)
async def test_store(
        taxi_cctv_admin, mongodb, mocked_time, load_json, input_file, cipher,
):
    mocked_time.set(utils.parse_date_str('2022-04-07 00:01:07.0+00'))
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    mongodb.cctv_cameras.remove({})
    input_data = load_json(input_file)

    initial_value = input_data.get('initial_value')
    if initial_value:
        encrypted_uri = cipher.encrypt(initial_value['uri'].encode('utf-8'))
        initial_value['uri'] = {
            'encrypted_data': encrypted_uri['data'],
            'dek': encrypted_uri['dek'],
        }
        mongodb.cctv_cameras.insert(initial_value)

    camera_id = input_data['camera_id']
    camera_uri = input_data['new_value']['uri']

    prev_updated_ts = input_data.get('prev_updated_ts')
    body = {}
    if prev_updated_ts:
        body['prev_updated_ts'] = prev_updated_ts

    request_header = {
        'X-YaCctv-Camera-ID': camera_id,
        'X-YaCctv-Camera-URI': camera_uri,
    }

    response = await taxi_cctv_admin.post(
        '/v1/camera/store', headers=request_header, json=body,
    )
    assert response.status_code == input_data['expected_code']
    result = mongodb.cctv_cameras.find_one({'_id': camera_id})

    expected_value = input_data.get('expected_value')
    if not expected_value:
        assert not result
        return

    encrypted_data = {
        'data': result['uri']['encrypted_data'],
        'dek': result['uri']['dek'],
    }
    result['uri'] = cipher.decrypt(encrypted_data).decode('utf-8')
    assert expected_value == result
