from subprocess import Popen  # pylint: disable=import-only-modules
from typing import List
from typing import NamedTuple
from typing import Sequence

import pytest

import olap_release
from tests.utils import repository
from tests.utils.examples import backend_py3


class Params(NamedTuple):
    commits: Sequence[repository.Commit]
    changed_files: List = []


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                commits=[
                    repository.Commit(
                        'commit',
                        [
                            'services/taxi-adjust/file.xmla',
                            'services/taxi-adjust/folder/Order.xmla',
                            'services/taxi-adjust/folder/some',
                            'services/new_service/debian/changelog',
                            'services/new_service/service.yamml',
                            'services/new_service/service.xmla',
                            'Makefile.imports',
                        ],
                    ),
                ],
                changed_files=[
                    'services/taxi-adjust/file.xmla',
                    'services/taxi-adjust/folder/Order.xmla',
                ],
            ),
            id='changes-with-xmla',
        ),
        pytest.param(
            Params(
                commits=[
                    repository.Commit(
                        'commit',
                        [
                            'services/new_service/debian/changelog',
                            'services/new_service/service.yaml',
                            'Makefile.imports',
                        ],
                    ),
                ],
            ),
            id='changes-without-xmla',
        ),
    ],
)
def test_check_service_changes(
        tmpdir, chdir, monkeypatch, startrek, params: Params,
):
    repo = backend_py3.init(tmpdir)
    monkeypatch.setattr('subprocess.Popen', Popen)
    monkeypatch.setenv('CUBE_NAME', 'taxi-adjust')
    monkeypatch.setenv('DEBIAN_PACKAGE_DIR', 'services/taxi-adjust/')
    chdir(repo.working_tree_dir)
    repository.apply_commits(repo, params.commits)
    monkeypatch.setenv('BUILD_VCS_NUMBER', repo.git.rev_parse('HEAD'))
    repo.git.checkout('masters/taxi-adjust')

    if not params.changed_files:
        with pytest.raises(olap_release.NoChangedFilesError):
            olap_release.main()
        return
    assert (
        olap_release.get_changed_files()
        == '\n'.join(params.changed_files) + '\n'
    )

    olap_release.main()
    assert len(startrek.create_comment.calls) == 1
