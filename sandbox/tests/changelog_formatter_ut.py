from __future__ import unicode_literals

import pytest

import sandbox.projects.release_machine.helpers.changelog_formatter as cf


class ComponentInfoMock(object):
    pass


c_info = ComponentInfoMock()
c_info.svn_cfg__REPO_NAME = "arc"
c_info.testenv_cfg__trunk_db = "te_trunk_db"
HEADERS = ("revision", "review_ids", "reasons", "te_problems")
CHANGELOG = [
    {
        "revision": 123456,
        "review_ids": [444, 5555],
        "reasons": ["PATHS", "MARKER"],
        "te_problems": {
            "auto resolved: qqq": [
                {
                    "resolved": True,
                    "te_diff_id": 33333
                }
            ],
            "!!empty!!": [
                {
                    "resolved": True,
                    "te_diff_id": 11111
                },
                {
                    "resolved": False,
                    "te_diff_id": 22222
                }
            ]
        }
    },
    {"revision": 321654, "review_ids": [], "reasons": ["TESTENV"], "te_problems": {}},
]


@pytest.mark.parametrize(
    "changelog, headers, expected",
    [
        (
            CHANGELOG,
            HEADERS,
            [
                "",
                "#|",
                "|| **REVISION** | **REVIEW_IDS** | **REASONS** | **TE_PROBLEMS** ||",
                (
                    "|| ((https://a.yandex-team.ru/arc/commit/123456 123456)) "
                    "| ((https://a.yandex-team.ru/review/444/files 444))\n((https://a.yandex-team.ru/review/5555/files 5555)) "
                    "| PATHS\nMARKER "
                    "| !!There are unresolved problems!!\n"
                    "auto resolved: qqq: ((https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=33333 33333))\n"
                    "!!empty!!: ((https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=11111 11111)), "
                    "??((https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=22222 22222))?? "
                    "||"
                ),
                "|| ((https://a.yandex-team.ru/arc/commit/321654 321654)) |  | TESTENV |  ||",
                "|#",
                "",
            ]
        )
    ]
)
def test__wiki_formatter(changelog, headers, expected):
    changelog_table_data = cf.ChangeLogDataWiki(c_info, headers, changelog)
    assert cf.ChangeLogWiki().format_table(changelog_table_data) == "\n".join(expected)


def test__html_formatter():
    expected = [
        "<html><body><table border=1>",
        "<tr><th>REVISION</th><th>REVIEW_IDS</th><th>REASONS</th><th>TE_PROBLEMS</th></tr>",
        (
            "<tr>"
            "<td style=\"padding: 4px\"><a href=\"https://a.yandex-team.ru/arc/commit/123456\">123456</a></td>"
            "<td style=\"padding: 4px\">"
            "<a href=\"https://a.yandex-team.ru/review/444/files\">444</a><br/>"
            "<a href=\"https://a.yandex-team.ru/review/5555/files\">5555</a></td>"
            "<td style=\"padding: 4px\">PATHS<br/>MARKER</td>"
            "<td style=\"padding: 4px\">"
            "auto resolved: qqq: "
            "<a href=\"https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=33333\">33333</a><br/>"
            "!!empty!!: "
            "<a href=\"https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=11111\">11111</a>, "
            "<a href=\"https://testenv.yandex-team.ru/?screen=problem&database=te_trunk_db&id=22222\">22222</a>"
            "</td>"
            "</tr>"
        ),
        "<tr>"
        "<td style=\"padding: 4px\"><a href=\"https://a.yandex-team.ru/arc/commit/321654\">321654</a></td>"
        "<td style=\"padding: 4px\"></td>"
        "<td style=\"padding: 4px\">TESTENV</td>"
        "<td style=\"padding: 4px\"></td>"
        "</tr>",
        "</table></body></html>",
    ]
    changelog_table_data = cf.ChangeLogDataHtml(c_info, HEADERS, CHANGELOG)
    assert cf.ChangeLogHtml().format_table(changelog_table_data) == "\n".join(expected)
