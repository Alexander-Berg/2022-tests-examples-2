import pytest


def execute_and_return_single_row(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()[0]


@pytest.mark.now('2020-06-09T18:00:00+03')
async def test_delete_old_custom_checks(taxi_hejmdal, pgsql, mocked_time):
    cursor = pgsql['hejmdal'].cursor()
    query = 'select deleted from custom_checks'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0]

    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select deleted from custom_checks'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1

    mocked_time.sleep(60 * 4)
    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select deleted from custom_checks'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1

    mocked_time.sleep(65)
    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select deleted from custom_checks'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res == []


@pytest.mark.config(
    HEJMDAL_CLEANUP={
        'old_incidents_cleanup': {
            'enabled': True,
            'ttl_days': 365,
            'delete_command_control': {
                'network_timeout_ms': 300,
                'statement_timeout_ms': 300,
            },
        },
        'period_sec': 10,
    },
)
@pytest.mark.now('2020-06-09T17:56:40+0000')
async def test_remove_old_incidents(taxi_hejmdal, pgsql):
    cursor = pgsql['hejmdal'].cursor()
    query = (
        'select circuit_id, end_time from incident_history '
        + 'order by end_time desc'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 2
    assert db_res[0][0] == 'test_circuit_1'
    assert db_res[1][0] == 'test_circuit_2'

    query = 'select name from services order by name'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 4
    assert db_res[0][0] == 'test_service_1'
    assert db_res[1][0] == 'test_service_2'
    assert db_res[2][0] == 'test_service_3'
    assert db_res[3][0] == 'test_service_4'

    query = (
        'select spec_template_id from spec_template_mods '
        + 'order by spec_template_id'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 4
    assert db_res[0][0] == 'spec_template_id_1'
    assert db_res[1][0] == 'spec_template_id_2'
    assert db_res[2][0] == 'spec_template_id_3'
    assert db_res[3][0] == 'spec_template_id_4'

    query = 'select id from external_events order by id'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 4
    assert db_res[0][0] == 1
    assert db_res[1][0] == 2
    assert db_res[2][0] == 3
    assert db_res[3][0] == 4

    await taxi_hejmdal.run_task('distlock/db_cleanup')

    query = (
        'select circuit_id, end_time from incident_history '
        + 'order by end_time desc'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] == 'test_circuit_1'

    query = 'select name from services order by name'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 3
    assert db_res[0][0] == 'test_service_1'
    assert db_res[1][0] == 'test_service_2'
    assert db_res[2][0] == 'test_service_3'

    query = (
        'select spec_template_id from spec_template_mods '
        + 'order by spec_template_id'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 3
    assert db_res[0][0] == 'spec_template_id_1'
    assert db_res[1][0] == 'spec_template_id_2'
    assert db_res[2][0] == 'spec_template_id_3'

    query = 'select id from external_events order by id'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 3
    assert db_res[0][0] == 1
    assert db_res[1][0] == 2
    assert db_res[2][0] == 3


@pytest.mark.now('2021-09-25T10:00:10+0000')
async def test_remove_old_services_uptime(taxi_hejmdal, pgsql, mocked_time):
    cursor = pgsql['hejmdal'].cursor()
    query = 'select service_id, updated from services_uptime'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] == 3

    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select service_id, updated from services_uptime'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] == 3

    mocked_time.sleep(72 * 60 * 60)
    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select service_id, updated from services_uptime'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res == []
