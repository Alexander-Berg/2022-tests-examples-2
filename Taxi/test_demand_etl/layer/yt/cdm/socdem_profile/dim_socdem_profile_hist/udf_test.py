from demand_etl.layer.yt.cdm.socdem_profile.dim_socdem_profile_hist.impl import reduce_init, reduce_append
from .impl import build_init_input_stream, build_append_input_stream, build_output_stream


def test_reduce_init():
    assert list(reduce_init('id1', build_init_input_stream([
        ('2021-01-01', 0.0, 'C2', False),
        ('2021-01-02', 0.1, 'C2', False),
        ('2021-01-03', 0.100001, 'C2', False),
        ('2021-01-04', 0.1, 'C2', False),
        ('2021-01-05', 0.1, 'C1', False),
        ('2021-01-06', 0.0, 'C1', False),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 0.0, 'C2', False),
        ('2021-01-02', '2021-01-05', 0.1, 'C2', False),
        ('2021-01-05', '2021-01-06', 0.1, 'C1', False),
        ('2021-01-06', '9999-12-31', 0.0, 'C1', False),
    ])

    assert list(reduce_init('id1', build_init_input_stream([
        ('2021-01-01', 1.00001, 'B2', False),
        ('2021-01-02', 1.00002, 'B2', True),
        ('2021-01-03', 1.00003, 'B2', True),
        ('2021-01-04', 1.00004, 'B2', False),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 1.00001, 'B2', False),
        ('2021-01-02', '2021-01-04', 1.00002, 'B2', True),
        ('2021-01-04', '9999-12-31', 1.00004, 'B2', False),
    ])


def test_reduce_append():
    assert list(reduce_append('id1', build_append_input_stream([
        ('2021-01-01', 1.0, 'B2', False, 2),
        ('2021-01-02', 1.0, 'B2', True, 2),
        ('2021-01-03', 1.00001, 'B2', True, 1),
        ('2021-01-04', 1.00002, 'B2', False, 1),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 1.0, 'B2', False),
        ('2021-01-02', '2021-01-04', 1.0, 'B2', True),
        ('2021-01-04', '9999-12-31', 1.00002, 'B2', False),
    ])

    assert list(reduce_append('id1', build_append_input_stream([
        ('2021-01-01', 0.1, 'B1', False, 2),
        ('2021-01-02', 0.2, 'B2', True, 2),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 0.1, 'B1', False),
        ('2021-01-02', '9999-12-31', 0.2, 'B2', True),
    ])

    assert list(reduce_append('id1', build_append_input_stream([
        ('2021-01-01', 0.1, 'B1', False, 1),
        ('2021-01-02', 0.2, 'B2', True, 1),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 0.1, 'B1', False),
        ('2021-01-02', '9999-12-31', 0.2, 'B2', True),
    ])

    assert list(reduce_append('id1', build_append_input_stream([
        ('2021-01-01', 0.1, 'B1', False, 1),
        ('2021-01-01', 0.1, 'B1', False, 2),
        ('2021-01-02', 0.2, 'B2', True, 1),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 0.1, 'B1', False),
        ('2021-01-02', '9999-12-31', 0.2, 'B2', True),
    ])

    assert list(reduce_append('id1', build_append_input_stream([
        ('2021-01-01', 0.0, 'C2', False, 1),
        ('2021-01-01', 0.0, 'C2', False, 2),
        ('2021-01-02', 0.1, 'C2', False, 1),
        ('2021-01-03', 0.100001, 'C2', False, 1),
        ('2021-01-04', 0.1, 'C2', False, 1),
        ('2021-01-05', 0.1, 'C1', False, 1),
        ('2021-01-06', 0.0, 'C1', False, 1),
    ]))) == build_output_stream([
        ('2021-01-01', '2021-01-02', 0.0, 'C2', False),
        ('2021-01-02', '2021-01-05', 0.1, 'C2', False),
        ('2021-01-05', '2021-01-06', 0.1, 'C1', False),
        ('2021-01-06', '9999-12-31', 0.0, 'C1', False),
    ])
