import json


import pytest


import tests_eats_eaters.edm_utils as edm_utils


EXPECTED_SETTINGS = {
    'service_name': 'eats-eaters',
    'pg_cluster_name': 'postgresql-eats_eaters',
    'pg_scheme': 'eats_eaters',
    'pg_table_name': 'users',
    'pg_updated_at_field_name': 'updated_at',
    'pg_create_at_field_name': 'created_at',
    'pg_id_field_name': 'id',
    'pg_fields_delimiter': ';',
    'pg_pairs': [
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'passport_uid',
            'id2_field_type': 'yandex_uid',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'personal_email_id',
            'id2_field_type': 'personal_email_id',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'client_id',
            'id2_field_type': 'eater_uuid',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'personal_phone_id',
            'id2_field_type': 'personal_phone_id',
        },
    ],
    'chunk_size': 2,
    'send_interval_ms': 500,
    'read_delay_sec': 120,
    'pg_cc_execute_ms': 500,
    'pg_cc_statement_ms': 500,
    'start_from_the_very_beginning': True,
}


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_settings(taxi_eats_eaters, testpoint, mockserver):
    @testpoint('testpoint_edm_task_settings')
    def testpoint_edm_task_settings(data):
        data['pg_pairs'].sort(key=json.dumps)
        EXPECTED_SETTINGS['pg_pairs'].sort(key=json.dumps)
        assert EXPECTED_SETTINGS == data

    await edm_utils.run_task(taxi_eats_eaters)

    assert testpoint_edm_task_settings.times_called == 1


EXPECTED_SETTINGS_2 = {
    'service_name': 'eats-eaters',
    'pg_cluster_name': 'postgresql-eats_eaters',
    'pg_scheme': 'eats_eaters',
    'pg_table_name': 'users',
    'pg_updated_at_field_name': 'updated_at',
    'pg_create_at_field_name': 'created_at',
    'pg_id_field_name': 'id',
    'pg_fields_delimiter': ';',
    'pg_pairs': [
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'passport_uid',
            'id2_field_type': 'yandex_uid',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'personal_email_id',
            'id2_field_type': 'personal_email_id',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'client_id',
            'id2_field_type': 'eater_uuid',
        },
        {
            'id1_field_name': 'id',
            'id1_field_type': 'eater_id',
            'id2_field_name': 'personal_phone_id',
            'id2_field_type': 'personal_phone_id',
        },
    ],
    'chunk_size': 15,
    'send_interval_ms': 1000,
    'read_delay_sec': 600,
    'pg_cc_execute_ms': 600,
    'pg_cc_statement_ms': 600,
    'start_from_the_very_beginning': True,
}


async def test_edm_task_settings_default(
        taxi_eats_eaters, testpoint, mockserver, taxi_config,
):
    @testpoint('testpoint_edm_task_settings')
    def testpoint_edm_task_settings(data):
        data['pg_pairs'].sort(key=json.dumps)
        EXPECTED_SETTINGS_2['pg_pairs'].sort(key=json.dumps)
        assert EXPECTED_SETTINGS_2 == data

    config = edm_utils.get_default_config()
    del config['eats-eaters']
    taxi_config.set_values({'EATS_DATA_MAPPINGS_UPLOAD_PARAMS': config})
    await taxi_eats_eaters.invalidate_caches()

    await edm_utils.run_task(taxi_eats_eaters)

    assert testpoint_edm_task_settings.times_called == 1
