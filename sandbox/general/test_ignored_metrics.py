from sandbox.projects.common.metrics_launch_manager import mlm_analysis as mlma
from sandbox.projects.release_machine.tasks.LaunchMetrics import ignored_metrics


def test_ignored_metrics():
    mlma.verify_ignore_list(ignored_metrics.CRITICAL_METRICS_IGNORE_LIST)
