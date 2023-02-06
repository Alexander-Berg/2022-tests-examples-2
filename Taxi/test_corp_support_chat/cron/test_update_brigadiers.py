# pylint: disable=redefined-outer-name
import pytest

from corp_support_chat.generated.cron import run_cron


@pytest.mark.pgsql('corp_support_chat', files=('support_chat_brigadier.sql',))
@pytest.mark.yt(dyn_table_data=['yt_user.yaml'])
@pytest.mark.usefixtures('yt_apply')
async def test_update_brigadiers(pgsql, mock_sf_data_load, cron_context):
    cursor = pgsql['corp_support_chat'].cursor()
    query = """
        SELECT * FROM corp_support_chat.brigadiers
    """
    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [('1', 'login_1'), ('2', 'login_2'), ('3', 'login_3')]

    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103
    users_path = '//home/taxi-dwh/ods/salesforce_b2b/user/user'

    await yt.unmount_table(users_path, sync=True)
    await yt.mount_table(users_path, sync=True)

    await run_cron.main(
        ['corp_support_chat.crontasks.update_brigadier', '-t', '0'],
    )

    query = """
            SELECT * FROM corp_support_chat.brigadiers
        """
    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [('1', 'login_1'), ('2', 'new_login_2'), ('4', 'login_4')]
