import os
import pytest
import random
import six.moves

import sandbox.projects.common.yabs.server.util.libs.delimited as delimited

TEST_FILE_FILENAME = 'temp_test_file_filename'


def generate_test_line(length, excluded_chars, binary=False):
    char_list = []
    list_length = 0
    while list_length < length:
        char = chr(random.randrange(256))
        if char not in excluded_chars:
            char_list.append(char)
            list_length += 1
    result = ''.join(char_list)
    return six.b(result) if binary else result


def generate_test_string(num_of_lines, len_of_line, delimiter, binary=False):
    test_line_list = [generate_test_line(len_of_line, delimiter, binary) for _ in six.moves.xrange(num_of_lines)]
    delimiter = six.b(delimiter) if binary else delimiter
    return delimiter.join(test_line_list) + delimiter, test_line_list


class TestDelimited(object):
    @pytest.mark.parametrize('num_of_lines', (1, 10, 100))
    @pytest.mark.parametrize('len_of_line', (1, 1000, 5000))
    @pytest.mark.parametrize('delimiter', (
        '\r',
        '\r\n',
        '\r\n\r\n\n'
    ))
    @pytest.mark.parametrize('binary', (True, False))
    def test_delimited(self, num_of_lines, len_of_line, delimiter, binary):
        open_kwargs = dict(newline='') if six.PY3 and not binary else {}
        with open(TEST_FILE_FILENAME, 'w' + ('b' if binary else ''), **open_kwargs) as f:
            test_string, test_list = generate_test_string(num_of_lines, len_of_line, delimiter, binary)
            assert len(test_list) == num_of_lines
            f.write(test_string)
        with open(TEST_FILE_FILENAME, 'r' + ('b' if binary else ''), **open_kwargs) as f:
            for index, line in enumerate(delimited.delimited_file_read(f, delimiter)):
                assert line == test_list[index] + (six.b(delimiter) if binary else delimiter)
            assert index == num_of_lines - 1
        os.remove(TEST_FILE_FILENAME)
