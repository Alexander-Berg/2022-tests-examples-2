# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.pgsql('corp_support_chat', files=('support_chat_pause.sql',))
async def test_chat_change_status(pgsql, taxi_corp_support_chat_web):
    cursor = pgsql['corp_support_chat'].cursor()

    body = {'sf_id': '2', 'status': 'Closed'}

    resp = await taxi_corp_support_chat_web.post(
        '/v1/chats/change_status/', json=body,
    )
    assert resp.status == 200

    body = {'sf_id': '3', 'status': 'OnHold'}
    resp = await taxi_corp_support_chat_web.post(
        '/v1/chats/change_status/', json=body,
    )

    assert resp.status == 200

    body = {'sf_id': '7', 'status': 'New'}
    resp = await taxi_corp_support_chat_web.post(
        '/v1/chats/change_status/', json=body,
    )

    assert resp.status == 200

    query = """
            SELECT
                sf_id,
                status
            FROM corp_support_chat.request
            ORDER BY sf_id;
        """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        ('1', 'close'),
        ('2', 'close'),
        ('3', 'pause'),
        ('4', 'open'),
        ('5', 'pause'),
        ('6', 'close'),
        ('7', 'open'),
    ]
