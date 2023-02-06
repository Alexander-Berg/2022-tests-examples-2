import mock
import pytest

from sandbox.projects.common.yabs.server.db import yt_bases
from sandbox.projects.yabs.qa.tasks.YabsServerRunCSImportWrapper import find_imports, find_import_node


@mock.patch('sandbox.projects.yabs.qa.tasks.YabsServerRunCSImportWrapper.yt_bases.find_node_to_reuse')
@pytest.mark.parametrize(('search_attributes', 'node_to_reuse', 'expected_existing_imports', 'expected_tasks_to_wait'), [
    (
        {'ExistingImporter': {}},
        {
            '$value': '//ExistingImporter',
            '$attributes': {
                yt_bases.IMPORT_COMPLETED_ATTRIBUTE: True,
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        {'ExistingImporter': '//ExistingImporter'},
        []
    ),
    (
        {'ExistingImporter': {}, 'ExistingImporter2': {}},
        {
            '$value': '//ExistingImporter',
            '$attributes': {
                yt_bases.IMPORT_COMPLETED_ATTRIBUTE: True,
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        {'ExistingImporter': '//ExistingImporter', 'ExistingImporter2': '//ExistingImporter'},
        []
    ),
    (
        {'NotExistingImporter': {}},
        None,
        {},
        []
    ),
    (
        {'ExistingImporter': {}},
        {
            '$value': '//ExecutingImporter',
            '$attributes': {
                yt_bases.IMPORT_COMPLETED_ATTRIBUTE: False,
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        {},
        [1]
    ),
    (
        {'ExistingImporter': {}},
        {
            '$value': '//ExecutingImporter',
            '$attributes': {
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        {},
        [1]
    ),

])
def test_find_imports(
        find_node_to_reuse_mock,
        search_attributes, node_to_reuse, expected_existing_imports, expected_tasks_to_wait
):
    find_node_to_reuse_mock.return_value = node_to_reuse
    existing_imports, tasks_to_wait = find_imports(
        search_attributes=search_attributes,
        imports_root_dir='',
        yt_client=None
    )
    assert existing_imports == expected_existing_imports
    assert tasks_to_wait == expected_tasks_to_wait


@mock.patch('sandbox.projects.yabs.qa.tasks.YabsServerRunCSImportWrapper.yt_bases.find_node_to_reuse')
@pytest.mark.parametrize(('node_to_reuse', 'expected_node_path', 'expected_task_to_wait'), [
    (None, None, None),
    (
        {
            '$value': '//ExistingImporter',
            '$attributes': {
                yt_bases.IMPORT_COMPLETED_ATTRIBUTE: True,
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        '//ExistingImporter',
        None
    ),
    (
        {
            '$value': '//ExecutingImporter',
            '$attributes': {
                yt_bases.IMPORT_COMPLETED_ATTRIBUTE: False,
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        None,
        1
    ),
    (
        {
            '$value': '//ExecutingImporter',
            '$attributes': {
                yt_bases.CREATED_BY_TASK_ATTRIBUTE: 1,
            }
        },
        None,
        1
    ),
])
def test_find_import_node(
        find_node_to_reuse_mock,
        node_to_reuse, expected_node_path, expected_task_to_wait
):
    find_node_to_reuse_mock.return_value = node_to_reuse
    existing_node_path, task_to_wait = find_import_node(
        search_attributes={},
        imports_root_dir='',
        yt_client=None
    )
    assert existing_node_path == expected_node_path
    assert task_to_wait == expected_task_to_wait
