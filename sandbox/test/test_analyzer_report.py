from datetime import datetime, timedelta
import pytest

import pytz

from sandbox.projects.yabs.qa.template_utils import get_template
from sandbox.projects.yabs.qa.tasks.YabsServerAnalyzeProductionWrapper import (
    TEMPLATES_DIR,
    ReportData,
    get_ab_links,
    split_datetime_interval,
    Events,
    UTC_DAY_BEGINNING,
    UTC_DAY_END,
    DEFAULT_INITIAL_ANALYSIS_DURATION,
)


ANALYSIS_INTERVALS = split_datetime_interval(
    start=datetime(year=2022, month=4, day=9, hour=12, minute=23, second=47, tzinfo=pytz.utc),
    duration=timedelta(seconds=DEFAULT_INITIAL_ANALYSIS_DURATION),
    day_start_time=UTC_DAY_BEGINNING,
    day_end_time=UTC_DAY_END,
)


def get_report_data(
        component_name='yabs_server',
        task_id=1267716164,
        task_type='YABS_SERVER_ANALYZE_PRODUCTION_WRAPPER',
        yabs_testing_version='r641-3',
        yabs_stable_version='r640-1',
        bs_testing_version='r641-3',
        bs_stable_version='r640-1',
        status=None,
        report_links=(
            ('Analysis report', 'https://proxy.sandbox.yandex-team.ru/2965297180/report.html'),
            ('Flame graphs', 'https://proxy.sandbox.yandex-team.ru/2965309019'),
        ),
        ab_experiment_links=get_ab_links(ANALYSIS_INTERVALS),
        checks=(
            (u'\U00002705', 'Enough clicks'),
            (u'\U0000274c', 'Timeouts validation failed'),
            (u'\U00002705', 'Statistics is good')
        ),
):
    return ReportData(
        task_id=task_id,
        task_type=task_type,
        component_name=component_name,
        yabs_testing_version=yabs_testing_version,
        yabs_stable_version=yabs_stable_version,
        bs_testing_version=bs_testing_version,
        bs_stable_version=bs_stable_version,
        status=status,
        report_links=report_links,
        ab_experiment_links=ab_experiment_links,
        checks=checks,
    )


class TestAnalyzerReportYachats(object):

    def test_yachats_fail(self):
        report_template_j2 = get_template('analyzer_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = (
            u'\U0001F6AB Prestable analysis is failed\n'
            u'\n'
            u'[YABS_SERVER_ANALYZE_PRODUCTION #1272297440](http://sandbox.yandex-team.ru:8081/task/1272297440) finished with FAILURE status\n'
            u'\n'
            u'@igorock please check if everything is ok with (pre)stable\n'
            u'\n'
            u'Sent by [YABS_SERVER_ANALYZE_PRODUCTION_WRAPPER #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)'
        )
        report_data = ReportData(
            component_name='yabs_server',
            task_id=1267716164,
            task_type='YABS_SERVER_ANALYZE_PRODUCTION_WRAPPER',
            status=Events.failed,
            analyze_production_task_id=1272297440,
            analyze_production_task_type='YABS_SERVER_ANALYZE_PRODUCTION',
            analyze_production_task_status='FAILURE',
        )

        assert expected_text == report_template_j2.render(report_data.as_dict(transport='yachats', mentions=['igorock']))

    @pytest.mark.parametrize('status', (Events.done, Events.not_done))
    def test_yachats(self, status):
        report_template_j2 = get_template('analyzer_report.j2', templates_dir=TEMPLATES_DIR)

        call = (
            (
                u'@igorock please check if everything is ok with (pre)stable\n'
                u'\n'
            ) if status == Events.not_done else u''
        )
        expected_text = (
            u'{status.value.icon} Prestable analysis is {status.value.text}\n'
            u'\n'
            u'\U00002705 Enough clicks\n'
            u'\U0000274c Timeouts validation failed\n'
            u'\U00002705 Statistics is good\n'
            u'\n'
            u'Compared versions:\n'
            u'YABS: r641-3 vs r640-1\n'
            u'BS: r641-3 vs r640-1\n'
            u'\n'
            u'[Analysis report](https://proxy.sandbox.yandex-team.ru/2965297180/report.html)\n'
            u'[Flame graphs](https://proxy.sandbox.yandex-team.ru/2965309019)\n'
            u'\n'
            u'2022-04-09 12:30:00+00:00 - 2022-04-09 17:00:00+00:00\n'
            u'[Stable vs Prestable BS]'
            u'(https://ab.yandex-team.ru/observation/1309116/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'[Stable vs Prestable all]'
            u'(https://ab.yandex-team.ru/observation/1063425/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'[Stable vs Prestable YABS]'
            u'(https://ab.yandex-team.ru/observation/1309117/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'\n'
            u'{call}'
            u'Sent by [YABS_SERVER_ANALYZE_PRODUCTION_WRAPPER #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)'
        ).format(status=status, call=call)

        assert expected_text == report_template_j2.render(get_report_data(status=status).as_dict(transport='yachats', mentions=['igorock']))

    def test_telegram_fail(self):
        report_template_j2 = get_template('analyzer_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = (
            u'\U0001F6AB Prestable analysis is failed\n'
            u'\n'
            u'[YABS\\_SERVER\\_ANALYZE\\_PRODUCTION \\#1272297440](http://sandbox.yandex-team.ru:8081/task/1272297440) finished with FAILURE status\n'
            u'\n'
            u'@igorock please check if everything is ok with \\(pre\\)stable\n'
            u'\n'
            u'\\#analysis \\#yabs\\_server\n'
            u'Sent by [YABS\\_SERVER\\_ANALYZE\\_PRODUCTION\\_WRAPPER \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)'
        )
        report_data = ReportData(
            component_name='yabs_server',
            task_id=1267716164,
            task_type='YABS_SERVER_ANALYZE_PRODUCTION_WRAPPER',
            status=Events.failed,
            analyze_production_task_id=1272297440,
            analyze_production_task_type='YABS_SERVER_ANALYZE_PRODUCTION',
            analyze_production_task_status='FAILURE',
        )

        assert expected_text == report_template_j2.render(report_data.as_dict(transport='telegram', mentions=['igorock']))

    @pytest.mark.parametrize('status', (Events.done, Events.not_done))
    def test_telegram(self, status):
        report_template_j2 = get_template('analyzer_report.j2', templates_dir=TEMPLATES_DIR)

        call = (
            (
                u'@igorock please check if everything is ok with \\(pre\\)stable\n'
                u'\n'
            ) if status == Events.not_done else u''
        )
        expected_text = (
            u'{status.value.icon} Prestable analysis is {status.value.text}\n'
            u'\n'
            u'\U00002705 Enough clicks\n'
            u'\U0000274c Timeouts validation failed\n'
            u'\U00002705 Statistics is good\n'
            u'\n'
            u'Compared versions:\n'
            u'YABS: r641\\-3 vs r640\\-1\n'
            u'BS: r641\\-3 vs r640\\-1\n'
            u'\n'
            u'[Analysis report](https://proxy.sandbox.yandex-team.ru/2965297180/report.html)\n'
            u'[Flame graphs](https://proxy.sandbox.yandex-team.ru/2965309019)\n'
            u'\n'
            u'2022\\-04\\-09 12:30:00\\+00:00 \\- 2022\\-04\\-09 17:00:00\\+00:00\n'
            u'[Stable vs Prestable BS]'
            u'(https://ab.yandex-team.ru/observation/1309116/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'[Stable vs Prestable all]'
            u'(https://ab.yandex-team.ru/observation/1063425/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'[Stable vs Prestable YABS]'
            u'(https://ab.yandex-team.ru/observation/1309117/calc/bs/20220409/20220409?'
            u'granularity=half&groups=clean_frauds_staff&aggr=fast&cache=1&ts_start=1649507400&ts_end=1649523600#colored=true)\n'
            u'\n'
            u'{call}'
            u'\\#analysis \\#yabs\\_server\n'
            u'Sent by [YABS\\_SERVER\\_ANALYZE\\_PRODUCTION\\_WRAPPER \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)'
        ).format(status=status, call=call)

        assert expected_text == report_template_j2.render(get_report_data(status=status).as_dict(transport='telegram', mentions=['igorock']))
