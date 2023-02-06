try:
    import lz4.block as lz4
except ImportError:
    import lz4


async def test_lz4_compress(taxi_arcadia_userver_test):
    test_data = b'This is a test string to compress'
    response = await taxi_arcadia_userver_test.post(
        '/lz4/compress', data=test_data,
    )

    assert response.status_code == 200
    assert lz4.decompress(response.content) == test_data


async def test_lz4_decompress(taxi_arcadia_userver_test):
    test_data = b'This is a test string to decompress'

    response = await taxi_arcadia_userver_test.post(
        '/lz4/decompress', data=lz4.compress(test_data),
    )

    assert response.status_code == 200
    assert response.content == test_data
