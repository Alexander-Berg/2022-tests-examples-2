import datetime
import decimal


def datetime_to_string(timepoint):
    if isinstance(timepoint, datetime.datetime):
        if timepoint.tzinfo is None:
            timepoint = timepoint.replace(tzinfo=datetime.timezone.utc)
        return timepoint.isoformat()
    return timepoint


async def test_cashback_settings_success_create_cashback(
        taxi_eats_restapp_promo, pgsql,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    starts = now + datetime.timedelta(days=30)
    ends = starts + datetime.timedelta(days=365)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '131313',
                    'place_has_plus': True,
                    'yandex_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                    'place_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                },
            ],
        },
    )

    assert response.status_code == 204

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT place_id, cashback, starts, ends, type , discount_task_id
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '131313'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()

    assert len(cashbacks_from_db) == 2
    assert cashbacks_from_db[0] == (
        '131313',
        '15.15',
        starts,
        ends,
        'place',
        '12345678-1234-1234-1234-123412345678',
    )
    assert cashbacks_from_db[1] == (
        '131313',
        '15.15',
        starts,
        ends,
        'yandex',
        '12345678-1234-1234-1234-123412345678',
    )

    cursor.execute(
        """
    SELECT place_id, status, cashback, starts, ends
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '131313'
    ORDER BY id
    """,
    )

    plus_statuses_from_db = cursor.fetchall()

    assert len(plus_statuses_from_db) == 1
    assert plus_statuses_from_db[0] == (
        '131313',
        'active',
        decimal.Decimal('15.15'),
        starts,
        ends,
    )


async def test_cashback_settings_create_cashback_with_null_end_date(
        taxi_eats_restapp_promo, pgsql,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    starts = now + datetime.timedelta(days=27)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '111',
                    'place_has_plus': True,
                    'place_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                    },
                },
            ],
        },
    )

    assert response.status_code == 204

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT place_id, cashback, starts, ends, type , discount_task_id
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '111'
    ORDER BY id
    """,
    )

    cashbacks_from_db = cursor.fetchall()

    assert len(cashbacks_from_db) == 1
    assert cashbacks_from_db[0] == (
        '111',
        '15.15',
        starts,
        None,
        'place',
        '12345678-1234-1234-1234-123412345678',
    )

    cursor.execute(
        """
    SELECT place_id, status, cashback, starts, ends
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '111'
    ORDER BY id
    """,
    )

    plus_statuses_from_db = cursor.fetchall()

    assert len(plus_statuses_from_db) == 1
    assert plus_statuses_from_db[0] == (
        '111',
        'active',
        decimal.Decimal('15.15'),
        starts,
        None,
    )


async def test_cashback_settings_create_cashback_exist_cashback(
        taxi_eats_restapp_promo, pgsql,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    starts = now + datetime.timedelta(days=15)
    ends = starts + datetime.timedelta(days=123)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '1',
                    'place_has_plus': True,
                    'yandex_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                    'place_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                },
            ],
        },
    )

    assert response.status_code == 204

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT place_id, cashback, starts, ends, type , discount_task_id
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    cashbacks_from_db_before = cursor.fetchall()
    cursor.execute(
        """
    SELECT place_id, status, cashback, starts, ends
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '1'
    ORDER BY id
    """,
    )
    plus_statuses_from_db_before = cursor.fetchall()

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '1',
                    'place_has_plus': True,
                    'yandex_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                    'place_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                },
            ],
        },
    )

    assert response.status_code == 204

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT place_id, cashback, starts, ends, type , discount_task_id
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '1'
    ORDER BY id
    """,
    )

    cashbacks_from_db_after = cursor.fetchall()
    cursor.execute(
        """
    SELECT place_id, status, cashback, starts, ends
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '1'
    ORDER BY id
    """,
    )
    plus_statuses_from_db_after = cursor.fetchall()

    assert cashbacks_from_db_before == cashbacks_from_db_after
    assert plus_statuses_from_db_before == plus_statuses_from_db_after


async def test_cashback_settings_create_with_offset_old_cashback_ends_date(
        taxi_eats_restapp_promo, pgsql,
):
    """Тест проверяет задание даты окончания кешбека
    при создании нового кешбека в будущем
    Существующий кешбек уже в БД"""

    now = datetime.datetime.now(datetime.timezone.utc)
    starts = now + datetime.timedelta(days=22)
    ends = starts + datetime.timedelta(days=300)

    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/plus/cashback/settings',
        json={
            'places_settings': [
                {
                    'place_id': '123',
                    'place_has_plus': True,
                    'yandex_cashback': {
                        'cashback': '15.15',
                        'starts': datetime_to_string(starts),
                        'ends': datetime_to_string(ends),
                    },
                    'place_cashback': {
                        'cashback': '51.51',
                        'starts': datetime_to_string(starts),
                    },
                },
            ],
        },
    )

    assert response.status_code == 204

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        """
    SELECT ends
    FROM  eats_restapp_promo.active_cashback_settings
    WHERE place_id = '123'
    ORDER BY id, type
    """,
    )

    cashbacks_from_db = cursor.fetchall()
    cursor.execute(
        """
    SELECT ends
    FROM  eats_restapp_promo.place_plus_activation
    WHERE place_id = '123'
    ORDER BY id
    """,
    )
    plus_statuses_from_db = cursor.fetchall()

    assert len(cashbacks_from_db) == 4
    assert len(plus_statuses_from_db) == 2

    assert cashbacks_from_db[0][0] is not None
    assert cashbacks_from_db[1][0] is not None
    assert cashbacks_from_db[2][0] is None
    assert cashbacks_from_db[3][0] is not None

    assert plus_statuses_from_db[0][0] is not None
    assert plus_statuses_from_db[1][0] is None
