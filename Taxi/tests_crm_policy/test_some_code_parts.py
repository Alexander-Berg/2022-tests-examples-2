async def test_uuid_form_wrong_trigger(
        taxi_crm_policy, pgsql, testpoint, load,
):
    is_data_race_inited = False
    resp_waited = {}

    @testpoint('BranchReadCommunicationTableInfoMadeInsert')
    async def _data_race_init_func(data):
        nonlocal is_data_race_inited
        nonlocal resp_waited
        if not is_data_race_inited:
            is_data_race_inited = True
            response2 = await taxi_crm_policy.get(
                '/v1/check_update_send_message',
                params={
                    'entity_id': 'testKeyID3',
                    'entity_type': 'user_id',
                    'channel_type': 'fullscreen',
                    'campaign_id': '1ed56ee7-f7cb-4d6c-b306-60b546d6dabf',
                    'experiment_id': '111',
                    'experiment_group_id': 'group_1',
                },
            )
            resp_waited = response2.json()

    pgsql['crm_policy'].cursor().execute(
        load('create_uuid_grop_and_other.sql'),
    )

    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'testKeyID3',
            'entity_type': 'user_id',
            'channel_type': 'fullscreen',
            'campaign_id': '1ed56ee7-f7cb-4d6c-b306-60b546d6dabf',
            'experiment_id': '111',
            'experiment_group_id': 'group_1',
        },
    )

    assert response.json() == {'allowed': False}
