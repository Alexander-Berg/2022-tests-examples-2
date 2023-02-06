import os
import pytest

from scripts.ci import lint_precommit as lp


def test_get_staged_files():
    assert ['main.yml'] == lp.filter_staged_files(['modified: main.yml', ''])


def test_get_py_files():
    assert ['script.py'] == lp.get_py_files(['main.yml', 'script.py', ''])


_PY_FILE_NAME = '_to_test_lint_failed.py'
_PY_FILE_TEXT = '''
def main(arg):
    pass
'''

def test_lint_staged_failed():
    # . create py file
    name = _PY_FILE_NAME
    with open(_PY_FILE_NAME, 'w') as f:
        f.write(_PY_FILE_TEXT)
    # . launch linter on staged changes
    lp.cmd(f'arc add {name}')
    with open('/dev/null', 'w') as f:
        with pytest.raises(SystemExit) as e:
            lp.lint(stdout=f)
            # lp.lint()
    # . check if it's pylint who failed
    assert e.value.code > 2
    # . cleanup
    os.remove(name)
    lp.cmd(f'arc add {name}')


def test_lint_changed_failed():
    # . create py file
    name = _PY_FILE_NAME
    with open(_PY_FILE_NAME, 'w') as f:
        f.write(_PY_FILE_TEXT)
    with open('/dev/null', 'w') as f:
        with pytest.raises(SystemExit) as e:
            lp.lint(mode=lp.MODE_CHANGED, stdout=f)
    # . check if it's pylint who failed
    assert e.value.code > 2
    # . cleanup
    os.remove(name)
