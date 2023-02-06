import pytest

from sandbox.projects.yabs.bases.YabsServerMakeBinBases import collect_metrics
from sandbox.projects.yabs.qa.utils import task_run_type


class TestCollectMetrics:
    def test_collect_metrics(self):
        reused_bases = ['reused_base']
        generated_bases = ['generated_base']
        run_type = task_run_type.RunType.ONESHOT_TEST
        testenv_database = 'yabs'
        expected_metrics = [
            {
                'labels': {
                    'sensor': 'reuse',
                    'base_tag': 'reused_base',
                    'status': 'reused',
                    'run_type': 'oneshot_test',
                    'testenv_database': 'yabs',
                },
                'value': 1,
            },
            {
                'labels': {
                    'sensor': 'reuse',
                    'base_tag': 'reused_base',
                    'status': 'not_reused',
                    'run_type': 'oneshot_test',
                    'testenv_database': 'yabs',
                },
                'value': 0,
            },
            {
                'labels': {
                    'sensor': 'reuse',
                    'base_tag': 'generated_base',
                    'status': 'reused',
                    'run_type': 'oneshot_test',
                    'testenv_database': 'yabs',
                },
                'value': 0,
            },
            {
                'labels': {
                    'sensor': 'reuse',
                    'base_tag': 'generated_base',
                    'status': 'not_reused',
                    'run_type': 'oneshot_test',
                    'testenv_database': 'yabs',
                },
                'value': 1,
            }
        ]

        assert collect_metrics(reused_bases, generated_bases, run_type, testenv_database) == expected_metrics

    @pytest.mark.parametrize(('run_type', 'expected_run_type_label'), [
        (task_run_type.RunType.ONESHOT_TEST, 'oneshot_test'),
        (task_run_type.RunType.CONTENT_SYSTEM_SETTINGS_CHANGE_TEST, 'content_system_settings_change_test'),
        (task_run_type.RunType.CREATE_ONESHOT_SPEC, 'create_oneshot_spec'),
        (task_run_type.RunType.PRECOMMIT_CHECK, 'precommit_check'),
        (task_run_type.RunType.COMMIT_CHECK, 'commit_check'),
        (None, 'unknown'),
    ])
    def test_run_type(self, run_type, expected_run_type_label):
        reused_bases = ['reuse_base']
        generated_bases = ['generated_base']
        metrics = collect_metrics(reused_bases, generated_bases, run_type=run_type)
        for item in metrics:
            assert item['labels']['run_type'] == expected_run_type_label

    def test_testenv_database(self):
        reused_bases = ['reuse_base']
        generated_bases = ['generated_base']
        testenv_database = 'db'
        metrics = collect_metrics(reused_bases, generated_bases, testenv_database=testenv_database)
        for item in metrics:
            assert item['labels']['testenv_database'] == testenv_database

    def test_no_optional_args(self):
        reused_bases = ['reuse_base']
        generated_bases = ['generated_base']
        metrics = collect_metrics(reused_bases, generated_bases)
        for item in metrics:
            assert item['labels']['run_type'] == 'unknown'
            assert 'testenv_database' not in item['labels']
