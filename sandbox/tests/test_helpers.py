from hamcrest import assert_that, calling, raises
from sandbox.projects.market.idx.MarketRunUniversalBundle import helpers

import mock


def test_calc_alert_status():
    assert helpers.calc_alert_status('CRIT') == 'CRIT'
    assert helpers.calc_alert_status('CRIT', 'OK') == 'WARN'
    assert helpers.calc_alert_status('CRIT', 'WARN') == 'CRIT'
    assert helpers.calc_alert_status('OK', 'CRIT') == 'OK'


def test_uses_by_last_released_task():
    resource_id = 2841953774
    resource_type = 'MARKET_IDX_UNIVERSAL_BUNDLE'
    release_status = 'stable'
    with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.resource_selectors.by_last_released_task', return_value=[resource_id, 200]) as by_last_released_task:
        with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.sdk2', autospec=True) as sdk2:
            sdk2.Resource = {resource_id : 'resource'}
            get_last_released_resource_result = helpers.get_last_released_resource(resource_type, release_status)
            by_last_released_task.assert_called_once_with(attrs=None, resource_type=resource_type , stage=release_status)
            assert get_last_released_resource_result == 'resource'


def test_fallback_to_simple_resource_selector():
    resource_type = 'MARKET_IDX_UNIVERSAL_BUNDLE'
    release_status = 'stable'
    with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.resource_selectors.by_last_released_task', return_value=[None, None]):
        with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.sdk2', autospec=True) as sdk2:
            sdk2.Resource.find.return_value.order.return_value.first.return_value = 'resource'
            get_last_released_resource_result = helpers.get_last_released_resource(resource_type, release_status)
            helpers.sdk2.Resource.find.assert_called_once_with(type=resource_type, state='READY', attrs={'released': 'stable'})
            helpers.sdk2.Resource.find.return_value.order.assert_called_once_with(-helpers.sdk2.Resource.id)
            assert get_last_released_resource_result == 'resource'


def test_not_existing_resource():
    resource_type = 'MARKET_IDX_UNIVERSAL_BUNDLE'
    release_status = 'stable'
    with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.resource_selectors.by_last_released_task', return_value=[None, None]):
        with mock.patch('sandbox.projects.market.idx.MarketRunUniversalBundle.helpers.sdk2', autospec=True) as sdk2:
            sdk2.Resource.find.return_value.order.return_value.first.return_value = None
            assert_that(calling(helpers.get_last_released_resource).with_args(resource_type, release_status), raises(Exception))
