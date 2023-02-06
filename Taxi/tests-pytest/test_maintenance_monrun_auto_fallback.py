import pytest

from taxi.core import async
from taxi_maintenance.monrun import main


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='ok')
@pytest.inline_callbacks
def test_ok():
    result = yield _get_stats()
    assert result == '0; OK'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='warning')
@pytest.inline_callbacks
def test_warning():
    result = yield _get_stats()
    assert result ==\
        '1; cnt_warn=1, card.UpdateBasket: 11/61'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='critical')
@pytest.inline_callbacks
def test_critical():
    result = yield _get_stats()
    assert result ==\
        '2; cnt_crit=1, card.UpdateBasket: 13/21'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='ok', order_proc='critical')
@pytest.inline_callbacks
def test_critical2():
    result = yield _get_stats()
    assert result ==\
        '2; cnt_crit=1, order: 1/1'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='warning_and_critical')
@pytest.inline_callbacks
def test_warning_and_critical():
    result = yield _get_stats()
    assert result == '2; cnt_crit=1, card.UpdateBasket: 13/21'


@pytest.inline_callbacks
def _get_stats():
    result = yield main.run(
        'auto_fallback --warn-level 0 --crit-level 0.25'.split(' ')
    )
    async.return_value(result)
