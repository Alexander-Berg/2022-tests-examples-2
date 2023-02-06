from ctaxi_pyml.personal_conversion import v1 as cxx
import pytest


@pytest.fixture
def resources_path(get_directory_path):
    return get_directory_path('')


def test_object(load):
    request = cxx.objects_pybind.Request.from_json_string(load('request.json'))
    assert request.tariff_zone == 'samara'
    assert request.history_features['total_orders_this_monthday'] == 9
    assert request.history_features['mean_orders_this_monthday'] == 0.12
    assert request.route_distance == 1223.2
    assert request.point_a['lon'] == 55.77557290200576
    assert len(request.classes_info) == 3
    assert request.classes_info.get('vip') is not None
    assert request.classes_info['vip'].surge_value == 1.2
    request.to_json_string()


def test_features_config(load):
    config = cxx.objects_pybind.PredictorConfig.from_json_string(
        load('config.json'),
    )
    features_config = config.features_config
    assert features_config.add_history_features is True
    assert features_config.add_pin_features is False
    assert (
        features_config.custom_default_values['mean_pin_conversion_time']
        == 1e9
    )
    assert features_config.geo_combinations_count == 3
    assert (
        'total_orders_this_monthday' in features_config.history_features_names
    )
    assert 'last_fifty_days_mean' not in features_config.history_features_names


def test_create_predictor(load, resources_path):
    predictor = cxx.features.create_predictor(
        resources_path + '/config.json',
        resources_path + '/model.cbm',
        mock_mode=True,
    )
    params = cxx.features.Params()
    request = cxx.objects_pybind.Request.from_json_string(load('request.json'))
    response = predictor(request, params)
    assert len(response.predictions) == 3
