import urllib.parse


def assert_headers(headers, expected_headers):
    for key, value in expected_headers.items():
        assert key in headers
        assert headers[key] == value


def assert_query_params(query_string, expected_params):
    query_params = {
        key: value
        for key, value in urllib.parse.parse_qsl(query_string.decode())
    }
    assert query_params == expected_params
