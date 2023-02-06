import datetime

import pytest


@pytest.fixture(name='mock_claims_points_eta')
def _mock_claims_points_eta(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler(request):
        mock_response = {
            'id': 'test_id',
            'route_points': [
                {
                    'id': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [35.8, 55.4],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                    },
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'id': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [37.8, 55.4],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                    },
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T18:28:00.00+00:00'},
                },
            ],
            'performer_position': [37.8, 55.4],
        }
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_cargo_claims')
def _mock_eats_cargo_claims(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        mock_response = {'phone': '12345', 'ext': '123', 'ttl_seconds': 600}
        return mockserver.make_response(json=mock_response, status=200)


async def test_sample_tasks(
        mock_eats_cargo_claims, mock_claims_points_eta, stq_runner,
):
    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'some_order_nr',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'claim_id': 'claim_id',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'courier_id': 'courier_id_2',
                'claim_alias': 'default',
                'personal_phone_id': 'phone_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )


@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_couriers(
        mock_eats_cargo_claims, mock_claims_points_eta, stq_runner, pgsql,
):

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'order_nr_1',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'courier_id': 'courier_id_1',
                'courier_is_hard_of_hearing': True,
            },
        },
    )
    data = sql_get_all_couriers(pgsql)
    expected_required = {
        'name': 'name',
        'raw_type': 'pedestrian',
        'type': 'pedestrian',
        'courier_id': 'courier_id_1',
        'is_hard_of_hearing': True,
    }
    assert data[0] == ('order_nr_1', expected_required)

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='all_fields',
        args=[],
        kwargs={
            'order_nr': 'order_nr_2',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'claim_id': 'claim_id',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'courier_id': 'courier_id_2',
                'claim_alias': 'default',
                'personal_phone_id': 'phone_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )
    data = sql_get_all_couriers(pgsql)
    expected_all = {
        'name': 'name',
        'raw_type': 'pedestrian',
        'type': 'pedestrian',
        'claim_id': 'claim_id',
        'car_model': 'car_model',
        'car_number': 'car_number',
        'courier_id': 'courier_id_2',
        'claim_alias': 'default',
        'personal_phone_id': 'phone_id_1',
        'is_hard_of_hearing': False,
    }

    assert data[1] == ('order_nr_2', expected_all)


@pytest.mark.now('2021-01-01T10:00:00+03:00')
@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_masked_phone_numbers(
        mock_eats_cargo_claims, mock_claims_points_eta, stq_runner, pgsql,
):

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'order_nr_1',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'courier_id': 'courier_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )

    data = sql_get_courier_phone_numbers(pgsql)
    assert data == []

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='all_fields',
        args=[],
        kwargs={
            'order_nr': 'order_nr_2',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'courier_id': 'courier_id_2',
                'claim_id': 'claim_id',
                'claim_alias': 'default',
                'courier_is_hard_of_hearing': False,
            },
        },
    )

    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [
        (
            'order_nr_2',
            '12345',
            '123',
            datetime.datetime(2021, 1, 1, 7, 10, 0),
            0,
        ),
    ]


@pytest.mark.config(
    EATS_ORDERS_TRACKING_COURIER_CARGO_CLAIMS_MASKING={
        'is_cargo_claims_voiceforwarding_enabled': False,
    },
)
@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_masked_phone_numbers_with_cargo_disabled(
        mock_eats_cargo_claims, stq_runner, pgsql,
):

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='all_fields',
        args=[],
        kwargs={
            'order_nr': 'order_nr_2',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'courier_id': 'courier_id_2',
                'claim_id': 'claim_id',
                'claim_alias': 'default',
                'courier_is_hard_of_hearing': False,
            },
        },
    )

    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [('order_nr_2', None, None, None, 0)]


@pytest.mark.now('2021-01-01T10:00:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_masked_phone_numbers_with_cargo_failure(
        mockserver, stq_runner, pgsql, mock_claims_points_eta,
):
    fail_cargo_claims = True

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        if fail_cargo_claims:
            mock_response = {'code': 'not_found', 'message': 'bad'}
            return mockserver.make_response(json=mock_response, status=404)
        mock_response = {'phone': '12345', 'ext': '123', 'ttl_seconds': 600}
        return mockserver.make_response(json=mock_response, status=200)

    task_kwargs = {
        'order_nr': 'order_nr_1',
        'courier': {
            'name': 'name',
            'type': 'pedestrian',
            'courier_id': 'courier_id_1',
            'claim_id': 'claim_id',
            'claim_alias': 'default',
            'courier_is_hard_of_hearing': False,
        },
    }

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='simple_task', kwargs=task_kwargs,
    )

    assert _handler_cargo_claims_driver_voiceforwarding.times_called == 1
    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [('order_nr_1', None, None, None, 1)]

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='simple_task', kwargs=task_kwargs,
    )

    assert _handler_cargo_claims_driver_voiceforwarding.times_called == 2
    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [('order_nr_1', None, None, None, 2)]

    fail_cargo_claims = False

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='simple_task', kwargs=task_kwargs,
    )

    assert _handler_cargo_claims_driver_voiceforwarding.times_called == 3
    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [
        (
            'order_nr_1',
            '12345',
            '123',
            datetime.datetime(2021, 1, 1, 10, 10, 0),
            0,
        ),
    ]


async def test_valid_claim_point_id(
        mockserver, mock_claims_points_eta, stq_runner,
):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        # 2 is id of destination point in mock_claims_points_eta
        assert request.json['point_id'] == 2
        mock_response = {'phone': '12345', 'ext': '123', 'ttl_seconds': 600}
        return mockserver.make_response(json=mock_response, status=200)

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'some_order_nr',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'claim_id': 'claim_id',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'courier_id': 'courier_id_2',
                'claim_alias': 'default',
                'personal_phone_id': 'phone_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )

    assert _handler_cargo_claims_driver_voiceforwarding.times_called == 1


async def test_points_eta_failed(mockserver, stq_runner):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_cargo_claims_points_eta(request):
        mock_response = {
            'code': 'point_not_found',
            'message': 'point not found',
        }
        return mockserver.make_response(json=mock_response, status=404)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        assert 'point_id' not in request.json
        mock_response = {'phone': '12345', 'ext': '123', 'ttl_seconds': 600}
        return mockserver.make_response(json=mock_response, status=200)

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'some_order_nr',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'claim_id': 'claim_id',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'courier_id': 'courier_id_2',
                'claim_alias': 'default',
                'personal_phone_id': 'phone_id_1',
                'courier_is_hard_of_hearing': False,
            },
        },
    )

    assert _handler_cargo_claims_points_eta.times_called == 1
    assert _handler_cargo_claims_driver_voiceforwarding.times_called == 1


@pytest.mark.now('2021-01-01T10:00:00+03:00')
@pytest.mark.pgsql('eats_orders_tracking')
async def test_check_stq_eta(mock_eats_cargo_claims, stq_runner, pgsql):

    await stq_runner.eats_orders_tracking_couriers.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'order_nr': 'order_nr_1',
            'courier': {
                'name': 'name',
                'type': 'pedestrian',
                'courier_id': 'courier_id_1',
                'courier_is_hard_of_hearing': False,
            },
            'eta': '2021-01-01T10:00:00+03:00',
        },
    )

    data = sql_get_all_orders_eta(pgsql)
    assert data == [('order_nr_1', datetime.datetime(2021, 1, 1, 7, 0, 0))]


def sql_get_all_couriers(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        select order_nr, payload
        from eats_orders_tracking.couriers
        """,
    )
    return list(cursor)


def sql_get_courier_phone_numbers(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        """
        select order_nr, phone_number, extension, ttl AT TIME ZONE 'UTC',
         error_count
        from eats_orders_tracking.masked_courier_phone_numbers
        """,
    )
    return list(cursor)


def sql_get_all_orders_eta(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        select order_nr, eta AT TIME ZONE 'UTC'
        from eats_orders_tracking.orders_eta
        """,
    )
    return list(cursor)
