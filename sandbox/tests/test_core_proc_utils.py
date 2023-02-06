import os
from sandbox.sdk2.helpers import coredump_filter


def test_coredump_detect_mode():
    import yatest.common

    source_path = yatest.common.source_path('sandbox/sdk2/helpers/coredump_filter/tests/data')
    answers = {
        'typical_lldb_coredump.txt': coredump_filter.CoredumpMode.LLDB,
        'typical_gdb_coredump.txt': coredump_filter.CoredumpMode.GDB,
        'typical_sdcassert_coredump.txt': coredump_filter.CoredumpMode.SDC_ASSERT,
    }
    for filename, mode in answers.items():
        with open(os.path.join(source_path, filename)) as fd:
            core_text = '\n'.join(fd.readlines())
            detected_mode = coredump_filter.detect_coredump_mode(core_text)
            assert detected_mode == mode
