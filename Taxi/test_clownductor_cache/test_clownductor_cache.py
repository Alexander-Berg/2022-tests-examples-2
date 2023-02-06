import os

import pytest

from clownductor_cache import components as components_module
from clownductor_cache import tree as tree_module
from clownductor_cache.generated.context import context as context_module
import test_clownductor_cache


MOCKS = ['clown_cache_mocks']

TAXI_NAMESPACE = tree_module.Namespace(id_=1, name='taxi')
TAXI_SUPPORT_PROJECT = tree_module.Project(
    id_=39,
    name='taxi-support',
    namespace_id=1,
    owners=({'groups': ['grp-1'], 'logins': ['admin-1']}),
)
COMPENDIUM_NANNY_SERVICE = tree_module.Service(
    id_=355298,
    name='compendium',
    project_id=39,
    cluster_type='nanny',
    abc_slug='taxicompendium',
)
COMPENDIUM_NANNY_STABLE = tree_module.Branch(
    env='stable',
    id_=296533,
    name='stable',
    service_id=355298,
    direct_link='taxi_compendium_stable',
    podset_id='taxi-compendium-stable',
)


@pytest.fixture(name='load_from_file_cache')
def _load_from_file_cache(monkeypatch):
    def _empty(*args):
        pass

    def _wrapper(folder_name):
        monkeypatch.setattr(
            components_module,
            'CACHE_PATH',
            os.path.join(
                os.path.dirname(test_clownductor_cache.__file__),
                'static',
                'default',
                folder_name,
            ),
        )
        monkeypatch.setattr(
            components_module.ClownductorCacheComponent,
            '_save_to_file',
            _empty,
        )

    return _wrapper


@pytest.fixture(name='load_from_file_good_cache')
def _load_from_file_good_cache(load_from_file_cache):
    return load_from_file_cache('good_cache')


@pytest.fixture(name='load_from_file_bad_cache')
def _load_from_file_bad_cache(load_from_file_cache):
    return load_from_file_cache('bad_cache')


@pytest.mark.usefixtures(*MOCKS)
def test_cache(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    assert len(tree.namespaces) == 3
    assert len(tree.projects) == 5
    assert len(tree.services) == 7
    assert len(tree.branches) == 19


@pytest.mark.usefixtures(*MOCKS)
def test_bad_keys(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    with pytest.raises(KeyError):
        tree.namespaces.get_by_id(-1)
    with pytest.raises(KeyError):
        tree.projects.get_by_id(-1)
    with pytest.raises(KeyError):
        tree.services.get_by_id(-1)
    with pytest.raises(KeyError):
        tree.branches.get_by_id(-1)


@pytest.mark.usefixtures(*MOCKS)
def test_namespaces(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    taxi_namespace = tree.namespaces.get_by_id(1)
    projects = tree.projects.get_by_namespace_id(1)
    assert len(projects) == 3
    assert taxi_namespace == TAXI_NAMESPACE


@pytest.mark.usefixtures(*MOCKS)
def test_projects(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    taxi_support = tree.projects.get_by_id(39)
    services = tree.services.get_by_project_id(39)
    assert len(services) == 3
    assert taxi_support == TAXI_SUPPORT_PROJECT


@pytest.mark.usefixtures(*MOCKS)
def test_projects_functions(library_context):
    tree = library_context.clownductor_cache.tree
    assert len(tree.projects.get_by_namespace_id(1)) == 3
    assert not tree.projects.get_by_namespace_id(100)


@pytest.mark.usefixtures(*MOCKS)
def test_services(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    compendium_nanny = tree.services.get_by_id(355298)
    branches = tree.branches.get_by_service_id(355298)
    assert len(branches) == 3
    assert compendium_nanny == COMPENDIUM_NANNY_SERVICE


@pytest.mark.usefixtures(*MOCKS)
def test_services_functions(library_context):
    tree = library_context.clownductor_cache.tree
    assert len(tree.services.get_by_project_id(39)) == 3
    assert not tree.services.get_by_project_id(100)


@pytest.mark.usefixtures(*MOCKS)
def test_branches(library_context):
    cache = library_context.clownductor_cache
    tree = cache.tree
    compendium_nanny_stable = tree.branches.get_by_id(296533)
    assert compendium_nanny_stable == COMPENDIUM_NANNY_STABLE


@pytest.mark.usefixtures(*MOCKS)
def test_branches_functions(library_context):
    tree = library_context.clownductor_cache.tree
    assert len(tree.branches.get_by_service_id(354601)) == 2
    assert not tree.branches.get_by_service_id(5)
    assert not tree.branches.get_by_service_id(100)


@pytest.mark.usefixtures('load_from_file_good_cache')
def test_bad_start_good_cache(library_context):
    tree = library_context.clownductor_cache.tree
    assert len(tree.namespaces) == 1
    assert len(tree.projects) == 1
    assert len(tree.services) == 1
    assert len(tree.branches) == 1
    assert tree.namespaces.get_by_id(1) == tree_module.Namespace(
        1, 'namespace',
    )
    assert tree.projects.get_by_id(1) == tree_module.Project(
        1, 'project', 1, {'groups': ['group-1'], 'logins': ['admin-1']},
    )
    assert tree.services.get_by_id(1) == tree_module.Service(
        1, 'service', 'nanny', 1, 'serviceabc',
    )
    assert tree.branches.get_by_id(1) == tree_module.Branch(
        1, 'branch', 'stable', 1, '', '',
    )


@pytest.mark.usefixtures('load_from_file_bad_cache')
async def test_bad_start_bad_cache():
    ctx = context_module.create_context()
    with pytest.raises(FileNotFoundError):
        await ctx.on_startup(None)
    await ctx.on_shutdown(None)


@pytest.mark.usefixtures(*MOCKS)
@pytest.mark.parametrize(
    'podset_id, expected_branch',
    [
        pytest.param(
            'taxi-compendium-stable', COMPENDIUM_NANNY_STABLE, id='existing',
        ),
        pytest.param('non-existing', None, id='not existing branch'),
    ],
)
def test_get_branch_by_podset_id(library_context, podset_id, expected_branch):
    tree = library_context.clownductor_cache.tree
    _branch = tree.branches.get_by_podset_id(podset_id)
    assert _branch == expected_branch
