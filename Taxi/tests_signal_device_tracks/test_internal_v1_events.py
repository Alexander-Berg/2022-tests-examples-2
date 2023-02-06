import pytest


ENDPOINT = 'internal/signal-device-tracks/v1/events'


def _count_tracks(pgsql):
    db = pgsql['signal_device_tracks'].cursor()
    query_str = 'SELECT COUNT(TRUE) FROM signal_device_tracks.events'
    db.execute(query_str)
    return list(db)[0][0]


@pytest.mark.pgsql(
    'signal_device_tracks', files=['signal_device_tracks_db.sql'],
)
@pytest.mark.parametrize(
    'events, left_tracks_amount',
    [pytest.param(['xxx', 'zzz'], 1, id='test_one')],
)
async def test_ok(
        taxi_signal_device_tracks, pgsql, events, left_tracks_amount,
):
    response = await taxi_signal_device_tracks.delete(
        ENDPOINT, json={'public_event_ids': events},
    )

    assert response.status == 200, response.text

    assert _count_tracks(pgsql) == left_tracks_amount
