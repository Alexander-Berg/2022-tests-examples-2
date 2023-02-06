import json

from taxi_ml_cxx.zoo.expected_sources import FeaturesExtractor


if __name__ == '__main__':
    with open('body.json', 'r') as body_file:
        body = json.load(body_file)
    with open('all_ex_candidates.json', 'r') as candidates_file:
        candidates = json.load(candidates_file)

    features_extractor = FeaturesExtractor()
    features = features_extractor(body, candidates)

    with open('features.json', 'r') as features_file:
        feature_reference = json.load(features_file)
    for feature, ground_truth in zip(features, feature_reference):
        if isinstance(feature, float) and isinstance(ground_truth, float):
            assert abs(feature - ground_truth) < 1e-32
        else:
            assert feature == ground_truth

print('Test OK')
