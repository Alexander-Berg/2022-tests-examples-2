import datetime
import logging


import pytest


import tests_eats_eaters.edm_utils as edm_utils


NOW_DATETIME = datetime.datetime(
    2020, 6, 15, 14, 0, 0, tzinfo=datetime.timezone.utc,
)


# no email
NOT_FULL_USER_1 = (
    'INSERT INTO eats_eaters.users'
    '(id, passport_uid, client_id, personal_phone_id,'
    'updated_at, created_at, client_type)'
    'VALUES({user_id}, \'yandex_uid_{user_id}\', \'uuid_{user_id}\','
    '\'ppid_{user_id}\', \'{updated_at}\',\'{created_at}\','
    '\'no matter\')'.format(
        user_id=1,
        updated_at='2020-06-15T13:00:00+00:00',
        created_at=edm_utils.DEFAULT_CREATED_AT,
    )
)

# user 2 is full

# no email, phone, yandex_uid,
NOT_FULL_USER_2 = (
    'INSERT INTO eats_eaters.users'
    '(id, client_id, updated_at, created_at, client_type)'
    'VALUES({user_id}, \'uuid_{user_id}\', \'{updated_at}\','
    '\'{created_at}\', \'no matter\')'.format(
        user_id=3,
        updated_at='2020-06-15T13:02:00+00:00',
        created_at=edm_utils.DEFAULT_CREATED_AT,
    )
)

EXPECTED_PHASE_1 = [
    {
        'first_entity_type': 'eater_id',
        'first_entity_value': '1',
        'second_entity_type': 'yandex_uid',
        'second_entity_value': 'yandex_uid_1',
        'created_at': edm_utils.DEFAULT_CREATED_AT,
    },
    {
        'first_entity_type': 'eater_id',
        'first_entity_value': '1',
        'second_entity_type': 'eater_uuid',
        'second_entity_value': 'uuid_1',
        'created_at': edm_utils.DEFAULT_CREATED_AT,
    },
    {
        'first_entity_type': 'eater_id',
        'first_entity_value': '1',
        'second_entity_type': 'personal_phone_id',
        'second_entity_value': 'ppid_1',
        'created_at': edm_utils.DEFAULT_CREATED_AT,
    },
]
EXPECTED_PHASE_1.extend(edm_utils.user_expected(2))

EXPECTED_PHASE_2 = [
    {
        'first_entity_type': 'eater_id',
        'first_entity_value': '3',
        'second_entity_type': 'eater_uuid',
        'second_entity_value': 'uuid_3',
        'created_at': edm_utils.DEFAULT_CREATED_AT,
    },
]


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_send_not_full_data(
        taxi_eats_eaters,
        mockserver,
        pgsql,
        mocked_time,
        testpoint,
        rewind_period,
):
    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        if phase == 1:
            assert {'pairs': EXPECTED_PHASE_1} == request.json
        if phase == 2:
            assert {'pairs': EXPECTED_PHASE_2} == request.json
        return mockserver.make_response(status=204)

    mock_now_value = NOW_DATETIME

    @testpoint('testpoint_mock_now')
    def testpoint_mock_now(data):
        return edm_utils.mock_now(mock_now_value)

    psql_cursor = pgsql['eats_eaters'].cursor()

    edm_utils.initialize_meta_table(psql_cursor)

    # chunk 1
    psql_cursor.execute(NOT_FULL_USER_1)
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')

    # chunk 2
    psql_cursor.execute(NOT_FULL_USER_2)

    mocked_time.set(NOW_DATETIME)
    await taxi_eats_eaters.invalidate_caches()

    phase = 1
    logging.info('==== Phase #%d ====', phase)
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1
    assert testpoint_mock_now.times_called == 3

    phase = 2
    logging.info('==== Phase #%d ====', phase)
    mock_now_value = await rewind_period()
    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 2
    assert testpoint_mock_now.times_called == 6
