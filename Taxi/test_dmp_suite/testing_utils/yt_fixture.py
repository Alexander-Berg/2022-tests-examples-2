import datetime
import abc
import os
import logging
import json
from typing import Iterator, Optional, Text, Union, Any, IO, Type

from yt.wrapper.format import create_format, yson

from dmp_suite import datetime_utils as dtu
from dmp_suite.string_utils import to_unicode
from dmp_suite.yt.table import Table
from dmp_suite.yt.meta import YTMeta, resolve_meta
from dmp_suite.yt import operation as op, etl
from dmp_suite.yt.dyntable_operation.operations import temporarily_unmounted_target

logger = logging.getLogger(__name__)


class SerializerBase(abc.ABC):
    @abc.abstractmethod
    def load(self, file_like_object):  # type: (IO) -> Iterator
        raise NotImplementedError()

    @abc.abstractmethod
    def dump(self, data, file_like_object):  # type: (Any, IO) -> IO
        raise NotImplementedError()

    @abc.abstractmethod
    def file_extension(self):  # type: () -> Text
        raise NotImplementedError()


class JsonSerializer(SerializerBase):
    def __init__(self, encoding='utf8', ensure_ascii=False, sort_keys=True, indent=None):
        self._encoding = encoding
        self._ensure_ascii = ensure_ascii
        self._indent = indent
        self.sort_keys = sort_keys

    def dump(self, data, file_like_object):
        json.dump(
            data,
            file_like_object,
            ensure_ascii=self._ensure_ascii,
            sort_keys=self.sort_keys,
            indent=self._indent,
        )

    def load(self, file_like_object):
        for line in json.load(file_like_object, encoding=self._encoding):
            yield line

    def file_extension(self):  # type: () -> Text
        return 'json'


class YtSerializer(SerializerBase):
    def __init__(self, yson_name):
        """
        Creates serializer by YSON string
        :param yson_name: YSON string like ``'<lenval=false;has_subkey=false>yamr'``.
        """
        self.yt_serializer = create_format(yson_name)
        self._file_extension = str(yson._loads_from_native_str(yson_name))

    def dump(self, data, file_like_object):
        self.yt_serializer.dump_rows(data,  file_like_object)

    def load(self, file_like_object):
        return self.yt_serializer.load_rows(file_like_object)

    def file_extension(self):
        return self._file_extension


class YtFixture(object):
    PATH_SPLITTER = '__'

    def __init__(self, table,  # type: Union[Type[Table], YTMeta]
                 file_folder,  # type: Text
                 custom_file_name=None,  # type: Optional[Text]
                 custom_target_path=None,  # type:  Optional[Text],
                 serializer='json',  # type: Union[SerializerBase, Text]
                 ):
        if isinstance(serializer, str):
            self.serializer = YtSerializer(to_unicode(serializer))
            self.raw_mode = True
        else:
            self.serializer = serializer
            self.raw_mode = False

        self.file_folder = file_folder
        if isinstance(table, YTMeta):
            self.meta = table
        else:
            self.meta = YTMeta(table)
            if self.meta.partition_scale and not all([custom_file_name, custom_target_path]):
                raise ValueError(
                    'Table {} has partition scale, use YTMeta for set period.'.format(self.meta.table.__name__))

        self.file_name = custom_file_name or self.file_name_by_meta()
        self.target_path = custom_target_path or self.meta.target_path()

    @property
    def file_full_path(self):
        return os.path.join(self.file_folder, self.file_name)

    @classmethod
    def yt_path_to_file_name(cls, path):
        if cls.PATH_SPLITTER in path:
            raise ValueError('Found the splitter {} in path {}'.format(cls.PATH_SPLITTER, path))
        return path.strip('/').replace('/', cls.PATH_SPLITTER)

    def file_name_by_meta(self):
        if isinstance(self.serializer, str):
            # TODO: вроде эта ветка никогда не должна выполняться,
            #       потому что в конструкторе self.serializer всегда устанавливается в объект
            ext = to_unicode(self.serializer)
        else:
            ext = self.serializer.file_extension()

        relative_path = self.meta.target_path()[len(self.meta.target_prefix):]
        return '{}.{}'.format(self.yt_path_to_file_name(relative_path), ext)

    def read_file(self):
        logger.debug('read from file: {}'.format(self.file_full_path))
        with open(self.file_full_path, mode='r') as file_:
            if self.raw_mode:
                for item in file_:
                    yield item
            else:
                for item in self.serializer.load(file_):
                    yield item

    def write_file(self, data, force=False):
        full_path = self.file_full_path
        if not force and os.path.exists(full_path):
            raise ValueError('File exists: {}'.format(full_path))
        logger.debug('write file: {}'.format(full_path))
        with open(full_path, 'w') as file_:
            if self.raw_mode:
                file_.writelines(data)
            else:
                self.serializer.dump(list(data), file_)
        logger.debug('write complete')

    def read_yt(self):
        logger.debug('read table: {}'.format(self.target_path))
        if self.raw_mode:
            for item in op.read_yt_table(self.target_path, unordered=False, raw=True,
                                         format=self.serializer.file_extension()):
                yield item
        else:
            for item in op.read_yt_table(self.target_path, raw=False, unordered=False):
                yield item

    def write_yt(self, data, force=False, sort=False):
        if not force and op.yt_path_exists(self.target_path):
            raise ValueError('Table already exist: {}'.format(self.target_path))
        etl.init_target_table(self.meta)
        logger.debug('write yt table: {}'.format(self.target_path))
        if self.raw_mode:
            op.write_yt_table(self.target_path, data, raw=True, format=self.serializer.file_extension())
        else:
            if sort:
                etl.init_buffer_table(self.meta)
                op.write_yt_table(self.meta.buffer_path(), data)
                etl.buffer_to_rotation(self.meta)
                etl.rotation_to_target(self.meta)
            else:
                if not self.meta.is_dynamic:
                    op.write_yt_table(self.target_path, data)
        logger.debug('upload complete')

    def file_to_yt(self, force=False, sort=False):
        logger.debug('upload file to yt')
        self.write_yt(self.read_file(), force=force, sort=sort)

    def yt_to_file(self, force=False):
        self.write_file(self.read_yt(), force=force)


def get_fixtures_for_period(tables,  # type: Iterator[Union[Type[Table], YtFixture, YTMeta]]
                            file_folder,  # type: Text
                            start_date,  # type:  Union[Text, datetime.datetime]
                            end_date,  # type:  Union[Text, datetime.datetime]
                            serializer  # type: Text
                            ):  # type: (...) -> Iterator[YtFixture]
    fixtures = []
    for item in tables:
        if isinstance(item, YtFixture):
            fixtures.append(item)
            continue

        meta = resolve_meta(item)
        if meta.has_partition_scale:
            for partition in meta.partition_scale.split_in_partitions(dtu.period(start_date, end_date)):
                meta = YTMeta(item, partition=partition)
                fixtures.append(YtFixture(meta, file_folder, serializer=serializer))
        else:
            fixtures.append(YtFixture(meta, file_folder, serializer=serializer))
    return fixtures
