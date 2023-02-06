async def count_couriers(context) -> int:
    async with context.pg.master_pool.acquire() as connection:
        return await connection.fetchval('SELECT count(*) FROM couriers')


async def courier_info(context, courier_id: int) -> dict:
    async with context.pg.master_pool.acquire() as connection:
        row = await connection.fetchrow(
            'SELECT * FROM couriers WHERE courier_id = $1', courier_id,
        )
    return dict(row) if row else {}


async def test_service_update_invited_courier_post(
        web_app_client, web_context,
):
    old_courier_id = 2
    new_courier_id = 101
    old_courier_info = await courier_info(web_context, old_courier_id)

    response = await web_app_client.post(
        '/service/update-invited-courier',
        json={
            'old_courier_id': old_courier_id,
            'new_courier_id': new_courier_id,
        },
    )
    assert response.status == 200

    new_courier_info = await courier_info(web_context, new_courier_id)
    assert (
        old_courier_info['invite_promocode']
        == new_courier_info['invite_promocode']
    )
    assert new_courier_info['history_courier_id'] == old_courier_id
    assert new_courier_info['park_id'] is None
    assert new_courier_info['driver_id'] is None


async def test_not_found(web_app_client, web_context):
    old_courier_id = 100
    new_courier_id = 101
    start_count = await count_couriers(web_context)

    response = await web_app_client.post(
        '/service/update-invited-courier',
        json={
            'old_courier_id': old_courier_id,
            'new_courier_id': new_courier_id,
        },
    )
    assert response.status == 400

    finish_count = await count_couriers(web_context)
    assert finish_count == start_count
