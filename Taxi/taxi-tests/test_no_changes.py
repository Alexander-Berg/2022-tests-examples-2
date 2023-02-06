import glob
import os
import pytest


@pytest.mark.parametrize(
    'filename',
    glob.glob(
        os.path.join(
            os.path.dirname(__file__), 'static', 'no_changes', '*.py',
        ),
    ),
)
def test_static(black_format, filename):
    with open(filename, 'rb') as f:
        data = f.read()
    assert data.decode('utf-8') == black_format(data).decode('utf-8')
