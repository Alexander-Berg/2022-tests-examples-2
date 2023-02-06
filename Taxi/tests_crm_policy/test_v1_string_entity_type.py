# pylint: disable=import-only-modules
import pytest

from tests_crm_policy.utils import select_columns_from_table


async def send_bulk(taxi_crm_policy, entity):
    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {'experiment_group_id': '0_testing', 'entity_id': entity},
            ],
        },
    )
    return response


@pytest.mark.parametrize(
    'entity_type_and_id',
    [
        {'type': 'user_id', 'type_id': 2},
        {'type': 'dbid_uuid', 'type_id': 1},
        {'type': 'eda_user_id', 'type_id': 4},
        {'type': 'lavka_user_id', 'type_id': 5},
        {'type': 'geo_id', 'type_id': 6},
    ],
)
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_entity_type(
        taxi_crm_policy, mockserver, pgsql, mocked_time, entity_type_and_id,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': entity_type_and_id['type'],
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, 'user2')
    assert response.json() == {'allowed': [True]}
    assert response.status_code == 200
    recieved_entity_type = select_columns_from_table(
        'crm_policy.entity_ids', ['type_id'], pgsql['crm_policy'],
    )
    assert recieved_entity_type == [{'type_id': entity_type_and_id['type_id']}]


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_wrong_entity_str(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': 'string',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, 'asdasd')
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Unexpected entity string \'asdasd\'',
    }

    response = await send_bulk(
        taxi_crm_policy,
        'taximeter:iver:741ba20abdfe4fd3a709c4fcd79c04cd'
        ':0a4090c3c7e443faaa4a806c4df66a15',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Unexpected entity string \'taximeter:iver'
            ':741ba20abdfe4fd3a709c4fcd79c04cd'
            ':0a4090c3c7e443faaa4a806c4df66a15\''
        ),
    }

    response = await send_bulk(
        taxi_crm_policy,
        'taximeter:Driver'
        ':741ba20abdfe4fd3a709c4fcd70a4090c3c7e443faaa4a806c4df66a15',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Unexpected entity string \'taximeter'
            ':Driver:741ba20abdfe4fd3a709c4fcd70'
            'a4090c3c7e443faaa4a806c4df66a15\''
        ),
    }


@pytest.mark.parametrize(
    'entity',
    [
        'taximeter:City:Москва',
        'taximeter:Country:russia',
        'taximeter:Domain:dbid',
        'taximeter:Tag:xxx',
    ],
)
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_entity_always_allowed(
        taxi_crm_policy, mockserver, pgsql, mocked_time, entity,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': 'string',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(taxi_crm_policy, entity)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True]}

    response = await send_bulk(taxi_crm_policy, entity)
    assert response.status_code == 200
    assert response.json() == {'allowed': [True]}


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_entity_dbib_uuid(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': 'string',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await send_bulk(
        taxi_crm_policy,
        'taximeter:Driver:741ba20abdfe4fd3a709c4fcd79c04cd'
        ':0a4090c3c7e443faaa4a806c4df66a15',
    )
    assert response.status_code == 200
    assert response.json() == {'allowed': [True]}

    recieved_entity_type = select_columns_from_table(
        'crm_policy.entity_ids', ['entity_str'], pgsql['crm_policy'],
    )

    assert recieved_entity_type == [
        {
            'entity_str': (
                '741ba20abdfe4fd3a709c4fcd79c04cd'
                '_0a4090c3c7e443faaa4a806c4df66a15'
            ),
        },
    ]


@pytest.mark.config(
    CRM_POLICY_ENTITY_WHITE_LIST={'dbid_uuid': ['park1_user2']},
)
@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_entity_mixed1(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': 'string',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '0_testing',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': 'taximeter:City:Москва',
                },
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': (
                        'taximeter:Driver'
                        ':741ba20abdfe4fd3a709c4fcd79c04cd'
                        ':0a4090c3c7e443faaa4a806c4df66a15'
                    ),
                },
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': 'taximeter:Driver:park1:user2',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': [True, True, True]}

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': 'taximeter:City:Москва',
                },
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': (
                        'taximeter:Driver'
                        ':741ba20abdfe4fd3a709c4fcd79c04cd'
                        ':0a4090c3c7e443faaa4a806c4df66a15'
                    ),
                },
                {
                    'experiment_group_id': '0_testing',
                    'entity_id': 'taximeter:Driver:park1:user2',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': [True, False, True]}

    recieved_entity_type = select_columns_from_table(
        'crm_policy.entity_ids', ['entity_str'], pgsql['crm_policy'],
    )
    dbid_uuid = (
        '741ba20abdfe4fd3a709c4fcd79c04cd_0a4090c3c7e443faaa4a806c4df66a15'
    )
    assert sorted(recieved_entity_type, key=lambda x: x['entity_str']) == [
        {'entity_str': dbid_uuid},
        {'entity_str': 'park1_user2'},
    ]


@pytest.mark.pgsql(
    'crm_policy',
    files=['create_channels_default.sql', 'fill_entity_types.sql'],
)
async def test_recieved_entity_dbib_uuid_without_group(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': 'string',
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {
                    'entity_id': (
                        'taximeter:Driver'
                        ':741ba20abdfe4fd3a709c4fcd79c04cd'
                        ':0a4090c3c7e443faaa4a806c4df66a15'
                    ),
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': [True]}

    recieved_entity_type = select_columns_from_table(
        'crm_policy.entity_ids', ['entity_str'], pgsql['crm_policy'],
    )

    assert recieved_entity_type == [
        {
            'entity_str': (
                '741ba20abdfe4fd3a709c4fcd79c04cd'
                '_0a4090c3c7e443faaa4a806c4df66a15'
            ),
        },
    ]


@pytest.mark.parametrize(
    'entity_type_and_id',
    [
        {'type': 'string', 'type_id': 1, 'raw_type_id': 3},
        {'type': 'dbid_uuid', 'type_id': 1, 'raw_type_id': 1},
        {'type': 'user_id', 'type_id': 2, 'raw_type_id': 2},
    ],
)
@pytest.mark.pgsql(
    'crm_policy',
    files=[
        'create_channels_default.sql',
        'fill_entity_types.sql',
        'create_old_comm_info.sql',
    ],
)
async def test_update_and_apply_old_infos(
        taxi_crm_policy, mockserver, pgsql, mocked_time, entity_type_and_id,
):
    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin(request):
        resp = [
            {
                'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                'valid_until': '2020-12-31T23:59:59+00:00',
                'entity_type': entity_type_and_id['type'],
                'experiment': {
                    'experiment_id': (
                        'crm:hub:push_transporting_seatbelts_poll'
                    ),
                    'groups': [
                        {
                            'group_id': '__default__',
                            'channel': 'push',
                            'cooldown': 100,
                        },
                    ],
                },
            },
        ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    response = await taxi_crm_policy.post(
        '/v1/check_update_send_message_bulk',
        json={
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'items': [
                {
                    'entity_id': (
                        'taximeter:Driver'
                        ':741ba20abdfe4fd3a709c4fcd79c04cd'
                        ':0a4090c3c7e443faaa4a806c4df66a15'
                    ),
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'allowed': [True]}

    recieved_entity_type = select_columns_from_table(
        'crm_policy.registered_external_communications',
        ['expected_entity_type_id'],
        pgsql['crm_policy'],
    )

    assert recieved_entity_type == [
        {'expected_entity_type_id': entity_type_and_id['raw_type_id']},
    ]

    applied_entity_type = select_columns_from_table(
        'crm_policy.entity_ids', ['type_id'], pgsql['crm_policy'],
    )

    assert applied_entity_type == [{'type_id': entity_type_and_id['type_id']}]
