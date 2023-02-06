import pytest


def assert_non_equal(response, keys):
    assert response.status_code == 409
    json = response.json()
    assert json['code'] == 'responses_are_different'
    assert json['message'] == 'Legacy and fallback responses does not match'
    assert json['details']['different_keys'] == keys


@pytest.mark.parametrize(
    'legacy,fallback,result,keys',
    [
        ({}, {}, True, []),
        ({'a': None}, {}, True, []),
        ({'a': 1}, {}, False, ['a']),
        ({'a': 1}, {'b': 2}, False, ['a', 'b']),
        ({'a': 1}, {'a': 2}, False, ['a']),
        ({'a': {'b': 1}}, {'a': 2}, False, ['a']),
        ({'a': {'b': 1}}, {'a': {'b': 1}}, True, []),
        ({'a': {'b': 1}}, {'a': {'b': 2}}, False, ['a', 'a.b']),
        (
            {'a': {'b': 1, 'c': 3}},
            {'a': {'b': 2, 'c': 4}},
            False,
            ['a', 'a.b', 'a.c'],
        ),
        ({'a': {'b': 1, 'd': 1}}, {'a': {'b': 2}}, False, ['a', 'a.d']),
        ({'a': 'a'}, {'a': {'b': 2}}, False, ['a']),
        ({'a': 'a'}, {'a': 3}, False, ['a']),
        ({'a': 'a'}, {'a': []}, False, ['a']),
        ({'a': []}, {'a': []}, True, []),
        ({'a': ['b']}, {'a': []}, False, ['a']),
        ({'a': [{'b': 1}]}, {'a': [{'b': 2}]}, False, ['a', 'a.0', 'a.0.b']),
    ],
)
async def test_compare(taxi_zoneinfo, legacy, fallback, result, keys):
    request = {'response_legacy': legacy, 'response_fallback': fallback}
    response = await taxi_zoneinfo.post('v1/zoneinfo/compare', json=request)
    if result:
        assert response.status_code == 200
    else:
        assert_non_equal(response, keys)


@pytest.mark.parametrize(
    'legacy,fallback,result,keys',
    [
        ({'a': 1}, {}, True, []),
        ({'a': 1}, {'b': 2}, False, ['b']),
        ({'a': 1}, {'a': 2}, True, []),
        ({'c': {'b': 1}}, {'c': {'b': 2}}, True, []),
        ({'c': {'a': 1}}, {'c': {'a': 2}}, False, ['c', 'c.a']),
        ({'c': [{'b': 1}]}, {'c': [{'b': 2}]}, True, []),
        ({'c': [{'a': 1}]}, {'c': [{'a': 2}]}, False, ['c', 'c.0', 'c.0.a']),
    ],
)
@pytest.mark.config(ZONEINFO_COMPARE_CONFIG={'ignore_keys': ['a', 'c.b']})
async def test_config(taxi_zoneinfo, legacy, fallback, result, keys):
    request = {'response_legacy': legacy, 'response_fallback': fallback}
    response = await taxi_zoneinfo.post('v1/zoneinfo/compare', json=request)
    if result:
        assert response.status_code == 200
    else:
        assert_non_equal(response, keys)


@pytest.mark.parametrize(
    'legacy,fallback,result,keys',
    [
        (
            {'array': [{'id': 'to_exclude_a'}]},
            {'array': [{'id': 'to_exclude_b'}]},
            True,
            [],
        ),
        (
            {'array': [{'id': 'a'}]},
            {'array': [{'id': 'to_exclude_a'}, {'id': 'a'}]},
            True,
            [],
        ),
        (
            {'array': [{'id': 'b'}, {'id': 'a'}]},
            {'array': [{'id': 'a'}, {'id': 'b'}]},
            True,
            [],
        ),
        (
            {'array': [{'id': 'to_exclude_a'}, {'id': 'b'}, {'id': 'a'}]},
            {'array': [{'id': 'a'}, {'id': 'b'}]},
            True,
            [],
        ),
    ],
)
@pytest.mark.config(
    ZONEINFO_COMPARE_CONFIG={
        'sort_array_rules': [
            {
                'array_path': 'array',
                'id_key': 'id',
                'ignore_elements': ['to_exclude_a', 'to_exclude_b'],
            },
        ],
    },
)
async def test_config_array(taxi_zoneinfo, legacy, fallback, result, keys):
    request = {'response_legacy': legacy, 'response_fallback': fallback}
    response = await taxi_zoneinfo.post('v1/zoneinfo/compare', json=request)
    if result:
        assert response.status_code == 200
    else:
        assert_non_equal(response, keys)


@pytest.mark.parametrize(
    'legacy,fallback,result,keys',
    [
        (
            {'array': [{'nested_array': ['a', 'b']}]},
            {'array': [{'nested_array': ['b', 'a']}]},
            True,
            [],
        ),
        (
            {'array': [{'nested_array': ['a', 'b', 'c']}]},
            {'array': [{'nested_array': ['b', 'a']}]},
            True,
            [],
        ),
        (
            {'array': [{'nested_array': ['a', 'b', 'c', 'd']}]},
            {'array': [{'nested_array': ['b', 'a']}]},
            False,
            ['array', 'array.0', 'array.0.nested_array'],
        ),
    ],
)
@pytest.mark.config(
    ZONEINFO_COMPARE_CONFIG={
        'sort_array_rules': [
            {
                'array_path': 'array.nested_array',
                'id_key': '',
                'ignore_elements': ['c'],
            },
        ],
    },
)
async def test_config_nested_array(
        taxi_zoneinfo, legacy, fallback, result, keys,
):
    request = {'response_legacy': legacy, 'response_fallback': fallback}
    response = await taxi_zoneinfo.post('v1/zoneinfo/compare', json=request)
    if result:
        assert response.status_code == 200
    else:
        assert_non_equal(response, keys)
