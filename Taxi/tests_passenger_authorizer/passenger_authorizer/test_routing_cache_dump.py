import json


async def test_dump_write_read(
        taxi_passenger_authorizer,
        read_latest_dump,
        load_binary,
        object_substitute,
):
    await taxi_passenger_authorizer.write_cache_dumps(names=['rules-cache'])

    assert json.loads(read_latest_dump('rules-cache')) == object_substitute(
        json.loads(load_binary('routing-rules.json')),
    )

    await taxi_passenger_authorizer.read_cache_dumps(names=['rules-cache'])
