import os

import pytest


class GitMock:
    def __init__(self, path: str):
        assert path
        current_file = __file__
        current_file_name = os.path.splitext(os.path.basename(current_file))[0]
        current_dir = os.path.dirname(current_file)
        static_dir = os.path.join(current_dir, 'static', current_file_name)
        self._repo_path = os.path.join(static_dir, 'infra-cfg-graphs')

    @property
    def working_dir(self):
        return self._repo_path


@pytest.fixture(name='git_infra_graphs_mock')
def _git_infra_graphs_mock(monkeypatch):
    monkeypatch.setattr('git.Repo', GitMock)


@pytest.fixture(name='arc_infra_graphs_mock')
def _arc_infra_graphs_mock(monkeypatch):
    monkeypatch.setattr(
        'dashboards.components.infra_graphs_repo.CACHE_REPO_FOLDER', '/tmp',
    )

    root_dir = '/tmp/arc/infra-cfg-graphs/'
    os.makedirs(root_dir, exist_ok=True)
    yield root_dir
    os.rmdir(root_dir)
