#!/usr/bin/env python

import shutil
import json
import os
import sys
import tarfile
import subprocess
import tempfile
import argparse
from os.path import join as pj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pkg-json", help="RTHub package json.", required=True)
    parser.add_argument("--svn-branch", help="Trunk or branch name in svn. Default: trunk.", default="trunk")

    args = parser.parse_args()

    output_path = pj(os.getcwd(), "udf_data_resources.tar")
    svn_path = "svn+ssh://arcadia-ro.yandex.ru/arc/" + args.svn_branch + "/arcadia/"

    with open(args.pkg_json, 'r') as f:
        data = json.load(f)

    sandbox_resources = {}
    arc_resources = []
    for s in data['data']:
        if 'data/resources' in s['destination']['path']:
            if s['source']['type'] == "SANDBOX_RESOURCE":
                sandbox_resources[s['source']['path']] = s['source']['id']
            elif s['source']['type'] == "ARCADIA":
                if 'files' in s['source']:
                    for f in s['source']['files']:
                        arc_resources.append(["{}/{}".format(s['source']['path'], f), "{}".format(s['destination']['path']).replace('/data/resources/', '')])
                else:
                    arc_resources.append([s['source']['path'], ''])
            else:
                print "Unknown source type {}".format(s['source']['type'])

    res_path = tempfile.mkdtemp()

    if (sandbox_resources):
        for r in sandbox_resources:
            sky_cmd = ['/usr/local/bin/sky', 'get', '-uw', '-d', res_path, 'sbr:{}'.format(sandbox_resources[r])]
            print "Run: {}".format(sky_cmd)
            subprocess.check_call(sky_cmd, stdout=sys.stderr, stderr=subprocess.STDOUT)
            if 'YQL_' in r:
                if not r.split('/')[-1].startswith('YQL_'):
                    shutil.move(pj(res_path, r[r.find('YQL_'):]), res_path)

    if (arc_resources):
        cur_dir = os.getcwd()
        os.chdir(res_path)
        for r in arc_resources:
            svn_dest = r[1]
            if svn_dest:
                if not os.path.isdir(svn_dest):
                    os.mkdir(svn_dest)
                svn_cmd = ['/usr/bin/svn', 'export', '{}/{}'.format(svn_path, r[0]), svn_dest]
            else:
                svn_cmd = ['/usr/bin/svn', 'export', '{}/{}'.format(svn_path, r[0])]
            print "Run: {}".format(svn_cmd)
            subprocess.check_call(svn_cmd, stdout=sys.stderr, stderr=subprocess.STDOUT)
        os.chdir(cur_dir)

    with tarfile.open(output_path, "w") as tar:
        for f in os.listdir(res_path):
            tar.add(pj(res_path, f), arcname=f)

    shutil.rmtree(res_path)
