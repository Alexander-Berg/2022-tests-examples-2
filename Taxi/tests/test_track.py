from pytest import approx
from ..track import Track


def test_track_properties(yt_input_table_tracks):
    for row in yt_input_table_tracks.get():
        t = Track.load_yt(row['track_slice_yson'])
        assert t is not None, '''Can't load track'''
