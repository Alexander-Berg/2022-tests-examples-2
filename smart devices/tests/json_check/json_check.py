from pathlib import Path

import pytest
import yatest.common as yc


class Config:
    def __init__(self):
        json_files_inc = Path(yc.source_path('smart_devices/packages/tests/json_check/json_files.inc'))
        raw_lines = [
            line.strip()
            for line in json_files_inc.read_text().splitlines()
        ]
        self.paths = sorted(
            line[8:] for line in raw_lines  # len('arcadia/') == 8
            if line.startswith('arcadia/')
        )


CONFIG = Config()


@pytest.mark.parametrize('json_file_path', CONFIG.paths)
def test_json(json_file_path):
    json_file_check_path = yc.binary_path('smart_devices/tools/json_file_check/json_file_check')

    yc.execute(
        [json_file_check_path, yc.source_path(json_file_path)],
    )
