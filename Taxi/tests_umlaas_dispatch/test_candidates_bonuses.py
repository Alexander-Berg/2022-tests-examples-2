# pylint: disable=import-error

import pytest
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
from yamaps_tools import (
    driving_matrix as yamaps_driving_matrix,
)  # noqa: F401 C5521


def compare_responses(lhs, rhs):
    assert len(lhs['responses']) == len(rhs['responses'])
    for resp_l, resp_r in zip(lhs['responses'], rhs['responses']):
        assert len(resp_l['candidates']) == len(resp_r['candidates'])
        for cand_l, cand_r in zip(resp_l['candidates'], resp_r['candidates']):
            assert len(cand_l['bonuses']) == len(cand_r['bonuses'])
            assert cand_l['id'] == cand_r['id']
            bonuses_l = {b['name']: b['value'] for b in cand_l['bonuses']}
            bonuses_r = {b['name']: b['value'] for b in cand_r['bonuses']}
            assert bonuses_l == bonuses_r, (cand_l['id'], cand_l['id'])


async def test_ml_dispatch_bonuses_ok_driver_trackstory(
        taxi_umlaas_dispatch, load_json, load_binary, mockserver,
):
    @mockserver.handler('driver-trackstory/v2/shorttracks')
    def mock_driver_trackstory(request):
        # use flatc if need
        # flatc --force-defaults -b schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs services/umlaas-dispatch/testsuite/tests_umlaas_dispatch/static/test_umlaas_dispatch_bonuses/v2_shorttracks_response_1.json # noqa: E501

        return mockserver.make_response(
            response=load_binary('v2_shorttracks_response_1.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler('driver-trackstory/shorttracks_extended')
    def _mock_shorttracks_extended(request):
        return {}

    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        '/umlaas-dispatch/v1/candidates-bonuses', json=request,
    )
    assert response.status_code == 200
    assert len(response.json()['responses']) == len(request['requests'])

    driver_trackstory_request = await mock_driver_trackstory.wait_call()
    driver_trackstory_data = driver_trackstory_request['request'].json
    assert {*driver_trackstory_data['driver_ids']} == {
        'candidate_id_3',
        'candidate_id_2',
        'candidate_id_1',
    }
    assert driver_trackstory_data['type'] == 'both'
    assert driver_trackstory_data['num_positions'] == 10


@pytest.mark.experiments3(filename='exp_predictor_params.json')
async def test_ml_dispatch_bonuses_ml_predictor(
        taxi_umlaas_dispatch, load_json, load_binary, mockserver,
):
    @mockserver.handler('driver-trackstory/v2/shorttracks')
    def _mock_shorttracks(request):
        # use flatc if need
        # flatc --force-defaults -b schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs services/umlaas-dispatch/testsuite/tests_umlaas_dispatch/static/test_umlaas_dispatch_bonuses/v2_shorttracks_response_2.json # noqa: E501
        return mockserver.make_response(
            response=load_binary('v2_shorttracks_response_2.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler('driver-trackstory/shorttracks_extended')
    def _mock_shorttracks_extended(request):
        return load_json('shorttracks_extended_response.json')

    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        '/umlaas-dispatch/v1/candidates-bonuses', json=request,
    )
    assert _mock_shorttracks.has_calls
    assert _mock_shorttracks_extended.has_calls
    assert response.status_code == 200
    compare_responses(response.json(), load_json('response.json'))


@pytest.mark.experiments3(filename='exp_predictor_params_prolongation.json')
async def test_ml_dispatch_bonuses_prolongation(
        taxi_umlaas_dispatch, load_json, load_binary, mockserver,
):
    @mockserver.handler('driver-trackstory/v2/shorttracks')
    def _mock_shorttracks(request):
        # use flatc if need
        # flatc --force-defaults -b schemas/fbs/driver-trackstory/handlers/shorttracks_extended_response.fbs services/umlaas-dispatch/testsuite/tests_umlaas_dispatch/static/test_umlaas_dispatch_bonuses/v2_shorttracks_response_2.json # noqa: E501
        return mockserver.make_response(
            response=load_binary('v2_shorttracks_response_2.bin'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler('driver-trackstory/shorttracks_extended')
    def _mock_shorttracks_extended(request):
        return load_json('shorttracks_extended_response.json')

    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_route_matrix(request):
        assert request.method == 'GET'

        cnt_src = len(request.query.get('srcll').split('~'))
        cnt_dst = len(request.query.get('dstll').split('~'))
        assert cnt_dst == 1
        data = []
        for _ in range(0, cnt_src):
            data.append({'time': 300, 'distance': 1000})

        return mockserver.make_response(
            response=yamaps_driving_matrix.proto_matrix(data),
            status=200,
            content_type='application/x-protobuf',
        )

    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        '/umlaas-dispatch/v1/candidates-bonuses', json=request,
    )
    assert _mock_shorttracks.has_calls
    assert _mock_shorttracks_extended.has_calls
    assert response.status_code == 200
    compare_responses(response.json(), load_json('response.json'))


@pytest.mark.config(DISPATCH_BONUSES_SHORTTRACKS_ENABLED=False)
@pytest.mark.config(DISPATCH_BONUSES_SHORTTRACKS_EXTENDED_ENABLED=False)
@pytest.mark.config(
    DISPATCH_BONUSES_ML_PREDICTOR_RESOURCES=['dispatch_bonuses_v2_lib'],
)
@pytest.mark.experiments3(filename='exp_config.json')
async def test_ml_dispatch_bonuses_v2_lib(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        '/umlaas-dispatch/v1/candidates-bonuses', json=request,
    )
    assert response.status_code == 200
    compare_responses(response.json(), load_json('expected_response_v2.json'))
