# pylint: disable=import-only-modules
import pytest


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_retrieve_1.json', id='conventional retrieve'),
        pytest.param('test_retrieve_2.json', id='error: processor is absent'),
        pytest.param('test_retrieve_2.json', id='retrieve with absent fields'),
    ],
)
async def test_retrieve(
        taxi_cctv_admin, mongodb, mocked_time, load_json, input_file,
):
    mongodb.cctv_processors.remove({})
    input_data = load_json(input_file)

    initial_value = input_data.get('initial_value')
    if initial_value:
        mongodb.cctv_processors.insert(initial_value)

    processor_id = input_data['processor_id']

    response = await taxi_cctv_admin.post(
        '/v1/processor/retrieve',
        headers={'X-YaCctv-Processor-ID': processor_id},
    )

    assert response.status_code == input_data['expected_code']

    expected_value = input_data.get('expected_value')
    if not expected_value:
        return

    assert expected_value == response.json()
