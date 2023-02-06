async def test_yt_replica_reader_cache_read_write(taxi_cargo_claims):
    await taxi_cargo_claims.write_cache_dumps(
        names=['replication-yt-targets-cache'],
    )
    await taxi_cargo_claims.read_cache_dumps(
        names=['replication-yt-targets-cache'],
    )
