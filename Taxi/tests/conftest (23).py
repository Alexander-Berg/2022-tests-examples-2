import os
import pathlib
import subprocess
from typing import Dict
from typing import Union

import pytest


@pytest.fixture
def make_dir_tree():
    def make_tree(tree: Dict[str, Union[Dict, str]], root_path: pathlib.Path):
        def run(tree: Dict[str, Union[Dict, str]], root_path: pathlib.Path):
            for sub_path, value in tree.items():
                if isinstance(value, dict):
                    run(value, root_path / sub_path)
                elif isinstance(value, str):
                    if sub_path.endswith('.symlink'):
                        root_path.joinpath(sub_path).symlink_to(value)
                    else:
                        root_path.mkdir(parents=True, exist_ok=True)
                        root_path.joinpath(sub_path).write_text(value)

        run(tree, root_path)

        for top, dirs, _ in os.walk(root_path, topdown=False):
            if '/.git' in top:
                continue

            if '.git' in dirs:
                subprocess.run(
                    ['git', 'init', '--quiet'],
                    stdout=subprocess.PIPE,
                    encoding='utf-8',
                    check=True,
                    cwd=root_path.resolve(),
                )
                subprocess.run(
                    ['git', 'add', '.'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    encoding='utf-8',
                    check=True,
                    cwd=top,
                )

                subprocess.run(
                    ['git', 'commit', '-m', '"init commit"'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    encoding='utf-8',
                    check=True,
                    cwd=top,
                )

    return make_tree


@pytest.fixture
def tmp_path(tmpdir):
    return pathlib.Path(tmpdir)
