import pytest

from sandbox.projects.tank.Firestarter.status import FirestarterError
from sandbox.projects.tank.Firestarter.define_hosts import DefineHosts


parsing_result = {
    'target': {
        'value': 'Berlin',
        'port': 905,
    },
    'tank': {
        'value': 'T-34',
        'port': 2206,
    },
    'operator': 'zhukov',
    'task': 'BOB-4145',
    'dc': 'MSK',
}
DF = DefineHosts(parsing_result)


class TestDefineHosts:

    @pytest.mark.parametrize(
        'target, error_msg',
        [
            (
                'nanny:odessa_mama',
                'RTC service nanny:odessa_mama has no instances'
            ),
            (
                'deploy:saint.petersburg',
                'Deploy stage deploy:saint.petersburg has no instances'
            ),
            (
                'sandbox:minsk',
                'The sandbox task is not sufficiently specified in the value sandbox:minsk'
            ),
            (
                'sandbox:brest.skaya.krepost',
                'Sandbox task brest has no host in output parameters',
            ),
            (
                'kiev',
                'No one host is found for target kiev'
            ),
        ],
    )
    def test_get_target_raise_error(self, mocker, target, error_msg):
        with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.call_tank_finder_nanny', return_value=[]):
            with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.call_tank_finder_deploy', return_value=[]):
                with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.get_sandbox_output', return_value=[]):
                    with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.DefineHosts._preliminary_tank_dc_', return_value=''):
                        with pytest.raises(FirestarterError) as fe:
                            DF.parsing_result.update({'target': {'value': target, 'port': 777}})
                            DF.get_target()
        assert fe.type is FirestarterError
        assert fe.value.section == 'get_target'
        assert fe.value.error == error_msg
 
    class NotEqual:
        def __eq__(self, other):
            return False

    @pytest.mark.parametrize(
        'dc, error_msg',
        [
            (
                None,
                'Impossible to determine the datacenter for the tank armata.tanks.yandex.net'
            ),
            (
                NotEqual(),
                'Tank and target are not in the same DC'
            ),
        ],
    )
    def test_get_tank_no_tank_dc(self, mocker, dc, error_msg):
        with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.define_host_dc', return_value=dc):
            DF.parsing_result.update({'tank': {'value': 'armata.tanks.yandex.net', 'port': 8083}})
            with pytest.raises(FirestarterError) as fe:
                DF.get_tanks('test')
        assert fe.type is FirestarterError
        assert fe.value.section == 'get_tanks'
        assert fe.value.error == error_msg

    @pytest.mark.parametrize(
        'tank, target, error_msg',
        [
            (
                'common',
                'in_config',
                'Shooting with custom generators from public tanks is not allowed'
            ),
            (
                'nanny:production_yandex_tank',
                'in_config',
                'Shooting with custom generators from public tanks is not allowed'
            ),
            (
                'common',
                'nanny:orehovo_zuevo',
                'Crossdc shooting from public tanks is not allowed'
            ),
            (
                'nanny:production_yandex_tank',
                'deploy:min.vody',
                'Crossdc shooting from public tanks is not allowed'
            ),
        ],
    )
    def test_get_tanks_denied_for_common_tanks(self, mocker, tank, target, error_msg):
        DF.parsing_result.update({'tank': {'value': tank, 'port': 8083}})
        with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.define_host_dc', return_value=None):
            with pytest.raises(FirestarterError) as fe:
                DF.get_tanks(target)
        assert fe.type is FirestarterError
        assert fe.value.section == 'get_tanks'
        assert fe.value.error == error_msg

    @pytest.mark.parametrize('tank', ['deploy:gus.khrystalny', 'nanny:rostov_na_dony'])
    def test_get_tanks_no_tank_found(self, mocker, tank):
        with mocker.patch('sandbox.projects.tank.Firestarter.define_hosts.call_tank_finder', return_value=[]):
            DF.parsing_result.update({'tank': {'value': tank, 'port': 8083}})
            with pytest.raises(FirestarterError) as fe:
                DF.get_tanks('test')
        assert fe.type is FirestarterError
        assert fe.value.section == 'get_tanks'
        assert fe.value.error == 'No tank was found for the target test'
