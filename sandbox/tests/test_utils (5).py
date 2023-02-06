import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerRunCSImportWrapper.utils import (
    get_importer_with_dependencies_version,
    get_importers_after,
    get_importers_to_run,
    import_node_is_reusable,
    is_st_update_mode,
    separate_base_tags,
)
from sandbox.projects.yabs.qa.utils.general import get_json_md5
from sandbox.projects.yabs.qa.utils.importer import CSDataError


@pytest.mark.parametrize(('base_tags', 'result'), [
    ([], []),
    (['a', 'b', 'c'], ['a', 'b', 'c']),
    (['st001'], ['st001']),
    (['bs_st001'], ['bs_st001', 'yabs_st001']),
    (['yabs_st001'], ['bs_st001', 'yabs_st001']),
    (['yabs_st001', 'bs_st001'], ['bs_st001', 'yabs_st001']),
    (['yabs_st001', 'bs_st001', 'bs_st002'], ['bs_st001', 'yabs_st001', 'bs_st002', 'yabs_st002']),
    (['lmng_01'], ['lmng_01']),
    (['yabs_lmng_01'], ['yabs_lmng_01', 'bs_lmng_01']),
    (['yabs_lmng_01', 'bs_lmng_01'], ['bs_lmng_01', 'yabs_lmng_01']),
    (['yabs_lmng_01', 'bs_lmng_01', 'bs_lmng_01'], ['bs_lmng_01', 'yabs_lmng_01', 'bs_lmng_01', 'yabs_lmng_01']),
    (['lmcounters_01'], ['lmcounters_01']),
    (['yabs_lmcounters_01'], ['yabs_lmcounters_01', 'bs_lmcounters_01']),
    (['yabs_lmcounters_01', 'bs_lmcounters_01'], ['bs_lmcounters_01', 'yabs_lmcounters_01']),
    (['yabs_lmcounters_01', 'bs_lmcounters_01', 'bs_lmcounters_01'], ['bs_lmcounters_01', 'yabs_lmcounters_01', 'bs_lmcounters_01', 'yabs_lmcounters_01']),
    (['bs_dbe'], ['bs_dbe', 'yabs_dbe']),
    (['yabs_dbe'], ['bs_dbe', 'yabs_dbe']),
])
def test_separate_base_tags(base_tags, result):
    assert set(separate_base_tags(base_tags)) == set(result)


@pytest.mark.parametrize(('importers', 'expected_importers_after'), [
    (['1'], ['2', '3', '4', '5', '7']),
    (['1', '2'], ['2', '3', '4', '5', '7']),
    (['2', '3'], ['4', '5', '7']),
    (['2', '6'], ['4', '7']),
    (['8'], []),
])
def test_get_importers_after(importers, expected_importers_after):
    importers_info = {
        '1': {'dependencies': []},
        '2': {'dependencies': ['1']},
        '3': {'dependencies': ['1']},
        '4': {'dependencies': ['2', '3']},
        '5': {'dependencies': ['3']},
        '6': {'dependencies': []},
        '7': {'dependencies': ['3', '6']},
        '8': {'dependencies': []},
    }
    assert sorted(get_importers_after(importers, importers_info)) == expected_importers_after


@pytest.mark.parametrize(('importers',), [
    (['11'],),
    (['12'],),
])
def test_get_importers_after_raises(importers):
    importers_info = {
        '1': {'dependencies': []},
        '2': {'dependencies': ['1']},
        '11': {},
    }
    with pytest.raises(CSDataError):
        get_importers_after(importers, importers_info)


@pytest.mark.parametrize(('bases', 'result'), [
    ([], False),
    (['base'], False),
    (['st_update1'], False),
    (['st_update_1'], True),
    (['st_update_1', 'base'], True),
])
def test_is_st_update_mode(bases, result):
    assert is_st_update_mode(bases) == result


@pytest.mark.parametrize(('importers', 'existing_imports', 'expected'), [
    (
        ['1', '2', '3'],
        ['2', '3'],
        ['1', '2', '3']
    ),
    (
        ['1', '4'],
        ['4'],
        ['1', '4']
    ),
    (
        ['1', '2', '3'],
        ['1', '2', '3'],
        []
    ),
    (
        ['1', '2', '3'],
        [],
        ['1', '2', '3'],
    ),
    (
        ['1', '2', '3'],
        [],
        ['1', '2', '3'],
    ),
    (
        ['1', '2', '3'],
        ['1'],
        ['2', '3'],
    ),
])
def test_get_importers_to_run(importers, existing_imports, expected):
    importers_info = {
        '1': {'dependencies': []},
        '2': {'dependencies': ['1']},
        '3': {'dependencies': ['1']},
        '4': {'dependencies': ['1']},
    }

    assert set(get_importers_to_run(importers, existing_imports, importers_info)) == set(expected)


@pytest.mark.parametrize(('importer', 'importer_versions'), [
    ('1', {'1': 'v1'}),
    ('2', {'1': 'v1', '2': 'v2'}),
    ('3', {'1': 'v1', '2': 'v2', '3': 'v3'}),
    ('4', {'1': 'v1', '2': 'v2', '4': 'v4'}),
])
def test_get_importer_with_dependencies_version(importer, importer_versions):
    importers_info = {
        '1': {'dependencies': []},
        '2': {'dependencies': ['1']},
        '3': {'dependencies': ['2']},
        '4': {'dependencies': ['2']},
    }
    versions = {
        '1': 'v1',
        '2': 'v2',
        '3': 'v3',
        '4': 'v4',
    }
    assert get_importer_with_dependencies_version(importer, importers_info, versions) == get_json_md5(importer_versions)


@pytest.mark.parametrize(('importer', 'versions'), [
    ('5', {'1': 'v1', '2': 'v2'}),
    ('5', {'1': 'v1', '2': 'v2', '5': ''}),
    ('5', {'1': 'v1', '2': 'v2', '5': None}),
    ('5', {'1': 'v1', '2': 'v2', '5': 'v5'}),
    ('5', {'1': 'v1', '2': 'v2', '5': 'v5', '6': ''}),
    ('5', {'1': 'v1', '2': 'v2', '5': 'v5', '6': None}),
])
def test_get_importer_with_dependencies_version_raises(importer, versions):
    importers_info = {
        '1': {'dependencies': []},
        '2': {'dependencies': ['1']},
        '5': {'dependencies': ['6']},
    }
    with pytest.raises(CSDataError):
        get_importer_with_dependencies_version(importer, importers_info, versions)


@pytest.mark.parametrize(("oneshot_path", "drop_import_result", "tags", "is_reusable"), [
    (None, False, [], True),
    (None, False, ["WITH-PATCH"], False),
    (None, True, [], False),
    (None, True, ["WITH-PATCH"], False),
    ("oneshot", False, [], False),
    ("oneshot", False, ["WITH-PATCH"], False),
    ("oneshot", True, [], False),
    ("oneshot", True, ["WITH-PATCH"], False),
])
def test_import_node_is_reusable(oneshot_path, drop_import_result, tags, is_reusable):
    assert import_node_is_reusable(oneshot_path, drop_import_result, tags) == is_reusable
