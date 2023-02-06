import logging
import re
from copy import deepcopy

from sandbox.projects.yabs.release.binary_search import (
    intervals,
    report,
)


logger = logging.getLogger(__name__)


def get_original_revision(revision_info, is_trunk=True):
    if is_trunk:
        return revision_info['revision']
    pattern = r"\[original_trunk_revision:(?P<revision>\d+)\]"
    try:
        return int(re.search(pattern, revision_info['message']).groupdict()['revision'])
    except:
        logger.error("Cannot get original revision number from %s", revision_info['message'], exc_info=True)
    return None


def get_test_diffs(testenv_api_client, project_name, job_name, revision_gte=None, revision_lte=None):
    limit = 100
    offset = 0
    diffs = []

    while True:
        params = dict(limit=limit, offset=offset)
        if revision_lte:
            params.update(revision_lte=revision_lte)
        if revision_gte:
            params.update(revision_gte=revision_gte)
        chunk = testenv_api_client['projects'][project_name]['jobs'][job_name]['diffs'].GET(params=params)
        for diff in chunk:
            diffs.append(diff)
        offset += limit
        if len(chunk) < limit:
            break

    return diffs


def get_problems(testenv_api_client, project_name, job_name, revision_gte=None, revision_lte=None, status='unresolved'):
    params = dict(job_name=job_name, revision_gte=revision_gte, revision_lte=revision_lte)
    if revision_lte:
        params.update(revision_lte=revision_lte)
    if revision_gte:
        params.update(revision_gte=revision_gte)
    return testenv_api_client.projects[project_name]['problems'].GET(params=params)


def get_interval_map_from_db(testenv_api_client, database, test, start, finish, is_trunk=True):
    tests = testenv_api_client['projects'][database]['jobs'].GET()
    if test not in (t['name'] for t in tests):
        return {}

    interval_map = {}
    diffs = get_test_diffs(testenv_api_client, database, test, revision_gte=start, revision_lte=finish)
    for diff in diffs:
        if diff["diff_type"] in (intervals.NO_DIFF, intervals.DIFF_DATA):
            right_revision = get_original_revision(diff["right_revision"], is_trunk=is_trunk)
            left_revision = get_original_revision(diff["left_revision"], is_trunk=is_trunk)
            left_revision, right_revision = min(right_revision, left_revision), max(right_revision, left_revision)
            if right_revision and left_revision and start <= left_revision < finish and start < right_revision <= finish:
                interval_key = left_revision, right_revision

                interval_map[interval_key] = {"diff_type": diff["diff_type"],
                                              "task_id": diff["task_id"],
                                              "owner": diff["problem"].get("owner", ''),
                                              "database": database}

    return interval_map


def update_interval_info(base_interval_map, base_problems_by_interval, database_interval_map, database_problems, is_trunk=True):
    new_interval_map = deepcopy(base_interval_map)
    new_problems_by_interval = deepcopy(base_problems_by_interval)

    base_interval_map_keys = list(base_interval_map.keys())
    base_problems_by_interval_keys = list(base_problems_by_interval.keys())
    database_interval_min, database_interval_max = None, None

    if not database_interval_map:
        return new_interval_map, new_problems_by_interval

    for l, r in database_interval_map.keys():
        database_interval_min = min(database_interval_min or l, l)
        database_interval_max = max(database_interval_max or r, r)

    for l, r in base_interval_map_keys:
        if database_interval_min <= l < database_interval_max and database_interval_min < r <= database_interval_max:
            del new_interval_map[(l, r)]

    for rev in base_problems_by_interval_keys:
        if database_interval_min < rev <= database_interval_max:
            del new_problems_by_interval[rev]

    if is_trunk:
        new_problems_by_interval.update({
            problem["diff"]["right_revision"]["revision"]: problem
            for problem in database_problems
        })
    else:
        new_problems_by_interval.update({
            get_original_revision(problem["diff"]["left_revision"], is_trunk=is_trunk): problem
            for problem in database_problems
        })

    new_interval_map.update(database_interval_map)
    return new_interval_map, new_problems_by_interval


def get_interval_info_for_test(testenv_api_client, base_database, test, start, finish):
    base_database_info = testenv_api_client.projects[base_database]['edit'].GET()
    is_trunk = base_database_info['svn_path'] == 'trunk'
    interval_map = get_interval_map_from_db(testenv_api_client, base_database, test, start, finish, is_trunk=is_trunk)

    problems = get_problems(testenv_api_client, base_database, test, revision_gte=start, revision_lte=finish, status='unresolved')
    if is_trunk:
        problems_by_interval = {
            problem["diff"]["right_revision"]["revision"]: problem
            for problem in problems
        }
    else:
        problems_by_interval = {
            get_original_revision(problem["diff"]["left_revision"], is_trunk=is_trunk): problem
            for problem in problems
        }

    # Collect rerun info (database name SHOULT contain 'rerun' in database name)
    databases = testenv_api_client.projects.GET(params=dict(type='custom_check', name=base_database, status='working'))
    logger.debug('Got databases: %s', databases)
    for database in databases:
        if 'rerun' not in database['name']:
            continue

        rerun_database_info = testenv_api_client['projects'][database['name']]['edit'].GET()
        is_trunk = rerun_database_info['svn_path'] == 'trunk'

        rerun_start = start if is_trunk else None
        rerun_finish = finish if is_trunk else None

        rerun_interval_map = get_interval_map_from_db(testenv_api_client, database['name'], test, start, finish, is_trunk=is_trunk)
        rerun_problems = get_problems(testenv_api_client, database['name'], test, revision_gte=rerun_start, revision_lte=rerun_finish, status='unresolved')

        interval_map, problems_by_interval = update_interval_info(interval_map, problems_by_interval, rerun_interval_map, rerun_problems, is_trunk=is_trunk)

    logger.debug("Got interval map: %s", interval_map)
    logger.debug("Got problems map: %s", problems_by_interval)

    return interval_map, problems_by_interval


def iter_release_reports(sandbox_client, testenv_api_client, db, tests, start, finish, try_get_original_revisions=False):
    for test in tests:
        interval_map, problems_by_interval = get_interval_info_for_test(testenv_api_client, db, test, start, finish)
        interval_sequence = intervals.Partitioner(interval_map).partition_interval((start, finish))

        summary_rows, interval_table_rows = report.get_report_data(sandbox_client, interval_sequence, problems_by_interval)
        yield report.create_startrek_report(summary_rows, interval_table_rows, test)
