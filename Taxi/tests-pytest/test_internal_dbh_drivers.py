import pytest

from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('state,active', [
    ('active', True),
    ('importing', True),
    ('nopermit', False),
    ('unknown', False),
])
def test_no_permit(state, active):
    cls = dbh.drivers.Doc
    assert cls({cls.import_state: state}).active is active
