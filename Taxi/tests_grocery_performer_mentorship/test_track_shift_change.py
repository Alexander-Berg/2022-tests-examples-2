import pytest

SQL_CHANGES = (
    'SELECT status, changes_counter '
    'FROM grocery_performer_mentorship.mentorship'
    ' WHERE mentor_shift_id = \'100\''
)
SQL_STATUS = (
    'SELECT performer_id, status FROM grocery_performer_mentorship.shifts'
    ' WHERE shift_id = \'100\''
)


def connect(pgsql):
    db = pgsql['grocery_performer_mentorship']
    cursor = db.cursor()

    class Context:
        @staticmethod
        def retrieve(sql):
            cursor.execute(sql)
            return [[item[0], item[1]] for item in cursor.fetchall()][0]

        @staticmethod
        def execute(sql):
            return cursor.execute(sql)

    return Context


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_paris(pgsql):
    db = connect(pgsql)
    assert db.retrieve(SQL_STATUS) == ['123_001', 'waiting']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 0]
    db.execute(
        'UPDATE grocery_performer_mentorship.shifts '
        'SET status = \'closed\' WHERE shift_id = \'100\'',
    )
    assert db.retrieve(SQL_STATUS) == ['123_001', 'closed']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 1]


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_paris_cancel(pgsql):
    db = connect(pgsql)
    assert db.retrieve(SQL_STATUS) == ['123_001', 'waiting']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 0]
    db.execute(
        'UPDATE grocery_performer_mentorship.shifts '
        'SET performer_id = NULL, status = \'request\' '
        'WHERE shift_id = \'100\'',
    )
    assert db.retrieve(SQL_STATUS) == [None, 'request']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 1]


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_paris_cancel_by_closed(pgsql):
    db = connect(pgsql)
    assert db.retrieve(SQL_STATUS) == ['123_001', 'waiting']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 0]
    db.execute(
        'UPDATE grocery_performer_mentorship.shifts '
        'SET performer_id = NULL, status = \'closed\', '
        '    started_at = NULL, closes_at = NULL '
        'WHERE shift_id = \'100\'',
    )
    assert db.retrieve(SQL_STATUS) == [None, 'closed']
    assert db.retrieve(SQL_CHANGES) == ['assigned', 1]
