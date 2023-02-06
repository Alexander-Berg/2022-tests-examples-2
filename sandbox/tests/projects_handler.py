from __future__ import absolute_import

import pytest

from sandbox import common


class TestProjectsHandler(object):
    @pytest.mark.usefixtures("sandbox_tasks_dir")
    def test__task_type_relative_path(self):
        common.projects_handler.load_project_types(raise_exceptions=True)
        task_code_path = common.projects_handler.task_type_relative_path("TEST_TASK")
        assert task_code_path == "projects/sandbox/test_task/__init__.py"
