# -*- coding: utf-8 -*-
from enum import Enum

from sandbox.projects.browser.autotests_qa_tools.classes.autotests_bundle import get_isolate_autotest_bundle, get_latest_autotests_bundle_by_framework_branch


class Attribute(Enum):

    AutomationStatus = 'Automation Status'
    AutomarkedTagName = 'automatic_markedtrue'


class AutomationStatus(Enum):
    Ready = ['Ready']


class ReportStatuses(Enum):

    WillBeAutoMarked = (
        u"Автоматизированны и будут размечены автоматически",
    )
    NotCorrectlyMarked = (
        u"Автоматизированные кейсы без теста",
        u"Неверно размечено как Automation status = Rady, но кейс отсутствует в автотестах",
    )
    NotCorrectlyNotMarked = (
        u"Кейсы размеченные тегом",
        u"Разметка Automation status отсутствует, автотест есть, но автоматическая разметка запрещена automatic_markedtrue",
    )
    Problems = (
        u"Кейсы с проблемной разметкой. Не удалось обработать",
    )


class TestcasesAnalyst(object):

    def __init__(self, ya_clients):
        self.clients = ya_clients

    def check_automated_mapping(self, projects, tests_builds, consider_platforms, treat_blacklisted_cases_as_automated,
                                desktop_autotests_branch=None):

        result = {}
        autotests_bundles = [
            get_isolate_autotest_bundle(tests_build_id, self.clients, tested_application='browser') for tests_build_id in tests_builds] + [
            get_isolate_autotest_bundle(tests_build_id, self.clients, tested_application='searchapp') for tests_build_id in tests_builds]

        if desktop_autotests_branch:
            desktop_bundle = get_latest_autotests_bundle_by_framework_branch(desktop_autotests_branch, None, self.clients)
            if desktop_bundle:
                autotests_bundles.append(desktop_bundle)

        for project in projects:
            cases = self.clients.testpalm.get_cases(
                project,
                include_fields=('id', 'attributes', 'status', 'removed'))
            for case in cases:
                if case.case_data.get("status") != u'ACTUAL' or case.case_data.get("removed"):  # or case.get_definition_map_id(Attribute.AutomationStatus.value) is None
                    continue
                target = None
                try:
                    testpalm_status = case.mapped_attributes.get(Attribute.AutomationStatus.value, [])
                    tag_status = Attribute.AutomarkedTagName.value in case.mapped_attributes.get("Tags", [])

                except:
                    target = ReportStatuses.Problems

                if target is None:
                    autotests_status = False
                    for platform in consider_platforms:
                        for autoteste_bundle in autotests_bundles:
                            autotests_status = autotests_status or autoteste_bundle.is_automated_in_tests(
                                "{}-{}".format(case.project, case.id),
                                platform,
                                ignore_blacklists=treat_blacklisted_cases_as_automated)

                    if autotests_status:
                        if not testpalm_status:
                            if not tag_status:
                                target = ReportStatuses.WillBeAutoMarked
                            else:
                                target = ReportStatuses.NotCorrectlyNotMarked
                        else:
                            pass
                    else:
                        if testpalm_status == AutomationStatus.Ready.value:
                            target = ReportStatuses.NotCorrectlyMarked
                        else:
                            pass

                if target is not None:
                    result.setdefault(target, []).append(case)

        return result

    def render_report(self, report_dict, projects, tests_builds):

        html_report = u"<h3>Отчёт о соответствии разметки кейсов существующим автотестам</h3>"
        html_report += u"По проектам: <ul>{}</ul>".format(
            "".join(
                '<li><a href="https://testpalm.yandex-team.ru/{}" target="_blank">{}</a></li>'.format(_p, _p) for _p in projects
            )
        )
        html_report += u"Сборки с автотестами: <ul>{}</ul>".format(
            "".join(
                '<li><a href="https://teamcity.browser.yandex-team.ru/viewLog.html?buildId={}" target="_blank">#{}</a></li>'.format(_b, _b) for _b in tests_builds
            )
        )
        for title, cases in report_dict.iteritems():
            html_report += u"<hr><div>{}:<ol>{}</ol></div>".format(
                ".<br/>".join(title.value),
                u"".join(u'<li><a href="{}" target="_blank">{}</a></li>'.format(
                    _c.url,
                    "{}-{}".format(_c.project, _c.id)) for _c in sorted(cases, key=lambda x: x.url))
            )
        return u"<html><title>Анализ разметки кейсов</title><body>{}</body></html>".format(html_report)

    def mark_cases_as_automated(self, cases):
        self.clients.testpalm.update_cases_attribute(
            cases,
            {
                Attribute.AutomationStatus.value: AutomationStatus.Ready.value
            },
            add_tags=[Attribute.AutomarkedTagName.value]
        )
