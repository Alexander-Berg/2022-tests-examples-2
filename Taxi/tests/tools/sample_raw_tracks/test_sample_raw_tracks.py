import subprocess


def test_sample_raw_tracks(yt_table_loader):
    test_table_path = yt_table_loader.upload_yql_table('raw_tracks')

    assert subprocess.call(['python',
                            '-m',
                            'metrics.tools.sample_raw_tracks',
                            '--sample-size',
                            '0.4',
                            test_table_path,
                            yt_table_loader.get_discard_table()]) == 0
