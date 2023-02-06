import subprocess


def test_raw_tracks_context_slice(yt_table_loader):
    raw_table_path = yt_table_loader.upload_yql_table('raw_tracks')
    sample_table_path = yt_table_loader.upload_yql_table('sampled_points')

    assert subprocess.call(['python',
                            '-m',
                            'metrics.tools.raw_tracks_context_slice',
                            '--forward', '5',
                            '--backward', '7',
                            raw_table_path,
                            sample_table_path,
                            yt_table_loader.get_discard_table()]) == 0
