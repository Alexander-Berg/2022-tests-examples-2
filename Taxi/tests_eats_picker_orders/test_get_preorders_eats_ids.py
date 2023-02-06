import datetime


async def test_get_preorders(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
):
    now_utc = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now()
    place_id = 12
    create_order(
        eats_id='eats_id1',
        place_id=place_id,
        estimated_delivery_time=now - datetime.timedelta(hours=4),
        is_asap=False,
    )

    create_order(
        eats_id='eats_id2',
        place_id=place_id,
        estimated_delivery_time=now - datetime.timedelta(hours=3, minutes=1),
        is_asap=True,
    )

    create_order(
        eats_id='eats_id3',
        estimated_delivery_time=now - datetime.timedelta(hours=2),
        is_asap=False,
    )
    create_order(
        eats_id='eats_id4',
        estimated_delivery_time=now - datetime.timedelta(hours=1),
        is_asap=True,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/orders/preorders',
        params={
            'from': (now_utc - datetime.timedelta(hours=4)).strftime(
                '%Y-%m-%dT%H:%M:%S+0000',
            ),
            'to': (now_utc - datetime.timedelta(hours=3)).strftime(
                '%Y-%m-%dT%H:%M:%S+0000',
            ),
        },
    )

    assert response.status_code == 200
    assert len(response.json()['preorders']) == 2
    preorders = sorted(
        response.json()['preorders'], key=lambda preorder: preorder['eats_id'],
    )
    assert preorders[0]['eats_id'] == 'eats_id1'
    assert not preorders[0]['is_asap']
    assert preorders[1]['eats_id'] == 'eats_id2'
    assert preorders[1]['is_asap']
