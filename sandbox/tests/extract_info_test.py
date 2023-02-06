# -*- coding: utf-8 -*-

from sandbox.projects.CalcCoverage.lib.extract_info import extract_coverage_info_from_ya_make_output, merge_coverage_info


def test_extract_normal():
    out = 'some\n' \
          'lines\n' \
          'of output\n' \
          'Summary coverage rate:\n' \
          '  lines......: 88.6% (466 of 526 lines)\n' \
          '  functions..: 92.0% (69 of 75 functions)\n' \
          '  branches...: no data found\n' \
          'some\n' \
          'lines\n' \
          'of output\n' \

    ret = extract_coverage_info_from_ya_make_output(out)
    assert 'lines_covered' in ret
    assert 'functions_covered' in ret
    assert 'branches_covered' not in ret

    assert 'lines_total' in ret
    assert 'functions_total' in ret
    assert 'branches_total' not in ret

    assert 'lines_coverage' in ret
    assert 'functions_coverage' in ret
    assert 'branches_coverage' not in ret

    assert ret['lines_covered'] == 466
    assert ret['functions_covered'] == 69

    assert ret['lines_total'] == 526
    assert ret['functions_total'] == 75

    assert round(ret['lines_coverage'] * 10.0) == 886
    assert round(ret['functions_coverage'] * 10.0) == 920


def test_merge_coverage_info():
    test_info = {
        'search/wizard/entitysearch/common': {
            'lines_total': 568,
            'lines_covered': 528,
            'lines_coverage': 93.0,
            'functions_total': 77,
            'functions_covered': 72,
            'functions_coverage': 93.5,
            'target': 'search/wizard/entitysearch/common'
        },
        'search/wizard/entitysearch/card/': {
            'lines_total': 855,
            'lines_covered': 301,
            'lines_coverage': 35.0,
            'functions_total': 128,
            'functions_covered': 64,
            'functions_coverage': 50.0,
            'target': 'search/wizard/entitysearch/card'
        },
        'search/wizard/entitysearch': {
            'lines_total': 100,
            'lines_covered': 50,
            'lines_coverage': 50.0,
            'functions_total': 150,
            'functions_covered': 100,
            'functions_coverage': 66.6,
            'target': 'search/wizard/entitysearch'
        },
        'search/ugc': {
            'lines_total': 32,
            'lines_covered': 22,
            'lines_coverage': 68,
            'functions_total': 5,
            'functions_covered': 4,
            'functions_coverage': 80.0,
            'branches_total': 100,
            'branches_covered': 98,
            'branches_coverage': 98.0,
            'target': 'search/ugc'
        }
    }
    info = test_info.copy()
    merge_coverage_info(info)
    assert info['search/ugc'] == test_info['search/ugc']
    assert info['search/wizard/entitysearch/common'] == test_info['search/wizard/entitysearch/common']
    assert info['search/wizard/entitysearch/card/'] == test_info['search/wizard/entitysearch/card/']

    assert len(info) == 6

    assert info.get('search/wizard/entitysearch/*')
    assert info['search/wizard/entitysearch/*']['target'] == 'search/wizard/entitysearch/*'
    assert info['search/wizard/entitysearch/*']['lines_total'] == 1523
    assert info['search/wizard/entitysearch/*']['lines_covered'] == 879
    assert round(info['search/wizard/entitysearch/*']['lines_coverage'] * 10.0) == 577
    assert info['search/wizard/entitysearch/*']['functions_total'] == 355
    assert info['search/wizard/entitysearch/*']['functions_covered'] == 236
    assert round(info['search/wizard/entitysearch/*']['functions_coverage'] * 10.0) == 665
    assert not info['search/wizard/entitysearch/*'].get('branches_total')
    assert not info['search/wizard/entitysearch/*'].get('branches_covered')
    assert not info['search/wizard/entitysearch/*'].get('branches_coverage')

    assert not info.get('search/wizard/*')

    assert info.get('search/*')
    assert info['search/*']['target'] == 'search/*'
    assert info['search/*']['lines_total'] == 1555
    assert info['search/*']['lines_covered'] == 901
    assert info['search/*']['lines_coverage'] == 57.9
    assert info['search/*']['functions_total'] == 360
    assert info['search/*']['functions_covered'] == 240
    assert round(info['search/*']['functions_coverage'] * 10.0) == 667
    assert info['search/*']['branches_total'] == 100
    assert info['search/*']['branches_covered'] == 98
    assert round(info['search/*']['branches_coverage'] * 10.0) == 980


def test_merge_coverage_info_common_root():
    test_info = {
        'search': {
            'lines_total': 568,
            'lines_covered': 528,
            'lines_coverage': 93.0,
            'target': 'search'
        },
        'entity': {
            'functions_total': 128,
            'functions_covered': 64,
            'functions_coverage': 50.0,
            'target': 'entity'
        }
    }
    info = test_info.copy()
    merge_coverage_info(info)
    assert info['search'] == test_info['search']
    assert info['entity'] == test_info['entity']

    assert len(info) == 3

    assert info.get('*')
    assert info['*']['target'] == '*'
    assert info['*']['lines_total'] == 568
    assert info['*']['lines_covered'] == 528
    assert round(info['*']['lines_coverage'] * 10.0) == 930
    assert info['*']['functions_total'] == 128
    assert info['*']['functions_covered'] == 64
    assert round(info['*']['functions_coverage'] * 10.0) == 500
    assert not info['*'].get('branches_total')
    assert not info['*'].get('branches_covered')
    assert not info['*'].get('branches_coverage')
