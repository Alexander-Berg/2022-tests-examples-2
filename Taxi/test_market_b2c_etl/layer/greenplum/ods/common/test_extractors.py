import market_b2c_etl.layer.greenplum.ods.common.extractors as extractor


def test_safe_get_happy_path():
    obj = {
        'a': {
            'x': 'this_is_value',
            'y': 'this_is_another_value'
        }
    }
    actual = extractor.safe_get(obj, ['a', 'x'])
    assert actual == 'this_is_value'


def test_safe_get_no_key_without_default():
    obj = {
        'a': {
            'x': 'this_is_value',
            'y': 'this_is_another_value'
        }
    }
    actual = extractor.safe_get(obj, ['a', 'z'])
    assert actual is None


def test_safe_get_no_key_with_default():
    obj = {
        'a': {
            'x': 'this_is_value',
            'y': 'this_is_another_value'
        }
    }
    actual = extractor.safe_get(obj, ['a', 'z'], 'default')
    assert actual == 'default'


def test_safe_get_no_intemediate_key_with_default():
    obj = {
        'a': {
            'x': 'this_is_value',
            'y': 'this_is_another_value'
        }
    }
    actual = extractor.safe_get(obj, ['z', 'x'], 'default')
    assert actual == 'default'


def execute_extractors(obj, extractors: dict) -> dict:
    res = {}
    for (key, value) in extractors.items():
        if isinstance(value, str):
            res[key] = get_value_by_path(obj, value)
        elif callable(value):
            res[key] = value(obj)
        else:
            raise NotImplementedError()
    return res


def get_value_by_path(obj: dict, path: str):
    parts = path.split('.')
    tmp = obj
    for i in parts:
        if i in tmp:
            tmp = tmp[i]
        else:
            return None
    return tmp
