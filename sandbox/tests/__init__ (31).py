# -*- coding: utf-8 -*-

import pytest

from sandbox.projects.browser.autotests.classes.functionalities import (
    get_issue_functionalities, Functionality, FunctionalitiesTree, get_testcase_functionalities,
    get_testcase_depends_on_functionalities, should_run_case_in_regression, STARCASES_DONE_TAG,
    STARCASES_NOT_NEEDED_TAG, get_functionality_from_issue_field)


class ComponentMock(object):
    def __init__(self, display):
        self.display = display


class IssueMock(object):
    def __init__(self, components, tags, functionality):
        self.tags = tags
        self.components = [ComponentMock(component) for component in components]
        self.key = 'TESTISSUE-100500'
        self.functionality = functionality


class TestcaseMock(object):
    def __init__(self, component, functionalities, depends_on_functionalities):
        self.mapped_attributes = {
            'Depends on Functionality': depends_on_functionalities,
            'Functionality': functionalities,
            'Component': component
        }
        self.project = 'test'
        self.id = '1'


@pytest.mark.parametrize(
    'content, expected', [
        pytest.param('', None, id='empty'),
        pytest.param('A:B:C', None, id='not_close_to_json'),
        pytest.param('{"funcs": ["C:D:E", "F:G"]}', ['F:G', 'C:D:E'], id='well_formatted'),
        pytest.param('{"funcs": ["C:D:E", "F:G"]', None, id='malformed_json'),
    ]
)
def test_get_functionality_from_issue_field(content, expected):
    assert get_functionality_from_issue_field(content) == expected


@pytest.mark.parametrize(
    'st_components, st_tags, st_functionality, exp_functionalities', [
        pytest.param(['A'], [], '', {'A'}, id='no_tags'),
        pytest.param(['A'], [STARCASES_DONE_TAG, 'func_A:b:c', 'func_A:b:d'], '', {'A:b:c', 'A:b:d'},
                     id='simple_starcase'),
        # functionalities not from issue components. We trust STARCASES_DONE_TAG
        pytest.param(['A', 'B'], [STARCASES_DONE_TAG, 'func_B:c:d', 'func_D:e:f'], '', {'B:c:d', 'D:e:f'},
                     id='functionality_not_from_issue_componets'),
        # functionalities that are different in startrek and testpalm
        pytest.param(['Installer+Updater'], [], '', {'Installer', 'Updater'}, id='Installer+Updater'),
        pytest.param(['Browser-Update'], [], '', {'Installer', 'Updater'}, id='Browser-Update'),
        # starcases not needed: for some reasons testes do not want this issue to influence regression scope
        pytest.param(['A'], [STARCASES_NOT_NEEDED_TAG, 'func_A:b'], '', set(), id='starcases_not_needed_tag_1'),
        pytest.param(['A'], [STARCASES_NOT_NEEDED_TAG], 'A:b', set(), id='starcases_not_needed_tag_2'),
        pytest.param(['A'], [STARCASES_DONE_TAG], '', {'A'}, id='starcases_done_with_no_functionalities'),
        # use functionality field
        pytest.param(['A'], [STARCASES_DONE_TAG, 'func_A:B:C'],
                     '{"funcs": ["C:D:E", "F:G"]}', {'C:D:E', 'F:G'},
                     id='functionality_field_with_functionalities'),
    ]
)
def test_get_issue_functionalities(st_components, st_tags, st_functionality, exp_functionalities):
    res_func = get_issue_functionalities(IssueMock(st_components, st_tags, st_functionality))
    assert exp_functionalities == {str(func) for func in res_func}


@pytest.mark.parametrize(
    'tp_component, tp_functionalities, exp_functionalities', [
        pytest.param(['A'], [], {'A'}, id='no_functionalities_in_case'),
        pytest.param(['A'], ['A:b:c', 'A:b:d'], {'A:b:c', 'A:b:d', 'A'}, id='simple_case'),
    ]
)
def test_get_testcase_functionalities(tp_component, tp_functionalities, exp_functionalities):
    res_func = get_testcase_functionalities(TestcaseMock(tp_component, tp_functionalities, []))
    assert exp_functionalities == {str(func) for func in res_func}


@pytest.mark.parametrize(
    'tp_component, tp_dof, exp_functionalities', [
        pytest.param(['A'], [], set(), id='no_dof'),
        pytest.param(['A'], ['A:b:c', 'A:b:d'], {'A:b:c', 'A:b:d'}, id='simple_case'),
    ]
)
def test_get_testcase_dofs(tp_component, tp_dof, exp_functionalities):
    res_func = get_testcase_depends_on_functionalities(TestcaseMock(tp_component, [], tp_dof))
    assert exp_functionalities == {str(func) for func in res_func}


@pytest.mark.parametrize(
    'st_functionalities, testcase_functionality, should_check_case', [
        pytest.param({'A:b:c1'}, 'A:b:c1', True, id='same_functionality'),
        pytest.param({'A:b:c1'}, 'A:b:c2', False, id='same_level_different_functionalities'),
        pytest.param({'A:b:c1'}, 'A:b', False, id='upper_level_in_case'),
        pytest.param({'A:b'}, 'A:b:c1', True, id='upper_level_in_issue'),
        pytest.param(set(), 'A', False, id='no_functionalities_in_diff'),
    ]
)
def test_should_check_functionality(st_functionalities, testcase_functionality, should_check_case):
    functionalities = [Functionality.from_str(f) for f in st_functionalities]
    tree = FunctionalitiesTree(functionalities)
    assert should_check_case == tree.should_check_functionality(Functionality.from_str(testcase_functionality))


@pytest.mark.parametrize(
    'st_functionalities, testcase_dof, should_check_case', [
        pytest.param({'A:b:c1'}, 'A:b:c1', True, id='same_functionality'),
        pytest.param({'A:b:c1'}, 'A:b:c2', False, id='same_level_different_functionalities'),
        pytest.param({'A:b:c1'}, 'A:b', True, id='upper_level_in_case'),
        pytest.param({'A:b'}, 'A:b:c1', True, id='upper_level_in_issue'),
        pytest.param(set(), 'A', False, id='no_functionalities_in_diff'),
    ]
)
def test_should_check_depends_on_functionality(st_functionalities, testcase_dof, should_check_case):
    functionalities = [Functionality.from_str(f) for f in st_functionalities]
    tree = FunctionalitiesTree(functionalities)
    assert should_check_case == tree.should_check_depends_on_functionality(Functionality.from_str(testcase_dof))


@pytest.mark.parametrize(
    'st_functionalities, case_functionalities, case_dof, component, should_check_case', [
        pytest.param({'A:b:c1'}, ['A:b:c1'], [], ['A'], True, id='because_functionality'),
        pytest.param({'A:b:c1'}, ['A:b:c2'], ['A:b'], ['A'], True, id='because_dof'),
        pytest.param({'A:b:c1'}, ['D:b'], [], ['D'], False, id='case_not_from_diff'),
        pytest.param(set(), ['A'], [], ['A'], False, id='empty_diff'),
        pytest.param({u'2020:редизайн'}, [], [], [u'2020:редизайн'], True, id='unicode'),
        pytest.param({'Cloud DOC'}, ['CloudDOC:a:b'], [], ['Cloud DOC'], True,
                     id='functionality_component_differs_from_startrek1'),
        pytest.param({'CloudDOC'}, ['CloudDOC:a:b'], [], ['Cloud DOC'], True,
                     id='functionality_component_differs_from_startrek2'),
    ]
)
def test_should_check_testcase(st_functionalities, case_functionalities, case_dof, component, should_check_case):
    functionalities = [Functionality.from_str(f) for f in st_functionalities]
    tree = FunctionalitiesTree(functionalities)
    testcase = TestcaseMock(component, case_functionalities, case_dof)
    assert should_check_case == should_run_case_in_regression(tree, testcase)


def test_get_all_layer_functionalities():
    expected_functionalities = {'A', 'A:B', 'A:B:C', 'D', 'D:E'}
    functionalities_srings = ['A:B:C', 'D:E']
    functionalities = [Functionality.from_str(f) for f in functionalities_srings]
    tree = FunctionalitiesTree(functionalities)
    all_functionalities = tree.get_all_layer_functionalities()
    assert expected_functionalities == {str(f) for f in all_functionalities}
