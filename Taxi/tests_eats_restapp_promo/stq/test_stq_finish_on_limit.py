async def test_stq_stop_promo_with_single_discount_id(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(status=200, json={})

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT promo_id FROM eats_restapp_promo.promos'
        f' WHERE status = \'completed\'',
    )
    status_before_data = cursor.fetchall()
    assert not status_before_data

    await stq_runner.eats_restapp_promo_finish_on_limit.call(
        task_id='1',
        kwargs={
            'id': '1',
            'discount_id': '11',
            'hierarchy': 'restaurant_discounts',
        },
    )

    cursor.execute(
        'SELECT promo_id FROM eats_restapp_promo.promos'
        f' WHERE status = \'completed\'',
    )
    status_after_data = cursor.fetchall()

    assert len(status_after_data) == 1
    assert status_after_data[0][0] == 301


async def test_stq_stop_promo_with_multiple_discount_ids(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(status=200, json={})

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT promo_id FROM eats_restapp_promo.promos'
        f' WHERE status = \'completed\'',
    )
    status_before_data = cursor.fetchall()
    assert not status_before_data

    await stq_runner.eats_restapp_promo_finish_on_limit.call(
        task_id='1',
        kwargs={
            'id': '1',
            'discount_id': '55',
            'hierarchy': 'restaurant_discounts',
        },
    )

    cursor.execute(
        'SELECT promo_id FROM eats_restapp_promo.promos'
        f' WHERE status = \'completed\'',
    )
    status_after_data = cursor.fetchall()

    assert len(status_after_data) == 1
    assert status_after_data[0][0] == 307


async def test_stq_stop_promo_with_bad_request_to_eats_discounts(
        stq_runner, mockserver, pgsql,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT promo_id FROM eats_restapp_promo.promos'
        f' WHERE status = \'completed\'',
    )
    status_before_data = cursor.fetchall()
    assert not status_before_data

    await stq_runner.eats_restapp_promo_finish_on_limit.call(
        task_id='1',
        kwargs={
            'id': '1',
            'discount_id': '13',
            'hierarchy': 'restaurant_discounts',
        },
        expect_fail=True,
    )
