from passport.backend.library.configurator import Configurator
import pytest
import yatest.common as yc


def test_configurator():
    test_config_path = yc.source_path() + '/passport/backend/library/configurator/tests/test_config.yaml'

    c = Configurator(
        name='test',
        configs=[
            {'template_variable': 3},
            test_config_path,
        ],
    )
    assert c['a'] == {
        'b': 1,
        'c': 2,
        'd': 3,
    }
    assert c['template_variable'] == 3
    assert not c.has_missed_configs()


def test_non_extistent_config():
    non_existent_test_config_path = yc.source_path() + '/passport/backend/library/configurator/tests/kek.yaml'
    with pytest.raises(IOError):
        Configurator(
            name='test',
            configs=[
                {'template_variable': 3},
                non_existent_test_config_path,
            ],
        )


def test_optional():
    optional_test_config_path = yc.source_path() + '/passport/backend/library/configurator/tests/kek.yaml?'
    c = Configurator(
        name='test',
        configs=[
            {'template_variable': 3},
            optional_test_config_path,
        ],
    )
    assert c == {'template_variable': 3}
    assert c.has_missed_configs()
