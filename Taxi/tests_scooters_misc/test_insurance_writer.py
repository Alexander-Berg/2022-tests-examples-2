import psycopg2
import pytest


DISTLOCK_NAME = 'scooters-misc-insurance-writer'
BATCH_SIZE = 4
INSURED_RIDES_COUNT = 3

DEFAULT_SETTINGS = {
    'enabled': True,
    'sleep-time-ms': 100,
    'compiled_rides_batch_size': BATCH_SIZE,
    'insurance_product_codes': {
        'standart': 'Yandex_NS_GO',
        'full': 'Yandex_NS_GO_Property',
    },
    'tariffs_to_cities_matching': {
        'scooters_minutes': 'Москва',
        'fixpoint_scooter': 'Москва',
    },
}

SELECT_INSURANCE_POLICIES = 'SELECT * FROM scooters_misc.insurance_policies;'
SELECT_TABLE_CURSORS = 'SELECT * FROM scooters_misc.drive_tables_cursors;'


def get_alfa_create_response(load_json, idx, session_id):
    response = load_json('alfa_insurance_create_response.json')
    response['policies'][0]['policy_id'] += idx
    response['policies'][0]['external_id'] = session_id
    return response


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
@pytest.mark.now('2022-04-18T12:00:00+0000')
async def test_simple(taxi_scooters_misc, mockserver, load_json, pgsql):
    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        assert request.query['confirm'] == 'true'
        expected_product_code = (
            'Yandex_NS_GO'
            if request.json['external_id'] == 'session_id_100'
            else 'Yandex_NS_GO_Property'
        )
        assert request.json['product']['code'] == expected_product_code
        assert request.json['begin_date'] == '2021-06-21T07:46:40+00:00'
        assert request.json['end_date'] == '2021-06-21T10:00:00+00:00'

        return get_alfa_create_response(
            load_json,
            mock_alfa_create_policies.times_called,
            request.json['external_id'],
        )

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert mock_alfa_create_policies.times_called == INSURED_RIDES_COUNT

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(SELECT_TABLE_CURSORS)
    cursors_dict = {rec['drive_table']: rec['drive_cursor'] for rec in cursor}
    assert cursors_dict == {'insurance_writer:compiled_rides': 1 + BATCH_SIZE}

    cursor.execute(SELECT_INSURANCE_POLICIES)
    insurance_policies = cursor.fetchall()
    assert len(insurance_policies) == INSURED_RIDES_COUNT
    sessions = set(p['session_id'] for p in insurance_policies)
    assert len(sessions) == INSURED_RIDES_COUNT
    for policy in insurance_policies:
        assert policy['policy_url'] is not None
        assert policy['created_at'] is not None
        assert policy['data'] is not None


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
async def test_no_new_records(
        taxi_scooters_misc, mockserver, load_json, pgsql,
):
    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        pass

    cursor = pgsql['scooter_backend'].cursor()
    query = """
        UPDATE scooters_misc.drive_tables_cursors
        SET drive_cursor = 100
        WHERE drive_table = 'insurance_writer:compiled_rides';
    """
    cursor.execute(query)

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert not mock_alfa_create_policies.has_calls

    cursor.execute(SELECT_INSURANCE_POLICIES)
    insurance_policies = cursor.fetchall()
    assert not insurance_policies


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
async def test_alfa_api_fail(taxi_scooters_misc, mockserver, load_json, pgsql):
    failed_session_id = 'session_id_101'

    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        if request.json['external_id'] == failed_session_id:
            return mockserver.make_response(status=500, json={})

        return get_alfa_create_response(
            load_json,
            mock_alfa_create_policies.times_called,
            request.json['external_id'],
        )

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    assert mock_alfa_create_policies.times_called == INSURED_RIDES_COUNT
    cursor.execute(SELECT_TABLE_CURSORS)
    cursors_dict = {rec['drive_table']: rec['drive_cursor'] for rec in cursor}
    assert cursors_dict == {'insurance_writer:compiled_rides': 1 + BATCH_SIZE}

    cursor.execute(SELECT_INSURANCE_POLICIES)
    insurance_policies = cursor.fetchall()
    assert not [
        p for p in insurance_policies if p['session_id'] == failed_session_id
    ]
    assert len(insurance_policies) == INSURED_RIDES_COUNT - 1


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
async def test_insurance_already_exist(
        taxi_scooters_misc, mockserver, load_json, pgsql,
):
    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        return get_alfa_create_response(
            load_json,
            mock_alfa_create_policies.times_called,
            request.json['external_id'],
        )

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

    session_id_with_insurance = 'session_id_101'
    query = f"""
        INSERT INTO scooters_misc.insurance_policies
            (policy_id, session_id, policy_url, created_at, data)
        VALUES
            (1000, '{session_id_with_insurance}',
             'url', '2022-03-10T20:23:52.9', NULL)
    """
    cursor.execute(query)

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    assert mock_alfa_create_policies.times_called == INSURED_RIDES_COUNT - 1
    cursor.execute(SELECT_TABLE_CURSORS)
    cursors_dict = {rec['drive_table']: rec['drive_cursor'] for rec in cursor}
    assert cursors_dict == {'insurance_writer:compiled_rides': 1 + BATCH_SIZE}

    cursor.execute(SELECT_INSURANCE_POLICIES)
    insurance_policies = cursor.fetchall()
    assert len(insurance_policies) == INSURED_RIDES_COUNT


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
async def test_no_insured_rides(
        taxi_scooters_misc, mockserver, load_json, pgsql,
):
    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        pass

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

    query = """
        UPDATE scooters_misc.drive_tables_cursors
        SET drive_cursor = 4
        WHERE drive_table = 'insurance_writer:compiled_rides';
    """
    cursor.execute(query)

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    assert mock_alfa_create_policies.times_called == 0
    cursor.execute(SELECT_TABLE_CURSORS)
    cursors_dict = {rec['drive_table']: rec['drive_cursor'] for rec in cursor}
    assert cursors_dict == {'insurance_writer:compiled_rides': 1 + BATCH_SIZE}

    cursor.execute(SELECT_INSURANCE_POLICIES)
    insurance_policies = cursor.fetchall()
    assert not insurance_policies


@pytest.mark.config(SCOOTERS_MISC_INSURANCE_WRITER_SETTINGS=DEFAULT_SETTINGS)
async def test_no_nickname(taxi_scooters_misc, mockserver, load_json, pgsql):
    @mockserver.json_handler('/alfa-tes-insurance/policies')
    def mock_alfa_create_policies(request):
        assert request.json['insureds'][0]['nick_name'] == 'UNKNOWN'

    cursor = pgsql['scooter_backend'].cursor()

    query = """
        UPDATE public.user
        SET first_name = '', last_name = '', username = ''
        WHERE id = '7922cc9e-031f-4b5c-9aac-6ca5308ea886';
    """
    cursor.execute(query)

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert mock_alfa_create_policies.times_called == INSURED_RIDES_COUNT
