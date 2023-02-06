from ctaxi_pyml.geosuggest.pickup_points import v1 as cxx


def test_extractors(load):
    candidates_extractor = cxx.CandidatesExtractor(
        config=cxx.CandidatesConfig(max_size=100, max_distance=200),
    )
    features_extractor = cxx.FeaturesExtractor(
        config=cxx.FeaturesConfig.from_json(load('features_config.json')),
    )

    request = cxx.Request.from_json(load('request.json'))
    candidates = candidates_extractor(request)
    features = features_extractor(candidates, request)

    assert len(candidates) == 2
    assert len(features.numerical) == 2
