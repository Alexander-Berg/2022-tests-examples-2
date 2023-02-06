import pytest


@pytest.mark.now('2019-07-26T10:10:00+0000')
@pytest.mark.parametrize(
    'rule_name,expected,status',
    [
        (
            'test_rule',
            {
                'targets_timestamp': '2018-11-12T12:00:00+0000',
                'replicate_by': 'updated',
                'queue_timestamp': '2019-03-14T12:00:00+0000',
            },
            200,
        ),
        (
            'test_sharded_rule',
            {
                'targets_timestamp': None,
                'replicate_by': 'updated',
                'queue_timestamp': '2019-03-14T03:00:00+0000',
            },
            200,
        ),
        ('wrong_rule', 'Rule wrong_rule not found', 404),
        (
            'test_sharded_mongo',
            {
                'targets_timestamp': '2019-07-26T01:00:00+0000',
                'replicate_by': 'updated',
                'queue_timestamp': '2019-07-26T03:00:00+0000',
            },
            200,
        ),
    ],
)
async def test_get_min_ts(replication_client, rule_name, expected, status):
    response = await replication_client.get(f'/state/min_ts/{rule_name}')
    assert response.status == status
    if status == 200:
        response_data = await response.json()
    else:
        response_data = await response.text()
    assert response_data == expected, rule_name


@pytest.mark.now('2019-07-26T10:20:00+0000')
async def test_get_min_ts_no_progress_outdated(replication_client):
    response = await replication_client.get('/state/min_ts/test_sharded_mongo')
    assert response.status == 200
    assert (await response.json()) == {
        'targets_timestamp': '2019-01-20T03:00:00+0000',
        'replicate_by': 'updated',
        'queue_timestamp': '2019-01-20T03:00:00+0000',
    }


@pytest.mark.parametrize(
    'target_name,expected,status',
    [
        (
            'test_rule_bson',
            {
                'table_path': 'test/test_bson',
                'full_table_path': '//home/taxi/unittests/test/test_bson',
                'clients_delays': [
                    {
                        'client_name': 'arni',
                        'current_timestamp': '2018-11-14T03:00:00+0000',
                        'current_delay': 100,
                    },
                    {
                        'client_name': 'hahn',
                        'current_timestamp': '2018-11-14T03:01:40+0000',
                        'current_delay': 0,
                    },
                ],
                'target_names': ['test_rule_bson'],
            },
            200,
        ),
        (
            'non_existent',
            'No replication rules for target non_existent found',
            404,
        ),
    ],
)
@pytest.mark.filldb(replication_state='yt_target_info')
async def test_get_yt_target_info(
        replication_client, target_name, expected, status,
):
    response = await replication_client.get(
        f'/state/yt_target_info/{target_name}',
    )
    assert response.status == status
    if status == 200:
        response_data = await response.json()
    else:
        response_data = await response.text()
    assert response_data == expected


@pytest.mark.filldb(replication_state='yt_target_info')
async def test_get_all_yt_targets_info(replication_client):
    response = await replication_client.get('/state/all_yt_target_info')
    assert response.status == 200
    assert (
        sorted(
            (await response.json())['targets_info'],
            key=lambda val: (val['table_path'], val['target_names'][0]),
        )
        == [
            {
                'table_path': 'test/test_bson',
                'full_table_path': '//home/taxi/unittests/test/test_bson',
                'clients_delays': [
                    {
                        'client_name': 'arni',
                        'current_timestamp': '2018-11-14T03:00:00+0000',
                        'current_delay': 100,
                    },
                    {
                        'client_name': 'hahn',
                        'current_timestamp': '2018-11-14T03:01:40+0000',
                        'current_delay': 0,
                    },
                ],
                'target_names': ['test_rule_bson'],
            },
            {
                'clients_delays': [
                    {
                        'client_name': 'arni',
                        'current_delay': 0,
                        'current_timestamp': '2019-11-05T10:00:00+0000',
                    },
                ],
                'table_path': 'test/test_struct_2',
                'full_table_path': (
                    '//allowed/unittests/data/test/test_struct_2'
                ),
                'target_names': ['test_errors_rule_struct_2'],
            },
            {
                'clients_delays': [
                    {
                        'client_name': 'hahn',
                        'current_delay': None,
                        'current_timestamp': None,
                    },
                    {
                        'client_name': 'seneca-vla',
                        'current_delay': 0,
                        'current_timestamp': '2019-03-14T12:00:00+0000',
                    },
                ],
                'table_path': 'test/test_struct_sharded',
                'full_table_path': (
                    '//home/taxi/unittests/test/test_struct_sharded'
                ),
                'target_names': [
                    'test_sharded_rule2_sharded_struct',
                    'test_sharded_rule_sharded_struct',
                ],
            },
            {
                'clients_delays': [
                    {
                        'client_name': 'seneca-vla',
                        'current_delay': 0,
                        'current_timestamp': '2019-03-14T13:00:00+0000',
                    },
                ],
                'table_path': 'test/test_struct_sharded',
                'full_table_path': (
                    '//home/taxi/unittests/test/test_struct_sharded'
                ),
                'target_names': ['test_sharded_rule_sharded_struct_runtime'],
            },
            {
                'clients_delays': [
                    {
                        'client_name': 'arni',
                        'current_delay': None,
                        'current_timestamp': None,
                    },
                    {
                        'client_name': 'hahn',
                        'current_delay': 0,
                        'current_timestamp': '2019-03-14T12:00:00+0000',
                    },
                ],
                'table_path': 'test/test_struct_sharded_no_partial',
                'full_table_path': (
                    '//home/taxi/unittests/test/test_struct_sharded_no_partial'
                ),
                'target_names': ['test_sharded_rule_no_partial'],
            },
        ]
    )
