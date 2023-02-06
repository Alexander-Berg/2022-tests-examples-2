#!/skynet/python/bin/python -W ignore::UserWarning
# -*- coding: utf-8 -*-

import os
import unittest
import time
import cPickle

from sandbox.projects.common.base_search_quality import dolbilka_response_parser
from sandbox.projects.common.base_search_quality import dolbilka_response_diff
from sandbox.projects.common.base_search_quality import basesearch_response_parser
from sandbox.projects.common.base_search_quality import threadPool
from sandbox.projects.common.base_search_quality.tree import htmldiff
from sandbox.projects.common.differ import printers


class TestException(Exception):
    pass


_NCPU = 32


class MainTestCase(unittest.TestCase):
    test_data_dir = None

    tmp_dir = None

    diff_dir = None

    shouldWriteDiffs = True

    def setUp(self):
        self.DolbilkaOutput1 = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput1"), True)

        self.FACTOR_NAMES = open(os.path.join(self.test_data_dir, "factorNames")).read().split('\n')
        self.USER_REQUESTS = open(os.path.join(self.test_data_dir, "userRequests")).read().split('\n')

    def tearDown(self):
        pass

    def WriteDiffs(self, diffs, dirName):
        if self.shouldWriteDiffs:
            dir = os.path.join(self.diff_dir, dirName)
            os.mkdir(dir)
            dolbilka_response_diff.WriteDiffs(diffs, self.FACTOR_NAMES, self.USER_REQUESTS, dir)

    def test1(self):
        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, self.DolbilkaOutput1)

        if diffs.HasDifferences():
            raise Exception("there must be no any differences")

        if not diffs == dolbilka_response_diff.DiffsBetweenDolbilkas():
            raise Exception("DiffsBetweenDolbilkas is not filled correctly")

        self.WriteDiffs(diffs, "diff1")

    def test2(self):
        otherDolbilkaOutput = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput2"), True)

        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, otherDolbilkaOutput)

        if not diffs.HasDifferences():
            raise Exception("there must be difference")

        diff2 = dolbilka_response_diff.DiffsBetweenDolbilkas()

        diff2.Dolbilka1FoundNothingForQueries = set([4])

        if not diffs == diff2:
            raise Exception("DiffsBetweenDolbilkas is not filled correctly")

        self.WriteDiffs(diffs, "diff2")

    def test3(self):
        otherDolbilkaOutput = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput3"), True)

        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, otherDolbilkaOutput)

        if not diffs.HasDifferences():
            raise Exception("there must be difference")

        diff2 = dolbilka_response_diff.DiffsBetweenDolbilkas()

        diff2.Dolbilka2FoundNothingForQueries = set([5])

        if not diffs == diff2:
            raise Exception("DiffsBetweenDolbilkas is not filled correctly")

        self.WriteDiffs(diffs, "diff3")

    def test4(self):
        otherDolbilkaOutput = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput4"), True)

        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, otherDolbilkaOutput)

        if not diffs.HasDifferences():
            raise Exception("there must be difference")

        diff2 = dolbilka_response_diff.DiffsBetweenDolbilkas()

        diff2.Dolbilka1FoundNothingForQueries = set([4, 7])
        diff2.Dolbilka2FoundNothingForQueries = set([2, 5, 9])

        if not diffs == diff2:
            raise Exception("DiffsBetweenDolbilkas is not filled correctly")

        self.WriteDiffs(diffs, "diff4")

    def test5(self):
        otherDolbilkaOutput = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput5"), True)

        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, otherDolbilkaOutput)

        if not diffs.HasDifferences():
            raise Exception("there must be difference")

        diff2 = dolbilka_response_diff.DiffsBetweenDolbilkas()

        diff2.Dolbilka1FoundNothingForQueries = set([4, 7])
        diff2.Dolbilka2FoundNothingForQueries = set([2, 5, 9])

        diffForQuery3 = dolbilka_response_diff.DiffsForSingleQuery()
        diffForQuery3.Dolbilka2NotFoundUrls = set(["4139 www.newsru.com/religy/02aug2006/muromec.html", "2807 massarakshh.livejournal.com"])
        diff2.DiffsForQueries[3] = diffForQuery3

        diffForQuery8 = dolbilka_response_diff.DiffsForSingleQuery()
        diffForQuery8.Dolbilka1NotFoundUrls = set(["2216 www.test.com/test.html"])
        diff2.DiffsForQueries[8] = diffForQuery8

        if not diffs == diff2:
            raise Exception("DiffsBetweenDolbilkas is not filled correctly:\ndiffs: %s\ndiff2: %s" % (diffs, diff2))

        self.WriteDiffs(diffs, "diff5")

    def test6(self):
        otherDolbilkaOutput = dolbilka_response_parser.parse_and_group_by_query(os.path.join(self.test_data_dir, "dolbilkaOutput6"), True)

        diffs = dolbilka_response_diff.CompareResults(self.DolbilkaOutput1, otherDolbilkaOutput)

        if not diffs.HasDifferences():
            raise Exception("there must be difference")

        diff2 = dolbilka_response_diff.DiffsBetweenDolbilkas()

        diff2.Dolbilka1FoundNothingForQueries = set([4])

        diffForQuery3 = dolbilka_response_diff.DiffsForSingleQuery()

        diffForUrl = dolbilka_response_diff.DiffForSingleUrl()
        diffForUrl.DifferentRelevance = [101526232, 111222333]
        diffForUrl.DifferentFactorValues[1] = [0.00232684, 0.5556777]

        diffForQuery3.DiffsForUrls["2807 massarakshh.livejournal.com"] = diffForUrl

        diff2.DiffsForQueries[3] = diffForQuery3

        diffForQuery9 = dolbilka_response_diff.DiffsForSingleQuery()

        diffForUrl = dolbilka_response_diff.DiffForSingleUrl()
        diffForUrl.DifferentFactorValues[0] = [0.302198, 0.112233]
        diffForUrl.DifferentFactorValues[1] = [0.00687229, 0.445566]
        diffForUrl.DifferentFactorValues[14] = [0.513726, 0.123123]

        diffForQuery9.DiffsForUrls["4861 www.avtoweb.com/review-Volkswagen_Lupo_-out.html"] = diffForUrl

        diffForUrl = dolbilka_response_diff.DiffForSingleUrl()
        diffForUrl.DifferentFactorValues[15] = [0.753086, 0.567567]

        diffForQuery9.DiffsForUrls["1529 www.mkdoska.com"] = diffForUrl

        diff2.DiffsForQueries[9] = diffForQuery9

        if not diffs == diff2:
            raise Exception("DiffsBetweenDolbilkas is not filled correctly:\ndiffs: %s\ndiff2: %s" % (diffs, diff2))

        self.WriteDiffs(diffs, "diff6")

    def testMatchStringColorChanged(self):
        def get_res(s1, s2):
            res1, res2 = printers.match_string_color_changed(s1, s2)
            return [j for _, j in res1], [j for _, j in res2]

        tests_data = [
            ('true', 'false', ['tru', 'e'], ['fals', 'e']),
            ('komu', 'kogo', ['ko', 'mu'], ['ko', 'go']),
            ('sheeva', 'shiva', ['sh', 'ee', 'va'], ['sh', 'i', 'va']),
            ('deeds', 'meeting', ['d', 'ee', 'ds'], ['m', 'ee', 'ting']),
            ('abracadabra', 'logarithm', ['', 'a', 'b', 'r', 'acadabra'], ['log', 'a', '', 'r', 'ithm'])
        ]

        for s1, s2, expect_r1, expect_r2 in tests_data:
            r1, r2 = get_res(s1, s2)
            self.assertEqual(r1, expect_r1)
            self.assertEqual(r2, expect_r2)

    def testTreeHtmlDiff(self):
        trees = basesearch_response_parser.parse_responses(os.path.join(self.test_data_dir, "tree.txt"))

        trees = [cPickle.loads(t) for t in trees]

        tree1 = trees[0]
        tree2 = trees[1]
        tree3 = trees[2]
        tree4 = trees[3]

        self.assertEqual(str(htmldiff.get_tree_similarity(tree1, tree1)), "17")
        self.assertEqual(str(htmldiff.get_tree_similarity(tree1, tree2)), "15")
        self.assertEqual(str(htmldiff.get_tree_similarity(tree1, tree3)), "17")
        self.assertEqual(str(htmldiff.get_tree_similarity(tree1, tree4)), "9")

    def testBasesearchResponseParser(self):
        file1 = os.path.join(self.test_data_dir, "basesearch_responses1.txt")
        file2 = os.path.join(self.test_data_dir, "basesearch_responses2.txt")
        file3 = os.path.join(self.test_data_dir, "basesearch_responses3.txt")
        file4 = os.path.join(self.test_data_dir, "basesearch_responses4.txt")
        file5 = os.path.join(self.test_data_dir, "basesearch_responses5.txt")
        file6 = os.path.join(self.test_data_dir, "basesearch_responses6.txt")
        file7 = os.path.join(self.test_data_dir, "basesearch_responses7.txt")
        file8 = os.path.join(self.test_data_dir, "basesearch_responses8.txt")
        file9 = os.path.join(self.test_data_dir, "basesearch_responses9.txt")
        file10 = os.path.join(self.test_data_dir, "basesearch_responses10.txt")
        file11 = os.path.join(self.test_data_dir, "basesearch_responses11.txt")
        file12 = os.path.join(self.test_data_dir, "basesearch_responses12.txt")
        file13 = os.path.join(self.test_data_dir, "basesearch_responses13.txt")
        file14 = os.path.join(self.test_data_dir, "basesearch_responses14.txt")
        file15 = os.path.join(self.test_data_dir, "basesearch_responses15.txt")
        file16 = os.path.join(self.test_data_dir, "basesearch_responses16.txt")
        file17 = os.path.join(self.test_data_dir, "basesearch_responses17.txt")
        file18 = os.path.join(self.test_data_dir, "basesearch_responses18.txt")
        file19 = os.path.join(self.test_data_dir, "basesearch_responses19.txt")
        file20 = os.path.join(self.test_data_dir, "basesearch_responses20.txt")
        file21 = os.path.join(self.test_data_dir, "basesearch_responses21.txt")

        self.assertEqual(basesearch_response_parser.compare_response_files(file1, file1), True)
        self.assertEqual(basesearch_response_parser.compare_response_files(file1, file1, True), True)
        self.assertEqual(basesearch_response_parser.compare_response_files(file2, file2), True)
        self.assertEqual(basesearch_response_parser.compare_response_files(file1, file2), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file2, file1), False)
        try:
            self.assertEqual(basesearch_response_parser.compare_response_files(file1, file3), False)
        except Exception:
            pass
        else:
            raise Exception("must raise exception")
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file3), True)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file4), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file5), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file6), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file7), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file7, True), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file8), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file9), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file10), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file11), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file12), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file13), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file14), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file15), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file16), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file17), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file18), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file19), False)
        self.assertEqual(basesearch_response_parser.compare_response_files(file3, file20), False)

        responses1 = basesearch_response_parser.parse_responses(file1)
        responses2 = basesearch_response_parser.parse_responses(file2)

        responses1Stable = basesearch_response_parser.parse_responses(file1, remove_unstable_props=True)
        responses2Stable = basesearch_response_parser.parse_responses(file2, remove_unstable_props=True)

        responsesAsStrings = [cPickle.loads(r).ToStr() for r in responses1]
        tmpFileName = self.tmp_dir + "/responsesAsStr.txt"
        basesearch_response_parser.write_responses(tmpFileName, responsesAsStrings)

        responses3 = basesearch_response_parser.parse_responses(tmpFileName)

        self.assertEqual(basesearch_response_parser.compare_responses(responses1, responses3), True)
        self.assertEqual(basesearch_response_parser.compare_responses(responses2, responses3), False)

        self.assertEqual(basesearch_response_parser.compare_responses(responses1, responses2), False)
        self.assertEqual(basesearch_response_parser.compare_responses(responses1Stable, responses2Stable), True)

        htmlDiffFileName = os.path.join(self.tmp_dir, "diff.html")
        file = open(htmlDiffFileName, "w")

        # queries = ["&user_request=%s&lr=%s" % (n, n) for n in range(len(responses1))]

        # changedProps = htmldiff.ChangedProps()
        # basesearchResponsesDiff.write_html_diff(file, queries, responses1, responses2, changedProps)

        file.close()

        self.assertEqual(basesearch_response_parser.compare_responses(responses1, responses2), False)

        self.assertEqual(basesearch_response_parser.compare_responses(responses1Stable, responses2Stable), True)

        response21 = basesearch_response_parser.parse_responses(file21)[0]
        response21 = cPickle.loads(response21)
        basesearch_response_parser.check_response(response21)

    def testThreadPool(self):
        def test(use_processes):
            def DolberFunc1(datas, params):
                datas = list(datas)
                self.assertEqual(len(datas), 2)
                self.assertEqual(datas[0] + 1, datas[1])

                return [x*2 for x in datas]

            list_to_process = range(_NCPU * 2)

            results = threadPool.process_data(DolberFunc1, list_to_process, None, use_processes=use_processes)

            self.assertEqual(len(list_to_process), len(results))

            for input, output in zip(list_to_process, results):
                self.assertEqual(input * 2, output)

            def DolberFunc2(datas, params):
                time.sleep(1)

            try:
                timeout = None
                if not use_processes:
                    timeout = 0.1
                threadPool.process_data(DolberFunc2, list_to_process, None, use_processes=use_processes, timeout=timeout)
            except threadPool.TimeoutException:
                pass

            def DolberFunc3(datas, params):
                raise Exception("error in thread")

            class MyException(Exception):
                pass

            try:
                threadPool.process_data(DolberFunc3, list_to_process, None, use_processes=use_processes, timeout=2, default_exception_type=MyException)
            except MyException:
                pass
            else:
                raise Exception("must throw MyException")

            def DolberFunc4(datas, params):
                raise TestException("sandbox error in thread")

            try:
                threadPool.process_data(DolberFunc4, list_to_process, None, use_processes=use_processes, timeout=2)
            except TestException:
                pass
            else:
                raise Exception("must throw TestException")

        test(False)
        test(True)


def init_tests(tmp_dir):
    from sandbox.projects.common import base_search_quality
    MainTestCase.test_data_dir = os.path.join(os.path.dirname(base_search_quality.__file__), 'UnitTestsData')

    MainTestCase.tmp_dir = tmp_dir
    os.mkdir(MainTestCase.tmp_dir)

    MainTestCase.diff_dir = os.path.join(MainTestCase.tmp_dir, "diffs")
    os.mkdir(MainTestCase.diff_dir)
