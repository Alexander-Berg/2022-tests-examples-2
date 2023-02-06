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
@pytest.mark.filldb(event_stats='warn')
@pytest.inline_callbacks
def test_warn():
    result = yield _get_stats()
    assert result == '1; WARNING: card.UpdateBasket: 1/504'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='crit')
@pytest.inline_callbacks
def test_crit():
    result = yield _get_stats()
    assert result == '2; CRITICAL: card.CreateBasket: 6/12, card.UpdateBasket: 6/21'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='warn_and_crit')
@pytest.inline_callbacks
def test_warn_and_crit():
    result = yield _get_stats()
    assert result == '2; CRITICAL: card.UpdateBasket: 6/21; WARNING: card.CreateBasket: 1/201'


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.mark.filldb(event_stats='threshold')
@pytest.inline_callbacks
def test_threshold():
    result = yield _get_stats()
    assert result == '1; WARNING: card.CreateBasket: 1/201, card.UpdateBasket: 2/10'


@pytest.inline_callbacks
def _get_stats():
    result = yield main.run(
        ['billing_errors']
    )
    async.return_value(result)
