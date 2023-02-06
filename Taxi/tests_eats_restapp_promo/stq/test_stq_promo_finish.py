import pytest


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_stq_stop_promo_with_single_discount_id(
        stq_runner, mockserver, mock_partners_info, pgsql, testpoint,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        assert request.json['discounts_data'] == [
            {
                'hierarchy_name': 'restaurant_menu_discounts',
                'discount_id': '11',
            },
        ]
        return mockserver.make_response(status=200, json={})

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1', kwargs={'promo_id': 301, 'partner_id': 1},
    )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT status FROM eats_restapp_promo.promos'
        f' WHERE promo_id = 301',
    )
    status = cursor.fetchall()

    assert len(status) == 1
    assert status[0][0] == 'completed'

    assert _mock_finish_discounts.times_called == 1
    assert not _promo_finish_stq_restart.has_calls


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_stq_stop_promo_with_multiple_discount_ids(
        stq_runner, mockserver, mock_partners_info, pgsql, testpoint,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        assert request.json['discounts_data'] == [
            {'hierarchy_name': 'restaurant_discounts', 'discount_id': '12'},
            {'hierarchy_name': 'restaurant_discounts', 'discount_id': '13'},
        ]
        return mockserver.make_response(status=200, json={})

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1', kwargs={'promo_id': 302, 'partner_id': 1},
    )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT status FROM eats_restapp_promo.promos'
        f' WHERE promo_id = 302',
    )
    status = cursor.fetchall()

    assert len(status) == 1
    assert status[0][0] == 'completed'

    assert _mock_finish_discounts.times_called == 1
    assert not _promo_finish_stq_restart.has_calls


async def test_stq_not_stop_promo_with_not_completing_status(
        stq_runner, mockserver, mock_partners_info, pgsql, testpoint,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(status=200, json={})

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1', kwargs={'promo_id': 303, 'partner_id': 1},
    )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT status FROM eats_restapp_promo.promos'
        f' WHERE promo_id = 303',
    )
    status = cursor.fetchall()

    assert len(status) == 1
    assert status[0][0] == 'new'

    assert _mock_finish_discounts.times_called == 0
    assert not _promo_finish_stq_restart.has_calls


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    'reschedule_counter, has_stq_restarted',
    [(1, True), (2, True), (3, False)],
)
async def test_stq_stop_promo_with_bad_request_to_eats_discounts(
        stq_runner,
        mockserver,
        mock_partners_info,
        pgsql,
        testpoint,
        reschedule_counter,
        has_stq_restarted,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1',
        kwargs={'promo_id': 304, 'partner_id': 1},
        reschedule_counter=reschedule_counter,
    )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT status FROM eats_restapp_promo.promos'
        f' WHERE promo_id = 304',
    )
    status = cursor.fetchall()

    assert len(status) == 1
    assert status[0][0] == 'completing'

    assert _promo_finish_stq_restart.has_calls == has_stq_restarted


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_stq_stop_promo_not_found(
        stq_runner, mockserver, mock_partners_info, pgsql, testpoint,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(status=200, json={})

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1', kwargs={'promo_id': 306, 'partner_id': 1},
    )

    assert _mock_finish_discounts.times_called == 0
    assert not _promo_finish_stq_restart.has_calls


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_stq_stop_promo_with_empty_discount_ids(
        stq_runner, mockserver, mock_partners_info, pgsql, testpoint,
):
    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        assert request.json['discounts_data'] == []
        return mockserver.make_response(status=200, json={})

    @testpoint('promo_finish_stq_restart')
    def _promo_finish_stq_restart(data):
        return data

    await stq_runner.eats_restapp_promo_promo_finish.call(
        task_id='1', kwargs={'promo_id': 305, 'partner_id': 1},
    )

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT status FROM eats_restapp_promo.promos'
        f' WHERE promo_id = 305',
    )
    status = cursor.fetchall()

    assert len(status) == 1
    assert status[0][0] == 'completed'

    assert _mock_finish_discounts.times_called == 1
    assert not _promo_finish_stq_restart.has_calls
