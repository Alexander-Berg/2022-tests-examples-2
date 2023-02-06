import numpy as np
from projects.user_order_fakeness import features_extractor


def test_extractor(load_json):
    data = load_json('data.json')
    assert len(data) == 5

    for testcase in data:
        num_features = features_extractor.extract_num_features(
            testcase['request'],
        )
        cat_features = features_extractor.extract_cat_features(
            testcase['request'],
        )

        assert len(num_features) == len(testcase['num_features'])
        assert len(cat_features) == len(testcase['cat_features'])
        assert all(
            np.array(num_features) == np.array(testcase['num_features']),
        )
        assert all(
            np.array(cat_features) == np.array(testcase['cat_features']),
        )
