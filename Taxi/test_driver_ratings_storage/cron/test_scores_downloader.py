# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import pytest

from driver_ratings_storage.generated.cron import run_cron


@pytest.mark.config(RATING_SCORES_DOWNLOADER_ENABLED=True)
async def test_simple_insert(pgsql, patch):
    @patch('yt.wrapper.list')
    def yt_list(path, *args, **kwargs):
        assert path.endswith('features/ratings/2.0')
        return ['2019-05-20']

    @patch('yt.wrapper.read_table')
    def yt_read_table(*args, **kwargs):
        return [
            {
                'driver_id': '5b1fd1415a72575a42dbe592',
                'fraud': False,
                'order_id': '55f4c46a61743a9da2d6d40220be161b',
                'ts': 1558945655.078,
                'rating': 2,
            },
            {
                'driver_id': '5b1fd1415a72575a42dbe593',
                'fraud': False,
                'order_id': '55f4c46a61743a9da2d6d40220be161c',
                'ts': 1558945658.078,
                'rating': 5,
            },
        ]

    @patch('yt.wrapper.YtClient.move')
    def yt_move_table(s_path, d_path):
        assert s_path + '_handled' == d_path

    await run_cron.main(
        ['driver_ratings_storage.crontasks.scores_downloader', '-t', '0'],
    )

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute(
        'SELECT * '
        'FROM driver_ratings_storage.scores '
        'WHERE '
        'driver_id=\'5b1fd1415a72575a42dbe592\' OR '
        'driver_id=\'5b1fd1415a72575a42dbe593\'',
    )

    num_rows = 0
    for row in cursor:
        if row[1] == '5b1fd1415a72575a42dbe592':
            assert row[0] == '55f4c46a61743a9da2d6d40220be161b'
            assert row[2] == 2
        else:
            assert row[0] == '55f4c46a61743a9da2d6d40220be161c'
            assert row[1] == '5b1fd1415a72575a42dbe593'
            assert row[2] == 5
        num_rows += 1

    assert num_rows == 2
    cursor.close()


@pytest.mark.config(RATING_SCORES_DOWNLOADER_ENABLED=True)
async def test_fraud_delete(pgsql, patch):
    @patch('yt.wrapper.list')
    def yt_list(path, *args, **kwargs):
        assert path.endswith('features/ratings/2.0')
        return ['2019-05-20']

    @patch('yt.wrapper.read_table')
    def yt_read_table(*args, **kwargs):
        return [
            {
                'driver_id': 'driver_1',
                'fraud': True,
                'order_id': 'order_10_1',
                'ts': 1558945655.078,
                'rating': 2,
            },
        ]

    @patch('yt.wrapper.YtClient.move')
    def yt_move_table(s_path, d_path):
        assert s_path + '_handled' == d_path

    await run_cron.main(
        ['driver_ratings_storage.crontasks.scores_downloader', '-t', '0'],
    )

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute(
        'SELECT * '
        'FROM driver_ratings_storage.scores '
        'WHERE order_id=\'order_10_1\'',
    )

    for _ in cursor:
        assert False
    cursor.close()
