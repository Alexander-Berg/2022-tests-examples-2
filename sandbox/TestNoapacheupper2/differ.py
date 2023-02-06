# !/usr/bin/env python3

import codecs


def get_diff_between_dicts(d1, d2):
    diff_dict = {}
    for item, value in d1.items():
        other_value = d2.get(item)
        if d2.get(item) != value:
            diff_dict[item] = (value, other_value)
    return diff_dict


def get_without_noapache_cgi_parameters(d):
    update_dict = {}
    for item, value in d.items():
        query, params = item.split('&srcrwr=')
        params = params.split('&')
        del params[0]
        update_item = '&'.join([query] + params)
        update_dict[update_item] = value
    return update_dict


def print_to_file(d, path_file, encoding='utf-8', delimiter=' <-> '):
    with codecs.open(path_file, 'w', encoding=encoding) as f:  # need python3 for encoding
        for item, value in d.items():
            f.write(item)
            f.write(delimiter)
            f.write(str(value))
            f.write('\n')


def print_dict(d):
    for item, value in d.items():
        print(item, value)


def read_dict_from_file(path_file, encoding='utf-8', delimiter=' <-> '):
    result_dict = {}
    with codecs.open(path_file, 'r', encoding=encoding) as f:  # need python3 for encoding
        for line in f.readlines():
            item, value = line.strip().split(delimiter)
            result_dict[item] = value
    return result_dict
