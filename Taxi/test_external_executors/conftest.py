import tempfile

import pytest


@pytest.fixture(name='tmp_dir')
def _tmp_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as working_area:
        monkeypatch.setattr(
            'taxi.scripts.settings.WORKING_AREA_DIR', working_area,
        )
        yield working_area
