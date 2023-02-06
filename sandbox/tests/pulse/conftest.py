# coding=utf-8
import pytest
from mock import Mock


@pytest.fixture(scope="function")
def shooting_components_mock():
    sc = Mock()
    type(sc).enqueue = Mock()
    return sc


@pytest.fixture(scope="function")
def diff_fixture():
    report_data = [
        {
            'title': 'Touch',
            'subtitle': 'non-entry',
            'metrics': ['Foo', 'Bar', 'Baz', 'Qux', 'Quux'],
            'additional_columns': ['Diff'],
            'rows': [
                {
                    'name': 'name1',
                    'raw_name': 'name1',
                    'values': [
                        {'delta': 1, 'base': 0, 'actual': 1, 'aggregation_name': 'p25', 'is_exceeded': False},
                        {'delta': 1, 'base': 0, 'actual': 1, 'aggregation_name': 'p50', 'is_exceeded': False},
                        {'delta': 1, 'base': 0, 'actual': 1, 'aggregation_name': 'p80', 'is_exceeded': False},
                        {'delta': 1, 'base': 0, 'actual': 1, 'aggregation_name': 'p95', 'is_exceeded': False},
                        {'delta': 1, 'base': 0, 'actual': 1, 'aggregation_name': 'p99', 'is_exceeded': False},
                    ]
                },
            ],
        }
    ]

    return report_data


@pytest.fixture(scope="function")
def static_files_fixture():
    return [
        {
            "rows": [
                {
                    "raw_name": "_common.header.pre.css",
                    "values": [
                        {
                            "actual": 0,
                            "is_exceeded": False,
                            "file_size_limit": None,
                            "base": 0,
                            "link": "",
                            "delta": 0,
                            "limit": 1.5,
                            "is_significant": True
                        }
                    ],
                    "name": "_common.header.pre.css"
                },
                {
                    "raw_name": "_common.pre.css",
                    "values": [
                        {
                            "actual": 4.09,
                            "is_exceeded": False,
                            "file_size_limit": None,
                            "base": 4.09,
                            "link": "",
                            "delta": 0,
                            "limit": 1.5,
                            "is_significant": True
                        }
                    ],
                    "name": "_common.pre.css"
                },
            ],
            "aggregations": [
                "Gzip size (Kb)"
            ],
            "title": "images-touch-pad"
        },
    ]


@pytest.fixture(scope="function")
def pulse_genisys_fixture():
    return {
        'static_files': {
            'phone': ['bundles-touch-phone/page/_page.js'],
            'desktop': ['bundles-desktop/page/_page.js']
        },
        'limits': {
            'shooting': {
                'touch': {
                    'post_size_deflate': {'25': 0.5, '80': 1, '95': 1, '50': 0.5},
                    'post_total_template': {'25': 5, '80': 10, '95': 10, '50': 5},
                    'post_priv_template': {'25': 5, '80': 10, '95': 10, '50': 5},
                    'pre_priv_template': {'25': 2, '80': 2, '95': 2, '50': 2},
                    'pre_bemhtml_template': {'25': 2, '80': 2, '95': 2, '50': 2},
                    'pre_total_template': {'25': 3, '80': 3, '95': 3, '50': 3},
                    'post_bemhtml_template': {'25': 5, '80': 5, '95': 5, '50': 5},
                    'pre_size_deflate': {'25': 0.2, '80': 0.2, '95': 0.2, '50': 0.2}
                },
                'desktop': {
                    'post_size_deflate': {'25': 0.5, '80': 1, '95': 1, '50': 0.5},
                    'post_total_template': {'25': 5, '80': 10, '95': 10, '50': 5},
                    'post_priv_template': {'25': 5, '80': 10, '95': 10, '50': 5},
                    'pre_priv_template': {'25': 2, '80': 2, '95': 2, '50': 2},
                    'pre_bemhtml_template': {'25': 2, '80': 2, '95': 2, '50': 2},
                    'pre_total_template': {'25': 3, '80': 3, '95': 3, '50': 3},
                    'post_bemhtml_template': {'25': 5, '80': 5, '95': 5, '50': 5},
                    'pre_size_deflate': {'25': 0.2, '80': 0.2, '95': 0.2, '50': 0.2}
                }
            },
            'static': {
                'phone': {'_page.js': 1},
                'desktop': {'_page.js': 1}
            },
            'static_file_size': {
                'phone': {'_page.js': 5},
                'desktop': {'_page.js': 5}
            }
        }
    }


@pytest.fixture(scope="function")
def pulse_config_fixture():
    return {
        'static_files': {
            'phone': ['bundles-touch-phone/page/_page.js'],
            'desktop': ['bundles-desktop/page/_page.js']
        },
        'limits': {
            'shooting': {
                'touch': {
                    'post_size_deflate': {'p25': 0.5, 'p80': 1, 'p95': 1, 'p50': 0.5},
                    'post_total_template': {'p25': 5, 'p80': 10, 'p95': 10, 'p50': 5},
                    'post_priv_template': {'p25': 5, 'p80': 10, 'p95': 10, 'p50': 5},
                    'pre_priv_template': {'p25': 2, 'p80': 2, 'p95': 2, 'p50': 2},
                    'pre_bemhtml_template': {'p25': 2, 'p80': 2, 'p95': 2, 'p50': 2},
                    'pre_total_template': {'p25': 3, 'p80': 3, 'p95': 3, 'p50': 3},
                    'post_bemhtml_template': {'p25': 5, 'p80': 5, 'p95': 5, 'p50': 5},
                    'pre_size_deflate': {'p25': 0.2, 'p80': 0.2, 'p95': 0.2, 'p50': 0.2}
                },
                'desktop': {
                    'post_size_deflate': {'p25': 0.5, 'p80': 1, 'p95': 1, 'p50': 0.5},
                    'post_total_template': {'p25': 5, 'p80': 10, 'p95': 10, 'p50': 5},
                    'post_priv_template': {'p25': 5, 'p80': 10, 'p95': 10, 'p50': 5},
                    'pre_priv_template': {'p25': 2, 'p80': 2, 'p95': 2, 'p50': 2},
                    'pre_bemhtml_template': {'p25': 2, 'p80': 2, 'p95': 2, 'p50': 2},
                    'pre_total_template': {'p25': 3, 'p80': 3, 'p95': 3, 'p50': 3},
                    'post_bemhtml_template': {'p25': 5, 'p80': 5, 'p95': 5, 'p50': 5},
                    'pre_size_deflate': {'p25': 0.2, 'p80': 0.2, 'p95': 0.2, 'p50': 0.2}
                }
            },
            'static_delta': {
                'phone': {'_page.js': 1},
                'desktop': {'_page.js': 1}
            },
            'static_file_size': {
                'phone': {'_page.js': 5},
                'desktop': {'_page.js': 5}
            }
        }
    }
