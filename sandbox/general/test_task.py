# -*- coding: utf-8 -*-
import logging
import os
import csv
from sandbox.projects.clickhouse.util.report import create_test_html_report
from sandbox.projects.clickhouse.BaseOnCommitTask.base import BaseOnCommitTask, NeedToRunDescription
from sandbox.projects.clickhouse.util.task_helper import has_changes_in_code

import datetime
import traceback


class BaseOnCommitTestTask(BaseOnCommitTask):

    @staticmethod
    def need_to_run(pr_info):
        if not has_changes_in_code(pr_info):
            return NeedToRunDescription(False, "No diff in .cpp, .h, .py, etc...", False)

        return BaseOnCommitTask.need_to_run(pr_info)

    # return state, description, test_result, raw_log_path
    def run(self, commit, repo, pull_request):
        raise Exception("Unimplemented")

    def with_raw_logs(self):
        return False

    def get_additional_urls(self):
        return []

    def prepare_tests_results_for_clickhouse(
            self, commit, repo, pull_request, test_results,
            check_status, check_duration, check_start_time,
            report_url):

        pull_request_url = "https://github.com/ClickHouse/ClickHouse/commits/master"
        base_ref = "master"
        head_ref = "master"
        base_repo = repo.full_name
        head_repo = repo.full_name
        if pull_request.number != 0:
            pull_request_url = pull_request.html_url
            base_ref = pull_request.raw_data['base']['ref']
            base_repo = pull_request.raw_data['base']['repo']['full_name']
            head_ref = pull_request.raw_data['head']['ref']
            head_repo = pull_request.raw_data['head']['repo']['full_name']

        common_properties = dict(
            pull_request_number=pull_request.number,
            commit_sha=commit.sha,
            commit_url=commit.html_url,
            check_name=self.get_context_name(),
            check_status=check_status,
            check_duration_ms=int(float(check_duration) * 1000),
            check_start_time=check_start_time,
            report_url=report_url,
            pull_request_url=pull_request_url,
            base_ref=base_ref,
            base_repo=base_repo,
            head_ref=head_ref,
            head_repo=head_repo,
            task_url=self.task_url,
        )

        # Always publish a total record for all checks. For checks with individual
        # tests, also publish a record per test.
        result = [common_properties]
        for test_result in test_results:
            current_row = common_properties.copy()
            test_name = test_result[0]
            test_status = test_result[1]

            test_time = 0
            if len(test_result) > 2 and test_result[2]:
                test_time = test_result[2]
            current_row['test_duration_ms'] = int(float(test_time) * 1000)
            current_row['test_name'] = test_name
            current_row['test_status'] = test_status
            result.append(current_row)

        return result

    # TODO Move it to github. We can use user 'viewer' with password 'no-password' or pass it through env.
    def mark_flaky_tests(self, test_results):
        try:
            query = """
            SELECT DISTINCT test_name
            FROM checks
            WHERE
                check_start_time BETWEEN now() - INTERVAL 3 DAY AND now()
                AND check_name = '{check_name}'
                AND (test_status = 'FAIL' OR test_status = 'FLAKY')
                AND pull_request_number = 0
            """.format(check_name=self.get_context_name())

            tests_data = self.clickhouse_helper.select_json_each_row('gh-data', query)
            master_failed_tests = set([row['test_name'] for row in tests_data])
            logging.info("Found flaky tests: %s", ', '.join(master_failed_tests))

            for test_result in test_results:
                if test_result[1] == 'FAIL' and test_result[0] in master_failed_tests:
                    test_result[1] = 'FLAKY'
        except Exception as ex:
            logging.info("Exception happened during flaky tests fetch %s", ex)

    def with_coverage(self):
        return False

    def process_result_simple(self, result_folder, server_log_folder, perfraw_path, commit, repo, pull_request):
        test_results = []
        additional_files = []
        # Just upload all files from result_folder.
        # If task provides processed results, then it's responsible for content of result_folder.
        if os.path.exists(result_folder):
            test_files = [f for f in os.listdir(result_folder) if os.path.isfile(os.path.join(result_folder, f))]
            additional_files = [os.path.join(result_folder, f) for f in test_files]

        status_path = os.path.join(result_folder, "check_status.tsv")
        if not os.path.exists(status_path):
            # Task does not provide processed results
            # Or it's old branch on github (maybe release branch)
            try:
                return self.process_result(result_folder, server_log_folder, perfraw_path, commit, repo, pull_request)
            except Exception:
                traceback.print_exc()
                return "error", "Failed to process results", test_results, additional_files

        logging.info("Found test_results.tsv")
        status = list(csv.reader(open(status_path, 'r'), delimiter='\t'))
        if len(status) != 1 or len(status[0]) != 2:
            return "error", "Invalid check_status.tsv", test_results, additional_files
        state, description = status[0][0], status[0][1]

        try:
            results_path = os.path.join(result_folder, "test_results.tsv")
            test_results = list(csv.reader(open(results_path, 'r'), delimiter='\t'))
            if len(test_results) == 0:
                raise Exception("Empty results")

            if self.with_coverage():
                coverage_path = os.path.join(result_folder, "clickhouse_coverage.tar.gz")
                if os.path.exists(coverage_path):
                    self.make_coverage_resource(coverage_path, commit, pull_request)
                elif state == "success":
                    return "error", "Cannot get coverage", test_results, additional_files

            return state, description, test_results, additional_files
        except Exception:
            if state == "success":
                state, description = "error", "Failed to read test_results.tsv"
            return state, description, test_results, additional_files

    def process_logs(self, test_results, additional_logs, s3_path_prefix, with_raw_logs=False):
        proccessed_logs = dict()
        # Firstly convert paths of logs from test_results to urls to s3.
        for test_result in test_results:
            if len(test_result) <= 3 or with_raw_logs:
                continue

            # Convert from string repr of list to list.
            test_log_paths = eval(test_result[3])
            test_log_urls = []
            for log_path in test_log_paths:
                if log_path in proccessed_logs:
                    test_log_urls.append(proccessed_logs[log_path])
                elif log_path:
                    url = self.s3_client.upload_test_report_to_s3(
                        log_path,
                        s3_path_prefix + "/" + os.path.basename(log_path))
                    test_log_urls.append(url)
                    proccessed_logs[log_path] = url

            test_result[3] = test_log_urls

        additional_urls = []
        for log_path in additional_logs:
            if log_path and log_path not in proccessed_logs:
                additional_urls.append(
                    self.s3_client.upload_test_report_to_s3(
                        log_path,
                        s3_path_prefix + "/" + os.path.basename(log_path)))

        return additional_urls

    def process(self, commit, repo, pull_request):
        logging.info("Run job function")

        start_time = datetime.datetime.utcnow()
        result = self.run(self.commit, repo, pull_request)
        duration = (datetime.datetime.utcnow() - start_time).total_seconds()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

        if len(result) == 4:
            state, description, test_results, raw_log_path = result
            additional_logs = []
        elif len(result) == 5:
            state, description, test_results, raw_log_path, additional_logs = result

        logging.info("Job finished with state %s and description %s", state, description)
        if test_results is not None:
            s3_path_prefix = str(pull_request.number) + "/" + self.commit.sha + "/" + self.get_context_name().lower().replace(' ', '_')
            logging.info("s3 upload prefix %s", s3_path_prefix)
            if raw_log_path and os.path.exists(raw_log_path):
                raw_log_url = self.s3_client.upload_test_report_to_s3(
                    raw_log_path,
                    s3_path_prefix + "/" + os.path.basename(raw_log_path))
            else:
                raw_log_url = raw_log_path

            additional_urls = self.process_logs(test_results, additional_logs, s3_path_prefix, self.with_raw_logs())

            # Add link to help. Anchors in the docs must be adjusted accordingly.
            normalized_check_name = ''.join([c.lower() for c in self.get_context_name() if c.isalpha() or c == ' '])
            docs_anchor = '-'.join(normalized_check_name.split(' ')[:3])
            help_url = "https://clickhouse.tech/docs/en/development/continuous-integration/#" + docs_anchor
            additional_urls.append((help_url, "Help"))

            branch_url = repo.html_url
            branch_name = "master"
            if pull_request.number != 0:
                branch_name = "PR #{}".format(pull_request.number)
                branch_url = pull_request.html_url
            commit_url = commit.html_url

            self.mark_flaky_tests(test_results)

            html_report = create_test_html_report(
                self.get_context_name(),
                test_results,
                raw_log_url,
                self.task_url,
                branch_url,
                branch_name,
                commit_url,
                additional_urls=(additional_urls + self.get_additional_urls()),
                with_raw_logs=self.with_raw_logs()
            )
            with open('report.html', 'w') as f:
                f.write(html_report)
            url = self.s3_client.upload_test_report_to_s3('report.html', s3_path_prefix + ".html")
            try:
                test_results_for_ch = self.prepare_tests_results_for_clickhouse(
                    commit, repo, pull_request, test_results,
                    state, duration, start_time_str, url)

                self.clickhouse_helper.insert_events_into('gh-data', 'checks', test_results_for_ch)
            except Exception as ex:
                logging.info("Cannot insert data in clickhouse %s", ex)
        else:
            url = self.task_url

        logging.info("Search result in url %s", url)

        return state, description, url
