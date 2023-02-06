import pytest


async def get_notifications(web_context, mass_id):
    async with web_context.pg.slave_pool.acquire() as conn:
        query = (
            """SELECT * FROM agent.notifications
            WHERE mass_id=\'{}\'""".format(
                mass_id,
            )
        )
        return await conn.fetch(query)


@pytest.mark.parametrize(
    'login,status,count_before,count_after',
    [('webalex', 201, 2, 0), ('liambaev', 403, 2, 2)],
)
async def test_communications_admin_delete(
        web_context, web_app_client, login, status, count_before, count_after,
):

    notifications_before = await get_notifications(
        web_context=web_context, mass_id='faadb32303664af38b75ff2653e1bb43',
    )
    assert len(notifications_before) == count_before

    response = await web_app_client.post(
        '/v1/admin/communications/delete',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-ru'},
        json={'id': 'faadb32303664af38b75ff2653e1bb43'},
    )
    assert response.status == status

    notifications_after = await get_notifications(
        web_context=web_context, mass_id='faadb32303664af38b75ff2653e1bb43',
    )
    assert len(notifications_after) == count_after
