from ctaxi_pyml.combo_orders import v1 as cxx
import pytest
import json


@pytest.fixture
def resources_path(get_directory_path):
    return get_directory_path('')


def test_history_storage(load):
    config = {
        'geo_combinations_count': 5,
        'time_shifts_count': 3,
        'history_features_list': ['success_orders'],
        'geohash_precision': 6,
        'add_point_a_features': True,
        'add_point_b_features': True,
    }
    storage = cxx.features.HistoryFeaturesStorage()
    storage.add_history_feature(
        'v1yv33', 'point_a_success_orders_hourly_2', 12,
    )
    storage.add_history_feature(
        'v1yv33', 'point_a_success_orders_hourly_3', 10,
    )
    storage.add_history_feature(
        'v1yv33', 'point_a_success_orders_weekly_6', 35,
    )
    slice = {
        'point_a_success_orders_hourly_2': 24,
        'point_a_success_orders_hourly_3': 17,
    }
    storage.add_history_features_slices('v1xz3k', slice)
    features_config = cxx.objects_pybind.FeaturesConfig.from_json_string(
        json.dumps(config),
    )
    features_extractor = cxx.features.FeaturesExtractor(
        features_config, storage,
    )

    request = cxx.objects_pybind.Request.from_json_string(load('request.json'))

    features = features_extractor(request)
    assert len(features.to_list()) == 29


def test_predictor(load, resources_path):
    request = cxx.objects_pybind.Request.from_json_string(load('request.json'))
    predictor = cxx.features.create_predictor(
        config_path=resources_path + '/config.json',
        model_path=resources_path + '/model.cbm',
        storage_path=resources_path + '/history_features_storage.json',
        mock_mode=True,
    )
    storage = cxx.features.create_history_features_storage(
        storage_path=resources_path + '/history_features_storage.json',
        mock_mode=True,
    )

    assert len(storage.geohash_features) == 2

    params = cxx.features.Params()
    response = predictor(request, params)
    assert response.prediction_raw == 0.5
