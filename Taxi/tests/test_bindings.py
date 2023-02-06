def test_root():
    import ctaxi_pyml  # noqa: F401


def test_common_geo():
    import ctaxi_pyml.common.geo  # noqa: F401


def test_eats_places_ranking_api_v2():
    import ctaxi_pyml.eats.places_ranking.api.v2  # noqa: F401


def test_common_gzip():
    from ctaxi_pyml.common import gzip

    eng_str = 'string'
    rus_str = 'строка'
    eng_utf8_bytes = eng_str.encode('utf-8')
    rus_utf8_bytes = rus_str.encode('utf-8')

    assert eng_str == gzip.decompress_b64(gzip.compress_b64(eng_str))
    assert rus_str == gzip.decompress_b64(gzip.compress_b64(rus_str))

    assert eng_utf8_bytes == gzip.decompress(gzip.compress(eng_utf8_bytes))
    assert rus_utf8_bytes == gzip.decompress(gzip.compress(rus_utf8_bytes))

    assert eng_utf8_bytes == gzip.decompress(gzip.compress(eng_str))
    assert rus_utf8_bytes == gzip.decompress(gzip.compress(rus_str))
