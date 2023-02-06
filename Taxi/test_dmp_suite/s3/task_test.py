import dataclasses
import pathlib
import tempfile
import typing as tp
from datetime import datetime, date
from decimal import Decimal

import mock
import pandas as pd
import pytest

from dmp_suite.s3 import task as s3_task
from dmp_suite.task import cli
from dmp_suite.task.execution import run_task


@dataclasses.dataclass
class S3:
    bucket_name: str
    object_name: str
    file_name: str
    data: tp.Iterable[tp.Dict]

    def upload_fileobj(self, file_name: str, bucket_name: str, object_name: str):
        assert file_name.endswith(self.file_name)
        assert self.bucket_name == bucket_name
        assert self.object_name == object_name


@dataclasses.dataclass
class Writer(s3_task.FileWriter):
    df: pd.DataFrame
    file_name: str

    def write_file(self, df: pd.DataFrame, file_name: str):
        assert self.df.equals(df)
        assert file_name.endswith(self.file_name)


@dataclasses.dataclass
class WriterWTransform(s3_task.FileWriter):
    df: pd.DataFrame
    file_name: str

    @staticmethod
    def test_transform_df(df):
        df['a'] = df['a'].apply(lambda x: x + 1)
        return df

    def write_file(self, df: pd.DataFrame, file_name: str):
        assert self.test_transform_df(self.df).equals(df)
        assert file_name.endswith(self.file_name)


@dataclasses.dataclass
class DataSource:
    data: tp.Iterable[tp.Dict] = None

    def get_data(self):
        return self.data

    def get_value(self, args, _):
        self.data = args.data
        return self

    def get_sources(self):
        return []


@pytest.mark.parametrize('bucket_name, object_name, object_name_expected, file_name, args', [
    ('test_bucket', 'test.xlsx', 'test.xlsx', 'test.xlsx', dict(data=[dict(a=1)])),
    ('test_bucket', 'test.xlsx', 'test.xlsx', 'test.xlsx', dict(data=[dict(a=1)], date='2020-01-01')),
    ('test_bucket', 'test/{{ date }}.xlsx', 'test/2020-01-01.xlsx', '2020-01-01.xlsx', dict(data=[dict(a=1)], date='2020-01-01')),
    ('test_bucket', '/test/{{ date }}.xlsx', 'test/2020-01-01.xlsx', '2020-01-01.xlsx', dict(data=[dict(a=1)], date='2020-01-01')),
])
def test_upload_excel(bucket_name, object_name, object_name_expected, file_name, args):
    s3 = S3(
        bucket_name=bucket_name,
        object_name=object_name_expected,
        file_name=file_name,
        data=args['data'],
    )
    for func, writer in ((None, Writer(pd.DataFrame(args['data']), file_name)),
                         (WriterWTransform.test_transform_df,
                          WriterWTransform(pd.DataFrame(args['data']), file_name))
                         ):
        with mock.patch('connection.s3.get_client', return_value=s3):
            task = s3_task.upload_file(
                name='test',
                source=tp.cast(s3_task.UploadSource, DataSource()),
                s3_connection='test',
                bucket_name=bucket_name,
                object_name=object_name,
                file_writer=writer,
                transform=func
            ).arguments(
                data=cli.CliArg(''),
                date=cli.Datetime(default=None),
            )
            run_task(task, **args)


def test_excel_writer():
    df = pd.DataFrame([dict(a=1, b=1), dict(a=2, b=2)])
    with tempfile.TemporaryDirectory() as tmp:
        file_name = pathlib.Path() / tmp / 'test.xlsx'
        s3_task.ExcelWriter().write_file(df, file_name)
        assert pd.read_excel(file_name, engine='openpyxl').equals(df)


def test_csv_writer():
    df = pd.DataFrame([dict(a=1, b=1), dict(a=2, b=2)])
    with tempfile.TemporaryDirectory() as tmp:
        file_name = pathlib.Path() / tmp / 'test'
        s3_task.CsvWriter().write_file(df, file_name)
        assert pd.read_csv(file_name).equals(df)


@pytest.mark.parametrize(
    'pk_attrs,xml_row_str',
    [
        ((s3_task.XmlReportRowKey(row_attr='a_pk', column_name='a'),), ' a_pk="string"'),
        (
            (
                s3_task.XmlReportRowKey(row_attr='a_pk', column_name='a'),
                s3_task.XmlReportRowKey(row_attr='b_pk', column_name='b')
            ),
            ' a_pk="string" b_pk="3.14"',
        ),
(
            (
                s3_task.XmlReportRowKey(row_attr='a_pk', column_name='a'),
                s3_task.XmlReportRowKey(row_attr='c_pk', column_name='c')
            ),
            ' a_pk="string" c_pk="2022-01-01 12:00:00"',
        ),
        (tuple(), ''),
    ]
)
def test_xml_writer(pk_attrs, xml_row_str):
    test_row_for_df = {
        'a': 'string',
        'b': Decimal('3.14'),
        'c': pd.Timestamp(2022, 1, 1, 12),
        'd': date(2022, 1, 1),
        'e': datetime(2021, 1, 1, 12),
        'f': 15,
        'g': None,
    }
    df = pd.DataFrame([test_row_for_df])

    target_xml: str = f"""<?xml version="1.0" ?>
<Report>
   <Row{xml_row_str}>
      <Column name="a">string</Column>
      <Column name="b">3.14</Column>
      <Column name="c">2022-01-01 12:00:00</Column>
      <Column name="d">2022-01-01</Column>
      <Column name="e">2021-01-01 12:00:00</Column>
      <Column name="f">15</Column>
      <Column name="g"/>
   </Row>
</Report>
"""
    with tempfile.TemporaryDirectory() as tmp:
        file_name = pathlib.Path() / tmp / 'test'
        s3_task.XmlWriter(*pk_attrs).write_file(df, file_name)
        with open(file_name, 'r') as source_xml:
            source_xml = source_xml.read()
            assert source_xml == target_xml
