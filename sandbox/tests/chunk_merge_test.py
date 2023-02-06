import sandbox.projects.k50.sow_chunk_merge as sow_chunk_merge

TABLE_PATH = '//2020-01-01'
NUMBER_OF_CHUNKS = 20
CHUNK_SIZE = 2 ** 30  # 1 GB


def test_chunk_merge(yt_stuff):
    yt_client = yt_stuff.get_yt_client()

    # each new entry adds a new chunk to the table
    for i in range(NUMBER_OF_CHUNKS):
        yt_client.write_table('<append=%true>' + TABLE_PATH, [{'value': i}])

    builder = sow_chunk_merge.get_chunk_merge_builder(TABLE_PATH, CHUNK_SIZE)
    yt_client.run_operation(builder)

    assert 1 == yt_client.get_attribute(TABLE_PATH, 'chunk_count')
