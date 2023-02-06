import json
import re

from django.test import Client
import pytest

from taxi import config


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb
@pytest.mark.parametrize(
    'timestamp, tl, br, classes, geoareas_response, expected_filename',
    [
        (1510000000, [1.0, 1.0], [5.0, 5.0], ['econom'],
            'geoareas_response_1.json', 'expected_geoareas_1.json'),
        (1510000000, [1.0, 1.0], [1.0, 5.0], ['econom'],
            'geoareas_response_1.json', 'expected_geoareas_1.json'),
        (1510000000, [1.0, 1.0], [1.0, 1.0], ['econom'],
            'geoareas_response_1.json', 'expected_geoareas_1.json'),
        (1510000000, [1.0, 1.0], [11.0, 11.0], ['econom'],
            'geoareas_response_both.json', 'expected_geoareas_1.json'),
        (1510000000, [1.0, 1.0], [5.0, 5.0], ['comfort', 'comfortplus'],
            'geoareas_response_1.json', 'expected_geoareas_empty.json'),
        (1530000000, [1.0, 1.0], [5.0, 5.0], ['econom'],
            'geoareas_response_1.json', 'expected_geoareas_12.json'),
        (1530000000, [1.0, 1.0], [5.0, 5.0], [],
            'geoareas_response_1.json', 'expected_geoareas_12.json'),
        (1550000000, [1.0, 1.0], [5.0, 5.0], ['econom'],
            'geoareas_response_1.json', 'expected_geoareas_2.json'),
        (1550000000, [1.0, 1.0], [15.0, 15.0], ['econom'],
            'geoareas_response_both.json', 'expected_geoareas_both_2.json'),
        (1510000000, [18.0, 18.0], [19.0, 19.0], ['econom'],
            'geoareas_response_empty.json', 'expected_geoareas_empty.json'),
    ]
)
@pytest.mark.parametrize(
    'get_sg_from_wrapper', [False, True]
)
@pytest.inline_callbacks
def test_get_subvention_geoareas_geometry(
        areq_request, load, timestamp, tl, br, classes, geoareas_response, expected_filename, get_sg_from_wrapper):
    yield config.GET_SUBVENTION_GEOAREAS_BY_GEOMETRY_FROM_WRAPPER.save({
        '__default__': get_sg_from_wrapper
    })
    path = '/api/get_subvention_geoareas_geometry/'
    if tl == br:
        params = {
            'point': ','.join([str(x) for x in tl]),
            'timestamp': timestamp
        }
    else:
        params = {
            'tl': ','.join([str(x) for x in tl]),
            'br': ','.join([str(x) for x in br]),
            'timestamp': timestamp
        }
    if classes:
        params['classes'] = ','.join(classes)

    @areq_request
    def _geoareas_request(method, url, **kwargs):
        params = kwargs['params']

        assert 'point' in params or (
            'top_left' in params and 'bottom_right' in params)
        strings_to_check = []
        if 'point' in params:
            strings_to_check.append(params['point'])
        else:
            strings_to_check.append(params['top_left'])
            strings_to_check.append(params['bottom_right'])

        pattern = re.compile("^[0-9]+.?[0-9]*, ?[0-9]+.?[0-9]*$")

        for string_to_check in strings_to_check:
            assert pattern.match(string_to_check)

        return areq_request.response(200, load(geoareas_response))

    response = yield Client().get(path, params)
    assert response.status_code == 200

    result = json.loads(response.content)
    expected = json.loads(load(expected_filename))

    assert result == expected


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb
@pytest.inline_callbacks
def test_get_subvention_geoareas_geometry_no_points():
    path = '/api/get_subvention_geoareas_geometry/'
    params = {
        'timestamp': 1510000000
    }

    response = yield Client().get(path, params)
    assert response.status_code == 400
