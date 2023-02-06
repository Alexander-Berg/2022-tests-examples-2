import datetime
import difflib
import json
import typing

from sibilla import storage

GENERAL_NAME_FORMAT = 'summary.txt'
SUMMARY_NAME_FORMAT = '{session_uuid}_summary.txt'
REPORT_NAME_FORMAT = '{session_uuid}_testcase_{testcase_id:02d}.txt'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


def textify(val: typing.Any) -> str:
    txt = json.dumps(val, indent=4, sort_keys=True)
    if not txt.endswith('\n'):
        txt += '\n'
    return txt


def format_request(request: typing.Any) -> str:
    return textify(request)


def format_diff(expected: typing.Any, response: typing.Any) -> str:
    return '\n'.join(
        list(
            difflib.unified_diff(
                textify(expected).split('\n'),
                textify(response).split('\n'),
                fromfile='expected',
                tofile='response',
            ),
        ),
    )


def ms2str(time_ms: int) -> str:
    return datetime.datetime.fromtimestamp(time_ms / 1000).strftime(
        TIME_FORMAT,
    )


def generate_summary_report(
        out: typing.TextIO,
        session_stats: storage.SessionRec,
        testcase_stats: typing.Iterable[storage.TestcaseRec],
) -> None:
    out.write(
        """SESSION REPORT
UUID     : {uuid}
STARTED  : {started}
FINISHED : {finished}

OUTCOME  : {outcome}

NAME        : {name}
DESCRIPTION : {description}

TESTCASE COUNTS:
  TOTAL   : {tc_total}
  PASSED  : {tc_passed}
  SKIPPED : {tc_skipped}
  FAILED  : {tc_failed}
  ERROR   : {tc_error}

TEST COUNTS:
  TOTAL   : {total}
  PASSED  : {passed}
  SKIPPED : {skipped}
  FAILED  : {failed}
  ERROR   : {error}

DETAILS BY TESTCASE:
""".format(
            uuid=session_stats.session_uuid,
            started=ms2str(session_stats.start_ms),
            finished=ms2str(session_stats.finish_ms),
            outcome=session_stats.outcome.name,
            name=session_stats.name,
            description=session_stats.description,
            tc_total=(
                session_stats.num_passed_testcases
                + session_stats.num_skipped_testcases
                + session_stats.num_failed_testcases
                + session_stats.num_error_testcases
            ),
            tc_passed=session_stats.num_passed_testcases,
            tc_skipped=session_stats.num_skipped_testcases,
            tc_failed=session_stats.num_failed_testcases,
            tc_error=session_stats.num_error_testcases,
            total=(
                session_stats.num_passed_tests
                + session_stats.num_skipped_tests
                + session_stats.num_failed_tests
                + session_stats.num_error_tests
            ),
            passed=session_stats.num_passed_tests,
            skipped=session_stats.num_skipped_tests,
            failed=session_stats.num_failed_tests,
            error=session_stats.num_error_tests,
        ),
    )
    for tc_stat in testcase_stats:
        out.write(
            """TESTCASE #{testcase_id} REPORT
  STARTED  : {started}
  FINISHED : {finished}

  OUTCOME  : {outcome}

  NAME        : {name}
  DESCRIPTION : {description}

  COUNTS BY TESTS:
    TOTAL   : {total}
    PASSED  : {passed}
    SKIPPED : {skipped}
    FAILED  : {failed}
    ERROR   : {error}

""".format(
                testcase_id=tc_stat.testcase_id,
                started=ms2str(tc_stat.start_ms),
                finished=ms2str(tc_stat.finish_ms),
                outcome=tc_stat.outcome.name,
                name=tc_stat.name,
                description=tc_stat.description,
                total=(
                    tc_stat.num_passed_tests
                    + tc_stat.num_skipped_tests
                    + tc_stat.num_failed_tests
                    + tc_stat.num_error_tests
                ),
                passed=tc_stat.num_passed_tests,
                skipped=tc_stat.num_skipped_tests,
                failed=tc_stat.num_failed_tests,
                error=tc_stat.num_error_tests,
            ),
        )


def generate_test_report(out: typing.TextIO, rec: storage.TestResult) -> None:
    out.write(
        """TEST {session_uuid}:{testcase_id}:{test_id}
STARTED:  {started}
FINISHED: {finished}
OUTCOME: {outcome}
""".format(
            session_uuid=rec.session_uuid,
            testcase_id=rec.testcase_id,
            test_id=rec.test_id,
            started=ms2str(rec.start_ms),
            finished=ms2str(rec.finish_ms),
            outcome=rec.outcome.name,
        ),
    )
    if rec.outcome == storage.Outcome.FAILED:
        out.write(
            """
REQUEST:
{request}
EXPECTED vs RESPONSE:
{diff}
""".format(
                request=format_request(rec.request),
                diff=format_diff(rec.expected, rec.response),
            ),
        )
    elif rec.outcome == storage.Outcome.ERROR:
        out.write(
            """
REQUEST:
{request}
ERROR:
{error}
""".format(
                request=format_request(rec.request), error=rec.exc_info,
            ),
        )


def generate_report(
        outdir: str, stg: storage.Storage, session_uuid: str,
) -> typing.List[str]:
    """
    generate_report processes collected results and generates artifacts
    such as html report with statistics grouped by testcase
    and files with differences for each testcase

    :param outdir:str directory for storing artifacts. must be exists
    :param stg:storage.Storage database with test results
    :return: list of filenames of output files
    """

    retlist: typing.List[str] = []

    s_stat = stg.get_session(session_uuid)
    if not s_stat:
        return []
    tc_stats = list(stg.get_testcases(session_uuid))

    filename = '{dir}/{name}'.format(
        dir=outdir, name=SUMMARY_NAME_FORMAT.format(session_uuid=session_uuid),
    )
    out = open(filename, encoding='utf_8_sig', mode='wt')
    generate_summary_report(out, s_stat, tc_stats)
    out.close()
    retlist.append(filename)

    for tc_stat in tc_stats:
        filename = '{dir}/{name}'.format(
            dir=outdir,
            name=REPORT_NAME_FORMAT.format(
                session_uuid=tc_stat.session_uuid,
                testcase_id=tc_stat.testcase_id,
            ),
        )
        out = open(filename, encoding='utf_8_sig', mode='wt')
        recs = stg.results(
            tc_stat.session_uuid, testcase_id=tc_stat.testcase_id,
        )
        for rec in recs:
            generate_test_report(out, rec)
        out.close()
        retlist.append(filename)
    return retlist


def generate_general_report(outdir: str, stg: storage.Storage) -> str:
    """
    generate_general_report processes collected sessions
    and generate one report: summarize all of them

    :param outdir:str directory for storing artifacts. must be exists
    :param stg:storage.Storage database with test results
    :return: filename of output file
    """

    filename = f'{outdir}/{GENERAL_NAME_FORMAT}'

    out = open(filename, encoding='utf_8_sig', mode='wt')
    start_ms: int = 0
    finish_ms: int = 0

    stats: storage.Statistics = storage.Statistics()
    outcomes: typing.Dict[str, str] = {}

    for session in stg.get_sessions():
        start_ms = (
            min(start_ms, session.start_ms) if start_ms else session.start_ms
        )
        finish_ms = (
            max(finish_ms, session.finish_ms)
            if finish_ms
            else session.finish_ms
        )
        stats.add(session.outcome)
        outcomes[session.name] = session.outcome.value

    out.write(
        """GENERAL REPORT

STARTED  : {started}
FINISHED : {finished}

GENERAL OUTCOME: {outcome}

TEST SESSIONS OUTCOMES:
{session_list}

--- --- ---

    """.format(
            started=ms2str(start_ms),
            finished=ms2str(finish_ms),
            outcome=stats.aggregated_outcome.value,
            session_list='\n'.join(f'{x}: {y}' for x, y in outcomes.items()),
        ),
    )
    # print detailed information about sessions
    for session in stg.get_sessions():
        generate_summary_report(
            out, session, list(stg.get_testcases(session.session_uuid)),
        )

    # print detailed information about each test run
    for session in stg.get_sessions():
        empty = True
        for rec in stg.results(session.session_uuid):
            if empty:
                out.write(f'--- ISSUES FOR SESSION {session.session_uuid}\n')
                empty = False
            generate_test_report(out, rec)
        if empty:
            out.write(f'--- NO ISSUES FOR SESSION {session.session_uuid}\n')
    out.close()
    return filename
