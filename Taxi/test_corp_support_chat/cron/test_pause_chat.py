# pylint: disable=redefined-outer-name
import pytest

from corp_support_chat.generated.cron import run_cron


@pytest.mark.pgsql('corp_support_chat', files=('support_chat_pause.sql',))
@pytest.mark.now('2022-6-28 00:00:00')
async def test_pause_chat(pgsql, mock_sf_data_load):
    cursor = pgsql['corp_support_chat'].cursor()
    query = """
        SELECT sf_id FROM corp_support_chat.request WHERE status = 'pause'
    """
    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [('5',), ('7',)]
    await run_cron.main(['corp_support_chat.crontasks.pause_chat', '-t', '0'])

    query = """
            SELECT sf_id FROM corp_support_chat.request WHERE status = 'pause'
        """
    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [('5',), ('7',), ('2',), ('4',)]
