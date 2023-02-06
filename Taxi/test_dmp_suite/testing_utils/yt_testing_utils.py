import os
import logging

from io import StringIO

from functools import partial
from itertools import chain
from typing import Callable, Text, Iterator, Type, Union
from unittest import TestCase
from inspect import getabsfile
from dmp_suite.yt import Table
from .yt_fixture import YtFixture, get_fixtures_for_period, JsonSerializer, SerializerBase
from .depersonalization import Depersonalization

logger = logging.getLogger(__name__)


class YtLoaderTestCase(TestCase):
    def assert_loader_result(self,
                             loader,  # type: Callable
                             sources,  # type: Iterator[YtFixture]
                             expected  # type: Iterator[YtFixture]
                             ):
        for fixture in sources:
            fixture.file_to_yt(force=True)

        sorted_dicts = partial(sorted, key=lambda d: sorted(d.items()))

        loader()
        for expect_fixture in expected:
            if expect_fixture.raw_mode:
                expect = sorted_dicts(expect_fixture.serializer.load(expect_fixture.read_file()))
                actual = sorted_dicts(expect_fixture.serializer.load(expect_fixture.read_yt()))
            else:
                actual = list(expect_fixture.read_yt())
                if actual:
                    # hack for sync formats
                    buf = StringIO()
                    expect_fixture.serializer.dump(actual, buf)
                    buf.seek(0)
                    actual = sorted_dicts(expect_fixture.serializer.load(buf))

                else:
                    actual = sorted(actual)
                expect = sorted_dicts(expect_fixture.read_file())
            self.assertEqual(expect, actual)


class PeriodYtLoaderTest(YtLoaderTestCase):
    start_date = None  # type: Text
    end_date = None  # type: Text
    folder = None  # type: Text  # e.g. 'data/dm_order'
    sources_tables = None  # type: Iterator[Type[Table]]
    expected_tables = None  # type: Iterator[Type[Table]]
    serializer = JsonSerializer(indent=1)  # type: Union[Text, SerializerBase]

    @classmethod
    def get_sources(cls):  # type: () -> Iterator[YtFixture]
        return get_fixtures_for_period(cls.sources_tables, cls.abs_folder(), cls.start_date, cls.end_date,
                                       serializer=cls.serializer)

    @classmethod
    def get_expected(cls):  # type: () -> Iterator[YtFixture]
        return get_fixtures_for_period(cls.expected_tables, cls.abs_folder(), cls.start_date, cls.end_date,
                                       serializer=cls.serializer)

    @classmethod
    def abs_folder(cls):  # type: () -> Text
        return os.path.join(os.path.dirname(getabsfile(cls)), cls.folder)


def depersonalization_yt(test_case):  # type: (PeriodYtLoaderTest) -> None
    for fixture in test_case.get_sources():
        if fixture.raw_mode:
            raise ValueError('Raw mode not support')
        items = fixture.read_yt()
        items, replaced = Depersonalization().replace_inplace(list(items))

        if replaced:
            logger.debug('depersonalized table %s, upload it', fixture.target_path)
            if fixture.meta.has_sort_keys:
                logger.debug('sorting table %s', fixture.target_path)
                items = sorted(items, key=lambda i: [i.get(field_name) for field_name in fixture.meta.sort_key_names()])
            else:
                items = list(items)
            fixture.write_yt(items, force=True)


def download_fixture_from_yt(test_case, force=False):  # type: (Type[PeriodYtLoaderTest], bool) -> None
    for fixture in chain(test_case.get_sources(), test_case.get_expected()):
        fixture.yt_to_file(force=force)
