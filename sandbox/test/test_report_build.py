import textwrap
from collections import OrderedDict

from sandbox.projects.yabs.qa.template_utils import get_template
from sandbox.projects.yabs.release.notifications.environment.report_info import TaskInfo
from sandbox.projects.yabs.release.tasks.ReportBuildArtifacts import TEMPLATES_DIR, ReportData, ResourceInfo


ARTIFACTS = OrderedDict([
    (
        TaskInfo('BUILD_YABS_SERVER', 123456),
        [
            ResourceInfo('BS_RELEASE_TAR', 234567),
            ResourceInfo('BS_RELEASE_YT', 234568),
        ]
    ),
    (
        TaskInfo('SETUP_YA_MAKE', 123459),
        [
            ResourceInfo('MKDB_INFO_RESOURCE', 234569),
        ]
    )
])


class TestReportBuild(object):
    def test_report_build_telegram(self):
        report_template_j2 = get_template('build_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(r'''
            Component yabs\_server was built successfully from tag [r641\-3](https://a.yandex-team.ru/arc/tags/yabs_server/r641-3) and is ready to release

            \* [BUILD\_YABS\_SERVER \#123456](http://sandbox.yandex-team.ru:8081/task/123456):
              \* [BS\_RELEASE\_TAR \#234567](http://sandbox.yandex-team.ru:8081/resource/234567)
              \* [BS\_RELEASE\_YT \#234568](http://sandbox.yandex-team.ru:8081/resource/234568)
            \* [SETUP\_YA\_MAKE \#123459](http://sandbox.yandex-team.ru:8081/task/123459):
              \* [MKDB\_INFO\_RESOURCE \#234569](http://sandbox.yandex-team.ru:8081/resource/234569)

            @igorock your deploy links:
            [Deploy yabs\_server r641\-3](https://rm.z.yandex-team.ru/component/yabs_server/manage?branch=641&tag=3)

            \#build \#r641 \#r641\_3
            Sent by [YABS\_SERVER\_REPORT\_BUILD \#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n').decode()

        assert expected_text == report_template_j2.render(ReportData(
            artifacts=ARTIFACTS,
            major_version=641,
            minor_version=3,
            task_id=1267716164,
        ).as_dict(transport='telegram', mentions=['igorock']))

    def test_report_build_yachats(self):
        report_template_j2 = get_template('build_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(r'''
            Component yabs_server was built successfully from tag [r641-3](https://a.yandex-team.ru/arc/tags/yabs_server/r641-3) and is ready to release

            * [BUILD_YABS_SERVER #123456](http://sandbox.yandex-team.ru:8081/task/123456):
              * [BS_RELEASE_TAR #234567](http://sandbox.yandex-team.ru:8081/resource/234567)
              * [BS_RELEASE_YT #234568](http://sandbox.yandex-team.ru:8081/resource/234568)
            * [SETUP_YA_MAKE #123459](http://sandbox.yandex-team.ru:8081/task/123459):
              * [MKDB_INFO_RESOURCE #234569](http://sandbox.yandex-team.ru:8081/resource/234569)

            @igorock your deploy links:
            [Deploy yabs_server r641-3](https://rm.z.yandex-team.ru/component/yabs_server/manage?branch=641&tag=3)

            Sent by [YABS_SERVER_REPORT_BUILD #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n').decode()

        assert expected_text == report_template_j2.render(ReportData(
            artifacts=ARTIFACTS,
            major_version=641,
            minor_version=3,
            task_id=1267716164,
        ).as_dict(transport='yachats', mentions=['igorock']))

    def test_report_build_startrek(self):
        report_template_j2 = get_template('build_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(r'''
            Component yabs_server was built successfully from tag [r641-3](https://a.yandex-team.ru/arc/tags/yabs_server/r641-3) and is ready to release

            * [BUILD_YABS_SERVER #123456](http://sandbox.yandex-team.ru:8081/task/123456):
              * [BS_RELEASE_TAR #234567](http://sandbox.yandex-team.ru:8081/resource/234567)
              * [BS_RELEASE_YT #234568](http://sandbox.yandex-team.ru:8081/resource/234568)
            * [SETUP_YA_MAKE #123459](http://sandbox.yandex-team.ru:8081/task/123459):
              * [MKDB_INFO_RESOURCE #234569](http://sandbox.yandex-team.ru:8081/resource/234569)

            staff:igorock your deploy links:
            [Deploy yabs_server r641-3](https://rm.z.yandex-team.ru/component/yabs_server/manage?branch=641&tag=3)

            Sent by [YABS_SERVER_REPORT_BUILD #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n').decode()

        assert expected_text == report_template_j2.render(ReportData(
            artifacts=ARTIFACTS,
            major_version=641,
            minor_version=3,
            task_id=1267716164,
        ).as_dict(transport='startrek', mentions=['igorock']))

    def test_report_build_no_minor_version(self):
        report_template_j2 = get_template('build_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(r'''
            Component yabs\_server was built successfully and is ready to release

            \* [BUILD\_YABS\_SERVER \#123456](http://sandbox.yandex-team.ru:8081/task/123456):
              \* [BS\_RELEASE\_TAR \#234567](http://sandbox.yandex-team.ru:8081/resource/234567)
              \* [BS\_RELEASE\_YT \#234568](http://sandbox.yandex-team.ru:8081/resource/234568)
            \* [SETUP\_YA\_MAKE \#123459](http://sandbox.yandex-team.ru:8081/task/123459):
              \* [MKDB\_INFO\_RESOURCE \#234569](http://sandbox.yandex-team.ru:8081/resource/234569)

            @igorock nothing you can do from here

            \#build \#r641
        ''').lstrip('\n').decode()

        assert expected_text == report_template_j2.render(ReportData(
            artifacts=ARTIFACTS,
            major_version=641,
            minor_version=None,
        ).as_dict(transport='telegram', mentions=['igorock']))

    def test_report_build_no_mentions(self):
        report_template_j2 = get_template('build_report.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(r'''
            Component yabs\_server was built successfully from tag [r641\-3](https://a.yandex-team.ru/arc/tags/yabs_server/r641-3) and is ready to release

            \* [BUILD\_YABS\_SERVER \#123456](http://sandbox.yandex-team.ru:8081/task/123456):
              \* [BS\_RELEASE\_TAR \#234567](http://sandbox.yandex-team.ru:8081/resource/234567)
              \* [BS\_RELEASE\_YT \#234568](http://sandbox.yandex-team.ru:8081/resource/234568)
            \* [SETUP\_YA\_MAKE \#123459](http://sandbox.yandex-team.ru:8081/task/123459):
              \* [MKDB\_INFO\_RESOURCE \#234569](http://sandbox.yandex-team.ru:8081/resource/234569)

             your deploy links:
            [Deploy yabs\_server r641\-3](https://rm.z.yandex-team.ru/component/yabs_server/manage?branch=641&tag=3)

            \#build \#r641 \#r641\_3
        ''').lstrip('\n').decode()

        assert expected_text == report_template_j2.render(ReportData(
            artifacts=ARTIFACTS,
            major_version=641,
            minor_version=3,
        ).as_dict(transport='telegram'))
