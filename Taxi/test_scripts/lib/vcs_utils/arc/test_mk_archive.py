import os
import zipfile

import pytest

from scripts.lib.vcs_utils import arc


@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) fail on build agents'
    ),
)
@pytest.mark.enable_raw_arc_client
async def test_missing_directory(tmp_path, arc_mock, scripts_app):
    arc_mock_ = arc_mock(tmp_path)
    arc_mock_.mk_dir('taxi/infra/tools-py3/some_service')
    arc_mock_.write_file(
        'taxi/infra/tools-py3/some_service/some.py', 'print(1)',
    )
    arc_mock_.mk_dir('taxi/infra/tools-py3/another_service')
    arc_mock_.write_file(
        'taxi/infra/tools-py3/another_service/some.py', 'print(1)',
    )
    arc_mock_.mk_dir('taxi/infra/tools-py3/libraries')
    arc_mock_.write_file('taxi/infra/tools-py3/libraries/__init__.py', '')

    arc_client = arc.Arc(scripts_app, arc_mock_.root_dir)
    arc_client.update_work_dir('taxi', 'infra/tools-py3')
    await arc_client.mk_archive(
        extra_paths=['libraries', 'some_service', 'non-existing'],
    )
    with zipfile.ZipFile(arc_client.arch_path) as zip_file:
        zip_info_list = zip_file.infolist()
    assert len(zip_info_list) == 2
    assert [x.filename for x in zip_info_list] == [
        'taxi/infra/tools-py3/libraries/__init__.py',
        'taxi/infra/tools-py3/some_service/some.py',
    ]
