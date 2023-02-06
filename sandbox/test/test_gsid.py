from __future__ import absolute_import, division, print_function

from sandbox.projects.yabs.sandbox_task_tracing.info import gsid_info


def test_gsid_info_precommit_arc():
    text = ' '.join((
        'ARC_MERGE:ee99fff738eec25df33d6a3f97809d583de53685',
        'USER:altered',
        'ARCANUM:2322685',
        'TE:5pd3f:YABS_SERVER_27_CS_IMPORT_STABILITY_COMMON_SAMPLED:123074074:FULL-CIRCUIT',
        'SB:YABS_SERVER_CS_IMPORT_TEST_STABILITY:1212215011',
        'USER:robot-testenv',
        'SB:YABS_SERVER_RUN_CS_IMPORT_WRAPPER:1212216208',
        'USER:robot-testenv',
    ))
    assert gsid_info(text) == dict(
        _raw=text,
        revision=dict(
            arc_merge='ee99fff738eec25df33d6a3f97809d583de53685',
            arcanum=2322685,
        ),
        sandbox=[
            dict(
                task_id=1212215011,
                task_type='YABS_SERVER_CS_IMPORT_TEST_STABILITY',
                user='robot-testenv',
            ),
            dict(
                task_id=1212216208,
                task_type='YABS_SERVER_RUN_CS_IMPORT_WRAPPER',
                user='robot-testenv',
            ),
        ],
        testenv=dict(
            circuit='FULL-CIRCUIT',
            db_name='5pd3f',
            job_id=123074074,
            job_name='YABS_SERVER_27_CS_IMPORT_STABILITY_COMMON_SAMPLED',
        ),
        user='altered',
    )


def test_gsid_info_precommit_svn():
    text = ' '.join((
        'SVN_TXN:9103329-6b0ko',
        'USER:altered',
        'ARCANUM:2303115',
        'TE:5oem1:YABS_SERVER_30_BASE_GEN_B:122917220:FULL-CIRCUIT',
        'SB:YABS_SERVER_MAKE_BIN_BASES:1204119738',
        'USER:robot-testenv',
        'SB:YABS_SERVER_RUN_CS_IMPORT_WRAPPER:1204139962',
        'USER:robot-testenv',
    ))
    assert gsid_info(text) == dict(
        _raw=text,
        revision=dict(
            svn_txn='9103329-6b0ko',
            arcanum=2303115,
        ),
        sandbox=[
            dict(
                task_id=1204119738,
                task_type='YABS_SERVER_MAKE_BIN_BASES',
                user='robot-testenv',
            ),
            dict(
                task_id=1204139962,
                task_type='YABS_SERVER_RUN_CS_IMPORT_WRAPPER',
                user='robot-testenv',
            ),
        ],
        testenv=dict(
            circuit='FULL-CIRCUIT',
            db_name='5oem1',
            job_id=122917220,
            job_name='YABS_SERVER_30_BASE_GEN_B',
        ),
        user='altered',
    )


def test_gsid_info_precommit_svn_ya():
    text = ' '.join((
        'USER:altered',
        'YA:m6ojb85p671a4vuj',
        'SVN_TXN:9133805-6bt1h',
        'ARCANUM:2296818',
        'TE:5pd28:YABS_SERVER_30_BASE_GEN_COMMON_SAMPLED:123074272:FULL-CIRCUIT',
        'SB:YABS_SERVER_MAKE_BIN_BASES:1212220562',
        'USER:robot-testenv',
        'SB:YABS_SERVER_RUN_CS_IMPORT_WRAPPER:1212226812',
        'USER:robot-testenv'
    ))
    result = gsid_info(text)
    [error] = result.pop('_errors', None)
    assert result == dict(
        _raw=text,
        revision=dict(
            svn_txn='9133805-6bt1h',
            arcanum=2296818,
        ),
        sandbox=[
            dict(
                task_id=1212220562,
                task_type='YABS_SERVER_MAKE_BIN_BASES',
                user='robot-testenv',
            ),
            dict(
                task_id=1212226812,
                task_type='YABS_SERVER_RUN_CS_IMPORT_WRAPPER',
                user='robot-testenv',
            ),
        ],
        testenv=dict(
            circuit='FULL-CIRCUIT',
            db_name='5pd28',
            job_id=123074272,
            job_name='YABS_SERVER_30_BASE_GEN_COMMON_SAMPLED',
        ),
        user='altered',
    )
    assert error['word'] == 'YA:m6ojb85p671a4vuj'


def test_gsid_info_commit():
    text = ' '.join((
        'SVN:9126887',
        'TE:yabs-2.0:YABS_SERVER_60_CS_EXPORT_BANNERS:469180014:FULL-CIRCUIT',
        'SB:YABS_SERVER_CS_ADVMACHINE_EXPORT:1210495301',
        'USER:robot-testenv'
    ))
    assert gsid_info(text) == dict(
        _raw=text,
        revision=dict(
            svn=9126887,
        ),
        sandbox=[
            dict(
                task_id=1210495301,
                task_type='YABS_SERVER_CS_ADVMACHINE_EXPORT',
                user='robot-testenv',
            ),
        ],
        testenv=dict(
            circuit='FULL-CIRCUIT',
            db_name='yabs-2.0',
            job_id=469180014,
            job_name='YABS_SERVER_60_CS_EXPORT_BANNERS',
        ),
    )


def test_gsid_info_bad_testenv():
    text = ' '.join((
        'SVNDIFF:9128800:9130947',
        'TE:yabs-2.0:YABS_SERVER_60_CS_EXPORT_BANNERS:FULL-CIRCUIT:None',
        'SB:YQL_TASK_DIFF:1212058737',
        'USER:robot-testenv',
    ))
    result = gsid_info(text)
    [error] = result.pop('_errors', None)
    assert result == dict(
        _raw=text,
        sandbox=[
            dict(
                task_id=1212058737,
                task_type='YQL_TASK_DIFF',
                user='robot-testenv',
            ),
        ],
        svn_diff=[9128800, 9130947],
    )
    assert error['word'] == 'TE:yabs-2.0:YABS_SERVER_60_CS_EXPORT_BANNERS:FULL-CIRCUIT:None'
