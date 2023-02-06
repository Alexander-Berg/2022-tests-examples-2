import datetime as dt

import dateutil as du
import pytest

SQL_FACTOR_STRINGS = f"""
    SELECT subject_id, factor_id, value
    FROM eats_logistics_performer_payouts.factor_string_values
    ORDER BY subject_id, factor_id
    """
SQL_FACTOR_INTEGERS = f"""
    SELECT subject_id, factor_id, value
    FROM eats_logistics_performer_payouts.factor_integer_values
    ORDER BY subject_id, factor_id
    """
SQL_FACTOR_DATETIMES = f"""
    SELECT subject_id, factor_id, value
    FROM eats_logistics_performer_payouts.factor_datetime_values
    ORDER BY subject_id, factor_id
    """
SQL_FACTOR_DECIMALS = f"""
    SELECT subject_id, factor_id, value
    FROM eats_logistics_performer_payouts.factor_decimal_values
    ORDER BY subject_id, factor_id
    """

SQL_SUBJECTS = f"""
    SELECT id, external_id, subject_type_id, performer_id,
    active_from, active_to, time_point_at
    FROM eats_logistics_performer_payouts.subjects
    ORDER BY id
    """

SQL_SUBJECT_SUBJECTS = f"""
    SELECT subject_id, related_subject_id
    FROM eats_logistics_performer_payouts.subjects_subjects
    ORDER BY subject_id, related_subject_id
    """

SQL_PERFORMERS = f"""
    SELECT id, external_id
    FROM eats_logistics_performer_payouts.performers
    ORDER BY id
    """


def get_sql_data(pgsql):
    res = {}
    cursor = pgsql['eats_logistics_performer_payouts'].cursor()

    cursor.execute(SQL_FACTOR_STRINGS)
    res['strings'] = list(cursor)

    cursor.execute(SQL_FACTOR_INTEGERS)
    res['integers'] = list(cursor)

    cursor.execute(SQL_FACTOR_DATETIMES)
    res['datetimes'] = list(cursor)

    cursor.execute(SQL_FACTOR_DECIMALS)
    res['decimals'] = list(cursor)

    cursor.execute(SQL_SUBJECTS)
    res['subjects'] = list(cursor)

    cursor.execute(SQL_SUBJECT_SUBJECTS)
    res['s2s'] = list(cursor)

    cursor.execute(SQL_PERFORMERS)
    res['performers'] = list(cursor)

    return res


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    request = load_json('subjects_request.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [(1, 1, 'by foot')],
        'integers': [(1, 2, 1)],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (
                1,
                'test_subject1',
                1,
                1,
                None,
                None,
                dt.datetime(2020, 1, 8, 7, 5, 6, tzinfo=du.tz.tzlocal()),
            ),
            (2, 'myshift', 2, 1, None, None, None),
            (3, 'test_delivery1', 3, 1, None, None, None),
            (4, 'test_delivery2', 3, 1, None, None, None),
        ],
        's2s': [(1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 1)],
        'performers': [(1, 'test_subject1')],
    }

    request = load_json('subjects_update.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [(1, 1, 'by foot')],
        'integers': [(1, 2, 1)],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (
                1,
                'test_subject1',
                1,
                1,
                None,
                None,
                dt.datetime(2020, 1, 17, 7, 5, 6, tzinfo=du.tz.tzlocal()),
            ),
            (2, 'myshift', 2, 1, None, None, None),
            (3, 'test_delivery1', 3, 1, None, None, None),
            (4, 'test_delivery2', 3, 1, None, None, None),
        ],
        's2s': [(1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 1)],
        'performers': [(1, 'test_subject1')],
    }


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post_no_performer(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    request = load_json('subjects_request_not_performer.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [(1, 12, 'unknown')],
        'integers': [(1, 9, 123)],
        'datetimes': [
            (1, 10, dt.datetime(2020, 1, 8, 7, 5, 17, tzinfo=du.tz.tzlocal())),
        ],
        'decimals': [],
        'subjects': [
            (
                1,
                'Vasuki club',
                4,
                1,
                None,
                None,
                dt.datetime(2020, 1, 8, 7, 5, 17, tzinfo=du.tz.tzlocal()),
            ),
            (2, 'myshift', 2, None, None, None, None),
            (3, 'test_delivery1', 3, None, None, None, None),
            (4, 'Vasja Pupkin', 1, 1, None, None, None),
        ],
        's2s': [(1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 1)],
        'performers': [(1, 'Vasja Pupkin')],
    }


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post_invalid_type(
        taxi_eats_logistics_performer_payouts, load_json,
):
    request = load_json('subjects_invalid_type.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 400


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post_simple(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    request = load_json('subjects_simple.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [(1, 'd1', 3, None, None, None, None)],
        's2s': [],
        'performers': [],
    }


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post_complex(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    request = load_json('subjects_complex_1.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (1, 'd1', 3, 1, None, None, None),
            (2, 'p1', 1, 1, None, None, None),
            (3, 'po1', 4, None, None, None, None),
        ],
        's2s': [(1, 2), (1, 3), (2, 1), (3, 1)],
        'performers': [(1, 'p1')],
    }

    cursor = pgsql['eats_logistics_performer_payouts'].cursor()
    cursor.execute(
        'UPDATE eats_logistics_performer_payouts.subjects'
        ' SET performer_id=NULL',
    )
    cursor.execute('DELETE FROM eats_logistics_performer_payouts.performers')
    cursor.execute(
        'DELETE FROM eats_logistics_performer_payouts.subjects_subjects'
        ' WHERE subject_id=1 AND related_subject_id=2',
    )
    cursor.execute(
        'DELETE FROM eats_logistics_performer_payouts.subjects_subjects'
        ' WHERE subject_id=2 AND related_subject_id=1',
    )

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (1, 'd1', 3, None, None, None, None),
            (2, 'p1', 1, None, None, None, None),
            (3, 'po1', 4, None, None, None, None),
        ],
        's2s': [(1, 3), (3, 1)],
        'performers': [],
    }

    request = load_json('subjects_complex_2.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (1, 'd1', 3, 2, None, None, None),
            (2, 'p1', 1, 2, None, None, None),
            (3, 'po1', 4, None, None, None, None),
        ],
        's2s': [(1, 2), (1, 3), (2, 1), (3, 1)],
        'performers': [(2, 'p1')],
    }

    cursor = pgsql['eats_logistics_performer_payouts'].cursor()
    cursor.execute(
        'UPDATE eats_logistics_performer_payouts.subjects'
        ' SET performer_id=NULL',
    )
    cursor.execute(
        'DELETE FROM eats_logistics_performer_payouts.subjects WHERE id = 2',
    )
    cursor.execute('DELETE FROM eats_logistics_performer_payouts.performers')
    cursor.execute(
        'DELETE FROM eats_logistics_performer_payouts.subjects_subjects',
    )

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (1, 'd1', 3, None, None, None, None),
            (3, 'po1', 4, None, None, None, None),
        ],
        's2s': [],
        'performers': [],
    }

    request = load_json('subjects_complex_3.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    assert get_sql_data(pgsql) == {
        'strings': [],
        'integers': [],
        'datetimes': [],
        'decimals': [],
        'subjects': [
            (
                1,
                'd1',
                3,
                None,
                None,
                None,
                dt.datetime(2021, 11, 11, 16, 57, 00, tzinfo=du.tz.tzlocal()),
            ),
            (3, 'po1', 4, None, None, None, None),
        ],
        's2s': [(1, 3), (3, 1)],
        'performers': [],
    }


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
async def test_subjects_post_json_upsert_relation(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    def get_expected_s2s(delivery_id, performer_id, point_id):
        return sorted(
            [
                (delivery_id, performer_id),
                (delivery_id, point_id),
                (performer_id, delivery_id),
                (point_id, delivery_id),
            ],
        )

    request = load_json('subjects_request_delivery_performer.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200
    assert sorted(get_sql_data(pgsql)['s2s']) == sorted(
        get_expected_s2s(1, 2, 3),
    )

    request['relations'][0]['id'] = 'driver_profile2'

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200
    assert sorted(get_sql_data(pgsql)['s2s']) == sorted(
        get_expected_s2s(1, 5, 3),
    )


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_factors.sql'],
)
@pytest.mark.parametrize(
    (
        'remove_relations_on_value',
        'expected_status_code',
        'expected_s2s_in_db',
    ),
    [
        (['driver_profile'], 200, [(1, 3), (3, 1)]),
        (['invalid_type'], 400, None),
    ],
)
async def test_subjects_post_json_remove_relations_on(
        taxi_eats_logistics_performer_payouts,
        pgsql,
        load_json,
        remove_relations_on_value,
        expected_status_code,
        expected_s2s_in_db,
):
    request = load_json('subjects_request_delivery_performer.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 200

    request['relations'] = []
    request['remove_relations_on'] = remove_relations_on_value

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        data = get_sql_data(pgsql)
        assert data['s2s'] == expected_s2s_in_db


@pytest.mark.xfail(
    reason='should be deleted after refactor in subjects and factors',
)
async def test_subjects_relations_validation_fail(
        taxi_eats_logistics_performer_payouts, pgsql, load_json,
):
    request = load_json('subjects_request_incorrect_relations.json')

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/subjects', json=request,
    )
    assert response.status_code == 400
    assert (
        response.json()['errors'][0]['message']
        == 'More than 1 relation from subject_type_id:1 to subject_type_id:6'
    )
