#!/usr/bin/env python

import logging
import argparse
import os
import json
import yt.wrapper as yt
from os.path import join as pj
from collections import defaultdict

MB = 1024 * 1024
MAX_ROW_WEIGHT = 64 * MB
FILE_READ_STEP = 256 * MB
YT_LIST_RESPONSE_LIMIT = 15000


def get_client(proxy):
    return yt if proxy is None else yt.client.YtClient(proxy=proxy, token=yt.http_helpers.get_token())


def read_table(path, path_stripped, output_dir, data_spec, check_sorting, mock, proxy=None):
    client = get_client(proxy)
    if client.get_attribute(path, 'sorted') is False and check_sorting:
        raise Exception('{} is not sorted'.format(path))
    with open(pj(output_dir, path_stripped), 'w') as output_file:
        if mock:
            rich_path = client.TablePath(path, start_index=0, end_index=10)
        else:
            rich_path = path
        response = client.read_table(
            rich_path,
            raw=True,
            format=yt.format.YsonFormat(attributes={"skip_null_values": True}),
        )
        output_file.write(response.read())
    data_spec[path_stripped]['max_row_weight'] = MAX_ROW_WEIGHT
    if client.get_attribute(path, 'dynamic'):
        data_spec[path_stripped]['dynamic'] = True

        tablet_state = yt.get_attribute(path, 'tablet_state')
        if tablet_state == 'mounted':
            data_spec[path_stripped]['mount'] = True
        elif tablet_state == 'frozen':
            data_spec[path_stripped]['mount'] = True
            data_spec[path_stripped]['freeze'] = True

        schema = yt.get_attribute(path, 'schema')
        data_spec[path_stripped]['schema'] = {
            'attributes': schema.attributes,
            'value': list(schema)
        }
    else:
        if client.exists(path + '/@sorted_by'):
            data_spec[path_stripped]['sorted_by'] = list(client.get_attribute(path, 'sorted_by'))


def read_file(path, path_stripped, output_dir, data_spec, mock, proxy=None):
    client = get_client(proxy)
    with open(pj(output_dir, path_stripped), 'w') as output_file:
        if not mock:
            offset = 0
            while True:
                response = client.read_file(path, offset=offset, length=FILE_READ_STEP)
                data = response.read()
                if not data:
                    break
                output_file.write(data)
                offset += len(data)
                logging.info("Got {} bytes".format(offset))
    data_spec[path_stripped]['type'] = 'file'


def read_value(path, path_stripped, data_spec, node_type, proxy=None):
    client = get_client(proxy)
    value = client.get(path)
    data_spec[path_stripped]['type'] = node_type
    data_spec[path_stripped]['value'] = value


def read_attribute(path, path_stripped, data_spec, attribute, proxy=None):
    client = get_client(proxy)
    if client.exists(path + '/@' + attribute):
        if 'attributes' in data_spec[path_stripped]:
            data_spec[path_stripped]['attributes'][attribute] = client.get_attribute(path, attribute)
        else:
            data_spec[path_stripped]['attributes'] = {attribute: client.get_attribute(path, attribute)}


def recursive_read(
        path,
        strip_prefix,
        output_dir,
        data_spec,
        user_meta_attrs_to_save,
        check_sorting,
        mock,
        save_meta,
        proxy=None
):
    client = get_client(proxy)

    logging.info(path)
    node_type = client.get_attribute(path, 'type')
    path_stripped = path[len(strip_prefix):].lstrip('/') if path.startswith(strip_prefix) else None

    data_spec[path_stripped] = defaultdict(dict)
    if save_meta:
        user_meta_attrs_to_save += client.get_attribute(path, 'user_attribute_keys')
    for attribute in user_meta_attrs_to_save:
        read_attribute(path, path_stripped, data_spec, attribute, proxy=proxy)

    if node_type == 'table':
        read_table(path, path_stripped, output_dir, data_spec, check_sorting, mock, proxy=proxy)
    elif node_type == 'file':
        read_file(path, path_stripped, output_dir, data_spec, mock, proxy=proxy)
    elif node_type == 'map_node':
        if not os.path.exists(pj(output_dir, path_stripped)):
            os.makedirs(pj(output_dir, path_stripped))

        subnodes = client.list(path, absolute=True, max_size=YT_LIST_RESPONSE_LIMIT)
        for node in sorted(subnodes):
            recursive_read(
                node,
                strip_prefix,
                output_dir,
                data_spec,
                user_meta_attrs_to_save,
                check_sorting,
                mock,
                save_meta,
                proxy=proxy
            )
        if not subnodes:
            data_spec[path_stripped]['type'] = 'map_node'
    elif node_type in ('int64_node', 'uint64_node', 'double_node', 'boolean_node'):
        read_value(path, path_stripped, data_spec, node_type, proxy=proxy)
    else:
        logging.error(node_type)
        raise Exception('Unknown node type.')

    if not data_spec[path_stripped]:
        data_spec.pop(path_stripped)

    return data_spec


def do_prepare(output_dir, path, prefix, attributes_to_save, check_sorting, mock, save_meta, proxy=None):
    output_dir_abspath = os.path.abspath(output_dir)
    if not os.path.exists(output_dir_abspath):
        os.makedirs(output_dir_abspath)

    data_spec_dict = {}
    recursive_read(
        path=path,
        strip_prefix=prefix,
        data_spec=data_spec_dict,
        user_meta_attrs_to_save=attributes_to_save,
        check_sorting=check_sorting,
        mock=mock,
        output_dir=output_dir_abspath,
        save_meta=save_meta,
        proxy=proxy
    )

    with open(pj(output_dir_abspath, 'data_spec.json'), 'w') as data_spec_file:
        json.dump(data_spec_dict, data_spec_file, indent=4, separators=(',', ': '), sort_keys=True)


if __name__ == '__main__':
    _LOG_FORMAT = '%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)-100s'
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--prefix',
        required=False,
        default='//',
        help='Prefix will be stripped from paths in filesystem.'
    )

    parser.add_argument('--path', required=True)

    parser.add_argument('--output-dir', default='', help='Where to store results.')

    parser.add_argument(
        '--no-user-meta',
        action='store_false',
        help='I won\'t blame you, if you don\'t want to save user defined metaattributes in test data.',
        dest='save_meta'
    )

    parser.add_argument(
        '--save-attribute',
        action='append',
        help='What you ask is what you get. Can be used multiple times. Overrides --no-user-meta option.',
        dest='attributes_to_save',
        default=[]
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        help='Take only 10 first records from tables and create empty files.'
    )

    parser.add_argument(
        '--check-sorting',
        action='store_true',
        help='Require every table being read to be sorted.'
    )

    args = parser.parse_args()

    output_dir_abspath = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir_abspath):
        os.makedirs(output_dir_abspath)

    data_spec_dict = {}
    recursive_read(
        path=args.path,
        strip_prefix=args.prefix,
        data_spec=data_spec_dict,
        user_meta_attrs_to_save=args.attributes_to_save,
        check_sorting=args.check_sorting,
        mock=args.mock,
        output_dir=output_dir_abspath,
        save_meta=args.save_meta
    )

    with open(pj(output_dir_abspath, 'data_spec.json'), 'w') as data_spec_file:
        json.dump(data_spec_dict, data_spec_file, indent=4, separators=(',', ': '), sort_keys=True)
