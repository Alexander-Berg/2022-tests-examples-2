import logging
import re
from collections import defaultdict
from urlparse import parse_qs, urlparse

import requests

from sandbox.projects.release_machine.core import const as rm_const


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def testenv_database_exists(testenv_helper, database_name):
    url = rm_const.Urls.TESTENV + "handlers/systemInfo"
    params = {
        'database': database_name,
    }
    response = requests.get(url, params=params)
    if response.status_code in (requests.codes.NOT_FOUND, requests.codes.BAD_REQUEST):
        return False
    response.raise_for_status()
    return True


def get_launches_for_revision(testenv_helper, database_name, revision, test_names):
    last_results = testenv_helper.get_last_results(database_name)
    logger.debug("Last results for %s are %s", database_name, last_results)

    launches_for_revision = {}

    for test_results in last_results:
        for test_result in test_results:
            if test_result.get('name') in test_names and test_result.get('revision') == revision:
                launches_for_revision[test_result['name']] = test_result['task_id']

    return launches_for_revision


def get_aux_base_for_revision(testenv_helper, database_name, init_job_name, revision):
    aux_bases_by_revisions = defaultdict(dict)
    if not testenv_database_exists(testenv_helper, database_name):
        logger.warning("Database '%s' does not exist", database_name)
        return None

    aux_base_link_pattern = re.compile(r'href=[\'"]?(?P<link>[^\'" >]+)')
    aux_runs = testenv_helper.get_aux_runs(database_name)
    for aux_run in aux_runs:
        # TODO: TESTENV-2880
        m = aux_base_link_pattern.search(aux_run['auxiliary_check'])
        if m is None:
            continue
        parsed_url = urlparse(m.groupdict()['link'])
        parsed_query = parse_qs(parsed_url.query)
        aux_database_name_values = parsed_query.get('database', [])
        for aux_database_name in aux_database_name_values:
            if not testenv_database_exists(testenv_helper, aux_database_name):
                logger.warning("Auxiliary database '%s' does not exist", aux_database_name)
                continue
            aux_bases_by_revisions[aux_run['revision_to']][aux_database_name] = aux_run
    logger.debug("Found aux databases for %s:\n%s", database_name, aux_bases_by_revisions)
    aux_bases = aux_bases_by_revisions.get(revision, {})
    if aux_bases:
        return max(aux_bases.items(), key=lambda k: k[1]['create_timestamp'])[0]
    return None


def get_revision_for_aux_base(testenv_helper, database_name, desired_aux_database_name):
    if not testenv_database_exists(testenv_helper, database_name):
        logger.warning("Database '%s' does not exist", database_name)
        return None

    aux_base_link_pattern = re.compile(r'href=[\'"]?(?P<link>[^\'" >]+)')
    aux_runs = testenv_helper.get_aux_runs(database_name)
    for aux_run in aux_runs:
        # TODO: TESTENV-2880
        m = aux_base_link_pattern.search(aux_run['auxiliary_check'])
        if m is None:
            if aux_run['auxiliary_check'] == desired_aux_database_name:
                return aux_run['revision_to']
            continue
        parsed_url = urlparse(m.groupdict()['link'])
        parsed_query = parse_qs(parsed_url.query)
        aux_database_name_values = parsed_query.get('database', [])
        for aux_database_name in aux_database_name_values:
            if aux_database_name == desired_aux_database_name:
                return aux_run['revision_to']

    return None
