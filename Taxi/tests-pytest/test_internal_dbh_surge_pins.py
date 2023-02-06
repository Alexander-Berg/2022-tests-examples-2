from __future__ import unicode_literals

import pytest

from taxi.internal import dbh


@pytest.inline_callbacks
def test_count_in_rectangle():
    tl = [37.62, 55.78]
    br = [37.65, 55.74]
    count = yield dbh.surge_pins.Doc.count_in_rectangle(tl, br)
    assert count == 3
