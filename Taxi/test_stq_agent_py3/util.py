import os.path

import bson.json_util
import pytest

TEST_ID = 'test_id'


def parametrize_data(test_file_path, rel_json_path, param_names):
    assert TEST_ID not in param_names, f'{TEST_ID} reserved for tests names'
    json_path = os.path.join(
        os.path.dirname(test_file_path),
        'static',
        os.path.splitext(os.path.basename(test_file_path))[0],
        rel_json_path,
    )
    with open(json_path) as f_read:
        doc = bson.json_util.loads(f_read.read())

    test_params = []
    for test_item in doc:
        test_item_params = tuple(test_item[name] for name in param_names)
        if TEST_ID in test_item:
            test_params.append(
                pytest.param(*test_item_params, id=test_item[TEST_ID]),
            )
        else:
            test_params.append(test_item_params)
    return pytest.mark.parametrize(', '.join(param_names), test_params)
