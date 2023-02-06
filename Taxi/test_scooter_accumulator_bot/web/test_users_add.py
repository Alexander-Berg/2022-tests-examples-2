from test_scooter_accumulator_bot import utils


ENDPOINT = '/scooter-accumulator-bot/v1/users/add'


async def test_ok(
        taxi_scooter_accumulator_bot_web,
        scooter_accumulator_bot_personal_mocks,
        web_context,
):
    responses = [
        await taxi_scooter_accumulator_bot_web.post(
            ENDPOINT,
            json={
                'users': [
                    {
                        'id': 4535345,
                        'username': 'micky',
                        'role': 'storekeeper',
                        'region': 'moscow',
                    },
                ],
            },
        )
        for _ in range(2)
    ]

    assert [resp.status for resp in responses] == [200, 200]
    assert [await resp.json() for resp in responses] == [
        {
            'users': [
                {
                    'id': 4535345,
                    'role': 'storekeeper',
                    'username': 'micky',
                    'region': 'moscow',
                },
            ],
        },
        {
            'users': [
                {
                    'id': 4535345,
                    'role': 'storekeeper',
                    'username': 'micky',
                    'region': 'moscow',
                },
            ],
        },
    ]

    created_user = await utils.get_user(web_context.pg, 'pd_id_4535345')
    assert created_user is not None
    assert created_user['role'] == 'STOREKEEPER'
    assert created_user['region'] == 'moscow'

    assert (
        scooter_accumulator_bot_personal_mocks[
            '/v1/telegram_logins/bulk_store'
        ].times_called
        == 2
    )
    assert (
        scooter_accumulator_bot_personal_mocks[
            '/v1/telegram_ids/bulk_store'
        ].times_called
        == 2
    )
