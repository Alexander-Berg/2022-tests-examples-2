import pytest


@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_status.sql'])
async def test_dbfunc(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SELECT *'
        ' FROM callcenter_stats.operator_united_status(now())'
        ' ORDER BY agent_id, queue'
    )

    # agent_id                VARCHAR,
    # queue                   VARCHAR,
    # status                  VARCHAR,
    # substatus               VARCHAR

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    assert result == [
        ('agent03', 'queue1_on_1', 'connected', 'talking'),
        ('agent03', 'queue2_on_1', 'connected', 'busy'),
        ('agent04', 'queue1_on_1', 'connected', 'busy'),
        ('agent04', 'queue2_on_1', 'connected', 'talking'),
        ('agent05', 'queue1_on_1', 'connected', 'postcall'),
        ('agent06', 'queue2_on_1', 'connected', 'busy'),
        ('agent07', 'queue2_on_1', 'connected', 'waiting'),
        ('agent08', 'queue2_on_1', 'paused', None),
        ('agent09', 'queue2_on_1', 'connected', 'waiting'),
        ('agent10', 'queue3_on_1', 'paused', None),
        ('agent11', 'queue3_on_1', 'paused', 'p1'),
        ('agent12', 'queue3_on_1', 'paused', 'p2'),
        ('agent13', 'queue3_on_1', 'paused', 'p2'),
        ('agent14', 'queue3_on_1', 'paused', 'break'),
        ('agent15', 'queue1_on_1', 'connected', 'waiting'),
        ('agent21', 'queue4_on_1', 'connected', 'waiting'),
        ('agent22', 'queue4_on_1', 'connected', 'postcall'),
        ('agent23', 'queue4_on_1', 'connected', 'postcall'),
        ('agent24', 'queue4_on_1', 'connected', 'postcall'),
        ('agent25', 'queue4_on_1', 'connected', 'waiting'),
    ]
