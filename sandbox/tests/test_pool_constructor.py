import pytest

from sandbox.projects.autocheck.lib import pool_constructor as pc


@pytest.mark.parametrize('params, expected', [
    ([None, None, None, False, False], None),
    (['not-exists', None, None, False, False], None),
    (['not-exists', None, 'not/matter', False, False], None),
    (['distbuild-vla', None, None, False, False], '//vla/autocheck/postcommits/public'),
    (['distbuild-vla', None, None, True, False], '//vla/autocheck/precommits/public'),
    (['distbuild-vla', None, None, False, True], '//test_vla/autocheck/postcommits/public'),
    (['distbuild-vla', None, 'my/pool', False, False], '//vla/my/pool'),
    ([None, '//vla', 'my/pool', False, False], '//vla/my/pool'),
    (['distbuild-vla', '//man', 'my/pool', False, False], '//man/my/pool'),
])
def test_construct_pool_name(params, expected):
    assert pc.construct_pool_name(*params) == expected


@pytest.mark.parametrize('params, expected', [
    ([None, None, None, False], '//sas/autocheck/gg/postcommits/public'),
    ([None, None, None, True], '//sas_gg/autocheck/gg/precommits/public'),
    (['not-exists', None, None, False], '//sas/autocheck/gg/postcommits/public'),
    (['distbuild-sas-01', None, None, False], '//sas_gg/autocheck/gg/precommits/public'),
    (['distbuild-sas-00', None, None, True], '//sas/autocheck/gg/postcommits/public'),
    (['distbuild-sas-01', None, 'my/pool', True], '//sas_gg/my/pool'),
    ([None, '//sas_gg', None, True], '//sas_gg/autocheck/gg/precommits/public'),
    ([None, '//sas', None, False], '//sas/autocheck/gg/postcommits/public'),
    ([None, '//sas_gg', 'my/pool', False], '//sas_gg/my/pool'),
    (['distbuild-sas-00', '//sas_gg', 'my/pool', False], '//sas_gg/my/pool'),
])
def test_construct_gg_pool_name(params, expected):
    assert pc.construct_gg_pool_name(*params) == expected
