import pytest

from testsuite.utils import http

from driver_ratings_storage.generated.cron import run_cron


async def test_empty(pgsql, mock_unique_drivers):
    req_num = [0]

    @mock_unique_drivers('/v1/driver/new')
    async def _v1_driver_new(request: http.Request):
        if req_num == [0]:
            assert request.query.get('last_known_revision') is None
            req_num[0] += 1
            return {
                'last_revision': 'rev0',
                'drivers': [
                    {'id': 'did0', 'source': 'hell'},
                    {'id': 'did1', 'source': 'hell'},
                ],
            }

        if req_num == [1]:
            assert request.query.get('last_known_revision') == 'rev0'
            req_num[0] += 1
            return {
                'last_revision': 'rev1',
                'drivers': [
                    {'id': 'did2', 'source': 'hell'},
                    {'id': 'did3', 'source': 'hell'},
                ],
            }
        if req_num == [2]:
            assert request.query.get('last_known_revision') == 'rev1'
            req_num[0] += 1
            return {'last_revision': 'rev1', 'drivers': []}
        assert False, 'Must not request if empty drivers'

    await run_cron.main(
        ['driver_ratings_storage.crontasks.drivers_loader', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute('select driver_id from driver_ratings_storage.drivers;')
        rows = [x[0] for x in cursor]

    assert rows == ['driver_1', 'driver_2', 'did0', 'did1', 'did2', 'did3']

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute('select name, details from common.events;')
        rows = list(cursor)

    assert rows == [('drivers_loader', {'revision': 'rev1'})]


@pytest.mark.pgsql(
    'driver_ratings_storage',
    queries=[
        """
INSERT INTO common.events(task_id, name, details)
VALUES ('id1', 'drivers_loader', '{"revision":"rev1"}')
""",
    ],
)
async def test_revision(pgsql, mock_unique_drivers):
    is_called = [False]

    @mock_unique_drivers('/v1/driver/new')
    async def _v1_driver_new(request: http.Request):
        assert request.query.get('last_known_revision') == 'rev1'
        is_called[0] = True
        return {'last_revision': 'rev0', 'drivers': []}

    await run_cron.main(
        ['driver_ratings_storage.crontasks.drivers_loader', '-t', '0'],
    )

    assert is_called == [True], 'Must request new drivers once'
