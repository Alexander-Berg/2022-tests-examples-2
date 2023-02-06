import datetime

import pytest
import freezegun

import dateutil


@pytest.fixture(autouse=True)
def freeze(request):
    """
    Set current time to the one defined with 'now' marker or current time
    and freeze.
    """
    freeze_disable = list(request.node.iter_markers(name='dontfreeze'))
    if freeze_disable:
        yield None
        return

    def _timestr(now, offset):
        return now.strftime('%Y-%m-%dT%H:%M:%S') + '%+05d' % (offset * 100)

    now = getattr(request, 'param', None)
    if now is None:
        markers = list(request.node.iter_markers(name='now'))
        if markers:
            marker = markers[0]
            assert not marker.kwargs
            assert len(marker.args) == 1
            now = marker.args[0]

    if now is not None:
        now = dateutil.parser.parse(now)
        offset_seconds = now.tzinfo.utcoffset(now).seconds if now.tzinfo else 0
        offset = offset_seconds / 3600.0
    else:
        now = datetime.datetime.now()
        utcnow = datetime.datetime.utcnow()
        delta = now - utcnow
        offset = round((delta.seconds + delta.days * 86400) / 3600.0, 2)

    with freezegun.freeze_time(
            _timestr(now, offset),
            tz_offset=offset,
            ignore=[''],
            tick=bool(list(request.node.iter_markers(name='ticked_time'))),
    ) as frozen:
        yield frozen
