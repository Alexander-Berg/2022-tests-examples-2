import subprocess


def test_generate_raw_tracks(yt_table_loader):
    test_table_path = yt_table_loader.upload_yql_table('raw_points')

    assert subprocess.call(['python',
                            '-m',
                            'metrics.tools.generate_raw_tracks',
                            test_table_path,
                            yt_table_loader.get_discard_table()]) == 0
