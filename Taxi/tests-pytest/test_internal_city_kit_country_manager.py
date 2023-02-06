import pytest

from taxi.core import async
from taxi.internal.city_kit import country_manager


@pytest.mark.filldb
@pytest.inline_callbacks
def test_get_doc_by_zone_name():
    country = yield country_manager.get_doc_by_zone_name('moscow')
    assert country['_id'] == 'rus'

    country = yield country_manager.get_doc_by_zone_name('mytishchi')
    assert country['_id'] == 'rus'


@pytest.inline_callbacks
def test_get_countries(patch):
    @patch('taxi.external.territories.get_all_countries')
    @async.inline_callbacks
    def get_all_countries(*args, **kwargs):
        yield
        async.return_value([{'_id': 'expected'}])

    result = yield country_manager.get_countries()
    assert result == [{'_id': 'expected'}]
