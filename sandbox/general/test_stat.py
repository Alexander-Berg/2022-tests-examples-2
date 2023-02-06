import os
import json

RESULT = 'results.json'


def get_test_stat(directory):
    if not os.path.exists(os.path.join(directory, RESULT)):
        return None

    file_name = os.path.join(directory, RESULT)
    with open(file_name) as f:
        j = json.load(f)

        d = {'FAILED': 0, 'OK': 0, 'total': 0}

        for res in j['results']:
            if res['type'] == 'test':
                if res['status'] in d:
                    d[res['status']] += 1
                else:
                    d[res['status']] = 1
                d['total'] += 1

        return d


def change_stat_msg(stat_old, stat_new):

        rows = []

        if not stat_old or not stat_new:
            return "Result file not found"

        rows.append("Total: {} -> {} ({})\n".format(stat_old['total'], stat_new['total'],
                                                    stat_new['total'] - stat_old['total']))

        for st in stat_old:
            if st != 'total':
                st_new = stat_new[st] if st in stat_new else 0
                rows.append("{}: {} -> {} ({})\n".format(st,
                                                         stat_old[st], st_new,
                                                         st_new - stat_old[st]))

        for st in stat_new:
            if st not in stat_old:
                rows.append("{}: {} -> {} ({})\n".format(st,
                                                         0, stat_new[st],
                                                         stat_new[st]))

        return "".join(rows)
