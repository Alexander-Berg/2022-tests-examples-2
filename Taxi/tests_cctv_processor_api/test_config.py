# pylint: disable=import-only-modules
import pytest


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_get_1.json', id='200: get'),
        pytest.param('test_get_2.json', id='error: processor is absent'),
        pytest.param('test_get_3.json', id='error:wrong ticket'),
        pytest.param('test_get_4.json', id='304: no changes'),
        pytest.param('test_get_5.json', id='200: get without updated_ts'),
    ],
)
async def test_get(
        taxi_cctv_processor_api,
        mongodb,
        mocked_time,
        load_json,
        input_file,
        cipher,
):
    mongodb.cctv_processors.remove({})
    input_data = load_json(input_file)

    initial_value = input_data.get('initial_value')
    if initial_value:
        initial_value['ticket'] = initial_value['ticket'].encode('utf-8')
        mongodb.cctv_processors.insert(initial_value)

    initial_value_cameras = input_data.get('initial_value_cameras')
    if initial_value_cameras:
        for initial_value_camera in initial_value_cameras:
            encrypted_uri = cipher.encrypt(
                initial_value_camera['uri'].encode('utf-8'),
            )
            initial_value_camera['uri'] = {
                'encrypted_data': encrypted_uri['data'],
                'dek': encrypted_uri['dek'],
            }
            mongodb.cctv_cameras.insert(initial_value_camera)

    processor_id = input_data['processor_id']
    processor_ticket = input_data['processor_ticket']
    headers = {
        'X-YaCctv-Processor-ID': processor_id,
        'X-YaCctv-Processor-Ticket': processor_ticket,
    }
    query_params = {}
    if 'updated_ts' in input_data:
        query_params['updated_ts'] = str(input_data['updated_ts'])

    response = await taxi_cctv_processor_api.get(
        '/v1/config', headers=headers, params=query_params,
    )

    assert response.status_code == input_data['expected_code']

    expected_value = input_data.get('expected_value')
    if not expected_value:
        return

    assert expected_value == response.json()
