import pytest

from tests_tristero_parcels import headers


def param_available_timeslots_exp(
        depot_id=None, uid=None, vendor=None, personal_phone_id=None,
):
    predicate = {'type': 'true'}
    if depot_id is not None:
        predicate['depot_id'] = depot_id
    if uid is not None:
        predicate['yandex_uid'] = uid
    if vendor is not None:
        predicate['vendor'] = vendor
    if personal_phone_id is not None:
        predicate['personal_phone_id'] = personal_phone_id

    return pytest.mark.experiments3(
        name='tristero_enable_available_timeslots',
        consumers=['tristero-parcels/available-timeslots'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': predicate,
                'value': {'enabled': True},
            },
        ],
        is_config=True,
    )


@param_available_timeslots_exp()
async def test_order_info_timeslot(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    depot_id = tristero_parcels_db.make_depot_id(1)

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            timeslot_start='2021-12-15T17:09:00+03:00',
            timeslot_end='2021-12-15T18:09:00+03:00',
        )

        # lets add some parcels
        order.add_parcel(1, status='in_depot', partner_id='some_partner_id')

    @mockserver.json_handler(
        '/logistic-platform-market/api/platform/request/delivery_hour_slots',
    )
    def delivery_hours_handler(request):
        assert 'request_id' in request.query
        return {}

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={'ref_order': order.ref_order, 'vendor': order.vendor},
    )

    assert response.status_code == 200
    assert response.json()['timeslot'] == {
        'start': '2021-12-15T14:09:00+00:00',
        'end': '2021-12-15T15:09:00+00:00',
    }
    assert delivery_hours_handler.times_called == 1


async def test_retrieve_orders_timeslot(
        taxi_tristero_parcels, tristero_parcels_db,
):
    depot_id_parcels = tristero_parcels_db.make_depot_id(1)

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id_parcels,
            timeslot_start='2021-12-15T17:09:00+03:00',
            timeslot_end='2021-12-15T18:09:00+03:00',
        )
        order.add_parcel(1, status='in_depot')

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/retrieve-orders',
        headers=headers.DEFAULT_HEADERS,
        json={'depot_id': depot_id_parcels},
    )

    assert response.status_code == 200
    assert response.json()['orders'][0]['timeslot'] == {
        'start': '2021-12-15T14:09:00+00:00',
        'end': '2021-12-15T15:09:00+00:00',
    }


@param_available_timeslots_exp()
async def test_order_info_alternative_timeslots(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    depot_id = tristero_parcels_db.make_depot_id(1)
    token = 'some-token'
    alternative_timeslots = {
        'available_timeslots': [
            {
                'from': '2021-12-15T17:00:0.000000Z',
                'to': '2021-12-15T18:00:0.000000Z',
            },
            {
                'from': '2021-12-15T18:00:0.000000Z',
                'to': '2021-12-15T19:00:0.000000Z',
            },
            {
                'from': '2021-12-16T12:00:0.000000Z',
                'to': '2021-12-16T13:00:0.000000Z',
            },
        ],
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            timeslot_start='2021-12-15T17:09:00+03:00',
            timeslot_end='2021-12-15T18:09:00+03:00',
            token=token,
        )

        order.add_parcel(1, status='in_depot', partner_id='some_partner_id')

    @mockserver.json_handler(
        '/logistic-platform-market/api/platform/request/delivery_hour_slots',
    )
    def delivery_hours_handler(request):
        assert request.query['request_id'] == token
        return alternative_timeslots

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={'ref_order': order.ref_order, 'vendor': order.vendor},
    )

    assert response.json()['alternative_timeslots'] == [
        {
            'start': '2021-12-15T17:00:00+00:00',
            'end': '2021-12-15T18:00:00+00:00',
        },
        {
            'start': '2021-12-15T18:00:00+00:00',
            'end': '2021-12-15T19:00:00+00:00',
        },
        {
            'start': '2021-12-16T12:00:00+00:00',
            'end': '2021-12-16T13:00:00+00:00',
        },
    ]
    assert response.status_code == 200
    assert delivery_hours_handler.times_called == 1


@param_available_timeslots_exp()
async def test_order_info_platform_error(
        taxi_tristero_parcels, tristero_parcels_db, mockserver,
):
    depot_id = tristero_parcels_db.make_depot_id(1)

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            timeslot_start='2021-12-15T17:09:00+03:00',
            timeslot_end='2021-12-15T18:09:00+03:00',
        )

        # lets add some parcels
        order.add_parcel(1, status='in_depot', partner_id='some_partner_id')

    @mockserver.json_handler(
        '/logistic-platform-market/api/platform/request/delivery_hour_slots',
    )
    def delivery_hours_handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_tristero_parcels.get(
        '/internal/v1/parcels/v1/order-info',
        headers=headers.DEFAULT_HEADERS,
        params={'ref_order': order.ref_order, 'vendor': order.vendor},
    )

    assert response.status_code == 200
    assert response.json()['timeslot'] == {
        'start': '2021-12-15T14:09:00+00:00',
        'end': '2021-12-15T15:09:00+00:00',
    }
    assert 'alternative_timeslots' not in response.json()
    assert delivery_hours_handler.times_called == 2  # 500 retry
