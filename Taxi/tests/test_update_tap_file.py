import pathlib
from typing import NamedTuple
from typing import Optional

import pytest

from tests.utils.examples import tap
import update_tap_file


class Params(NamedTuple):
    tap_file: str
    content_expected: str
    revision: int
    resources_id: Optional[str] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                tap_file='libyandex-taxi-graph2.rb',
                content_expected="""
VERSION = "1"
RESOURCES_ID = "2;7"

Some code
blah-blah-blah
""".lstrip(),
                revision=1,
                resources_id='2;7',
            ),
            id='change revision and resource id',
        ),
        pytest.param(
            Params(
                tap_file='persqueue-wrapper.rb',
                content_expected="""
VERSION = "999"

Some code too
blah-blah-blah
""".lstrip(),
                revision=999,
            ),
            id='change revision only',
        ),
        pytest.param(
            Params(
                tap_file='libyandex-taxi-graph.rb',
                content_expected="""
VERSION = "555"
RESOURCES_ID = "2;7;1"

Some code
blah-blah-blah
ololo
""".lstrip(),
                revision=555,
                resources_id='2;7;1',
            ),
            id='change several resources id',
        ),
    ],
)
def test_change(tmpdir, params):
    repo = tap.init(tmpdir)
    path_to_repo = repo.working_tree_dir

    args = [
        '--path-to-repo',
        path_to_repo,
        '--revision',
        str(params.revision),
        params.tap_file,
    ]
    if params.resources_id:
        args.extend(['--resources-id', params.resources_id])

    update_tap_file.main(args)

    updated_file = pathlib.Path(tmpdir) / 'repo' / params.tap_file
    assert updated_file.read_text() == params.content_expected
