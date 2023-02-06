import psycopg2
import pytest

from tests_subvention_schedule import utils


@pytest.mark.parametrize(
    'db, throws',
    [
        ('mask_overlap.json', True),
        ('mask_not_full_single.json', False),
        ('mask_not_continuous.json', True),
        ('mask_not_full.json', False),
        ('duplicates.json', True),
        ('overlap.json', True),
        ('overlap_activity.json', True),
        ('ok.json', False),
    ],
)
async def test_db(pgsql, load_json, db, throws):
    throwed = False

    try:
        utils.load_db(pgsql, load_json(db))
    except psycopg2.Error:
        throwed = True
        if throwed != throws:
            raise

    assert throwed == throws
