import os
import yatest.common as tc

from sandbox.sdk2.helpers import coredump_filter

_TEST_DATA_SOURCE_PATH = 'sandbox/sdk2/helpers/coredump_filter/tests/data'
_TEST_CASES_AMOUNT = 13


class MockStream:
    def __init__(self):
        self._store = []

    def write(self, payload):
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        assert isinstance(payload, str)
        self._store.append(payload)

    @property
    def get(self):
        return ''.join(self._store)


def _read_file(file_name):
    with open(file_name) as f:
        return f.read()


def _write_file(file_name, contents):
    with open(file_name, 'w') as f:
        f.write(contents)


def test_fingerprint():
    data_dir = tc.source_path(_TEST_DATA_SOURCE_PATH)
    canonical_files = {}

    for test_case_id in range(1, _TEST_CASES_AMOUNT + 1):
        base_name = 'test{}.txt'.format(test_case_id)
        stack_file_name = os.path.join(data_dir, base_name)

        fp_name = '{}.fp'.format(base_name)
        html_name = '{}.html'.format(base_name)

        full_fp_name = tc.output_path(fp_name)
        full_html_name = tc.output_path(html_name)
        timestamp = '@@timestamp-for-tests@@'

        coredump_mode = coredump_filter.detect_coredump_mode(_read_file(stack_file_name))
        ignore_bad_frames = coredump_mode == coredump_filter.CoredumpMode.SDC_ASSERT

        # Test fingerprinting
        stream_fingerprint = MockStream()
        coredump_filter.filter_stack_dump(
            stack_file_name=stack_file_name,
            use_fingerprint=True,
            output_stream=stream_fingerprint,
            timestamp=timestamp,
            ignore_bad_frames=ignore_bad_frames,
        )
        fingerprint = stream_fingerprint.get
        _write_file(full_fp_name, fingerprint)
        canonical_files[fp_name] = tc.canonical_file(full_fp_name)

        # Test HTML output
        stream_html = MockStream()
        coredump_filter.filter_stack_dump(
            stack_file_name=stack_file_name,
            use_fingerprint=False,
            output_stream=stream_html,
            timestamp=timestamp,
            ignore_bad_frames=ignore_bad_frames,
        )
        html = stream_html.get
        _write_file(full_html_name, html)
        canonical_files[html_name] = tc.canonical_file(full_html_name)

        # test obsolete interface, for backwards compatibility
        stream_old_iface = MockStream()
        coredump_filter.filter_stackdump(
            file_lines=_read_file(stack_file_name).split('\n'),
            use_fingerprint=True,
            stream=stream_old_iface,
            ignore_bad_frames=ignore_bad_frames,
            mode=coredump_mode,
        )

        if coredump_mode == coredump_filter.CoredumpMode.LLDB:
            assert stream_old_iface.get == stream_fingerprint.get

        # test packing and unpacking
        core_parsed, raw_core, signal = coredump_filter.filter_stack_dump(core_text=_read_file(stack_file_name))
        stack_groups_str = coredump_filter.serialize_stacks(core_parsed)
        stack_groups = coredump_filter.deserialize_stacks(stack_groups_str)
        assert len(core_parsed) == len(stack_groups)
        assert core_parsed[0][0].important == stack_groups[0][0].important
        assert stack_groups[0][0].important > 50  # first stack must be important

    return canonical_files


def test_old_iface():
    data_dir = tc.source_path(_TEST_DATA_SOURCE_PATH)

    test_case_id = 1
    timestamp = '@@timestamp-for-tests@@'
    base_name = 'test{}.txt'.format(test_case_id)
    stack_file_name = os.path.join(data_dir, base_name)
    stream_html = MockStream()
    coredump_filter.filter_stackdump(
        file_name=stack_file_name,
        use_fingerprint=False,
        stream=stream_html,
        timestamp=timestamp,
        ignore_bad_frames=False,
    )
