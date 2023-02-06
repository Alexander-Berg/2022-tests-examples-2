import collections

import pytest


@pytest.fixture
def verify_file_paths(static_dir,
                      _verified_static_dirs, get_all_static_file_paths):
    def _verify(verifier, check_name, text_at_fail):
        if check_name in _verified_static_dirs[static_dir]:
            return
        for file_path in get_all_static_file_paths():
            if not verifier(file_path):
                pytest.fail(
                    '%s %s' % (file_path, text_at_fail),
                )
        _verified_static_dirs[static_dir].add(check_name)

    return _verify


@pytest.fixture(scope='session')
def _verified_static_dirs():
    return collections.defaultdict(set)
