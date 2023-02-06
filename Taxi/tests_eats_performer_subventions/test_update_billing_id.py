async def test_update_billing_id(
        db_select_orders_billing_id,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr = 'order-nr'
    order_status = 'complete'
    profile_id = 'profile-id'

    make_order(
        eats_id=order_nr,
        order_status=order_status,
        eats_profile_id=profile_id,
    )

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services',
    )
    def _mock_eats_order_revision(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={
                'origin_revision_id': '260979192',
                'created_at': '2022-05-06T17:10:47.695188+00:00',
                'customer_services': [
                    {
                        'discounts': [],
                        'id': 'delivery-1',
                        'name': 'Доставка',
                        'cost_for_customer': '399',
                        'currency': 'RUB',
                        'type': 'delivery',
                        'vat': 'nds_none',
                        'trust_product_id': 'eda_107819207_ride',
                        'place_id': '1873',
                        'personal_tin_id': '374e953e3b484fdfa6fa1c205da71c75',
                        'balance_client_id': '1354462619',
                    },
                ],
            },
            status=200,
        )

    await taxi_eats_performer_subventions.run_task('update-billing-id-task')

    assert _mock_eats_order_revision.times_called == 1

    assert db_select_orders_billing_id() == [
        {'eats_id': 'order-nr', 'billing_client_id': '1354462619'},
    ]

    await taxi_eats_performer_subventions.run_task('update-billing-id-task')

    assert _mock_eats_order_revision.times_called == 1


async def test_update_billing_id_no_delivery(
        db_select_orders_billing_id,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr = 'order-nr'
    order_status = 'complete'
    profile_id = 'profile-id'

    make_order(
        eats_id=order_nr,
        order_status=order_status,
        eats_profile_id=profile_id,
    )

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services',
    )
    def _mock_eats_order_revision(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={
                'origin_revision_id': '260979192',
                'created_at': '2022-05-06T17:10:47.695188+00:00',
                'customer_services': [],
            },
            status=200,
        )

    await taxi_eats_performer_subventions.run_task('update-billing-id-task')

    assert _mock_eats_order_revision.times_called == 1

    assert db_select_orders_billing_id() == [
        {'eats_id': 'order-nr', 'billing_client_id': None},
    ]


async def test_update_billing_id_500(
        db_select_orders_billing_id,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr = 'order-nr'
    order_status = 'complete'
    profile_id = 'profile-id'

    make_order(
        eats_id=order_nr,
        order_status=order_status,
        eats_profile_id=profile_id,
    )

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services',
    )
    def _mock_eats_order_revision(request):
        assert request.method == 'POST'
        return mockserver.make_response(status=500)

    await taxi_eats_performer_subventions.run_task('update-billing-id-task')

    assert _mock_eats_order_revision.times_called == 1

    assert db_select_orders_billing_id() == [
        {'eats_id': 'order-nr', 'billing_client_id': None},
    ]
