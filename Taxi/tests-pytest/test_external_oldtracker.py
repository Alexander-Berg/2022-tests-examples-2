import cStringIO
import datetime
import gzip

import pytest

from taxi.external import oldtracker


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'xml_report, tracks',
    [
        (
            'track.xml',
            [
                (
                    '1956789382',
                    '4977bb2d5967e51186a4001e671f718d',
                    36.0,
                    56.0,
                    151.0,
                    30.0,
                    datetime.datetime.utcfromtimestamp(1449591732)
                ),
            ]
        ),
    ]
)
@pytest.inline_callbacks
def test_parse_gzipped_xml(load, xml_report, tracks):
    track_raw = load(xml_report)
    out = cStringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(track_raw)

    result = yield oldtracker._parse_gzipped_xml_with_tracks(out.getvalue())

    assert result == tracks
