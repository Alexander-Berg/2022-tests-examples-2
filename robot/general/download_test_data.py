import json
import logging
import os
import random
import re
import shutil
import string
import tarfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps


import yt.wrapper.client
from yt.wrapper.common import chunk_iter_stream, MB
from yt.wrapper.ypath import TablePath

from robot.jupiter.library.python import yt_utils


def get_temp_dir(target=None):
    random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    if target is None:
        dir_name = random_string
    else:
        dir_name = target.split('.')[0] + "_" + random_string
    return os.path.join(os.getcwd(), dir_name)


def concurrent_yt_operation(func):
    @wraps(func)
    def wrapper(mr_server, yt_token, *args, **kwargs):
        client = yt.wrapper.client.Yt(mr_server, token=yt_token)
        func(client, *args, **kwargs)

    return wrapper


NAMES_TO_SKIP = set([
    "JUPITER_MIDDLE_SEARCH_BUNDLE",
    "JUPITER_DSSM_MODELS",
    "REALFEED_DATA",
    "JUPITER_HR_FAST",
    "IndexUserOwn",
    "IndexUserOwnQ",
    ".*\\.r2c"
])

ROW_LIMITS = {
    "IndexAnn": 512,
    "QueryUrlUserData": 256,
    "RegSiteBrowser": 50000,
    "UrlMenu": 500,
}


def should_skip(name):
    for reg_ex in NAMES_TO_SKIP:
        if re.search(reg_ex, name):
            return True
    return False


def row_limit(rel_path):
    for pattern, limit in ROW_LIMITS.items():
        if re.search(pattern, rel_path):
            return limit


def make_mock(yt_path, fs_path):
    open(fs_path, 'w').close()
    logging.info('Made a mock of %s in %s', yt_path, fs_path)


def read_from_yt(istream, ostream):
    for chunk in chunk_iter_stream(istream, 16 * MB):
        ostream.write(chunk)
    istream.close()  # object does not provide .__exit__ :(


def download_from_yt(istream, fs_path):
    with open(fs_path, 'w') as ostream:
        read_from_yt(istream, ostream)


@concurrent_yt_operation
def read_file(client, yt_path, fs_path):
    istream = client.read_file(yt_path)
    download_from_yt(istream, fs_path)
    logging.info('File %s downloaded to %s', yt_path, fs_path)


@concurrent_yt_operation
def read_table(client, yt_path, fs_path, yt_fmt, limit=None):
    if limit is not None:
        ypath = TablePath(yt_path, start_index=0, end_index=limit)
    else:
        ypath = yt_path
    istream = client.read_table(ypath, format=yt_fmt, raw=True)
    download_from_yt(istream, fs_path)
    logging.info('Table %s downloaded to %s', yt_path, fs_path)


def read_attributes(client, yt_path):
    keys = client.get(os.path.join(yt_path, "@user_attribute_keys"))
    attributes = {}
    for key in keys:
        attributes[key] = client.get(os.path.join(yt_path, "@" + key))
    return attributes


@concurrent_yt_operation
def copy_attributes(client, yt_path, data_spec, rel_path, node_type):
    data_spec[rel_path]["type"] = node_type
    data_spec[rel_path]["attributes"] = read_attributes(client, yt_path)


def download_item(executor, features, client, yt_path, rel_path, data_spec, node_type, yt_fmt, tmp_dir, mr_server, yt_token):
    fs_path = os.path.join(tmp_dir, rel_path)
    yt_path = os.path.join(yt_path, rel_path)
    logging.info('Downloading %s to %s', yt_path, fs_path)

    if node_type == "table":
        feature = executor.submit(add_table_spec_entry, mr_server, yt_token, data_spec, rel_path, yt_path, node_type)
        features.append(feature)

    if should_skip(rel_path):
        feature = executor.submit(make_mock, yt_path, fs_path)
        features.append(feature)
    elif node_type == "table":
        feature = executor.submit(read_table, mr_server, yt_token, yt_path, fs_path, yt_fmt, row_limit(rel_path))
        features.append(feature)
    elif node_type == "file":
        feature = executor.submit(read_file, mr_server, yt_token, yt_path, fs_path)
        features.append(feature)
    else:
        raise ValueError("Invalid node type")


@concurrent_yt_operation
def add_table_spec_entry(client, data_spec, rel_path, yt_path, node_type):

    def get_attr_path(attr):
        return os.path.join(yt_path, "@" + attr)

    def get_attr(attr):
        return client.get(get_attr_path(attr))

    data_spec[rel_path]["max_row_weight"] = 128 * 1024 * 1024

    if get_attr("dynamic"):
        data_spec[rel_path]["dynamic"] = True

        tablet_state = get_attr("tablet_state")
        if tablet_state == "mounted":
            data_spec[rel_path]["mount"] = True
        elif tablet_state == "frozen":
            data_spec[rel_path]["mount"] = True
            data_spec[rel_path]["freeze"] = True

        schema = get_attr("schema")
        data_spec[rel_path]["schema"] = {
            'attributes': schema.attributes,
            'value': list(schema)
        }
    else:
        sorted_by_attr_path = get_attr_path("sorted_by")
        if client.exists(sorted_by_attr_path):
            data_spec[rel_path]["sorted_by"] = client.get(sorted_by_attr_path)


def recursive_download_from_yt_impl(executor, features, client, yt_path, rel_path, data_spec, yt_fmt, tmp_dir, mr_server, yt_token):
    full_yt_path = os.path.join(yt_path, rel_path)
    node_type = client.get(os.path.join(full_yt_path, "@type"))
    feature = executor.submit(copy_attributes, mr_server, yt_token, full_yt_path, data_spec, rel_path, node_type)
    features.append(feature)

    if node_type != "map_node":
        download_item(executor, features, client, yt_path, rel_path, data_spec,
                      node_type, yt_fmt, tmp_dir, mr_server, yt_token)
    else:
        fs_path = os.path.join(tmp_dir, rel_path)
        if not os.path.exists(fs_path):
            os.makedirs(fs_path)

        subdirs = client.list(full_yt_path)
        for subdir in subdirs:
            recursive_download_from_yt_impl(executor, features, client, yt_path,
                                            os.path.join(rel_path, subdir), data_spec, yt_fmt, tmp_dir, mr_server, yt_token)
        if not subdirs:
            data_spec[rel_path]["type"] = "map_node"


def recursive_download_from_yt(client, yt_path, yt_fmt, tmp_dir, mr_server, yt_token):
    make_defaultdict = lambda: defaultdict(make_defaultdict)
    data_spec = make_defaultdict()

    with ThreadPoolExecutor(max_workers=16) as executor:
        features = list()
        for subdir in client.list(yt_path):
            logging.info('Downloading %s/%s', yt_path, subdir)
            recursive_download_from_yt_impl(executor, features, client, yt_path, subdir,
                                            data_spec, yt_fmt, tmp_dir, mr_server, yt_token)

        for feature in features:
            feature.result()
        executor.shutdown(wait=True)
        return data_spec


def download(mr_server, mr_prefix, sample_type, yt_fmt, tmp_dir, state=None, yt_token=None):
    client = yt.wrapper.client.Yt(mr_server, token=yt_token)
    if state is None or state == "Last":
        state = client.get(os.path.join(mr_prefix, "@jupiter_meta", "sample_prev_state"))
    logging.info('Collecting data sampled at %s', state)

    sample_dir = os.path.join(mr_prefix, "sample", state, sample_type)
    data_spec = recursive_download_from_yt(client, sample_dir, yt_fmt, tmp_dir, mr_server, yt_token)

    data_spec[os.curdir]["type"] = "map_node"
    data_spec[os.curdir]["attributes"] = yt_utils.get_user_attributes(client, sample_dir)

    data_spec_file_name = "data_spec.json"
    config_path = os.path.join(tmp_dir, data_spec_file_name)
    with open(config_path, 'w') as config_file:
        json.dump(data_spec, config_file, sort_keys=True, indent=4, ensure_ascii=False)


def pack(output, tmp_dir, keep_tmp_dir=False):
    logging.debug("Packing %s to %s.", tmp_dir, output)
    with tarfile.open(output, mode='w') as archive:
        for subdir in os.listdir(tmp_dir):
            logging.info("Adding %s to archive", subdir)
            archive.add(os.path.join(tmp_dir, subdir), arcname=subdir)
    logging.info("Size of %s: %s", output, os.path.getsize(output))

    if not keep_tmp_dir:
        logging.info("Removing temporary directory %s", tmp_dir)
        shutil.rmtree(tmp_dir)


def create_test_data(mr_server, mr_prefix, sample_type, state, output, download_kwargs={}):
    tmp_dir = get_temp_dir()
    yt_fmt = "yson"
    download(mr_server, mr_prefix, sample_type, yt_fmt, tmp_dir, state, **download_kwargs)
    pack(output, tmp_dir)
