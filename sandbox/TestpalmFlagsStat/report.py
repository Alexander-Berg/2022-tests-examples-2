import os
import jinja2
import shutil
import logging


class FlagsReport():
    def __init__(self, params, testcases, flags):
        self.flags = flags
        self.params = params
        self.testcases = testcases

        self.template_path = os.path.dirname(os.path.abspath(__file__))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_path))
        self.template = env.get_template('report.tmpl')

    def get_flags_stats(self):
        res = {
            'online': 0,
            'total': 0,
            'offline': [],
            'no_testids': [],
            'no_storage': {}
        }

        for flagHash in self.flags:
            flag = self.flags[flagHash]
            if flag['testid'] is not None:
                res['total'] += 1
                if flag['online'] is True:
                    res['online'] += 1
                else:
                    res['offline'].append(flagHash)
            else:
                res['no_testids'].append(flagHash)

            if flag['in_storage'] is False:
                if flag['name'] in res['no_storage']:
                    saved_list = res['no_storage'][flag['name']]
                    res['no_storage'][flag['name']] = saved_list + list(set(saved_list) - set(flag['testcases']))
                else:
                    res['no_storage'][flag['name']] = flag['testcases']

        return res

    def get_testcases_stats(self):
        res = {
            'total': len(self.testcases),
            'online': 0,
            'offline': [],
            'offline_total': 0
        }

        for testcase in self.testcases:
            online = []
            offline = []

            for flagHash in testcase['parsed_flags']:
                flag = self.flags[flagHash]
                if flag['online'] is True:
                    online.append(flagHash)
                else:
                    res['offline_total'] += 1
                    offline.append(flagHash)

            if len(testcase['parsed_flags']) != len(online):
                res['offline'].append({
                    'id': testcase['id'],
                    'name': testcase['name'],
                    'online': online,
                    'offline': offline
                })
            else:
                res['online'] += 1

            if str(testcase['id']) == '23300':
                logging.info(testcase)

        return res

    def write(self, path):
        self.template.stream({
            "project": self.params.project_name,
            "flags": self.flags,
            "stat": self.get_flags_stats(),
            "testcases": self.get_testcases_stats()
        }).dump(os.path.join(path, 'report.html'))

        shutil.copy(os.path.join(self.template_path, 'report.css'), os.path.join(path, 'report.css'))
