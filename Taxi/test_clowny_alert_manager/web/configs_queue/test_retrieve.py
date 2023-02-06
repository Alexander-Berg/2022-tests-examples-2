async def test_list(get_configs_queue_list):
    assert (await get_configs_queue_list(1))['configs'] == [
        {
            'branch_id': 1,
            'clown_branch_ids': [1],
            'status': 'pending',
            'updated_at': '2020-06-08T15:00:00+03:00',
        },
        {
            'branch_id': 2,
            'clown_branch_ids': [2],
            'status': 'applied',
            'updated_at': '2020-06-08T15:10:00+03:00',
        },
        {
            'branch_id': 3,
            'clown_branch_ids': [3],
            'status': 'failed',
            'updated_at': '2020-06-08T15:20:00+03:00',
        },
    ]
