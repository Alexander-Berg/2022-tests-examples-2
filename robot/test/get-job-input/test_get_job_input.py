#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import subprocess

from mapreduce.yt.python.yt_stuff import yt_stuff  # noqa
import yatest.common

import yt.yson as yson
import yt.wrapper

GET_JOB_INPUT = yatest.common.binary_path('robot/jupiter/tools/get_job_input/get_job_input')


def record(host, path, data=None):
    m = {
        'host': host,
        'path': path,
    }
    if data is not None:
        m['data'] = data
    return m


def obj_list(yt_stuff, yson_text):  # noqa
    return list(yson.loads(yson_text, yson_type='list_fragment'))


def write_records(yt_stuff, table, row_list):  # noqa
    yt_client = yt_stuff.get_yt_client()
    yt_format = yt.wrapper.YsonFormat()
    bytes_data = StringIO.StringIO()
    yt_format.dump_rows(row_list, bytes_data)
    yt_client.write_table(table, bytes_data.getvalue(), format=yt_format, raw=True)


def test_single_table(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    records = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/', 'data2'),
        record('http://example.com', '/1', 'data3'),
        record('http://example2.com', '/1', 'data4'),
        record('http://example2.com', '/2', 'data5'),
    ]
    table_name = '//test_single_table'
    write_records(yt_stuff, yt_client.TablePath(table_name, sorted_by=['host', 'path']), records)
    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host', '--reduce-by=path',
        '--primary-table', table_name,
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data2";
};
<"key_switch"=%true;>#;
{
    "path" = "/1";
    "host" = "http://example.com";
    "data" = "data3";
};
<"key_switch"=%true;>#;
{
    "path" = "/1";
    "host" = "http://example2.com";
    "data" = "data4";
};
<"key_switch"=%true;>#;
{
    "path" = "/2";
    "host" = "http://example2.com";
    "data" = "data5";
};
""")


def test_multiple_table_reduce(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    table1 = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/1', 'data2'),
    ]
    table2 = [
        record('http://example.com', '/', 'otherdata1'),
        record('http://example.com', '/2', 'otherdata2'),
        record('http://example.com', '/2', 'otherdata3'),
    ]
    table_name_1 = '//test_multiple_table_reduce_1'
    table_name_2 = '//test_multiple_table_reduce_2'
    write_records(yt_stuff, yt_client.TablePath(table_name_1, sorted_by=['host', 'path']), table1)
    write_records(yt_stuff, yt_client.TablePath(table_name_2, sorted_by=['host', 'path']), table2)

    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host', '--reduce-by=path',
        '--primary-table', table_name_1,
        '--primary-table', table_name_2,
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
<"table_index"=1;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "otherdata1";
};
<"key_switch"=%true;>#;
<"table_index"=0;>#;
{
    "path" = "/1";
    "host" = "http://example.com";
    "data" = "data2";
};
<"key_switch"=%true;>#;
<"table_index"=1;>#;
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata2";
};
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata3";
};
""")


def test_join_reduce(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    table1 = [
        record('http://example1.com', '', 'hostdata1'),
        record('http://example2.com', '', 'hostdata2'),
    ]
    table2 = [
        record('http://example1.com', '/', 'otherdata1'),
        record('http://example1.com', '/1', 'otherdata11'),
        record('http://example3.com', '/2', 'otherdata2'),
        record('http://example3.com', '/2', 'otherdata3'),
    ]
    table_name_1 = '//test_multiple_table_reduce_1'
    table_name_2 = '//test_multiple_table_reduce_2'
    write_records(yt_stuff, yt_client.TablePath(table_name_1, sorted_by=['host', 'path']), table1)
    write_records(yt_stuff, yt_client.TablePath(table_name_2, sorted_by=['host', 'path']), table2)

    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--join-by=host',
        '--reduce-by=host', '--reduce-by=path',
        '--join-table', table_name_1,
        '--primary-table', table_name_2,
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "";
    "host" = "http://example1.com";
    "data" = "hostdata1";
};
<"table_index"=1;>#;
{
    "path" = "/";
    "host" = "http://example1.com";
    "data" = "otherdata1";
};
{
    "path" = "/1";
    "host" = "http://example1.com";
    "data" = "otherdata11";
};
<"key_switch"=%true;>#;
<"table_index"=0;>#;
{
    "path" = "";
    "host" = "http://example2.com";
    "data" = "hostdata2";
};
<"key_switch"=%true;>#;
<"table_index"=1;>#;
{
    "path" = "/2";
    "host" = "http://example3.com";
    "data" = "otherdata2";
};
{
    "path" = "/2";
    "host" = "http://example3.com";
    "data" = "otherdata3";
};
""")


def test_break_at_any_record(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    records = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/', 'data2'),
        record('http://example.com', '/1', 'data3'),
        record('http://example2.com', '/1', 'data4'),
        record('http://example2.com', '/2', 'data5'),
    ]
    table_name = '//test_single_table'
    write_records(yt_stuff, yt_client.TablePath(table_name, sorted_by=['host', 'path']), records)
    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--primary-table', table_name,
        '--size=1b',
        '--break-at=any-record',
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
""")


def test_break_at_reduce_key(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    records = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/', 'data2'),
        record('http://example.com', '/1', 'data3'),
        record('http://example2.com', '/1', 'data4'),
        record('http://example2.com', '/2', 'data5'),
    ]
    table_name = '//test_single_table'
    write_records(yt_stuff, yt_client.TablePath(table_name, sorted_by=['host', 'path']), records)
    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host', '--reduce-by=path',
        '--primary-table', table_name,
        '--size=1b',
        '--break-at=reduce-key',
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data2";
};
""")


def test_multiple_table_reduce_table_order(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    table1 = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/', 'data2'),
        record('http://example.com', '/', 'data3'),
        record('http://example.com', '/1', 'data4'),
    ]
    table2 = [
        record('http://example.com', '/', 'otherdata1'),
        record('http://example.com', '/', 'otherdata2'),
        record('http://example.com', '/2', 'otherdata3'),
        record('http://example.com', '/2', 'otherdata4'),
    ]
    table_name_1 = '//test_multiple_table_reduce_1'
    table_name_2 = '//test_multiple_table_reduce_2'
    write_records(yt_stuff, yt_client.TablePath(table_name_1, sorted_by=['host', 'path']), table1)
    write_records(yt_stuff, yt_client.TablePath(table_name_2, sorted_by=['host', 'path']), table2)

    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host', '--reduce-by=path',
        '--primary-table', table_name_1,
        '--primary-table', table_name_2,
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data2";
};
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data3";
};
<"table_index"=1;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "otherdata1";
};
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "otherdata2";
};
<"key_switch"=%true;>#;
<"table_index"=0;>#;
{
    "path" = "/1";
    "host" = "http://example.com";
    "data" = "data4";
};
<"key_switch"=%true;>#;
<"table_index"=1;>#;
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata3";
};
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata4";
};
""")


def test_specify_table_indeces(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    table1 = [
        record('http://example.com', '/', 'data1'),
        record('http://example.com', '/1', 'data2'),
    ]
    table2 = [
        record('http://example.com', '/', 'otherdata1'),
        record('http://example.com', '/2', 'otherdata2'),
        record('http://example.com', '/2', 'otherdata3'),
    ]
    table_name_1 = '//test_multiple_table_reduce_1'
    table_name_2 = '//test_multiple_table_reduce_2'
    write_records(yt_stuff, yt_client.TablePath(table_name_1, sorted_by=['host', 'path']), table1)
    write_records(yt_stuff, yt_client.TablePath(table_name_2, sorted_by=['host', 'path']), table2)

    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host', '--reduce-by=path',
        '--primary-table', "2::{}".format(table_name_1),
        '--primary-table', "1::{}".format(table_name_2),
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "otherdata1";
};
<"table_index"=1;>#;
{
    "path" = "/";
    "host" = "http://example.com";
    "data" = "data1";
};
<"key_switch"=%true;>#;
{
    "path" = "/1";
    "host" = "http://example.com";
    "data" = "data2";
};
<"key_switch"=%true;>#;
<"table_index"=0;>#;
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata2";
};
{
    "path" = "/2";
    "host" = "http://example.com";
    "data" = "otherdata3";
};
""")


def test_sort_by(yt_stuff):  # noqa
    yt_client = yt_stuff.get_yt_client()
    table1 = [
        record('http://example.com', '/2'),
    ]
    table2 = [
        record('http://example.com', '/1'),
        record('http://example.com', '/3'),
    ]
    table_name_1 = '//test_sort_by_1'
    table_name_2 = '//test_sort_by_2'
    write_records(yt_stuff, yt_client.TablePath(table_name_1, sorted_by=['host', 'path']), table1)
    write_records(yt_stuff, yt_client.TablePath(table_name_2, sorted_by=['host', 'path']), table2)

    res = subprocess.check_output([
        GET_JOB_INPUT, "prepare-job-input",
        '--reduce-by=host',
        '--sort-by=host', '--sort-by=path',
        '--primary-table', "1::{}".format(table_name_1),
        '--primary-table', "2::{}".format(table_name_2),
        '--pretty',
    ], env={
        'YT_PROXY': yt_stuff.get_server(),
    })
    assert obj_list(yt_stuff, res) == obj_list(yt_stuff, """\
<"key_switch"=%true;>#;
<"table_index"=1;>#;
{
    "path" = "/1";
    "host" = "http://example.com";
};
<"table_index"=0;>#;
{
    "path" = "/2";
    "host" = "http://example.com";
};
<"table_index"=1;>#;
{
    "path" = "/3";
    "host" = "http://example.com";
};
""")
