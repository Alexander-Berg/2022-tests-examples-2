# pylint: disable=protected-access
import pytest

from replication.utils import attr_kit


@pytest.mark.parametrize(
    'current_env, env_user_dict',
    [
        ('production', {'production': True}),
        ('production', {'production': True, 'testing': False}),
        ('testing', {'production': False, 'testing': True}),
        ('testing', {'production': False, 'testing': True}),
        (
            'testing',
            {
                'production': False,
                'testing': True,
                'unittests': False,
                'development': False,
            },
        ),
        ('unittests', {'production': False, 'testing': True}),
        ('unittests', {'production': True}),
        ('unittests', {'production': False, 'unittests': True}),
        (
            'unittests',
            {'production': True, 'testing': False, 'unittests': True},
        ),
    ],
)
@pytest.mark.nofilldb
def test_get_suitable_env(monkeypatch, current_env, env_user_dict):
    suitable_env = attr_kit._get_suitable_env(
        attr_kit.REQUIRED_ENVIRONMENTS, current_env, env_user_dict,
    )

    monkeypatch.setattr(attr_kit.settings, 'ENVIRONMENT', current_env)
    applied_value = attr_kit.apply_environment_converter(env_user_dict)
    assert applied_value is True

    assert env_user_dict[suitable_env] is applied_value
