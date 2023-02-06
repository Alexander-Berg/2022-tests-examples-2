import pytest

# Shortcuts:

PERIODIC_NAME = 'pseudo-crons-periodic'

# DB helpers:

DB_NAME = 'eats_logistics_performer_payouts'
PG_FILES = [DB_NAME + '/insert_subjects_to_trim.sql']

CRON_CURSOR_NAME = 'PSEUDO_CRONS'


def upsert_cursor(pgsql, cursor_name, cursor_value):
    schema = DB_NAME
    pg_cursor = pgsql[DB_NAME].dict_cursor()
    pg_cursor.execute(
        f'INSERT INTO {schema}.cursors (id, cursor, updated_at) '
        f'VALUES (\'{cursor_name}\', \'{cursor_value}\'::TEXT, NOW()) '
        f'ON CONFLICT (id) DO '
        f'UPDATE SET '
        f'cursor = EXCLUDED.cursor, '
        f'updated_at = EXCLUDED.updated_at',
    )


def assert_subj_present(pgsql, subj_id):
    schema = DB_NAME
    pg_cursor = pgsql[DB_NAME].dict_cursor()

    # Count the subjects
    pg_cursor.execute(
        f'SELECT COUNT(*) AS num '
        f'FROM {schema}.subjects '
        f'WHERE id = \'{subj_id}\'',
    )
    subj_num = pg_cursor.fetchone()['num']
    assert subj_num == 1


def assert_subj_trimmed(pgsql, subj_id):
    schema = DB_NAME
    pg_cursor = pgsql[DB_NAME].dict_cursor()

    # Count the subjects
    pg_cursor.execute(
        f'SELECT COUNT(*) AS num '
        f'FROM {schema}.subjects '
        f'WHERE id = \'{subj_id}\'',
    )
    subj_num = pg_cursor.fetchone()['num']
    assert subj_num == 0

    # Count relations
    pg_cursor.execute(
        f'SELECT COUNT(*) AS num '
        f'FROM {schema}.subjects_subjects '
        f'WHERE subject_id = \'{subj_id}\' '
        f'  OR related_subject_id = \'{subj_id}\'',
    )
    rel_num = pg_cursor.fetchone()['num']
    assert rel_num == 0

    # Count calculation_results
    pg_cursor.execute(
        f'SELECT COUNT(*) AS num '
        f'FROM {schema}.calculation_results '
        f'WHERE subject_id = \'{subj_id}\'',
    )
    cr_num = pg_cursor.fetchone()['num']
    assert cr_num == 0

    # Count factor values
    ft_table_list = [
        'factor_string_values',
        'factor_integer_values',
        'factor_decimal_values',
        'factor_datetime_values',
    ]
    for ft_table in ft_table_list:
        pg_cursor.execute(
            f'SELECT COUNT(*) AS num '
            f'FROM {schema}.{ft_table} '
            f'WHERE subject_id = \'{subj_id}\'',
        )
        ft_num = pg_cursor.fetchone()['num']
        assert ft_num == 0


# Config helpers:

CFG_TRIMMING = {
    'limit': 1000,
    'selection_batch_size': 10,
    'deletion_batch_size': 10,
    'default_lt_interval_d': 1,
    'fulltimer_lt_interval_d': 3,
    'nocalc_lt_interval_d': 5,
    'fulltimer_calc_schemas': ['eda_fulltimers'],
    'type_ids': [2, 3, 4, 7, 8, 9, 10, 11],
    'base_type_id': 2,
}

CRON_NAME = 'DB_TRIMMING'


def cfg_crons(cron_list):
    cfg_json = {CRON_NAME: {'kind': 'daily_times', 'times': cron_list}}
    return cfg_json


# Parameter helpers:

STATIC = [
    # 'courier_service'
    1000,
    # 'driver_profile'
    1001,
    # 'performer'
    1002,
]

STRAY_06_20 = [
    # 'delivery_proposal'
    1006,
    # 'delivery_adoption'
    1014,
    # 'order'
    1041,
]

FULLTIMER_06_20 = [
    # 'shift'
    1003,
    # 'delivery_proposal'
    1007,
    1008,
    1009,
    # 'delivery_adoption'
    1015,
    1016,
    # 'delivery'
    1021,
    1022,
    # 'point'
    1027,
    1028,
    1029,
    1030,
    1031,
    1032,
    # 'order'
    1042,
    1043,
    1044,
]

FULLTIMER_06_21 = [
    # 'shift'
    1004,
    # 'delivery_proposal'
    1010,
    1011,
    # 'delivery_adoption'
    1017,
    1018,
    # 'delivery'
    1023,
    1024,
    # 'point'
    1033,
    1034,
    1035,
    1036,
    # 'order'
    1045,
    1046,
]

NOCALC_06_22 = [
    # 'shift'
    1005,
    # 'delivery_proposal'
    1012,
    1013,
    # 'delivery_adoption'
    1019,
    1020,
    # 'delivery'
    1025,
    1026,
    # 'point'
    1037,
    1038,
    1039,
    1040,
    # 'order'
    1047,
    1048,
]


# Tests:


@pytest.mark.parametrize(
    'spared_subj_ids,trimmed_subj_ids,cron_cursor',
    [
        pytest.param(
            STATIC + FULLTIMER_06_20 + FULLTIMER_06_21 + NOCALC_06_22,
            STRAY_06_20,
            '2020-06-21 21:29:10+03',
            marks=pytest.mark.now('2020-06-21T21:30:10+0300'),
            id='trim stray by dft LTI',
        ),
        pytest.param(
            STATIC + FULLTIMER_06_21 + NOCALC_06_22,
            STRAY_06_20 + FULLTIMER_06_20,
            '2020-06-23 21:29:10+03',
            marks=pytest.mark.now('2020-06-23T21:30:10+0300'),
            id='trim fulltimer by special LTI',
        ),
        pytest.param(
            STATIC + NOCALC_06_22,
            STRAY_06_20 + FULLTIMER_06_20 + FULLTIMER_06_21,
            '2020-06-26 21:29:10+03',
            marks=pytest.mark.now('2020-06-26T21:30:10+0300'),
            id='keep nocalc by special LTI',
        ),
    ],
)
@pytest.mark.pgsql(DB_NAME, files=PG_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_DB_TRIMMING_SETTINGS_V3=CFG_TRIMMING,
    EATS_LOGISTICS_PERFORMER_PAYOUTS_PSEUDO_CRONS=cfg_crons(['21:30']),
)
async def test_distlock_daily_db_trimming(
        cron_cursor,
        pgsql,
        spared_subj_ids,
        taxi_eats_logistics_performer_payouts,
        trimmed_subj_ids,
):
    service = taxi_eats_logistics_performer_payouts
    upsert_cursor(pgsql, CRON_CURSOR_NAME, cron_cursor)
    await service.run_periodic_task(PERIODIC_NAME)

    for subj_id in spared_subj_ids:
        assert_subj_present(pgsql, subj_id)

    for subj_id in trimmed_subj_ids:
        assert_subj_trimmed(pgsql, subj_id)
