async def test_orders_fullness_checker(
        db_select_orders,
        db_select_orders_notifications,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr_1 = 'order-nr-1'
    order_nr_2 = 'order-nr-2'
    order_nr_3 = 'order-nr-3'
    create_status = 'created'
    finish_status = 'complete'

    make_order(
        eats_id=order_nr_1,
        order_status=finish_status,
        claim_id='claim-id',
        corp_client_type='corp_client_type',
        clid='clid',
        park_id='park-id',
        unique_driver_id='unique-driver-id',
        driver_id='driver-id',
        city_id='city-id',
        geo_hierarchy='geo-hierarchy',
        payment_type='payment-type',
        time_zone='time-zone',
        zone_name='zone-name',
        billing_client_id='billing-client-id',
        claim_attempt='1',
        park_driver_profile_id='park-driver-profile-id',
        oebs_mvp_id='oebs-mvp-id',
        taxi_alias_id='taxi-alias-id',
    )

    make_order(
        eats_id=order_nr_2,
        order_status=finish_status,
        claim_id='claim-id',
        corp_client_type='corp_client_type',
        clid='clid',
        park_id='park-id',
        unique_driver_id='unique-driver-id',
        driver_id='driver-id',
        city_id='city-id',
        geo_hierarchy='geo-hierarchy',
        payment_type='payment-type',
        time_zone='time-zone',
        zone_name='zone-name',
        billing_client_id='billing-client-id',
        claim_attempt='1',
        park_driver_profile_id='park-driver-profile-id',
        oebs_mvp_id='oebs-mvp-id',
        update_finished=True,
        taxi_alias_id='taxi-alias-id',
    )

    make_order(
        eats_id=order_nr_3, order_status=create_status, claim_id='claim-id',
    )

    task_name = 'orders-fullness-checker-periodic'
    await taxi_eats_performer_subventions.run_periodic_task(task_name)

    orders = db_select_orders()
    assert len(orders) == 3

    order = orders[0]
    assert order['eats_id'] == order_nr_1
    assert order['update_finished'] == True

    orders = db_select_orders_notifications()
    assert len(orders) == 1

    order = orders[0]
    assert order['eats_id'] == order_nr_1
