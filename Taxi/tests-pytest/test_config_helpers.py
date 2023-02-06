import pytest

from taxi import config


@pytest.mark.parametrize('value,experiments,zone,correct', [
    (
        {
            '__default__': {
                'use_graph_result': True
            }
        },
        ['exp1', 'exp2', 'exp3'],
        'zone',
        True
    ),
    (
        {
            '__default__': {
                'use_graph_result': True
            },
            'acquire_via_graph:vladivostok,vladimir,tver': {
                'use_graph_result': False
            }
        },
        ['exp1', 'acquire_via_graph', 'exp3'],
        'tver',
        False
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'acquire_via_graph:vladivostok,vladimir,tver': {
                'use_graph_result': True
            },
            'acquire_via_graph:moscow': {
                'use_graph_result': True
            }
        },
        ['exp1', 'exp2', 'exp3'],
        'moscow',
        False
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'acquire_via_graph:': {
                'use_graph_result': True
            }
        },
        ['exp1', 'acquire_via_graph', 'exp3'],
        'moscow',
        True
    ),
    (
        {
            '__default__': {
                'use_graph_result': True
            },
            'moscow': {
                'use_graph_result': False
            }
        },
        ['exp1', 'exp2', 'exp3'],
        'moscow',
        False
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'moscow': {
                'use_graph_result': True
            }
        },
        ['exp1', 'exp2', 'exp3'],
        'tver',
        False
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'exp:moscow': {
                'use_graph_result': False
            },
            'moscow': {
                'use_graph_result': True
            }
        },
        ['exp1', 'exp2', 'exp3'],
        'moscow',
        True
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'exp:moscow': {
                'use_graph_result': True
            },
            'moscow': {
                'use_graph_result': False
            }
        },
        ['exp', 'exp2', 'exp3'],
        'moscow',
        True
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'exp:moscow': {
                'use_graph_result': False
            },
            'exp:': {
                'use_graph_result': True
            }
        },
        ['exp', 'exp2', 'exp3'],
        'tver',
        True
    ),
    (
        {
            '__default__': {
                'use_graph_result': False
            },
            'exp:moscow': {
                'use_graph_result': True
            },
            'exp:': {
                'use_graph_result': False
            }
        },
        ['exp', 'exp2', 'exp3'],
        'moscow',
        True
    ),
])
def test_check_zonekey_packed_config(value, experiments, zone, correct):
    cfg = config.ConfigZoneMap(value)
    func = lambda v: v['use_graph_result']
    assert func(cfg.get(experiments, zone)) == correct


@pytest.mark.parametrize('value,tag,experiments,zone,correct', [
    (
        {
            '__default__': {
                'use_graph_result': True
            },
            'tag:exp:zone': {
                'use_graph_result': False
            }
        },
        'tag',
        ['exp'],
        'zone',
        False
    ),
])
def test_check_zonekey_packed_config_tag(value, tag, experiments, zone, correct):
    cfg = config.ConfigZoneMap(value)
    func = lambda v: v['use_graph_result']
    assert func(cfg.get(tag, experiments, zone)) == correct
