import json
import logging
import os
import shutil
import yatest.common
from os.path import join as pj

from google.protobuf.json_format import MessageToDict

import yt.wrapper
import yt.yson.yson_types

from robot.jupiter.library.python.ytcpp import YtCppClient, Table
from robot.blrt.protos.task_state_pb2 import TCaesarParentOrder, TCaesarParentBanner, TBannerGroup, TFeedToTasksMapping
from robot.blrt.protos.banners_state_pb2 import TBannersState
from robot.blrt.library.profiles.python import extract_selection_rank_profile_proto_as_dict, \
    extract_offer_profile_proto_as_dict, extract_simple_limit_profile_proto_as_dict, \
    extract_offer_storage_profile_proto_as_dict


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, yt.yson.yson_types.YsonStringProxy):
            obj = yt.yson.yson_types.get_bytes(obj)
        if isinstance(obj, bytes):
            try:
                return obj.decode()
            except UnicodeDecodeError:
                return '0x{}'.format(obj.hex())
        return super().default(obj)


def publish_difftool():
    src_path = yatest.common.binary_path("robot/blrt/tools/difftool/difftool")
    dst_path = yatest.common.output_path("difftool")
    if not os.path.exists(dst_path):
        shutil.copyfile(src_path, dst_path)


def prepare_dumps_dir():
    dumps_dir = yatest.common.output_path("dumps")
    if not os.path.exists(dumps_dir):
        os.mkdir(dumps_dir)
    return dumps_dir


def write_table_contents_to_dumps_dir(tables_contents):
    publish_difftool()
    dumps_dir = prepare_dumps_dir()
    for table_path, table_content in tables_contents.items():
        table_name = os.path.basename(table_path)
        file_path = pj(dumps_dir, table_name + ".json")

        logging.info("Dumping table {} into file {}".format(table_path, file_path))
        with open(file_path, "w") as file_stream:
            json.dump(table_content, file_stream, sort_keys=True, indent=2, ensure_ascii=False, cls=JSONEncoder)


def dump_pocket_tables(local_blrt):
    pocket_table_names = ["tasks_and_offers", "tasks_and_offers.final", "make_banners.add_avatars.done"]

    pocket_state = local_blrt.yt_client.get(pj(local_blrt.yt_prefix, local_blrt.task_type, "@jupiter_meta", "blrt_export_pocket_prev_state"))
    pocket_tables_contents = {}
    for table_name in pocket_table_names:
        table_path = pj(local_blrt.yt_prefix, local_blrt.task_type, "pocket_export", pocket_state, table_name)
        table_content = list(local_blrt.yt_client.read_table(table_path))
        pocket_tables_contents[table_path] = table_content

    write_table_contents_to_dumps_dir(pocket_tables_contents)


def dump_task_tables(local_blrt):
    task_table_protos = {
        "CaesarParentOrder": TCaesarParentOrder,
        "CaesarParentBanner": TCaesarParentBanner,
        "BannerGroup": TBannerGroup,
        "FeedToTasks": TFeedToTasksMapping,
    }

    yt_cpp_client = YtCppClient(client=local_blrt.yt_client)
    task_tables_contents = {}
    for table_name, table_proto in task_table_protos.items():
        table_path = pj(local_blrt.yt_prefix, "task", local_blrt.task_type, table_name)
        yt_cpp_table = Table(table_path, table_proto)
        task_tables_contents[table_path] = list(map(MessageToDict, yt_cpp_client.read_table(yt_cpp_table)))

    export_table_path = pj(local_blrt.yt_prefix, "task", local_blrt.task_type, "export_latest_state", "task_export")
    task_tables_contents[export_table_path] = list(local_blrt.yt_client.read_table(export_table_path))

    write_table_contents_to_dumps_dir(task_tables_contents)


def dump_state_tables(local_blrt):
    state_table_protos = {
        "BannersState": TBannersState,
        "InactiveBannersState": TBannersState,
    }

    profile_table_to_get_fields_function = {
        "profiles/Offer": extract_offer_profile_proto_as_dict,
        "profiles/SelectionRank": extract_selection_rank_profile_proto_as_dict,
        "profiles/OfferStorage": extract_offer_storage_profile_proto_as_dict,
        "profiles/ClientLimit": extract_simple_limit_profile_proto_as_dict,
        "profiles/DomainLimit": extract_simple_limit_profile_proto_as_dict
    }

    state_tables_contests = {}
    yt_cpp_client = YtCppClient(client=local_blrt.yt_client)
    for table_name, table_proto in state_table_protos.items():
        table_path = pj(local_blrt.yt_prefix, local_blrt.task_type, table_name)
        yt_cpp_table = Table(table_path, table_proto)
        state_tables_contests[table_path] = list(map(MessageToDict, yt_cpp_client.read_table(yt_cpp_table.select_current_proto_fields_only())))

    for table_name, profile_function in profile_table_to_get_fields_function.items():
        table_path = pj(local_blrt.yt_prefix, local_blrt.task_type, table_name)
        state_tables_contests[table_path] = list(profile_function(row) for row in local_blrt.yt_client.read_table(table_path, format=yt.wrapper.format.YsonFormat(encoding=None)))

    write_table_contents_to_dumps_dir(state_tables_contests)


def dump_funnel_tables(local_blrt):
    funnel_tables = ["FunnelExport"]

    funnel_state = local_blrt.yt_client.get(pj(local_blrt.yt_prefix, local_blrt.task_type, "@jupiter_meta", "blrt_funnel_prev_state"))
    funnel_tables_content = {}
    for table_name in funnel_tables:
        table_path = pj(local_blrt.yt_prefix, "funnel", local_blrt.task_type, funnel_state, table_name)
        funnel_tables_content[table_path] = list(local_blrt.yt_client.read_table(table_path))

    write_table_contents_to_dumps_dir(funnel_tables_content)
