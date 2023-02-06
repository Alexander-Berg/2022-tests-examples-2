import os.path
import yatest.common

from noc.packages.mondata_server.mondata.lib.lib import call_all_discoveries, DiscoveryException, find_readable, \
    load_file

PATHS_TEMPLS = ["/templates", "/solomon_templates", "/juggler_templates"]
ARC_PATH = "noc/mondata/kulebyaks"


def test_syntax():
    _, _, res = call_all_discoveries(yatest.common.source_path(ARC_PATH), recursive=True)
    for file, file_res in res.items():
        if isinstance(file_res, Exception):
            if isinstance(file_res, DiscoveryException):
                raise Exception("%s %s" % (os.path.basename(file), file_res.msg))
            raise Exception("%s %s" % (os.path.basename(file), file_res))

    for tpath in PATHS_TEMPLS:
        raw_files = find_readable(os.path.join(ARC_PATH, tpath), recursive=False)
        for file in raw_files:
            if file.endswith((".yaml", ".yml")):
                load_file(file)
