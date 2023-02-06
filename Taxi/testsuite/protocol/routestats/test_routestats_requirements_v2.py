import pytest


@pytest.mark.parametrize('supported', [False, True])
def test_requirements_v2_supported(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        supported,
):
    request = load_json('request.json')
    if not supported:
        request['supported'] = []
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    json = response.json()
    assert len(json['service_levels']) > 1
    if supported:
        for sl in json['service_levels']:
            assert 'unsupported_requirements' not in sl
    else:
        for sl in json['service_levels']:
            if sl['class'] != 'econom':
                assert 'unsupported_requirements' in sl
