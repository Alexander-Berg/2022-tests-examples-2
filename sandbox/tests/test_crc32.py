import pytest  # noqa

import sandbox.projects.quasar.utils as utils


def test_big_file():
    file_name = "big_file"
    with open(file_name, "wb") as write_file:
        write_file.write(b'a' * (1 << 31))
    assert utils.get_crc_32(file_name) != 0
