from ctaxi_pyml.geosuggest.clarify_points import shared as shared_cxx


def test_bindings(load):
    request_json = load('request.json')
    request_binding = shared_cxx.Request.from_json(request_json)
    assert request_binding['request_id'] == 'some_id'
    assert request_binding['state'].fields[0].position.lon == 37.642736
    assert request_binding['state'].fields[0].position.lat == 55.734385
    assert request_binding['summary_state']
    assert request_binding['orders']
