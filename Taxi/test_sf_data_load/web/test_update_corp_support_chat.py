import pytest


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BSupportChat',
            'source_field': 'sf_id',
            'sf_api_name': 'Id',
            'lookup_alias': 'b2b-support-chat',
            'load_period': 1,
        },
        {
            'source': 'B2BSupportChat',
            'source_field': 'status',
            'sf_api_name': 'Status',
            'lookup_alias': 'b2b-support-chat',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'b2b-support-chat': {
            'sf_org': 'b2b',
            'sf_object': 'Case',
            'source_key': 'sf_id',
            'update': True,
            'sf_key': 'Id',
        },
    },
)
async def test_load_corp_calls(taxi_sf_data_load_web, pgsql):
    cursor = pgsql['sf_data_load'].cursor()

    corp_call = {'sf_id': 'id_in_sf', 'status': 'open'}

    resp = await taxi_sf_data_load_web.put(
        '/v1/corp_support_chat/b2b/update_status/', json=corp_call,
    )
    assert resp.status == 200

    corp_call = {'sf_id': 'id_in_sf2', 'status': 'pause'}
    resp = await taxi_sf_data_load_web.put(
        '/v1/corp_support_chat/b2b/update_status', json=corp_call,
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
        ORDER BY source_field;
    """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        ('B2BSupportChat', 'sf_id', 'Id', 'b2b-support-chat', 'id_in_sf'),
        ('B2BSupportChat', 'sf_id', 'Id', 'b2b-support-chat', 'id_in_sf2'),
        ('B2BSupportChat', 'status', 'Status', 'b2b-support-chat', 'New'),
        ('B2BSupportChat', 'status', 'Status', 'b2b-support-chat', 'On Hold'),
    ]
