import pytest

PARK_ID = 'parkid'
DRIVER_ID = 'driverid'
CAR_ID = 'carid'
PARK_DRIVER_ID = f'{PARK_ID}_{DRIVER_ID}'
PARK_CAR_ID = f'{PARK_ID}_{CAR_ID}'

DRIVER = 'driver'
CAR = 'car'


@pytest.mark.parametrize(
    'params, expected_code, expected_response, qc_py_response',
    [
        (
            dict(park_driver_id=PARK_DRIVER_ID, type=DRIVER),
            200,
            dict(id=PARK_DRIVER_ID, type=DRIVER, exams=[]),
            None,
        ),
        (
            dict(park_driver_id=PARK_DRIVER_ID, type=DRIVER),
            200,
            dict(
                id=PARK_DRIVER_ID,
                type=DRIVER,
                exams=[
                    dict(
                        code='rqc',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                ],
            ),
            None,
        ),
        (
            dict(
                park_driver_id=PARK_DRIVER_ID,
                park_car_id=PARK_CAR_ID,
                type=CAR,
            ),
            200,
            dict(
                id=PARK_CAR_ID,
                type=CAR,
                exams=[
                    dict(
                        code='sts',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                ],
            ),
            None,
        ),
        (
            dict(park_driver_id=PARK_DRIVER_ID, type='ololo'),
            400,
            dict(
                code='INCORRECT_ENTITY_TYPE', message='Incorrect entity type',
            ),
            None,
        ),
        (
            dict(park_driver_id=PARK_DRIVER_ID, type=DRIVER),
            404,
            dict(code='ENTITY_NOT_FOUND', message='Entity not found in Qc'),
            None,
        ),
        (
            dict(park_driver_id=PARK_DRIVER_ID, type=CAR),
            400,
            dict(
                code='EMPTY_PARK_CAR_ID',
                message='Entity type is Car but park_car_id is not passed',
            ),
            None,
        ),
        pytest.param(
            dict(park_driver_id=PARK_DRIVER_ID, type=DRIVER),
            200,
            dict(
                id=PARK_DRIVER_ID,
                type=DRIVER,
                exams=[
                    dict(
                        code='no_config_for_exam',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='exam_visible',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='exam_block',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                ],
            ),
            dict(
                id=PARK_DRIVER_ID,
                type=DRIVER,
                exams=[
                    dict(
                        code='no_config_for_exam',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='exam_visible',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='exam_disable',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='exam_block',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                    dict(
                        code='disabled_by_config20',
                        enabled=False,
                        modified='2022-02-02T21:00:00+00:00',
                    ),
                ],
            ),
            marks=[pytest.mark.experiments3(filename='qc_exam_enable.json')],
        ),
    ],
)
async def test_state_simple(
        taxi_quality_control_cpp,
        mockserver,
        parks,
        params,
        expected_code,
        expected_response,
        qc_py_response,
):
    @mockserver.handler('/quality-control/api/v1/state')
    def _api_v1_state(request):
        if expected_code == 200:
            response = (
                expected_response if qc_py_response is None else qc_py_response
            )
            return mockserver.make_response(status=200, json=response)
        return mockserver.make_response('Some qc error', expected_code)

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_fetch_tags(request):
        return {'tags': ['tag1', 'tag2']}

    parks.set_driver_profiles_list(
        PARK_ID, DRIVER_ID, 'mock_responses/driver_profile_list_rus.json',
    )

    response = await taxi_quality_control_cpp.get(
        'api/v1/nocache-state', params=params,
    )
    assert response.status_code == expected_code
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )
    if expected_response:
        assert response.json() == expected_response
