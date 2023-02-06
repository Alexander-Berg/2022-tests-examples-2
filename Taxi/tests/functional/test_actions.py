import os
import tempfile
from os import listdir
from os.path import isfile, join

from pahtest.file import YmlFile
from pahtest.screenshot import ScreenDir

from .utils import check_with_yml


def test_screenshot():
    # we have permissions inside selenium container there
    with tempfile.TemporaryDirectory() as dir:
        def create_tests(**screenshot_options):
            return YmlFile(
                path='tests/functional/assets/screenshots.yml',
                cli_options={'screenshots': {
                    'dir': dir, 'before': 'none', 'after': 'none',
                    **screenshot_options
                }}
            )

        def list_files():
            if not listdir(dir):
                return []
            def cd_in(dir: str) -> str:
                return join(dir, sorted(listdir(dir))[-1])
            actual_dir = cd_in(cd_in(dir))
            return [
                f for f in sorted(listdir(actual_dir))
                if isfile(join(actual_dir, f)) and f.endswith('.png')
            ]

        # - test result for failed screens dir refresh
        tests = create_tests(dir='/tests_no_permissions/selenium_screenshots')
        results = tests.run()
        assert not results.success, [str(r) for r in results.list]
        assert 'Failed to create screenshots ' in results.notes.list[0].message
        # tests should be launched and have results even with wrong folder

        # - test before all has a screen
        ScreenDir().clear()
        create_tests(before='all').run()
        files = list_files()
        assert len(files) == 3, files
        assert files[0] == f'_before_001_get_ok.png'
        assert files[1] == f'_before_002_has.png'
        assert files[2] == f'_before_003_has.png'

        # - test before none has no screen
        ScreenDir().clear()
        create_tests(before='none', after='none').run()
        assert len(list_files()) == 0

        # - test after all has screen
        ScreenDir().clear()
        create_tests(after='all').run()
        files = list_files()
        assert len(files) == 3, files
        assert files[0] == f'after_001_get_ok.png', files
        assert files[1] == f'after_002_has.png'
        assert files[2] == f'after_003_failed_has.png'

        # - test after none has no screen
        ScreenDir().clear()
        create_tests(after='none').run()
        assert len(list_files()) == 0

        # - test after fail for success test has no screen
        ScreenDir().clear()
        create_tests(after='fail').run()
        files = list_files()
        assert len(files) == 1  # single failed test
        assert files[0] == f'after_003_failed_has.png'

        # - test only before all
        ScreenDir().clear()
        create_tests(before='all').run()
        assert list_files()


def test_env():
    """Env vars with "env:" notation inside the plugins should work."""
    os.environ['SITE_PATH'] = 'base.html'
    os.environ['SITE_WAIT_FOR'] = '/html/body/div'
    try:
        check_with_yml(YmlFile('tests/functional/assets/env.yml'))
    finally:
        os.environ.pop('SITE_PATH')
        os.environ.pop('SITE_WAIT_FOR')
