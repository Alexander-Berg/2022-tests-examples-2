import pytest


@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_status.sql'])
async def test_dbfunc(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SELECT *'
        ' FROM callcenter_stats.user_unified_status(now(), \'_on_\')'
        ' ORDER BY sip_username, metaqueue, subcluster'
    )

    # sip_username            VARCHAR,
    # metaqueue               VARCHAR,
    # subcluster              VARCHAR,
    # status                  VARCHAR,
    # substatus               VARCHAR

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    print(result)
    assert result == [
        ('agent03', 'queue1', '1', 'connected', 'talking', '_on_'),
        ('agent03', 'queue2', '1', 'connected', 'busy', '_on_'),
        ('agent04', 'queue1', '1', 'connected', 'busy', '_on_'),
        ('agent04', 'queue2', '1', 'connected', 'talking', '_on_'),
        ('agent05', 'queue1', '1', 'connected', 'postcall', '_on_'),
        ('agent06', 'queue2', '1', 'connected', 'busy', '_on_'),
        ('agent07', 'queue2', '1', 'connected', 'waiting', '_on_'),
        ('agent08', 'queue2', '1', 'paused', None, '_on_'),
        ('agent09', 'queue2', '1', 'connected', 'waiting', '_on_'),
        ('agent10', 'queue3', '1', 'paused', None, '_on_'),
        ('agent11', 'queue3', '1', 'paused', 'p1', '_on_'),
        ('agent12', 'queue3', '1', 'paused', 'p2', '_on_'),
        ('agent13', 'queue3', '1', 'paused', 'p2', '_on_'),
        ('agent14', 'queue3', '1', 'paused', 'break', '_on_'),
        ('agent15', 'queue1', '1', 'connected', 'waiting', '_on_'),
        ('agent21', 'queue4', '1', 'connected', 'waiting', '_on_'),
        ('agent22', 'queue4', '1', 'connected', 'postcall', '_on_'),
        ('agent23', 'queue4', '1', 'connected', 'postcall', '_on_'),
        ('agent24', 'queue4', '1', 'connected', 'postcall', '_on_'),
        ('agent25', 'queue4', '1', 'connected', 'waiting', '_on_'),
    ]
