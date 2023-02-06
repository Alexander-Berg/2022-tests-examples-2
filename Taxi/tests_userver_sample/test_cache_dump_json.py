import json


CACHE_NAME = 'json-dumped-cache'


async def test_dump_write_read(
        taxi_userver_sample, read_latest_dump, load_json,
):
    # Ensure that a cache dump has been written successfully
    await taxi_userver_sample.write_cache_dumps(names=[CACHE_NAME])

    # Check the contents of the dump by comparing it against the ground truth
    assert json.loads(read_latest_dump(CACHE_NAME)) == load_json(
        'gt-dump.json',
    )

    # Ensure that the dump has been read successfully
    await taxi_userver_sample.read_cache_dumps(names=[CACHE_NAME])
