from ctaxi_pyml.common.models import mock_catboost
from ctaxi_pyml.geosuggest.address_suggest import v1 as cxx

ALL_SELECTION_METHODS = [
    'userplace',
    'phone_history.source',
    'phone_history.destination',
    'phone_history.completion_point',
]


def get_common_params():
    return dict(
        max_top_size=10,
        max_middle_size=10,
        max_bottom_size=10,
        max_total_size=30,
        top_merge_distance=1000,
        top_merge_texts=False,
        userplace_merge_distance=1000,
        userplace_merge_texts=False,
        bottom_merge_distance=1000,
        bottom_merge_texts=False,
        min_probability=0,
        equal_probability_diff=0,
        methods=ALL_SELECTION_METHODS,
        min_center_distance=100,
    )


def create_candidates_extractor():
    return cxx.CandidatesExtractor(
        config=cxx.CandidatesExtractorConfig(
            max_size=10,
            min_center_distance=100,
            max_center_distance=100000,
            merge_distance=10,
            merge_use_texts=True,
            merge_userplaces=False,
            methods=ALL_SELECTION_METHODS,
        ),
    )


def test_serializations(load):
    request = cxx.Request.from_json(load('request.json'))
    request.userplaces[0].to_json()
    request.orders[0].to_json()
    request.orders[0].source.to_json()
    request.search_routes[0].to_json()
    request.suggest_addresses[0].to_json()

    popular_request = cxx.Request.from_json(
        load('request_with_popular_locations.json'),
    )
    popular_request.popular_locations[0].to_json()
    features_config = cxx.FeaturesExtractorConfig.from_json(
        load('features_config.json'),
    )
    features_config.to_json()


def test_rec_sys(load):
    request = cxx.Request.from_json(load('request.json'))

    candidates_extractor = create_candidates_extractor()
    features_config = cxx.FeaturesExtractorConfig.from_json(
        load('features_config.json'),
    )
    features_extractor = cxx.FeaturesExtractor(features_config)
    postprocessor = cxx.PostProcessor()
    params = cxx.Params(**get_common_params(), max_center_distance=100000)

    candidates_number = 3
    candidates = candidates_extractor(request)
    assert len(candidates) == candidates_number

    features = features_extractor(candidates, request)
    assert len(features.numerical) == candidates_number
    assert len(features.categorical) == candidates_number

    num_features_number = 348
    cat_features_number = 5
    for values in features.numerical:
        assert len(values) == num_features_number
    for values in features.categorical:
        assert len(values) == cat_features_number

    predictions_extractor = mock_catboost(
        num_factors_count=num_features_number,
        cat_factors_count=cat_features_number,
    )
    predictions = [-100, 300, 800]
    assert len(predictions) == candidates_number

    result = postprocessor(candidates, predictions, request, params)
    assert result is not None

    recommender = cxx.Recommender(
        candidates_extractor=candidates_extractor,
        features_extractor=features_extractor,
        predictions_extractor=predictions_extractor,
        postprocessor=postprocessor,
    )
    response = recommender(request, params)
    assert len(response.items) == 2


def test_rec_sys_no_searchroutes(load):
    request = cxx.Request.from_json(load('request.json'))

    candidates_extractor = create_candidates_extractor()
    features_config = cxx.FeaturesExtractorConfig.from_json(
        load('features_config_no_searchroutes.json'),
    )
    features_extractor = cxx.FeaturesExtractor(features_config)
    postprocessor = cxx.PostProcessor()
    params = cxx.Params(**get_common_params(), max_center_distance=100000)

    candidates_number = 3
    candidates = candidates_extractor(request)
    assert len(candidates) == candidates_number

    features = features_extractor(candidates, request)
    assert len(features.numerical) == candidates_number
    assert len(features.categorical) == candidates_number

    num_features_number = 220
    cat_features_number = 5
    for values in features.numerical:
        assert len(values) == num_features_number
    for values in features.categorical:
        assert len(values) == cat_features_number

    predictions_extractor = mock_catboost(
        num_factors_count=num_features_number,
        cat_factors_count=cat_features_number,
    )
    predictions = [-100, 300, 800]
    assert len(predictions) == candidates_number

    result = postprocessor(candidates, predictions, request, params)
    assert result is not None

    recommender = cxx.Recommender(
        candidates_extractor=candidates_extractor,
        features_extractor=features_extractor,
        predictions_extractor=predictions_extractor,
        postprocessor=postprocessor,
    )
    response = recommender(request, params)
    assert len(response.items) == 2


def test_popular_locations_recommender(load):
    request = cxx.Request.from_json(
        load('request_with_popular_locations.json'),
    )

    candidates_extractor = cxx.PopularCandidatesExtractor(
        config=cxx.PopularCandidatesConfig(
            max_size=100, max_distance=1000000000, min_distance=0,
        ),
    )
    candidates = candidates_extractor(request)
    assert len(candidates) == 1
    features_extractor = cxx.PopularFeaturesExtractor(
        config=cxx.PopularFeaturesConfig(
            embeddings_size=4,
            time_shifts_count=4,
            geo_combinations_count=4,
            angle_rotations_count=3,
        ),
    )
    features = features_extractor(candidates, request)
    assert len(features.numerical) == 1
    assert len(features.categorical) == 1
    for values in features.numerical:
        assert len(values) == features_extractor.get_num_features_size()
    for values in features.categorical:
        assert len(values) == features_extractor.get_cat_features_size()

    predictions = [1]
    postprocessor = cxx.PopularPostProcessor()

    params = cxx.Params(
        **get_common_params(),
        max_center_distance=10000000000,
        max_popular_locations_size=10,
        popular_locations_merge_distance=5,
    )
    result = postprocessor(candidates, predictions, request, params)
    assert len(result) == 1

    predictions_extractor = mock_catboost(
        num_factors_count=features_extractor.get_num_features_size(),
        cat_factors_count=features_extractor.get_cat_features_size(),
    )
    recommender = cxx.PopularRecommender(
        candidates_extractor=candidates_extractor,
        features_extractor=features_extractor,
        predictions_extractor=predictions_extractor,
        postprocessor=postprocessor,
    )
    result = recommender(request, params)
    assert len(result.items) == 1
