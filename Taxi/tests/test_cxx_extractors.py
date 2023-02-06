import argparse
import json
import itertools
import time

from taxi_ml_cxx.zoo.zerosuggest import CandidatesExtractor
from taxi_ml_cxx.zoo.zerosuggest import FeaturesExtractor
from taxi_ml_cxx.zoo.zerosuggest import Preprocessor


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--request-path', required=True)
    parser.add_argument('--features-path', required=True)
    args = parser.parse_args()

    with open(args.request_path) as f:
        request = json.load(f)
    with open(args.features_path) as f:
        expected_features = json.load(f)

    methods = [
        'userplace',
        'phone_history.source',
        'phone_history.destination',
        'phone_history.completion_point',
        'order_offers.source',
        'order_offers.destination'
    ]
    candidates_extractor = CandidatesExtractor(methods)
    features_extractor = FeaturesExtractor()
    preprocessor = Preprocessor(
        max_size=100,
        min_center_distance=0,
        max_center_distance=100,
        merge_distance=5,
        merge_use_texts=True,
        merge_userplaces=False,
        methods=methods
    )

    start = time.time()
    candidates = candidates_extractor(request)
    _ = preprocessor(candidates, request)
    features = features_extractor(candidates, request)
    end = time.time()

    assert len(features) == len(expected_features)
    for features_row, gt_row in itertools.izip(features, expected_features):
        assert len(features_row) == len(gt_row)
        for feature, gt_feature in itertools.izip(features_row, gt_row):
            if isinstance(feature, float) and isinstance(gt_feature, float):
                assert abs(feature - gt_feature) < 1e-32
            else:
                assert feature == gt_feature

    print('Test OK')
    print('{:.2f} ms'.format(1000 * (end - start)))
