import pytest


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'external_phone',
            'sf_api_name': 'ClientPhone',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'internal_phone',
            'sf_api_name': 'ManagerPhone',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'subject',
            'sf_api_name': 'Subject',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'call_id',
            'sf_api_name': 'CallExternalId',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'sf_org': 'b2b',
            'sf_object': 'Task',
            'source_key': 'call_id',
        },
    },
)
async def test_load_corp_calls(taxi_sf_data_load_web, pgsql):
    cursor = pgsql['sf_data_load'].cursor()

    corp_call = {
        'internal_phone': '215742',
        'external_phone': '88005553535',
        'subject': 'incoming',
        'call_init_datetime': '2022-05-23T16:14:00',
        'call_start_datetime': '2022-05-23T16:14:00',
        'call_end_datetime': '2022-05-23T16:14:00',
        'call_record_url': 'www.leningrad.spb.ru',
        'call_id': 'QWEEWQRTYYTR',
        'call_result': 'answer',
    }

    resp = await taxi_sf_data_load_web.put(
        '/v1/cc_sf_cti/b2b/', json=corp_call,
    )
    assert resp.status == 200

    resp = await taxi_sf_data_load_web.put(
        '/v1/cc_sf_cti/b2b/', json=corp_call,
    )

    assert resp.status == 200

    query = """
        SELECT
            source_class_name,
            source_field,
            sf_api_field_name,
            lookup_alias,
            data_value
        FROM sf_data_load.loading_fields
        WHERE source_key = 'QWEEWQRTYYTR'
        ORDER BY source_field;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        (
            'B2BCallsFromSfCti',
            'call_id',
            'CallExternalId',
            'b2b-cc-sf-cti',
            'QWEEWQRTYYTR',
        ),
        (
            'B2BCallsFromSfCti',
            'external_phone',
            'ClientPhone',
            'b2b-cc-sf-cti',
            '88005553535',
        ),
        (
            'B2BCallsFromSfCti',
            'internal_phone',
            'ManagerPhone',
            'b2b-cc-sf-cti',
            '215742',
        ),
        (
            'B2BCallsFromSfCti',
            'subject',
            'Subject',
            'b2b-cc-sf-cti',
            'incoming',
        ),
    ]


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'external_phone',
            'sf_api_name': 'ClientPhone',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'internal_phone',
            'sf_api_name': 'ManagerPhone',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'call_type',
            'sf_api_name': 'Subject',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'call_id',
            'sf_api_name': 'CallExternalId',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
        {
            'source': 'B2BCallsFromSfCti',
            'source_field': 'call_status',
            'sf_api_name': 'Status',
            'lookup_alias': 'b2b-cc-sf-cti',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'sf_org': 'b2b',
            'sf_object': 'Task',
            'source_key': 'call_id',
        },
    },
)
async def test_load_corp_calls_new(taxi_sf_data_load_web, pgsql):
    cursor = pgsql['sf_data_load'].cursor()
    corp_call = {
        'internal_phone': '215742',
        'external_phone': '88005553535',
        'subject': 'incoming',
        'call_init_datetime': '2022-05-23T16:14:00',
        'call_start_datetime': '2022-05-23T16:14:00',
        'call_end_datetime': '2022-05-23T16:14:00',
        'call_record_url': 'www.leningrad.spb.ru',
        'call_id': 'QWEEWQRTYYTR',
        'call_result': 'no_answer',
    }

    resp = await taxi_sf_data_load_web.put(
        '/v1/cc_sf_cti/b2b/', json=corp_call,
    )
    assert resp.status == 200

    query = """
            SELECT
                source_class_name,
                source_field,
                sf_api_field_name,
                lookup_alias,
                data_value
            FROM sf_data_load.loading_fields
            WHERE source_key = 'QWEEWQRTYYTR'
            ORDER BY source_field;
        """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        (
            'B2BCallsFromSfCti',
            'call_id',
            'CallExternalId',
            'b2b-cc-sf-cti',
            'QWEEWQRTYYTR',
        ),
        (
            'B2BCallsFromSfCti',
            'call_status',
            'Status',
            'b2b-cc-sf-cti',
            'Open',
        ),
        (
            'B2BCallsFromSfCti',
            'call_type',
            'Subject',
            'b2b-cc-sf-cti',
            'Обработать пропущенный звонок',
        ),
        (
            'B2BCallsFromSfCti',
            'external_phone',
            'ClientPhone',
            'b2b-cc-sf-cti',
            '88005553535',
        ),
        (
            'B2BCallsFromSfCti',
            'internal_phone',
            'ManagerPhone',
            'b2b-cc-sf-cti',
            '215742',
        ),
    ]
