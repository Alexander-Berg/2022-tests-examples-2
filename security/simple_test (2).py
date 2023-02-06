import pytest

from security.ant_secret.snooper import Snooper, SecretTypes


def test_search_oauth():
    input = b'Authorization: OAuth AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    snooper = Snooper()
    searcher = snooper.searcher()
    result = searcher.search(input)
    results = [r for r in result]
    assert len(results) == 1
    secret = results.pop()

    assert secret.secret == b'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    assert secret.is_yandex_oauth
    assert secret.type == SecretTypes.yandex_oauth
    assert secret.secret_from == 21
    assert secret.secret_len == 39
    assert secret.secret_to == 60
    masked = input[:secret.mask_from] + b'X' * secret.mask_len + input[secret.mask_to:]
    assert masked == b'Authorization: OAuth AQAD-qJSJpcjAAADwHXXXXXXXXXXXXXXXXXXXXX'


def test_search_yc_apikey():
    input = b'Authorization: Bearer AQVN0x35bd5AgbWb6X4WpwEW0_2f4sYy5aH5Z_aM'
    snooper = Snooper()
    searcher = snooper.searcher()
    result = searcher.search(input)
    results = [r for r in result]
    assert len(results) == 1
    secret = results.pop()

    assert secret.secret == b'AQVN0x35bd5AgbWb6X4WpwEW0_2f4sYy5aH5Z_aM'
    assert secret.is_yc_api_key
    assert secret.type == SecretTypes.yc_api_key
    assert secret.secret_from == 22
    assert secret.secret_len == 40
    assert secret.secret_to == 62
    masked = input[:secret.mask_from] + b'X' * secret.mask_len + input[secret.mask_to:]
    assert masked == b'Authorization: Bearer AQVNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'


def test_mask():
    input = b'Authorization: OAuth AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    snooper = Snooper()
    searcher = snooper.searcher()
    result = searcher.mask(input)
    assert result == b'Authorization: OAuth AQAD-qJSJpcjAAADwHXXXXXXXXXXXXXXXXXXXXX'
    assert input == b'Authorization: OAuth AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'


def test_mask_whole():
    input = b'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    snooper = Snooper()
    searcher = snooper.searcher()
    result = searcher.mask(input)
    assert result == b'AQAD-qJSJpcjAAADwHXXXXXXXXXXXXXXXXXXXXX'
    assert input == b'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'


if __name__ == '__main__':
    pytest.main([__file__])
