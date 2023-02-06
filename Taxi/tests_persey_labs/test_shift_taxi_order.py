import pytest

from tests_persey_labs import utils


SHIFT_NOT_FOUND = {
    'code': 'lab_employee_shift_not_found',
    'message': 'Shift not found in db',
}


@pytest.mark.now('2020-11-10T08:35:00+0300')
@pytest.mark.parametrize(
    ['shift_id', 'has_shift'], [['2', True], ['7', False]],
)
async def test_get_taxi_order_missing(
        taxi_persey_labs, fill_labs, load_json, pgsql, shift_id, has_shift,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    response = await taxi_persey_labs.get(
        f'/disp/v1/lab/employee/shift/taxi-order?shift_id={shift_id}',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_2'},
    )
    if has_shift:
        assert response.status_code == 200
        assert response.json() == {'status': 'missing'}
    else:
        assert response.status_code == 404
        assert response.json() == SHIFT_NOT_FOUND


@pytest.mark.now('2020-11-10T08:35:00+0300')
async def test_get_taxi_order(
        taxi_persey_labs, fill_labs, load_json, mockserver, pgsql,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def mock_orders_search(request):
        assert request.json == {'orderid': '123123123', 'sourceid': 'persey'}
        return load_json('orders_search_response.json')

    response = await taxi_persey_labs.get(
        '/disp/v1/lab/employee/shift/taxi-order?shift_id=3',
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_2'},
    )

    assert response.status_code == 200
    assert mock_orders_search.times_called == 1
    assert response.json() == load_json('shift_taxi_order_get_response.json')


@pytest.mark.now('2020-11-10T08:35:00+0300')
@utils.permission_variants('my_entity_2', 'my_lab_id_1')
async def test_get_taxi_order_forbidden(
        taxi_persey_labs,
        fill_labs,
        load_json,
        mockserver,
        headers,
        exp_resp_code,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_orders_search(request):
        assert request.json == {'orderid': '123123123', 'sourceid': 'persey'}
        return load_json('orders_search_response.json')

    response = await taxi_persey_labs.get(
        '/disp/v1/lab/employee/shift/taxi-order?shift_id=3', headers=headers,
    )

    assert response.status_code == exp_resp_code


MANUAL_TAXI_WRONG_STATUS = {
    'code': 'invalid_taxi_order_status',
    'message': 'Not allowed to order taxi manually in this status',
}
MANUAL_TAXI_TOO_EARLY = {
    'code': 'taxi_order_too_early',
    'message': 'Not allowed to order taxi manually this early',
}
MANUAL_TAXI_TOO_LATE = {
    'code': 'taxi_order_too_late',
    'message': 'Not allowed to order taxi manually this late',
}


@pytest.mark.now('2020-11-10T08:35:00+0300')
@pytest.mark.config(
    PERSEY_TAXI_MAESTRO={
        'check_period': 60,
        'enabled': True,
        'search_period': 9 * 60 * 60,
        'available_manual_search_states': ['incomplete'],
        'available_manual_search_taxi_order_statuses': ['cancelled'],
    },
)
@pytest.mark.parametrize(
    ['shift_id', 'taxi_order_status', 'expected_error'],
    [
        (1, None, MANUAL_TAXI_WRONG_STATUS),
        (2, None, MANUAL_TAXI_WRONG_STATUS),
        (3, 'cancelled', None),
        (3, 'riding', MANUAL_TAXI_WRONG_STATUS),
        (4, None, MANUAL_TAXI_WRONG_STATUS),
        (5, None, MANUAL_TAXI_TOO_LATE),
        (6, None, MANUAL_TAXI_TOO_EARLY),
    ],
)
async def test_post_taxi_order(
        taxi_persey_labs,
        fill_labs,
        load_json,
        mockserver,
        pgsql,
        stq,
        shift_id,
        taxi_order_status,
        expected_error,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def mock_orders_search(request):
        if taxi_order_status is None:
            return mockserver.make_response(code=500)
        return {
            'orders': [{'orderid': '123123123', 'status': taxi_order_status}],
        }

    response = await taxi_persey_labs.post(
        '/disp/v1/lab/employee/shift/taxi-order',
        {'shift_id': shift_id},
        headers={'X-YaTaxi-Lab-Entity-Id': 'my_entity_2'},
    )
    if expected_error is None:
        assert response.status_code == 200
        assert response.json() == {}
        assert stq.persey_taxi_order_create.times_called == 1
        stq_call = stq.persey_taxi_order_create.next_call()
        assert stq_call['id'] == str(shift_id)
    else:
        assert response.status_code == 409
        assert response.json() == expected_error
        assert stq.persey_taxi_order_create.times_called == 0

    if taxi_order_status is None:
        assert mock_orders_search.times_called == 0
    else:
        assert mock_orders_search.times_called == 1


@pytest.mark.now('2020-11-10T08:35:00+0300')
@pytest.mark.config(
    PERSEY_TAXI_MAESTRO={
        'check_period': 60,
        'enabled': True,
        'search_period': 9 * 60 * 60,
        'available_manual_search_states': ['incomplete'],
        'available_manual_search_taxi_order_statuses': ['cancelled'],
    },
)
@utils.permission_variants('my_entity_2', 'my_lab_id_1')
async def test_post_taxi_order_forbidden(
        taxi_persey_labs,
        fill_labs,
        load_json,
        mockserver,
        headers,
        exp_resp_code,
):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_orders_search(request):
        return {'orders': [{'orderid': '123123123', 'status': 'cancelled'}]}

    response = await taxi_persey_labs.post(
        '/disp/v1/lab/employee/shift/taxi-order',
        {'shift_id': 3},
        headers=headers,
    )

    assert response.status_code == exp_resp_code
