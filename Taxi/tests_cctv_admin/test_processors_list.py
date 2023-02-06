# pylint: disable=import-only-modules


async def _insert_processor(taxi_cctv_admin, processor_id):
    body = {'new_value': {'cameras': [], 'hostname': '127.0.0.1'}}
    response = await taxi_cctv_admin.post(
        '/v1/processor/store',
        headers={'X-YaCctv-Processor-ID': processor_id},
        json=body,
    )
    assert response.status_code == 200


async def test_processors_list(taxi_cctv_admin, mongodb):
    mongodb.cctv_processors.remove({})
    input_processors = {'processor_1', 'processor_2', 'processor_3'}

    for processor in input_processors:
        await _insert_processor(taxi_cctv_admin, processor)

    response = await taxi_cctv_admin.post('/v1/processors/list')
    processors_list = {processor for processor in response.json()}
    assert processors_list == input_processors
