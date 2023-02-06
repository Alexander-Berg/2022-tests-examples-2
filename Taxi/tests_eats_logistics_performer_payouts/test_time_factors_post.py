import datetime as dt
import decimal

import dateutil as du
import pytest

SQL_TIME_FACTOR = f"""
    SELECT id, performer_id, factor_id, external_id,
    value, reason, time_point_at
    FROM eats_logistics_performer_payouts.time_factor_values
    ORDER BY id
    """

SQL_PERFORMERS = f"""
    SELECT id, external_id
    FROM eats_logistics_performer_payouts.performers
    ORDER BY id
    """


def get_sql_data(pgsql):
    res = {}
    cursor = pgsql['eats_logistics_performer_payouts'].cursor()

    cursor.execute(SQL_TIME_FACTOR)
    res['time_factors'] = list(cursor)

    cursor.execute(SQL_PERFORMERS)
    res['performers'] = list(cursor)

    return res


def sort_res(data):
    return {
        'time_factors': sorted(data['time_factors'], key=lambda x: x[1]),
        'performers': sorted(data['performers'], key=lambda x: x[0]),
    }


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_time_factors_post(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):

    request = load_json('time_factors_request.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/time-factors', json=request,
    )
    assert response.status_code == 200

    def get_valid(id1, id2, id3):
        return sort_res(
            {
                'time_factors': [
                    (
                        1,
                        id1,
                        1,
                        'secret1',
                        decimal.Decimal('100.1234'),
                        'usok13 32',
                        dt.datetime(
                            2020, 1, 8, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                    (
                        2,
                        id2,
                        1,
                        'secret2',
                        decimal.Decimal('1.2234'),
                        'hurma 2',
                        dt.datetime(
                            2020, 2, 8, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                    (
                        3,
                        id3,
                        2,
                        'secret3',
                        decimal.Decimal('100.0000'),
                        'hurma 3',
                        dt.datetime(
                            2020, 2, 8, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                ],
                'performers': [
                    (id1, 'Vasja Pupkin'),
                    (id2, 'Maria Ivanovna'),
                    (id3, 'Vasja Susel'),
                ],
            },
        )

    # we need performer_id invariancy (order of id depends
    # on collision resolution of C++ unordered_set)
    ans = sort_res(get_sql_data(pgsql))
    assert (
        ans == get_valid(1, 2, 3)
        or ans == get_valid(1, 3, 2)
        or ans == get_valid(2, 1, 3)
        or ans == get_valid(2, 3, 1)
        or ans == get_valid(3, 1, 2)
        or ans == get_valid(3, 2, 1)
    )

    request = load_json('time_factors_update.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/time-factors', json=request,
    )
    assert response.status_code == 200

    def get_valid2(id1, id2, id3):
        return sort_res(
            {
                'time_factors': [
                    (
                        1,
                        id1,
                        1,
                        'secret1',
                        decimal.Decimal('102.1234'),
                        'usok13 32 (extra)',
                        dt.datetime(
                            2020, 1, 18, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                    (
                        2,
                        id2,
                        1,
                        'secret2',
                        decimal.Decimal('1.2234'),
                        'hurma 2',
                        dt.datetime(
                            2020, 2, 8, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                    (
                        3,
                        id3,
                        2,
                        'secret3',
                        decimal.Decimal('100.0000'),
                        'hurma 3',
                        dt.datetime(
                            2020, 2, 8, 7, 5, 17, tzinfo=du.tz.tzlocal(),
                        ),
                    ),
                ],
                'performers': [
                    (id1, 'Vasja Pupkin'),
                    (id2, 'Maria Ivanovna'),
                    (id3, 'Vasja Susel'),
                ],
            },
        )

    # we need performer_id invariancy (order of id depends
    # on collision resolution of C++ unordered_set)
    ans = sort_res(get_sql_data(pgsql))
    assert (
        ans == get_valid2(1, 2, 3)
        or ans == get_valid2(1, 3, 2)
        or ans == get_valid2(2, 1, 3)
        or ans == get_valid2(2, 3, 1)
        or ans == get_valid2(3, 1, 2)
        or ans == get_valid2(3, 2, 1)
    )


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_time_factors_post_invalid(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):

    request = load_json('time_factors_invalid.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/time-factors', json=request,
    )
    assert response.status_code == 400
