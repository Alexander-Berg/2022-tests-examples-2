# pylint: disable=import-only-modules
import pytest


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_retrieve_1.json', id='conventional retrieve'),
        pytest.param('test_retrieve_2.json', id='error: camera is absent'),
    ],
)
async def test_retrieve(
        taxi_cctv_admin, mongodb, mocked_time, load_json, input_file, cipher,
):
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

    response = await taxi_cctv_admin.post(
        '/v1/camera/retrieve', headers={'X-YaCctv-Camera-ID': camera_id},
    )

    assert response.status_code == input_data['expected_code']
    expected_value = input_data.get('expected_value')

    if not expected_value:
        return

    assert response.headers['X-YaCctv-Camera-URI'] == expected_value['uri']

    assert expected_value['updated_ts'] == response.json()['updated_ts']
