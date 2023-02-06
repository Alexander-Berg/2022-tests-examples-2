import io
import pytest
import yatest.common

import sandbox.projects.common.yabs.server.util.libs.filter_record as filter_record


YABS_FILTER_RECORD_EXECUTABLE = 'pack/yabs-filter-record'
IN_FILE = 'undecoded_response'
OUT_FILE = 'decoded_response'


class TestFilterRecord(object):
    @pytest.mark.parametrize('binary', (True, False))
    def test_filter_record(self, binary):
        decoder = filter_record.YabsFilterRecord(filter_binary_path=YABS_FILTER_RECORD_EXECUTABLE)
        with open(IN_FILE, 'r' + ('b' if binary else '')) as f:
            string_to_decode = f.read()
        with io.open(OUT_FILE, 'w' + ('b' if binary else '')) as f:
            result = decoder.decode(string_to_decode)
            if binary:
                result = result.encode('utf-8')
            f.write(result)
        return yatest.common.canonical_file(OUT_FILE)
