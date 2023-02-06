from __future__ import print_function
from os.path import join as pj
from random import randrange
import argparse
import StringIO
import os
import shutil
import yt.wrapper as yt
import tempfile
import tarfile

from yalibrary.upload import uploader

from robot.library.yuppie.prepare_yt_testdata import do_prepare


def generate_row_numbers(count, max_row_number):
    random_rows = set([])
    while len(random_rows) < count:
        random_rows.add(randrange(0, max_row_number))
    return random_rows


def generate_random_ranges_for_table(count, table_path):
    max_row_number = yt.get(table_path + '/@row_count')
    return generate_random_ranges(count, max_row_number)


def generate_random_ranges(count, max_row_number):
    rows = generate_row_numbers(count, max_row_number)
    ranges = []
    for row in rows:
        ranges.append({'exact': {'row_index': row}})
    return ranges


def filter_valid_docs(row):
    if row['HttpCode'] == 200 and row['HttpBody'] is not None:
        yield row


def sample_table(source, destination, row_count):
    ranges = generate_random_ranges_for_table(row_count, source)
    yt.create("map_node", os.path.dirname(destination), recursive=True, ignore_existing=True)
    source_table_path = yt.TablePath(source, ranges=ranges)
    yt.run_merge(source_table_path, destination, mode='sorted')
    yt.run_map(filter_valid_docs, destination, destination, ordered=True)


def get_keys(table_path, ranges=None):
    keys = set([])
    key_columns = ['Host', 'Path', 'LastAccess']
    table = yt.TablePath(table_path, columns=key_columns, ranges=ranges)
    for row in yt.read_table(table):
        keys.add((row['Host'] + row['Path'], row['LastAccess']))
    return keys


def write_keys(keys, file_path):
    out = StringIO.StringIO()
    for key in keys:
        print(key[0] + ',' + str(key[1]), file=out)

    yt.write_file(file_path, out.getvalue())
    out.close()


def prepare_yt_data(args):
    in_db = set([])
    not_in_db = set([])
    yt.remove(args.destination_prefix, recursive=True, force=True)
    for shard in xrange(args.shard_count):
        print('Will prepare data for shard ' + str(shard))
        suffix = pj('pages',  str(shard).zfill(3), 'data')
        source_path = pj(args.source_prefix, suffix)
        destination_path = pj(args.destination_prefix, suffix)
        print('Will sample table ' + source_path + ' to destination table ' + destination_path)
        sample_table(source_path, destination_path, args.row_count)
        in_db = in_db.union(get_keys(destination_path))
        not_in_db = not_in_db.union(get_keys(
            source_path,
            generate_random_ranges_for_table(args.row_count * 2, source_path)))

    not_in_db = not_in_db.difference(in_db)
    print('Will write out keys...')
    write_keys(in_db, pj(args.destination_prefix, 'in_db_list'))
    write_keys(not_in_db, pj(args.destination_prefix, 'not_in_db_list'))


def upload(path):
    return uploader.do(
        paths=[path],
        resource_owner='KWYT',
        transport='http',
        sandbox_token=os.environ.get('SANDBOX_TOKEN')
    )


def main():
    parser = argparse.ArgumentParser(description='Sample html database')
    parser.add_argument('--source-prefix')
    parser.add_argument('--destination-prefix')
    parser.add_argument('--row-count', type=int)
    parser.add_argument('--shard-count', required=True, type=int)

    args = parser.parse_args()

    yt.config['read_retries']['allow_multiple_ranges'] = True

    prepare_yt_data(args)
    temp_dir = tempfile.mkdtemp()
    tar_temp_dir = tempfile.mkdtemp()
    print(temp_dir)
    try:
        do_prepare(temp_dir, args.destination_prefix, args.destination_prefix, ['jupiter_meta'], True, False, True)
        arc_path = pj(tar_temp_dir, 'data.tar')
        with tarfile.open(name=arc_path, mode='w:') as tar:
            tar.add(temp_dir, arcname='')
        res_id = upload(arc_path)
        print(res_id)
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(tar_temp_dir)


if __name__ == "__main__":
    main()
