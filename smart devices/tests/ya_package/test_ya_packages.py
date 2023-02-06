import difflib
import logging
import sys

from pathlib import Path

import pytest
import yatest.common as yc

logger = logging.getLogger('test_ya_packages')


class Config:
    def __init__(self):
        self.generate_packages_tool = Path(yc.build_path('smart_devices/packages/generate_packages/generate_packages'))
        self.generated_dir = Path(yc.output_path('generated'))

        self.update_mode = yc.get_param('update')

        try:
            self.generated_dir.mkdir(parents=True)
            yc.execute([self.generate_packages_tool, 'write', self.generated_dir])
        except Exception:
            # Error reporting inside test discovery is weird.
            # Postpone it until an actual test run
            self.exc_info = sys.exc_info()
            self.files = []
        else:
            self.exc_info = None
            self.files = sorted(
                str(path.relative_to(self.generated_dir))
                for path in self.generated_dir.glob('**/*')
                if path.is_file()
            )


CONFIG = Config()


def test_generator_is_ok():
    """Re-raise generator failure inside a test"""

    err = CONFIG.exc_info
    if err is not None:
        raise err[0].with_traceback(err[1], err[2])


@pytest.mark.parametrize('rel_path', CONFIG.files)
def test_generated_package(rel_path):
    src_path = Path(yc.source_path(rel_path))
    gen_path = CONFIG.generated_dir / rel_path

    if CONFIG.update_mode:
        logger.info('update %s: %s from %s', rel_path, src_path, gen_path)
        src_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.write_text(gen_path.read_text())
    else:
        logger.info('check %s: %s vs %s', rel_path, src_path, gen_path)
        diff = list(difflib.context_diff(
            a=src_path.read_text().splitlines(),
            b=gen_path.read_text().splitlines(),
            fromfile=f'src/{rel_path}',
            tofile=f'gen/{rel_path}',
            lineterm='',
        ))
        is_equal = not bool(diff)

        assert is_equal, '\n'.join([
            'Found diff (rerun this test with `--test-param update=1` '
            'to apply changes to Arcadia:'
        ] + diff)
