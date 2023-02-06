import json
import re
import requests


TESTPALM_API = "https://testpalm-api.yandex-team.ru"
STARTRACK_API = "https://st-api.yandex-team.ru/v2"

ALL_TPL = '''
По результатам (({} прогона)):
**<#<span class="awesome-icon awesome-icon_icon_bug"></span>#> Найдено багов**: {}
**<#<span class="awesome-icon awesome-icon_icon_list"></span>#> Всего кейсов в наборе**: {}
'''
PASSED_TPL = '''
<{{**!!(green)<#<span class="awesome-icon awesome-icon_icon_check-circle"></span>#> Passed!!**: {}
{} }}>
'''
FAILED_TPL = '''
<{{**!!(red)<#<span class="awesome-icon awesome-icon_icon_times-circle"></span>#> Failed!!**: {}
{} }}>
'''
SKIPPED_TPL = '''
<{{**!!(grey)<#<span class="awesome-icon awesome-icon_icon_minus-circle"></span>#> Skipped!!**: {}
{} }}>
'''
BROKEN_TPL = '''
<{{**!!(yellow)<#<span class="awesome-icon awesome-icon_icon_times-circle-o"></span>#> Broken!!**: {}
{} }}>
'''
KNOWNBUG_TPL = '''
<{{**!!(red)<#<span class="awesome-icon awesome-icon_icon_bug"></span>#> Known bug!!**: {}
{} }}>
'''
BLOCKED_TPL = '''
<{{**!!(blue)<#<span class="awesome-icon awesome-icon_icon_exclamation-circle"></span>#> Blocked!!**: {}
{} }}>
'''


def get_project_from_url(run_url):
    project = re.compile(r"(https://testpalm.yandex-team.ru/)(\S*)/testrun")
    return project.search(run_url).group(2)


def get_run_id_from_url(run_url):
    run_id = re.compile(r"(https://testpalm.yandex-team.ru/)(\S*)(/testrun/)(\w*\d*)")
    return run_id.search(run_url).group(4)


def get_testrun_result(run_url, tp_oauth_token):
    project_id = get_project_from_url(run_url)
    run_id = get_run_id_from_url(run_url)
    session = requests.Session()
    session.headers.update({"Authorization": f"OAuth {tp_oauth_token}"})
    r = session.get(url=f"{TESTPALM_API}/testrun/{project_id}/{run_id}")
    return r.json()


def make_report_from_run(run_url, tp_oauth_token):
    project_id = get_project_from_url(run_url)
    run_id = get_run_id_from_url(run_url)

    report_json = get_testrun_result(run_url, tp_oauth_token)
    parent_ticket = report_json["parentIssue"]["id"]
    counter = report_json["resolution"]["counter"]
    total = int(counter['total'])
    passed = int(counter['passed'])
    failed = int(counter['failed'])
    skipped = int(counter['skipped'])
    knownbug = int(counter['knownbug'])
    blocked = int(counter['blocked'])
    broken = int(counter['broken'])

    bugs_found = set()
    test_cases = report_json["testGroups"][0]["testCases"]
    passed_list = []
    failed_list = []
    skipped_list = []
    knownbug_list = []
    blocked_list = []
    broken_list = []
    for test_case in test_cases:
        test_case_id = f"{project_id}-{test_case['testCase']['id']}"
        test_case_tpl = f"1. ((https://testpalm.yandex-team.ru/testcase/{test_case_id} {test_case_id}))"
        bugs = test_case['testCase']['bugs']
        if len(bugs) != 0:
            bugs_list = []
            for bug in bugs:
                if 'foundInTestRun' in bug.keys():
                    if bug['foundInTestRun'] == run_id:
                        bugs_list.append(f"https://st.yandex-team.ru/{bug['id']}")
                        bugs_found.add(bug['id'])
            if len(bugs_list) != 0:
                test_case_tpl = test_case_tpl + "\n"
                for b in bugs_list:
                    test_case_tpl = test_case_tpl + f"  * {b}\n"
                test_case_tpl = test_case_tpl.rstrip("\n")
        if test_case["status"] == "PASSED":
            passed_list.append(test_case_tpl)
        elif test_case["status"] == "FAILED":
            failed_list.append(test_case_tpl)
        elif test_case["status"] == "SKIPPED":
            skipped_list.append(test_case_tpl)
        elif test_case["status"] == "KNOWNBUG":
            knownbug_list.append(test_case_tpl)
        elif test_case["status"] == "BLOCKED":
            blocked_list.append(test_case_tpl)
        elif test_case["status"] == "BROKEN":
            broken_list.append(test_case_tpl)

    all_res = ALL_TPL.format(run_url, len(bugs_found), total)
    report_parts = [all_res]
    if passed != 0:
        passed_res = PASSED_TPL.format(passed, "\n".join(passed_list))
        report_parts.append(passed_res)
    if failed != 0:
        failed_res = FAILED_TPL.format(failed, "\n".join(failed_list))
        report_parts.append(failed_res)
    if skipped != 0:
        skipped_res = SKIPPED_TPL.format(skipped, "\n".join(skipped_list))
        report_parts.append(skipped_res)
    if broken != 0:
        broken_res = BROKEN_TPL.format(broken, "\n".join(broken_list))
        report_parts.append(broken_res)
    if knownbug != 0:
        knownbug_res = KNOWNBUG_TPL.format(knownbug, "\n".join(knownbug_list))
        report_parts.append(knownbug_res)
    if blocked != 0:
        blocked_res = BLOCKED_TPL.format(blocked, "\n".join(blocked_list))
        report_parts.append(blocked_res)

    report = "".join(report_parts)
    return report, parent_ticket


def post_test_report_to_startrack(run_url, ticket_id, summonees, st_oauth_token, tp_oauth_token):
    report, parent_ticket = make_report_from_run(run_url, tp_oauth_token)
    session = requests.Session()
    session.headers.update({"Authorization": f"OAuth {st_oauth_token}", "Content-Type": "application/json"})

    if ticket_id != "" and ticket_id != parent_ticket:
        ticket = ticket_id
    else:
        ticket = parent_ticket
        res1 = session.get(url=f"{STARTRACK_API}/issues/{parent_ticket}")
        grandparent_ticket = res1.json()["parent"]["id"]
        res2 = session.get(url=f"{STARTRACK_API}/issues/{grandparent_ticket}")
        new_summonee = res2.json()["createdBy"]["id"]
        if new_summonee not in summonees:
            summonees.append(new_summonee)

    payload = {
        "text": report,
        "summonees": summonees
    }
    res = session.post(url=f"{STARTRACK_API}/issues/{ticket}/comments",
                        json=payload)


if __name__ == '__main__':
    with open('settings.json', 'r') as f:
        j = json.load(f)
    test_run_url = j['run_url']
    st_token = j["startrack_token"]
    tp_token = j["testpalm_token"]
    ticket = j["ticket_id"]
    summonees = j["summonees"]
    post_test_report_to_startrack(test_run_url, ticket, summonees, st_token, tp_token)
