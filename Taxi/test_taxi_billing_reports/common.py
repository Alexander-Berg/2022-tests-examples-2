from taxi.billing import resource_limiter


def compare_resources(actual, expected_from_json):
    expected = [
        resource_limiter.Resource(name=res[0], amount=res[1])
        for res in expected_from_json
    ]
    sorted_actual = _sorted_resources(actual)
    sorted_expected = _sorted_resources(expected)
    assert (
        sorted_actual == sorted_expected
    ), f'{sorted_actual} != {sorted_expected}'


def _sorted_resources(resources):
    return sorted(resources, key=lambda res: res.name)
