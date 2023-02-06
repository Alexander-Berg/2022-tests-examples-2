import os
import pytest

import modules.common as common


class Testcommon(object):
    def test_read_syscall_output(self):
        assert "ping" in common.read_syscall_output("/bin/echo ping"), \
            "ping output doestn't found in 'echo ping' command"

    def test_get_syscall_exit_code(self):
        assert common.get_syscall_exit_code("/bin/echo ping") == 0, \
            "return non zero exit code"
        assert common.get_syscall_exit_code("/not_exist_dir/not_exist_file"), \
            "return successful status code for amazing command"

    def test_convert_dict_into_string(self):
        test_dict = {"testkey": 123, "random": "string"}
        possible_strings = ["testkey 123 random string",
                            "random string testkey 123"]
        assert common.convert_dict_into_string(test_dict) in possible_strings, \
            "convert_dict_into_string return incorrect dict"
