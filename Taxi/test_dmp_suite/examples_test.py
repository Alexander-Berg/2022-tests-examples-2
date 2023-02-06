import os
import sys
import pathlib
import subprocess
import json

import sources_root


def walk(module, root_path):
    for obj in os.listdir(root_path):
        if obj == '__pycache__':
            continue
        current_path = root_path / obj
        current_module = f'{module}.{obj}'.rstrip('.py')
        if current_path.is_dir():
            yield from walk(current_module, current_path)
        else:
            if current_path.is_file() and str(current_path).endswith('.py'):
                yield current_module


def test_all_examples():
    root_module = 'examples'
    source_root_path = pathlib.Path(sources_root.SOURCES_ROOT)
    dmp_suite_path = source_root_path / 'dmp_suite'
    examples_path = dmp_suite_path / root_module

    env = os.environ.copy()
    env['TAXIDWH_ENV_CONFIG'] = json.dumps({
        'ctl': {
            'storage_type': 'dict',
        },
        'luigi': {
            'local_scheduler': True,
        },
    })

    for module in walk(root_module, examples_path):
        cmd = [sys.executable, '-m', module]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            cwd=dmp_suite_path,
            env=env,
        )
        stdout, stderr = proc.communicate()
        assert proc.returncode == 0, (
            f'Error in executing `{" ".join(cmd)}:\n{stderr.decode("u8")}'
        )
