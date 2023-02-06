from psycopg2 import extras
import pytest

# root conftest for service eats-pics
pytest_plugins = ['eats_pics_plugins.pytest_plugins']


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_pics'].cursor(cursor_factory=extras.RealDictCursor)


@pytest.fixture(name='component_config')
def _component_config(testsuite_build_dir, load_yaml):
    class ComponentConfig:
        @staticmethod
        def get(section_name, var_name):
            config_path = testsuite_build_dir.joinpath('configs/service.yaml')
            config = load_yaml(config_path)
            config_vars = load_yaml(config['config_vars'])
            config_var_name = config['components_manager']['components'][
                section_name
            ][var_name]

            return config_vars[config_var_name[1:]]

    return ComponentConfig()


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_pics, taxi_eats_pics_monitor, testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_pics.run_distlock_task
            if is_distlock
            else taxi_eats_pics.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_pics-') :]
        )

        should_fail = False

        @testpoint(f'eats-pics_{periodic_short_name}::fail')
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(f'eats-pics_periodic-data::use-current-epoch')
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_pics.tests_control(reset_metrics=True)

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = await taxi_eats_pics_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 1
        assert data['oks'] == 1
        assert data['fails'] == 0
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

        should_fail = True
        try:
            await periodic_runner(periodic_name)
        except taxi_eats_pics.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = await taxi_eats_pics_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify
