import pytest


@pytest.fixture
def monkeypatch_make_link(patch):
    @patch('taxi.logs.auto_log_extra._make_link')
    def _make_link():
        return 'monkeypatched_link'
