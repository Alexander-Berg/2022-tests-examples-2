import json

import pytest

ACCEPT_LANGUAGE = 'Accept-Language'
USER_AGENT = 'User-Agent'

HEADERS = {ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 9.74 (1234)'}


@pytest.mark.parametrize(
    ('courier_app', 'do_restrict'),
    [(None, False), ('taximeter', False), ('eats', True)],
)
def test_wrong_courier_app(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        load_json,
        mock_qc_status,
        mock_driver_status,
        courier_app,
        do_restrict,
):
    driverid = 'courier_' + courier_app if courier_app else 'driver'

    driver_authorizer_service.set_session('1488', 'qwerty', driverid)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200

    content = response.json()
    courier_app_restrictions = [
        r
        for r in content.get('restrictions', [])
        if r['code'] == 'WrongCourierApp'
    ]
    if do_restrict:
        assert not content['can_take_orders']
    else:
        assert content['can_take_orders']
    assert bool(courier_app_restrictions) == do_restrict
    if do_restrict:
        assert courier_app_restrictions[0]['actions'] == {
            'primary': {
                'text': 'kWrongCourierAppButton',
                'url': 'eda.courier.yandex://orders',
            },
        }


@pytest.mark.parametrize(
    'do_block',
    [
        True,
        pytest.param(
            True, marks=(pytest.mark.config(EATS_COURIER_SERVICE_MAPPING={})),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={'selfemployed': '1488'},
                )
            ),
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={'selfemployed': '9999'},
                )
            ),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'courier_serivce_1': {'region_id_1': '1488'},
                    },
                )
            ),
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    EATS_COURIER_SERVICE_MAPPING={
                        'courier_serivce_1': {'region_id_1': '9999'},
                    },
                )
            ),
        ),
    ],
)
def test_skip_deactivated_check(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        load_json,
        mock_driver_status,
        do_block,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return {
            'classes': [
                {
                    'allowed': False,
                    'class': 'econom',
                    'forbidden_reasons': ['park_deactivated'],
                },
            ],
        }

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200

    content = response.json()
    deactivated_reasons = [
        r
        for r in content.get('reasons', [])
        if (r['code'] in ['DriverNoClasses', 'ParkDeactivated', 'class_exams'])
    ]
    assert bool(deactivated_reasons) == do_block
