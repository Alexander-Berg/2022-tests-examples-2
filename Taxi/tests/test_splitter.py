from ..track._splitter import (TrackSplitter, PointTrackSplitter, PathDuration)
from ..track import Track


def do_test_launch_given_splitter(yt_table, splitter):
    result = []
    for row in yt_table.get():
        t = Track.load_yt(row['track_slice_yson'])
        result += list(splitter.split(t))

    assert result is not None
    assert len(result) > 0
    assert None not in result


def test_splitter_running(yt_input_table_tracks):
    '''
    Check that splitter can be launched. Do not check the validity of results
    '''

    base_settings = {
        'min_count': 1,
        'max_count': 5,
        'min_units': 30,
        'max_units': 60,
    }

    launch_settings = base_settings.copy()
    launch_settings['is_backward'] = False
    launch_settings['unit'] = PathDuration()
    do_test_launch_given_splitter(
        yt_input_table_tracks, TrackSplitter(
            **launch_settings))


def test_point_splitter_running(yt_input_table_tracks):
    '''
    Check that splitter can be launched. Do not check the validity of results
    '''

    base_settings = {
        'min_count': 1,
        'max_count': 5,
        'targets': [30],
        'density': (0, 1000)
    }

    for backward in [True, False]:
        for unit in ['duration', 'length']:
            launch_settings = base_settings.copy()
            launch_settings['is_backward'] = backward
            launch_settings['unit'] = unit
            do_test_launch_given_splitter(
                yt_input_table_tracks,
                PointTrackSplitter(
                    **launch_settings))
