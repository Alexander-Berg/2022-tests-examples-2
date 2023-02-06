import pytest


@pytest.mark.now('2021-12-03T15:15:00.00')
async def test_stq_plus_finish_success(stq_runner, pgsql):

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert len(cashbacks_from_db) == 2

    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    plus_statuses_from_db = cursor.fetchall()
    assert len(plus_statuses_from_db) == 2

    await stq_runner.eats_restapp_promo_plus_finish.call(
        task_id='abbbaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
        kwargs={'place_id': '1'},
        expect_fail=False,
    )

    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert cashbacks_from_db == []

    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    plus_statuses_from_db = cursor.fetchall()
    assert plus_statuses_from_db == []


@pytest.mark.now('2021-12-03T15:15:00.00')
async def test_stq_plus_finish_success_with_terminated_cashback(
        stq_runner, pgsql,
):
    """
    Тест покрывает случай, когда у какого то кешбека
    дата конца уже в прошлом и уже нет необходимости
    закрывать его в eats-discounts.
    """

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '2'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert len(cashbacks_from_db) == 1

    await stq_runner.eats_restapp_promo_plus_finish.call(
        task_id='abbbaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2',
        kwargs={'place_id': '2'},
        expect_fail=False,
    )

    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '2'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert cashbacks_from_db == []


@pytest.mark.now('2021-12-03T15:15:00.00')
async def test_stq_plus_finish_fail(stq_runner, pgsql):
    """
    Тест проверяет, что таска упадет, если хотя бы
    у однгого кешбека нет discount id.
    Тест покрывает случай, когда у какого то кешбека
    отсутствет discount_id, в этом случае stq должна падать,
    пока таска создания не завершится в eats-discounts и
    периодик periodic-promo-status-update не получит
    статусы этих тасок.
    """

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '3'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert len(cashbacks_from_db) == 1

    await stq_runner.eats_restapp_promo_plus_finish.call(
        task_id='abbbaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3',
        kwargs={'place_id': '3'},
        expect_fail=True,
    )

    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '3'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    assert len(cashbacks_from_db) == 1


@pytest.mark.now('2021-11-03T15:15:00.00')
async def test_cashback_settings_success_finish_cashbacks(
        taxi_eats_restapp_promo, pgsql, stq,
):
    """
    Здесь ожидается, что при получении 'place_has_plus': False
    Поставится stq таска, которая будет пытаться закрыть кешбеки
    """
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={'places_settings': [{'place_id': '1', 'place_has_plus': False}]},
    )

    assert response.status_code == 204
    assert stq.eats_restapp_promo_plus_finish.times_called == 1

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT *
    FROM  eats_restapp_promo.place_plus_finish_tasks
    WHERE place_id = '1'
    """,
    )

    stq_task_in_db = cursor.fetchall()
    assert len(stq_task_in_db) == 1


@pytest.mark.now('2021-11-03T15:15:00.00')
async def test_finish_cashback_settings_double_stq_call(
        taxi_eats_restapp_promo, pgsql, stq,
):
    """
    Здесь проверяется, что ручка отдаст ошибку
    при попытке поставить таску на отключение
    плейса от плюса во второй раз
    """
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={'places_settings': [{'place_id': '1', 'place_has_plus': False}]},
    )

    assert response.status_code == 204

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={'places_settings': [{'place_id': '1', 'place_has_plus': False}]},
    )

    assert response.status_code == 400
    assert stq.eats_restapp_promo_plus_finish.times_called == 1


@pytest.mark.now('2021-11-03T15:15:00.00')
async def test_cashback_settings_success_finish_with_cashbacks_parts(
        taxi_eats_restapp_promo, pgsql, stq,
):
    """
    Тест покрывает случай, когда вместе с флагом place_has_plus
    на отключение плюса (false) приходят кешбеки. Ручка должна при
    place_has_plus = false игнорировать yandex_cashback и
    place_cashback, и после ручка должна отключить все кешбеки у плейса.
    Отключение плейса состоит из постановки stq
    eats_restapp_promo_plus_finish
    """
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '1',
                    'place_has_plus': False,
                    'yandex_cashback': {
                        'cashback': '15.15',
                        'starts': '2021-12-01T00:00:00+0300',
                        'ends': '2022-12-01T00:00:00+0300',
                    },
                    'place_cashback': {
                        'cashback': '15.15',
                        'starts': '2021-12-01T00:00:00+0300',
                        'ends': '2022-12-01T00:00:00+0300',
                    },
                },
            ],
        },
    )

    assert stq.eats_restapp_promo_plus_finish.times_called == 1
    assert response.status_code == 204
