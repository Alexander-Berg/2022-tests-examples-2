import os
import pytest

import test.info as testinfo
import ytio.readers as readers
import ytio.table_adapters as table_adapters
import pathutil
import yatest.common


def save_cypress(lyt, prefix, out_dir):
    readers.save_and_parse_tables(lyt, lyt.list_tables(prefix), out_dir)


def canonical_diff(items_list, diff_tool=["diff", "-U8"]):
    canonical_list = []
    for item in items_list:
        if os.path.exists(item):
            canonical_list.append(yatest.common.canonical_file(item, diff_tool=diff_tool))
        else:
            canonical_list.append(item)
    return canonical_list


def canonical_mapreduce_tables(lyt, tmpdir_module, prefix, diff_tool=["diff", "-U5"]):
    tables_out_dir = pathutil.get_valid_tmpdir("final_mr_tables", tmpdir_module)
    tables_list = lyt.list_tables(prefix)

    tables_list_file = os.path.join(tables_out_dir, "tables_list")
    with open(tables_list_file, 'w') as f:
        f.write("\n".join(tables_list))

    tables_files = filter(
        lambda t: testinfo.is_known_table(os.path.basename(t).replace("__", "/")),
        readers.save_and_parse_tables(lyt, tables_list, tables_out_dir)
    )
    return canonical_diff([tables_list_file]+tables_files, diff_tool)

