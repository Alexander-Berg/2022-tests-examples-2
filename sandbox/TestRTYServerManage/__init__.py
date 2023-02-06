# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.environments import SvnEnvironment
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import ssh

from sandbox.sandboxsdk.parameters import SandboxBoolParameter, SandboxRadioParameter, SandboxStringParameter

from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers

from helpers import sorted_json_dump
from helpers import commits_info

import imp
import json
import logging
import os
import time


class WhatToUpdateParameter(SandboxRadioParameter):
    name = 'what_to_update'
    description = 'Update: '
    choices = [('Testenv stat', 'testenv_stat'),
               ('Autocheck tests', 'autocheck'),
               ('Testenv autocheck list', 'te_autocheck')]


class DoCommitParameter(SandboxBoolParameter):
    name, description = 'do_commit', 'Commit changes to svn'
    default_value = False


class StatUnitAttrParameter(SandboxStringParameter):
    name, description = 'uint_stat_attr', 'attr for unit stat'
    default_value = 'unit'


test_file_part = '''
def test{TEST_TE_NAME}(metrics, links):
    test_name = '{TEST_NAME}'
    test_pars = '{TEST_PARAMS}'
    timeout = {TIMEOUT}
    run_test(test_name, test_pars, '{TEST_TE_NAME}', timeout, metrics=metrics, links=links)

'''

test_cluster_file_part = '''
def test{TEST_TE_NAME}(metrics, links):
    test_name = '{TEST_NAME}'
    test_pars = '{TEST_PARAMS}'
    timeout = {TIMEOUT}
    run_cluster_test(test_name, test_pars, '{TEST_TE_NAME}', timeout, metrics=metrics, links=links)

'''

TE_FILE = '''
RTY_TESTS_TIMES_MAX = {}

'''

TE_AC_FILE = '''
TESTS_AC = list()

'''


class TestRTYServerManage(SandboxTask):
    type = 'TEST_RTYSERVER_MANAGE'
    environment = [SvnEnvironment(), ]
    input_parameters = [DoCommitParameter,
                        WhatToUpdateParameter,
                        StatUnitAttrParameter
                        ]

    tests_arc_path = 'testenv/jobs/rtyserver/rty_tests.py'
    tests_arc_fat_list_path = 'testenv/jobs/rtyserver/autocheck_tests_fat.py'
    test_code_path = 'saas/rtyserver_test/tests'

    def needs_test_data(self, tdict):
        return 'rtyserver_test_data_dict_path' in tdict or 'rtyserver_test_data_path' in tdict

    def runnable_param(self, param):
        if not param:
            return True
        if '-g' in param:
            return False
        if '$CACHE' in param:
            return True
        return '$' not in param

    def get_rty_tests(self):
        Arcadia.export('arcadia:/arc/trunk/arcadia/' + self.tests_arc_path, self.path('rty_tests.py'))
        rty_tests = imp.load_source('rty_tests', self.path('rty_tests.py'))
        logging.info(dir(rty_tests))
        Tests = rty_tests.TESTS_
        testsNoRel = rty_tests.TESTS_DEBUG_BRANCH

        Arcadia.export('arcadia:/arc/trunk/arcadia/' + self.tests_arc_fat_list_path, self.path('autocheck_tests_fat.py'))
        autocheck_tests_fat = imp.load_source('autocheck_tests_fat', self.path('autocheck_tests_fat.py'))
        logging.info(dir(autocheck_tests_fat))
        FatTests = []
        for ft in autocheck_tests_fat.TESTS_AC_FAT:
            ft = ft[4:] if ft.startswith('test') else ft
            ft = ft if ft.endswith('_LINUX') else ft + '_LINUX'
            FatTests.append(ft)
        tests_res = []
        tests_morph = []
        tests_wdata = []
        tests_oxy = []
        tests_xl = []
        tests_rejected = []
        tests_gu_rejected = []
        tests_c_rejected = []
        tests_c_res = []
        tests_c_xl = []
        for ut in Tests['all']:
            test_param = ut[2] if len(ut) > 2 else ''
            test_ctx = ut[3] if len(ut) > 3 else {}
            if len(ut) < 3 or (self.runnable_param(test_param)):
                if ut[0] in testsNoRel:
                    continue
                if 'do_docs_times' in test_ctx:
                    tests_rejected.append(ut)
                    tests_c_rejected.append(ut)
                elif 'tester_timeout' in test_ctx and test_ctx['tester_timeout'] > 1200:
                    tests_xl.append(ut)
                    tests_c_xl.append(ut)
                elif len(ut) < 4 or not self.needs_test_data(test_ctx):
                    tests_res.append({'te_name': ut[0] + '_UNIT', 'tester_name': ut[1], 'test_params': test_param})
                    if len(ut) < 4:
                        tests_c_res.append({'te_name': ut[0] + '_UNIT_C', 'tester_name': ut[1],
                                            'test_params': ((test_param + ' ') if test_param else '') + '-g $CONF_PATH/cluster/cluster_nodm_1be.cfg'})
                    else:
                        tests_c_rejected.append(ut)
                elif self.needs_test_data(test_ctx) and 'rtyserver_test_data_path' not in test_ctx:
                    tests_morph.append({'te_name': ut[0] + '_UNIT', 'tester_name': ut[1],
                                        'test_params': ((test_param + ' ') if test_param else '') + '-o $DICT_PATH'})
                    tests_c_rejected.append(ut)
                elif 'Oxy' in ut[1]:
                    tests_oxy.append({'te_name': ut[0] + '_UNIT', 'tester_name': ut[1],
                                      'test_params': ((test_param + ' ') if test_param else '') + '-d $TEST_DATA_PATH'})
                    tests_c_rejected.append(ut)
                elif 'rtyserver_test_data_path' in test_ctx:
                    tests_wdata.append({'te_name': ut[0] + '_UNIT', 'tester_name': ut[1],
                                        'test_params': ((test_param + ' ') if test_param else '') + '-d $TEST_DATA_PATH'})
                    if 'rtyserver_test_data_dict_path' in test_ctx:
                        tests_wdata[-1]['test_params'] += ' -o $DICT_PATH'
                    tests_c_rejected.append(ut)
                else:
                    tests_rejected.append(ut)
                    tests_c_rejected.append(ut)
            else:
                if '-g' in test_param:
                    tests_gu_rejected.append(ut)
                else:
                    tests_rejected.append(ut)
                tests_c_rejected.append(ut)
        logging.info('rejected unit tests (%s): %s' % (len(tests_rejected), tests_rejected))
        logging.info('rejected unit -g tests (%s): %s' % (len(tests_gu_rejected), tests_gu_rejected))
        logging.info('rejected cluster tests (%s): %s' % (len(tests_c_rejected), tests_c_rejected))

        logging.info('big tests (%s): %s' % (len(tests_xl), tests_xl))
        logging.info('big cluster tests (%s): %s' % (len(tests_c_xl), tests_c_xl))

        rej_count = len(tests_rejected) + len(tests_gu_rejected) + len(testsNoRel)
        good_count = len(tests_res) + len(tests_wdata) + len(tests_morph) + len(tests_oxy) + len(tests_xl)
        if len(Tests['all']) != rej_count + good_count:
            raise Exception('Some tests are lost, %s != %s' % (len(Tests['all']), rej_count + good_count))
        return {'unit_common': tests_res,
                'unit_morph': tests_morph, 'unit_wdata': tests_wdata,
                'unit_oxy': tests_oxy,
                'unit_xl': tests_xl,
                'cluster_common': tests_c_res,
                'cluster_xl': tests_c_xl,
                'fat_marked': FatTests}

    def get_tests_stat(self, db_word):
        tstat_res = apihelpers.get_last_resource_with_attribute(resource_types.RTYSERVER_TESTS_STAT, db_word, '1')
        if not tstat_res:
            logging.error('cannot find tests stat')
            raise Exception('no tests stat')
        if tstat_res.timestamp < time.time() - 3600 * 36:
            logging.error('resource ts is too old: %s' % tstat_res.timestamp)
            raise Exception('no fresh resorces found')
        tstat_path = channel.task.sync_resource(tstat_res.id)
        with open(tstat_path, 'r') as f:
            txt = f.read()
            tests_st = json.loads(txt)
            logging.info('read stat for %s tests' % len(tests_st if 'autocheck' in db_word else tests_st['results']))
            return tests_st

    def select_short_tests(self, all_tests, short_tests, missing=False):
        if missing:
            tests = [t for t in all_tests if t['te_name'] + '_LINUX' not in short_tests]
        else:
            tests = [t for t in all_tests if t['te_name'] + '_LINUX' in short_tests]
        tests = sorted(tests, key=lambda x: x['te_name'])
        if not tests and not missing:
            raise Exception('no tests selected, something is wrong')
        return tests

    def validate_te_stat(self, times_te, db_word):
        if len(times_te) < 300:
            logging.error('too few tests for %s, %s' % (db_word, times_te))
            raise Exception('too few tests in stat')
        unit_num = len([t for t in times_te.keys() if 'UNIT_LINUX' in t])
        cluster_num = len([t for t in times_te.keys() if 'UNIT_C_LINUX' in t])
        if db_word == 'unit' and unit_num < 300:
            logging.error('too few unit tests: %s, %s' % (unit_num, times_te))
            raise Exception('too few unit tests for unit db')
        if db_word == 'cluster' and cluster_num < 300:
            logging.error('too few cluster tests: %s, %s' % (cluster_num, times_te))
            raise Exception('too few cluster tests for cluster db')

    def write_te_file(self, times_te, db_word):
        ftext = TE_FILE
        ROUND_INT = 30
        self.validate_te_stat(times_te, db_word)
        for test_name, test_time in sorted(times_te.items()):
            round_time = ROUND_INT * (1 + int(test_time) / ROUND_INT) if test_time > 0 else test_time
            ftext += 'RTY_TESTS_TIMES_MAX["' + test_name + '"] = ' + str(round_time) + '\n'
        te_res = self.path('times_stat_%s.py' % db_word)
        with open(te_res, 'w') as f:
            f.write(ftext)
        self._create_resource('stat file for testenv %s tests' % db_word, te_res, resource_types.RTY_RELATED_EXEC)
        return ftext

    def extract_ac_names(self, tests):
        test_names = [t['name'] for t in tests]
        test_names = [nm for nm in test_names if nm.startswith('test') and nm.endswith(('_UNIT', '_UNIT_C'))]
        test_names = [nm[4:] + '_LINUX' for nm in test_names]
        if len(test_names) < 200:
            raise Exception('too few tests wuth suitable names: %s from %s' % (test_names, len(tests)))
        return test_names

    def write_te_ac_file(self, tests):
        ftext = TE_AC_FILE
        test_names = self.extract_ac_names(tests)
        for test in sorted(test_names):
            ftext += 'TESTS_AC.append("' + test + '")\n'
        te_res = self.path('autocheck_tests.py')
        with open(te_res, 'w') as f:
            f.write(ftext)
        self._create_resource('saas autocheck list for testenv', te_res, resource_types.RTY_RELATED_EXEC)
        return ftext

    def update_te_ac(self):
        tests = self.get_tests_stat('autocheck_list')
        te_file_texts = {'autocheck_tests.py': self.write_te_ac_file(tests)}
        with ssh.Key(self, 'RTYSERVER-ROBOT', 'ssh_key'):
            if self.ctx['do_commit']:
                te_rep = Arcadia.checkout('arcadia:/arc/trunk/arcadia/testenv/jobs/rtyserver',
                                          self.path('rtyserver'))
                self.commit_tests(te_file_texts, te_rep)

    def edit_te_stat(self):
        te_file_texts = {}
        for db_word in ('unit', 'cluster'):
            tests_stat = self.get_tests_stat(db_word)
            times_te = {}
            for tr in tests_stat['results']:
                tmax = tr['data']['max']
                times_te[tr['test']] = tmax
            te_file_texts['times_stat_%s.py' % db_word] = self.write_te_file(times_te, db_word)
        with ssh.Key(self, 'RTYSERVER-ROBOT', 'ssh_key'):
            if self.ctx['do_commit']:
                te_rep = Arcadia.checkout('arcadia:/arc/trunk/arcadia/testenv/jobs/rtyserver',
                                          self.path('rtyserver'))
                self.commit_tests(te_file_texts, te_rep)

    def get_split_tests_by_times(self, db_word, fat_list):
        tests_st = self.get_tests_stat(db_word)
        if db_word == 'unit':
            tests_ac_st = self.get_tests_stat('autocheck-unit')
            tests_old_stat_d = dict([(tr['test'], tr) for tr in tests_st['results']])
            for tr in tests_ac_st['results']:
                tn = tr['test']
                tn = tn[4:] if tn.startswith('test') else tn
                tn = tn if tn.endswith('_LINUX') else (tn + '_LINUX')
                tr['test'] = tn
                if tn not in tests_old_stat_d:
                    tests_old_stat_d[tn] = tr
                    logging.info('added ac stat for %s' % tn)
                else:
                    if tr['data'].get('cnt', -1) > 12:
                        tests_old_stat_d[tn] = tr
                        logging.info('rewritten ac stat for %s' % tn)
                tests_st['results'] = sorted(tests_old_stat_d.values(), key=lambda x: x['test'])
        if db_word == 'unit':
            file_name = 'tests_gen_info.json'
        elif db_word == 'cluster':
            file_name = 'tests_gen_info_cluster.json'
        else:
            raise Exception('unknown db word')
        tests_info_path = Arcadia.export('arcadia:/arc/trunk/arcadia/' + self.test_code_path + '/' + file_name,
                                         self.path(file_name))
        with open(tests_info_path, 'r') as tsf:
            ts_txt = tsf.read()
            tests_old_st = json.loads(ts_txt)
            logging.info('read old stat for %s %s tests' % (len(tests_old_st), db_word))

        short_tests = []
        medium_tests = []
        long_tests = []
        tests_info = {}
        tests_total_count = len(tests_st['results'])
        for tr in tests_st['results']:
            tavg = tr['data']['avg']
            tmax = tr['data']['max']
            cnt_sufficient = tr['data'].get('cnt', 50) > 12 or tr['data'].get('cnt', 50) < 0
            if tr['test'] in fat_list \
                    or (not cnt_sufficient and tr['test'] not in tests_old_st):
                long_tests.append(tr['test'])
                continue
            if 0 < tavg < 120 and 0 < tmax < 180:
                short_tests.append(tr['test'])
                tests_info[tr['test']] = tr['data']
                tests_info[tr['test']]['size'] = 's'
            elif tavg == -1 and tr['test'] in tests_old_st:
                if tests_old_st[tr['test']]['size'] == 's':
                    short_tests.append(tr['test'])
                elif tests_old_st[tr['test']]['size'] == 'm':
                    medium_tests.append(tr['test'])
                tests_info[tr['test']] = tests_old_st[tr['test']]
            elif tr['test'] in tests_old_st and tests_old_st[tr['test']]['size'] == 's' and 0 < tavg < 180 and 0 < tmax < 210:
                short_tests.append(tr['test'])
                tests_info[tr['test']] = tr['data']
                tests_info[tr['test']]['size'] = 's'
            elif 0 < tavg < 480 and 0 < tmax < 510:
                medium_tests.append(tr['test'])
                tests_info[tr['test']] = tr['data']
                tests_info[tr['test']]['size'] = 'm'
            elif tr['test'] in tests_old_st and 0 < tavg < 510 and 0 < tmax < 540:
                medium_tests.append(tr['test'])
                tests_info[tr['test']] = tr['data']
                tests_info[tr['test']]['size'] = 'm'
            else:
                long_tests.append(tr['test'])
        if len(short_tests) + len(medium_tests) + len(long_tests) != tests_total_count:
            raise Exception('some tests are lost on time division: %s != %s + %s + %s' %
                            (tests_total_count, len(short_tests), len(medium_tests), len(long_tests)))
        return {'short_tests': short_tests, 'medium_tests': medium_tests, 'long_tests': long_tests, 'tests_info': tests_info}

    def gen_tests_file_text(self, tests, save_name, cluster=False, timeout=240):
        if cluster:
            tests_file_text = 'from test import run_cluster_test\n\n'
        else:
            tests_file_text = 'from test_common import run_test\n\n'
        for test in tests:
            if cluster:
                next_part_templ = test_cluster_file_part
            else:
                next_part_templ = test_file_part
            next_part = next_part_templ.format(TEST_TE_NAME=test['te_name'],
                                               TEST_NAME=test['tester_name'],
                                               TEST_PARAMS=test['test_params'],
                                               TIMEOUT=timeout)
            tests_file_text += next_part
        if save_name:
            tests_res_path = self.path(save_name)
            with open(tests_res_path, 'w') as f:
                f.write(tests_file_text)
            self._create_resource('tests code: ' + save_name, tests_res_path, resource_types.RTY_RELATED_EXEC)
        return tests_file_text

    def commit_tests(self, tests_file_text_dict, tests_rep, commit_folder=None):
        for file_path, file_text in tests_file_text_dict.items():
            tgen_path = os.path.join(tests_rep, file_path)
            with open(tgen_path, 'w') as f:
                f.write(file_text)
        commit_path = os.path.join(tests_rep, commit_folder) if commit_folder else tests_rep
        if self.ctx.get('do_commit'):
            comm = Arcadia.commit(
                commit_path,
                'generated tests, task ' + str(self.id) + ' : ' + self.descr,
                'saas-robot')
            with open(self.log_path('arcadia_commit.%s.out' % time.time()), 'w') as f:
                f.write(comm)
        else:
            diff = Arcadia.diff(commit_path)
            with open(self.log_path('diff_' + str(time.time())), 'w') as f:
                f.write(diff)

    def update_saas_tests(self):
        # get rty_tests
        tests_te_sets = self.get_rty_tests()
        tests_te = tests_te_sets['unit_common']
        tests_te_morph = tests_te_sets['unit_morph']
        tests_te_wdata = tests_te_sets['unit_wdata']
        tests_te_oxy = tests_te_sets['unit_oxy']
        tests_te_c = tests_te_sets['cluster_common']

        tests_fat_marked = tests_te_sets['fat_marked']

        # choose short tests
        short_long_stat = self.get_split_tests_by_times('unit', tests_fat_marked)
        short_tests = short_long_stat['short_tests']
        medium_tests = short_long_stat['medium_tests']
        long_tests = short_long_stat['long_tests']
        tests_info = short_long_stat['tests_info']

        logging.info('short tests(%s): %s' % (len(short_tests), short_tests))
        logging.info('medium tests(%s): %s' % (len(medium_tests), medium_tests))
        logging.info('long tests (%s): %s' % (len(long_tests), long_tests))

        tests = self.select_short_tests(tests_te, short_tests)
        tests_morph = self.select_short_tests(tests_te_morph, short_tests)
        tests_wdata = self.select_short_tests(tests_te_wdata, short_tests)
        tests_oxy = self.select_short_tests(tests_te_oxy, short_tests)
        tests_med = self.select_short_tests(tests_te, medium_tests)
        tests_ul = self.select_short_tests(tests_te, long_tests)
        tests_umis = self.select_short_tests(tests_te, long_tests + medium_tests + short_tests, missing=True)
        logging.info('long unit tests (%s) %s' % (len(tests_ul), tests_ul))
        logging.info('missing tests (%s) %s' % (len(tests_umis), tests_umis))

        short_long_c_stat = self.get_split_tests_by_times('cluster', tests_fat_marked)
        short_c_tests = short_long_c_stat['short_tests']
        tests_c_info = short_long_c_stat['tests_info']
        logging.info('short cluster tests: %s' % short_c_tests)

        tests_c = self.select_short_tests(tests_te_c, short_c_tests)

        # gen tests py file
        tests_file_text = self.gen_tests_file_text(tests, 'test_gen.py')
        tests_morph_file_text = self.gen_tests_file_text(tests_morph, 'test_dictable_gen.py')
        tests_wdata_file_text = self.gen_tests_file_text(tests_wdata, 'tests_with_data_gen.py')
        tests_oxy_file_text = self.gen_tests_file_text(tests_oxy, 'tests_oxygen_gen.py')
        tests_med_file_text = self.gen_tests_file_text(tests_med, 'tests_medium_gen.py', timeout=540)
        tests_long_file_text = self.gen_tests_file_text(tests_ul, 'tests_long_gen.py', timeout=1200)

        tests_c_file_text = self.gen_tests_file_text(tests_c, 'test_cluster_gen.py', cluster=True)

        with ssh.Key(self, 'RTYSERVER-ROBOT', 'ssh_key'):
            logging.info('key succeeded')
            if self.ctx['do_commit'] or True:
                tests_rep = Arcadia.checkout('arcadia:/arc/trunk/arcadia/' + self.test_code_path,
                                             self.path('tests'))
                self.commit_tests({'test_gen.py': tests_file_text, 'tests_gen_info.json': sorted_json_dump(tests_info)},
                                  tests_rep)
                self.commit_tests({'with_data/test_dictable_gen.py': tests_morph_file_text}, tests_rep, 'with_data')
                self.commit_tests({'with_data/test_with_data_gen.py': tests_wdata_file_text}, tests_rep, 'with_data')
                self.commit_tests({'oxygen/test_oxygen_gen.py': tests_oxy_file_text}, tests_rep, 'oxygen')
                self.commit_tests({'unit_10m/test_medium_gen.py': tests_med_file_text}, tests_rep, 'unit_10m')
                self.commit_tests({'unit_long/test_long_gen.py': tests_long_file_text}, tests_rep, 'unit_long')

                self.commit_tests({'cluster/test_cluster_gen.py': tests_c_file_text}, tests_rep, 'cluster')
                self.commit_tests({'tests_gen_info_cluster.json': sorted_json_dump(tests_c_info)}, tests_rep)

    def on_execute(self):
        if self.ctx.get(WhatToUpdateParameter.name) == 'testenv_stat':
            self.edit_te_stat()
        elif self.ctx.get(WhatToUpdateParameter.name) == 'te_autocheck':
            self.update_te_ac()
        elif self.ctx.get(WhatToUpdateParameter.name) == 'autocheck':
            self.update_saas_tests()
        else:
            raise Exception('error in parameter: %s' % self.ctx.get(WhatToUpdateParameter.name))
        cinf = commits_info(self.log_path())
        logging.info('commits: %s' % cinf)
        self.set_info('Commits (%s) : %s' % (len(cinf), '\n'.join([
            ','.join(c.get('files', [])) + ': '
            + '<a target="_blank" href="https://a.yandex-team.ru/arc/commit/{rev}">{rev}</a>'.format(rev=c.get('rev', ''))
            for c in cinf])), do_escape=False)


__Task__ = TestRTYServerManage
