from collections import OrderedDict

import json
import os


def sorted_json(json_dict):
    return OrderedDict(sorted(json_dict.items()))


def sorted_json_dump(json_dict, indent=4):
    if not isinstance(json_dict, dict):
        raise Exception('argument must be dict, found %s' % json_dict)
    return json.dumps(sorted_json(json_dict), indent=indent)


def commits_info(folder):
    res = []
    for lf in os.listdir(folder):
        if lf.startswith('arcadia_commit.'):
            with open(os.path.join(folder, lf)) as f:
                sent = []
                s_rev = ''
                for l in f.readlines():
                    pts = l.split()
                    if not pts:
                        continue
                    if pts[0] == 'Sending':
                        sent.append(pts[-1])
                    elif pts[0] == 'Committed':
                        s_rev = pts[-1].replace('.', '')
                if sent and s_rev:
                    res.append({'rev': s_rev, 'files': sent})
    return res
