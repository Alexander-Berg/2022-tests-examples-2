# -*- coding: utf-8 -*-
from enum import Enum

from sandbox.projects.browser.autotests.classes.frozendict import FrozenDict


class JobExecutors(Enum):

    manual = "manual"
    assessor = "assessor"


class SuiteInfo(FrozenDict):

    def __init__(self, suite_info):

        super(SuiteInfo, self).__init__(
            id=suite_info["id"],
            project=suite_info["project"],
            tags=tuple(suite_info["tags"]),
            url=suite_info["url"],
            aggregate_manual_runs=suite_info["aggregate_manual_runs"],
            aggregate_asessors_runs=suite_info["aggregate_asessors_runs"],
            honey_logs=suite_info.get("honey_logs") or False)


class TestingJob(FrozenDict):

    def __init__(self, uuid, case_id, case_project,
                 testrun_environment, build_info,
                 executor, component, is_automated, estimate, case_grouping_fields, suite_info):

        super(TestingJob, self).__init__(
            uuid=uuid,
            case_id=case_id,
            case_project=case_project,
            testrun_environment=testrun_environment,
            build_info=FrozenDict(build_info) if build_info is not None else None,
            executor=executor,
            component=component,
            is_automated=is_automated,
            estimate=estimate,
            case_grouping_fields=tuple(case_grouping_fields),
            suite_info=SuiteInfo(suite_info))


class TestrunTemplate(FrozenDict):

    def __init__(self, project, component, jobs, environment, build_info, part, suite_info):

        cases = {_j['case_id']: FrozenDict({"case_grouping_fields": tuple(_j['case_grouping_fields'])}) for _j in jobs}
        super(TestrunTemplate, self).__init__(
            project=project,
            component=component,
            cases=FrozenDict(cases),
            environment=environment,
            build_info=FrozenDict(build_info) if build_info is not None else None,
            part=part,
            suite_info=SuiteInfo(suite_info))


def get_jobs_statistic(jobs, stat_data=None):
    stat_data = {} if stat_data is None else stat_data
    result = []
    for job in jobs:
        job_dump = dict(
            testcase_id=job.get('testcase_id') or "{}-{}".format(job['case_project'], job['case_id']),
            uuid=job['uuid'],
            component=job['component'],
            testrun_environment=job['testrun_environment'],
            executor=job['executor'],
            is_automated=job['is_automated'],
            estimate=job['estimate']
        )
        for name, value in stat_data.iteritems():
            job_dump[name] = value
        result.append(job_dump)
    return result
