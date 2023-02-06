from ctaxi_pyml.airport_queue import v1 as cxx


def test_serializations(load):
    request = cxx.Request.from_json(load('request.json'))
    response = cxx.Response.from_json(load('response.json'))
    config = cxx.PredictorConfig.from_json(load('config.json'))
    inner_request = cxx.InnerRequest.from_json(load('inner_request.json'))

    request.to_json()
    response.to_json()
    config.to_json()
    inner_request.to_json()

    assert config.features_config.add_atlas_features is False
