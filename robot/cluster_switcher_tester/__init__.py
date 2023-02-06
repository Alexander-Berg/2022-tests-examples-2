from robot.cmpy.library.target import cm_target, start, finish  # noqa

import sys
import time

from os.path import join as pj
import robot.cmpy.library.yt_tools as yt_tools


def get_tablet_state(client, path):
    return client.get('{}/@tablet_state'.format(path))


@cm_target
def switch(cfg, server_name, table_to_unmount):
    client = yt_tools.client(proxy=cfg.Servers[server_name])

    # Hard way to test - just unmount table and see what happens
    table_path = pj(cfg.Prefixes[server_name]["prefix"], table_to_unmount)
    if client.exists(table_path):
        if get_tablet_state(client, table_path) == "mounted":
            print >>sys.stderr, "Unmounting..."
            client.unmount_table(table_path)
            print >>sys.stderr, "Waiting...{}".format(cfg.ClusterSwitcherTester.Duration)
            time.sleep(cfg.ClusterSwitcherTester.Duration)

        print >>sys.stderr, "Mounting..."
        client.mount_table(table_path)
