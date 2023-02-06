# pylint: disable=import-only-modules
import pytest

import tests_cctv_admin.utils as utils


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_insert_1.json', id='conventional insertion'),
        pytest.param('test_insert_2.json', id='minimal processor info'),
        pytest.param('test_insert_3.json', id='error: unknown camera'),
        pytest.param('test_insert_4.json', id='no camera'),
        pytest.param(
            'test_insert_5.json', id='error: processor is already inserted',
        ),
        pytest.param('test_insert_6.json', id='no hostname'),
        pytest.param('test_insert_7.json', id='empty hostname'),
        pytest.param('test_update_1.json', id='conventional update'),
        pytest.param('test_update_2.json', id='newer updated_ts in db'),
        pytest.param(
            'test_update_3.json',
            id='no update; can\'t update an absent processor',
        ),
        pytest.param(
            'test_update_4.json', id='checking unset of some fields 1',
        ),
        pytest.param(
            'test_update_5.json', id='checking unset of some fields 1',
        ),
        pytest.param('test_update_6.json', id='check ticket intouched'),
    ],
)
async def test_store(
        taxi_cctv_admin, mongodb, mocked_time, load_json, input_file,
):
    mocked_time.set(utils.parse_date_str('2022-04-07 00:01:07.0+00'))
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    mongodb.cctv_processors.remove({})
    input_data = load_json(input_file)

    initial_value = input_data.get('initial_value')
    if initial_value:
        mongodb.cctv_processors.insert(initial_value)

    processor_id = input_data['processor_id']

    body = {'new_value': input_data['new_value']}

    prev_updated_ts = input_data.get('prev_updated_ts')
    if prev_updated_ts:
        body['prev_updated_ts'] = prev_updated_ts

    response = await taxi_cctv_admin.post(
        '/v1/processor/store',
        headers={'X-YaCctv-Processor-ID': processor_id},
        json=body,
    )
    assert response.status_code == input_data['expected_code']
    result = mongodb.cctv_processors.find_one({'_id': processor_id})

    expected_value = input_data.get('expected_value')
    if not expected_value:
        assert not result

    assert expected_value == result
