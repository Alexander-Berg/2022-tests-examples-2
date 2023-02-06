import itertools

import pytest
import six

import sandbox.projects.browser.ab_experiments.BrowserExperimentsAbChecklist.checklists as checklists_lib
from sandbox.projects.browser.ab_experiments.BrowserExperimentsAbChecklist.checklists import util


@pytest.mark.parametrize(
    ('checklists', 'expected_merged_checklist'),
    [
        # Uppercase chars mean checked items
        # Underscore means nothing and used for easy reading

        ([], ''),
        (['abc'], 'abc'),
        (['abc', ''], 'abc'),

        # if no checked items, order items according to the order of checklists
        (['abc', 'def'], 'abc_def'),
        (['def', 'abc'], 'def_abc'),
        (['abc', 'def', 'ghi'], 'abc_def_ghi'),
        (['ghi', 'cba', 'def'], 'ghi_cba_def'),

        # first, pick items from most checked checklist
        (['abc', 'Def'], 'Def_abc'),
        (['abc', 'dEf'], 'dEf_abc'),
        (['aBc', 'dEf'], 'aBc_dEf'),
        (['dEf', 'aBc'], 'dEf_aBc'),
        (['aBc', 'Def'], 'Def_aBc'),
        (['Def', 'Abc', 'gHI'], 'gHI_Def_Abc'),
        (['Def', 'ABc', 'gHI'], 'ABc_gHI_Def'),
        (['dEf', 'Abc', 'gHI'], 'gHI_Abc_dEf'),

        (['aBCdef', 'gHi'], 'gHi_aBCdef'),
        (['ABcdef', 'gHi'], 'gHi_ABcdef'),
        (['ABCdef', 'gHi'], 'ABCdef_gHi'),
        (['ABCdef', 'Ghi'], 'Ghi_ABCdef'),
        (['gHi', 'ABCDef'], 'ABCDef_gHi'),

        # test intersecting lists
        (['abcde', 'bcd'], 'abcde'),
        (['abcde', 'bd'], 'abcde'),
        (['abcde', 'bfgd'], 'ab_fg_cde'),
        (['abcd', 'efcg'], 'abefcdg'),
        (['abcd', 'Efcg'], 'Efabcgd'),
        (['abcd', 'eFcg'], 'eFabcgd'),
        (['abc', 'def', 'ghi', 'aei'], 'abc_def_ghi'),
        (['abc', 'def', 'ghi', 'iea'], 'd_ghi_e_abc_f'),
        (['aei', 'abc', 'def', 'ghi'], 'abc_def_ghi'),
        (['abc', 'DEF', 'ghi', 'aei'], 'D_a_EF_bc_ghi'),
        (['abc', 'def', 'ghi', 'gec'], 'ab_d_gec_f_hi'),
        (['abc', 'DEF', 'ghi', 'gec'], 'D_g_EF_abc_hi'),
        (['abc', 'def', 'ghi', 'GEC'], 'Ghi_dEf_abC'),
        (['abc', 'def', 'ac', 'be', 'cd'], 'abc_def'),
    ]
)
def test_merge_checklists(checklists, expected_merged_checklist):
    checked_items = set(c.lower() for c in itertools.chain(*checklists) if c.isupper())
    checklists = [checklist.lower() for checklist in checklists]

    merged_checklist = util.merge_checklists(checklists, checked_items)
    merged_checklist = [item.upper() if item in checked_items else item for item in merged_checklist]

    assert merged_checklist == list(expected_merged_checklist.replace('_', ''))


@pytest.mark.parametrize('inconsistent_checklists', [
    [[0, 0]],
    [[0, 1, 0]],
    [[0, 1, 2, 3], [3, 0]],
    [[0, 1, 2, 3], [3, 1]],
    [[0, 1, 2, 3], [3, 4, 1]],
    [[0, 1, 2, 2, 3]],
    [[0, 1, 2, 2], [2, 3]],
    [[0, 1, 2], [2, 3, 4], [4, 5, 1]],
    [[0, 1, 2, 3], [4, 2, 5], [6, 5, 7, 1, 8]],
])
def test_merge_of_inconsistent_checklists(inconsistent_checklists):
    with pytest.raises(util.ChecklistsMergeError):
        util.merge_checklists(inconsistent_checklists, checked_items=set())

    items = set.union(*map(set, inconsistent_checklists))
    merged_items = util.merge_checklists(inconsistent_checklists,
                                         checked_items=set(), ignore_cycles=True)
    assert len(merged_items) == len(items)
    assert set(merged_items) == items


def test_checklists_consistency():
    """Check that checklists form a DAG (Directed Acyclic Graph)"""
    for checklists_mapping in checklists_lib._CHECKLISTS_BY_AB_QUEUE.values():
        checklists = list(checklists_mapping.values())
        items = set.union(*map(set, checklists))

        assert all(isinstance(item, six.string_types) for item in items)

        merged_items = util.merge_checklists(checklists, checked_items=set())
        assert len(merged_items) == len(items)
        assert set(merged_items) == items
