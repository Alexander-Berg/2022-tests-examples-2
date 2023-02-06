from tests_cargo_pricing import utils


PAID_CANCEL_IN_DRIVING_PRICE = '888'
PAID_CANCEL_PRICE = '100'
FREE_CANCEL_PRICE = '0'

CLIENT = 'client'
PERFORMER = 'performer'


def make_cancel_request_body(price_for, cancelled_by):
    req = utils.get_default_calc_request()
    req['price_for'] = price_for
    req['resolution_info'] = {'resolved_at': utils.from_start(minutes=20)}
    if cancelled_by == CLIENT:
        req['resolution_info']['resolution'] = 'cancelled_by_client'
    else:
        req['resolution_info']['resolution'] = 'failed_by_performer'

    for waypoint in req['waypoints']:
        waypoint['first_time_arrived_at'] = None

    return req


def set_first_point(
        request,
        *,
        arrived_at=None,
        eta=None,
        due=None,
        resolved_at=None,
        was_ready_at=None,
):
    first_point = request['waypoints'][0]
    first_point['first_time_arrived_at'] = arrived_at
    first_point['eta'] = eta
    first_point['due'] = due
    first_point['was_ready_at'] = was_ready_at
    first_point['resolution_info'] = {
        'resolution': 'skipped',
        'resolved_at': resolved_at,
    }


async def test_client_free_cancel(v1_calc_creator):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE


async def test_client_paid_cancel(v1_calc_creator):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        resolved_at=utils.from_start(minutes=1),
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == PAID_CANCEL_PRICE


async def test_driver_paid_cancel(v1_calc_creator):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=PERFORMER, cancelled_by=PERFORMER,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        eta=utils.from_start(minutes=5),
        resolved_at=utils.from_start(minutes=20),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == PAID_CANCEL_PRICE

    recalc_req = v1_calc_creator.mock_recalc.request
    assert (
        recalc_req['driver']['trip_details']['waiting_time']
        == recalc_req['user']['trip_details']['waiting_time']
        == 300.0
    )


async def test_driver_free_cancel_with_ready_point(v1_calc_creator):

    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=PERFORMER,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        due=utils.from_start(minutes=5),
        was_ready_at=utils.from_start(minutes=18),
        resolved_at=utils.from_start(minutes=20),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE
    # (timedelta between `due` and `was_ready_at`) - `free_waiting_time`
    assert float(response.json()['details']['paid_waiting_time']) == 180


async def test_driver_free_cancel(v1_calc_creator):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=PERFORMER, cancelled_by=PERFORMER,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        resolved_at=utils.from_start(minutes=2),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE

    assert len(v1_calc_creator.mock_prepare.request['waypoints']) > 1


async def test_driver_cancel_always_free(
        v1_calc_creator, setup_cancel_control,
):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=PERFORMER,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        resolved_at=utils.from_start(minutes=12),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE


async def test_client_cancel_after_finish_client_price(
        v1_calc_creator, setup_cancel_control,
):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=5),
        due=utils.from_start(minutes=10),
        resolved_at=utils.from_start(minutes=32),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE


async def test_client_cancel_after_finish_performer_price(
        v1_calc_creator, setup_cancel_control,
):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=PERFORMER, cancelled_by=CLIENT,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=5),
        due=utils.from_start(minutes=10),
        resolved_at=utils.from_start(minutes=32),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == FREE_CANCEL_PRICE


async def test_client_cancel_paid_cancel_start_override(
        v1_calc_creator, setup_cancel_control,
):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        resolved_at=utils.from_start(minutes=6),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == PAID_CANCEL_PRICE
    assert response.json()['details']['boarding_price'] == '99'
    assert response.json()['details']['paid_waiting_total_price'] == '1'


async def test_paid_supply_cancel(v1_calc_creator, v2_add_paid_supply):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    first_calc_id = response.json()['calc_id']
    v2_add_paid_supply.add_calc(calc_id=first_calc_id)

    response = await v2_add_paid_supply.execute()
    assert response.status_code == 200
    calc = response.json()['calculations'][0]['result']
    assert calc['cancel_options'] == {
        'paid_cancel_in_driving': {
            'cancel_price': '888',
            'free_cancel_timeout': 300,
        },
    }

    assert calc['details']['tariff']['category_name'] == 'cargocorp'
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )
    v1_calc_creator.payload['performer'] = {
        'assigned_at': utils.from_start(minutes=10),
    }
    v1_calc_creator.payload['previous_calc_id'] = first_calc_id

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == PAID_CANCEL_IN_DRIVING_PRICE


async def test_paid_waiting_time_cancel(v1_calc_creator, setup_cancel_control):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )

    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=0),
        resolved_at=utils.from_start(minutes=6),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == PAID_CANCEL_PRICE


async def test_paid_waiting_time_and_boarding_price(v1_calc_creator):
    v1_calc_creator.payload = make_cancel_request_body(
        price_for=CLIENT, cancelled_by=CLIENT,
    )
    set_first_point(
        v1_calc_creator.payload,
        arrived_at=utils.from_start(minutes=3),
        resolved_at=utils.from_start(minutes=20),
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    resp = response.json()
    assert int(resp['details']['boarding_price']) + int(
        resp['details']['paid_waiting_total_price'],
    ) == int(resp['price'])
