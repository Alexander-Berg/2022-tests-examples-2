# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import functools
import uuid

import dateutil.parser as date_parser
import pytest

from exams_platform_plugins import *  # noqa: F403 F401


LICENSES_MATCH = {
    '12AT123450': '0104248e26074dd88e46f350037459fa',
    '12AT123451': '1104248e26074dd88e46f350037459fa',
    '12AT123452': '2104248e26074dd88e46f350037459fa',
    '12AT123453': '3104248e26074dd88e46f350037459fa',
    '12AT123454': '4104248e26074dd88e46f350037459fa',
    '12AT123455': '5104248e26074dd88e46f350037459fa',
    '12AT123456': '6104248e26074dd88e46f350037459fa',
    '12AT123457': '7104248e26074dd88e46f350037459fa',
    '12AT123458': '8104248e26074dd88e46f350037459fa',
    '12AT123459': '9104248e26074dd88e46f350037459fa',
    '12AT123460': '0204248e26074dd88e46f350037459fa',
    '12AT123461': '1204248e26074dd88e46f350037459fa',
    '12AT123462': '2204248e26074dd88e46f350037459fa',
    '12AT123463': '3204248e26074dd88e46f350037459fa',
    '12AT123464': '4204248e26074dd88e46f350037459fa',
    '12AT123465': '5204248e26074dd88e46f350037459fa',
    'INVALID': None,
}
PERSONAL_NULL_RESPONSE = {
    'code': '400',
    'message': 'Field \'value\' is of a wrong type',
}


@functools.lru_cache(None)
def personal_response(type_, id_):
    if type_ == 'license_id':
        value = id_
        id_ = LICENSES_MATCH[value]
    else:
        raise ValueError
    response = {'value': value, 'id': id_}
    return response


@pytest.fixture  # noqa: F405
def _personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def store_licenses(request):
        type_ = 'license_id'
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response(type_, value)


def _recursive_compare_bodies(expected, actual):
    for key, value in expected.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                _recursive_compare_bodies(item, actual[key][i])
        elif isinstance(value, dict):
            _recursive_compare_bodies(value, actual[key])
        else:
            if value == 'uuid.UUID':
                assert uuid.UUID(actual[key])
            elif value == 'datetime.datetime':
                assert date_parser.parse(actual[key])
            else:
                assert actual[key] == value


@pytest.fixture
def request_exams_platform(taxi_exams_platform, _personal):
    async def _wrapper(
            url,
            method='post',
            headers=None,
            params=None,
            body=None,
            expected_response_code=200,
            expected_response_headers=None,
            expected_response_body=None,
    ):
        response = await taxi_exams_platform.request(
            method, url, headers=headers, params=params, json=body,
        )
        assert response.status == expected_response_code
        if expected_response_headers:
            assert response.headers == expected_response_headers
        if expected_response_body:
            _recursive_compare_bodies(expected_response_body, response.json())
        return response

    return _wrapper
