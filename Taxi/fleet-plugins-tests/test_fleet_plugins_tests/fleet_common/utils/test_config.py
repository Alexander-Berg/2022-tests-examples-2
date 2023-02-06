import pytest

from fleet_plugins_tests.generated.web.fleet_common.utils import config

DEFAULT_CONFIG = {
    'cities': [],
    'countries': [],
    'dbs': [],
    'dbs_disable': [],
    'enable': False,
    'enable_support': False,
    'enable_support_users': [],
}


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_enable(fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    assert not config.is_allowed(test_config, fleet_user)

    test_config['enable'] = True
    assert config.is_allowed(test_config, fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_cities(fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    test_config['enable'] = True

    test_config['cities'].append('Набережные Челны')
    assert not config.is_allowed(test_config, fleet_user)

    test_config['cities'].append('Москва')
    assert config.is_allowed(test_config, fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_countries(fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    test_config['enable'] = True

    test_config['countries'].append('asd')
    assert not config.is_allowed(test_config, fleet_user)

    test_config['countries'].append('rus')
    assert config.is_allowed(test_config, fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_parks(fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    test_config['enable'] = True

    test_config['dbs'].append('8adbd417a90f48f09597981cd13ac043')
    assert not config.is_allowed(test_config, fleet_user)

    test_config['dbs'].append('7ad36bc7560449998acbe2c57a75c293')
    assert config.is_allowed(test_config, fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_parks_disabled(fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    test_config['enable'] = True

    assert config.is_allowed(test_config, fleet_user)

    test_config['dbs_disable'].append('7ad36bc7560449998acbe2c57a75c293')
    assert not config.is_allowed(test_config, fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_support_enable(support_fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    assert not config.is_allowed(test_config, support_fleet_user)

    test_config['enable_support'] = True
    assert config.is_allowed(test_config, support_fleet_user)


@pytest.mark.config(test_config=DEFAULT_CONFIG)
async def test_support_users(support_fleet_user, taxi_config):
    test_config = taxi_config.get('test_config')

    assert not config.is_allowed(test_config, support_fleet_user)

    test_config['enable_support'] = True
    test_config['enable_support_users'].append('vasya')
    assert config.is_allowed(test_config, support_fleet_user)
