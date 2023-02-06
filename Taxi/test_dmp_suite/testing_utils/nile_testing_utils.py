import sys
import json
import logging
import datetime

from nile.local.format import DataFormat, record_from_dict_fast
from dmp_suite import datetime_utils as dtu
from dmp_suite.string_utils import ensure_utf8, to_bytes
from os import path
from io import BytesIO

from nile.api.v1.local import (
    DataSource,
    FileSource,
    DataSink,
    FileSink,
    ListSink,
    JsonFormat as NileJsonFormat,
)


from dmp_suite.file_utils import from_same_directory
from dmp_suite.test_utils import DmpTestCase

logger = logging.getLogger(__name__)


class JSONEncoderWithDatetime(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return dtu.format_datetime(o)


def _get_records(source):
    source.prepare()
    return list(source.get_stream())


def to_bytes_recursive(d):
    def _to_bytes(val):
        if isinstance(val, dict):
            return {
                _to_bytes(key): _to_bytes(value)
                for key, value in val.items()
            }
        if isinstance(val, list):
            return list(map(_to_bytes, val))
        if isinstance(val, tuple):
            return tuple(map(_to_bytes, val))
        if isinstance(val, str):
            return to_bytes(val)
        else:
            return val

    return _to_bytes(d)


class JsonFileFormat(DataFormat):
    """
    Формат, поддерживающий сериализацию/десериализацию записей в/из JSON список.
    """

    def __init__(self, encoding='utf8', ensure_ascii=False, sort_keys=True, read_as_bytes=False):
        """
        :param encoding: pass to json.dumps/loads
        :param ensure_ascii: pass to json.dumps
        :param sort_keys: pass to json.dumps
        :param read_as_bytes: emulate nile job mode bytes_decode_mode= 'never'
        """
        self._encoding = encoding
        self._ensure_ascii = ensure_ascii
        self.sort_keys = sort_keys
        self.read_as_bytes = read_as_bytes

    def serialize(self, records, stream):
        try:
            data = [ensure_utf8(r.to_dict()) for r in records]
            serialized = json.dumps(data, sort_keys=self.sort_keys)
            stream.write(serialized.encode('u8'))
        except ValueError as err:
            raise ValueError('Wrong file format: {}'.format(err))

    def deserialize(self, stream):
        json_str = stream.read() or '[]'
        for item in json.loads(json_str, encoding=self._encoding):
            if self.read_as_bytes:
                item = to_bytes_recursive(item)
            yield record_from_dict_fast(item)


class JsonFormatPy3(NileJsonFormat):
    """
    JsonFormat for py3.

    Mocks the behaviour of `bytes_decode_mode == 'strict'`: decode data
    reading it from a cluster and encode it before dump.
    """
    name = 'decoded_json'

    def deserialize(self, stream):
        # `readlines` is not a part of the nile public api, and
        # maybe we should remove it
        from nile.local.format import readlines, NEWLINE

        for line in readlines(stream):
            yield record_from_dict_fast(
                json.loads(
                    line.rstrip(NEWLINE),
                    encoding=self._encoding,
                )
            )


class NileJobTestCase(DmpTestCase):
    """A helper for writing local Nile job tests."""

    file_format = JsonFormatPy3()

    maxDiff = None

    def get_serializer(self):
        if isinstance(self.file_format, str):
            serializer = DataFormat.get_default_format_by_name(self.file_format)
        else:
            serializer = self.file_format
        return serializer

    def prepare_output(self, output):
        """
        todo: нужно оптимизировать, хак для рекурсивного кодирования и сортировки ключей
        :param output:
        :return:
        """
        flo = BytesIO()
        serializer = self.get_serializer()
        serializer.serialize(output, flo)
        if logger.isEnabledFor(logging.DEBUG):
            flo.seek(0)
            text = flo.read()
            logger.debug('#actual: \n%s', text)
        flo.seek(0)
        return serializer.deserialize(flo)

    def assertCorrectLocalRun(self, job, sources, expected_sinks, allow_arbitrary_order=True):
        """
        Run the job locally and validate the sink outputs.

        :param sources: a mapping from source labels to input sources
        :param expected_sinks: a mapping from sink labels to expected output *sources*
        :param allow_arbitrary_order: flag about pre-comparison sorting of given
               sources/expected_sinks will (default) or will not
               (useful when transformation sorting in test) be executed

        Any source can be provided by a `nile.api.v1.local.DataSource` instance
        or just by a filename relative to the 'your_test_case.py/data' subdirectory.
        """
        sink_outputs = {
            label: []
            for label in expected_sinks
        }
        self._local_run(
            job,
            sources=sources,
            sinks={
                label: ListSink(sink_output)
                for label, sink_output in sink_outputs.items()
            }
        )
        expected_sink_outputs = {
            label: _get_records(self._resolve_source(source))
            for label, source in expected_sinks.items()
        }

        for sink, output in sink_outputs.items():
            if allow_arbitrary_order:
                output = self.prepare_output(sorted(output))
                expected_output = sorted(expected_sink_outputs[sink])
            else:
                output = self.prepare_output(output)
                expected_output = expected_sink_outputs[sink]

            self.assert_records_equal(expected_output, output)

    @classmethod
    def _local_run(cls, job, sources, sinks):
        sinks_dict = {
            label: cls._resolve_sink(sink)
            for label, sink in sinks.items()
        }
        job.local_run(
            sources={
                label: cls._resolve_source(source)
                for label, source in sources.items()
            },
            sinks=sinks_dict,
        )

    @classmethod
    def _resolve_source(cls, source_reference):
        if isinstance(source_reference, str):
            test_case = sys.modules[cls.__module__].__file__
            return FileSource(
                from_same_directory(test_case, path.join("data", source_reference)),
                cls.file_format
            )
        if not isinstance(source_reference, DataSource):
            raise TypeError(
                "'{.__class__.__name__}' object"
                " is not a source".format(source_reference)
            )
        return source_reference

    @classmethod
    def _resolve_sink(cls, sink_reference):
        if isinstance(sink_reference, str):
            test_case = sys.modules[cls.__module__].__file__
            return FileSink(
                from_same_directory(test_case, path.join("data", sink_reference)),
                cls.file_format
            )
        if not isinstance(sink_reference, DataSink):
            raise TypeError(
                "'{.__class__.__name__}' object"
                " is not a sink".format(sink_reference)
            )
        return sink_reference
