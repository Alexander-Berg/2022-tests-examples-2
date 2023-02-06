# pylint: disable=import-only-modules
import base64

import pytest

import tests_cctv_admin.hasher as hasher
import tests_cctv_admin.utils as utils


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test1.json', id='processor has no ticket set'),
        pytest.param('test2.json', id='processor is absent'),
        pytest.param('test3.json', id='concurrent update'),
    ],
)
async def test_ticket(
        taxi_cctv_admin, mongodb, mocked_time, load_json, input_file,
):
    now = utils.parse_date_str('2022-04-07 00:01:07.0+00')
    mocked_time.set(now)
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    mongodb.cctv_cameras.remove({})
    input_data = load_json(input_file)

    initial_value = input_data.get('initial_value')
    mongodb.cctv_processors.insert(initial_value)

    processor_id = input_data['processor_id']

    request_header = {'X-YaCctv-Processor-ID': processor_id}

    response = await taxi_cctv_admin.post(
        '/v1/processor/ticket', headers=request_header,
    )
    assert response.status_code == input_data['expected_code']

    if response.status_code != 200:
        return

    result = mongodb.cctv_processors.find_one({'_id': processor_id})
    expected_hashed_ticket = result['ticket']
    response_ticket = base64.b64decode(
        response.json()['ticket'].encode('utf-8'),
    )
    assert result['updated_ts'] == utils.date_to_ms(now)
    assert hasher.hash_ticket(response_ticket) == expected_hashed_ticket
