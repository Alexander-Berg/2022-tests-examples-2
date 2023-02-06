import pytest

PERIODIC_NAME = 'clear-deleted-tg-logins-bindings-periodic'


def get_logins(pgsql, place_id):
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        f"""
        SELECT login_id
        FROM eats_restapp_communications.places_tg_logins
        WHERE place_id={place_id};
    """,
    )
    res = cursor.fetchall()
    return [row[0] for row in res]


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_PERIODICS={
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 3600},
    },
    EATS_RESTAPP_COMMUNICATIONS_CLEAR_DELETED_TG_LOGINS_BINDINGS_SETTINGS={
        'hours_after_deletion': 168,
    },
)
@pytest.mark.pgsql(
    'eats_restapp_communications',
    files=['test_clear_deleted_tg_login_bindings_periodics.sql'],
)
@pytest.mark.now('2022-06-20T15:00:00+0300')
async def test_clear_deleted_tg_login_bindings_periodics(
        mockserver, taxi_eats_restapp_communications, pgsql,
):

    data_before_periodic = get_logins(pgsql, 1)
    assert len(data_before_periodic) == 4
    assert 'some_login4' in data_before_periodic

    await taxi_eats_restapp_communications.run_distlock_task(PERIODIC_NAME)
    data_after_periodic = get_logins(pgsql, 1)

    assert len(data_after_periodic) == 3
    assert 'some_login4' not in data_after_periodic
