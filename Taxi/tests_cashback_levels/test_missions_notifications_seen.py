# pylint: disable=invalid-name
import pytest


async def post_missions_notifications_seen(
        taxi_cashback_levels, notification_ids,
):
    return await taxi_cashback_levels.post(
        '/4.0/cashback-levels/v1/missions/notifications/seen',
        headers={'X-Yandex-UID': '123'},
        json={'notification_ids': notification_ids},
    )


@pytest.mark.pgsql('cashback_levels', files=['mission_notifications_test.sql'])
async def test_mission_notifications_seen(taxi_cashback_levels, pgsql):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute('SELECT id FROM cashback_levels.missions_notifications')
    notification_ids = [item[0] for item in cursor]

    resp = await post_missions_notifications_seen(
        taxi_cashback_levels, notification_ids,
    )
    assert resp.status == 200

    cursor.execute(
        f"""
        SELECT id
        FROM cashback_levels.missions_notifications
        WHERE client_status != '{'seen'}';
        """,
    )
    assert not cursor.fetchone()
