from collections import namedtuple

from sandbox.projects.SuspiciousCommits import rules
from sandbox.projects.SuspiciousCommits.rules import diff_parse


Case = namedtuple('Case', 'path_2_revision_2_content items current_revision')
CaseItem = namedtuple('CaseItem', 'file_2_diff path_2_status, rule_name_2_match_line')


_CASES = [
    Case(
        {},
        [
            CaseItem(
                {
                    "some_good_file.h": """+#include <util/stream/out.h>\n+\n+void Do() { Cout << "Do" << Endl; }"""
                },
                {
                    "some_good_file.h": "M"
                },
                None
            ),
            CaseItem(
                {
                    "some_good_file.h": """+#include <util/stream/out.h>\n+\n+ void Do() { Cout << "Do" << Endl; }""",
                    "some_bad_file.h": """+#include <unistd.h>\n+\n+void Do() { write(0, "Do\n"); }"""
                },
                {
                    "some_good_file.h": "M",
                    "some_bad_file.h": "M",
                },
                {'BadHeaders': '+#include <unistd.h>'}
            ),
        ],
        1000000
    ),
    Case(
        {
            "good_file1.h": {
                9: """"""
            },
            "bad_file1.cpp": {
                9: """#include <stdlib.h>\n\nchar* Do1() { return getenv("xxx");}\n"""
            },
            "bad_file2.cpp": {
                9: """"""
            }
        },
        [
            CaseItem(
                {
                    "contrib/some_contrib_file.h": """\n+#include <stdlib.h>\n+\n+char* Do() { return getenv("xxx");}\n"""  # noqa
                },
                {
                    "contrib/some_contrib_file.h": "M"
                },
                None
            ),
            CaseItem(
                {
                    "bad_file1.cpp": """\n+char* Do2() { return getenv("xxx");}\n"""
                },
                {
                    "bad_file1.cpp": "M"
                },
                None
            ),
            CaseItem(
                {  # new file case
                    "bad_file3.h": """\n+#include <stdlib.h>\n+char* Do() { return getenv("xxx");}\n"""
                },
                {
                    "bad_file3.h": "M"
                },
                {'BadCppFunctions': '+char* Do() { return getenv("xxx");}'}
            ),
            CaseItem(
                {
                    "good_file1.cpp": """\n+char* Do() { return GetEnv("xxx");}\n""",
                    "good_file2.py": """\n+def x(): return sys.getenv("xxx")\n"""
                },
                {
                    "good_file1.cpp": "M",
                    "good_file2.py": "M"
                },
                None
            ),
            CaseItem(
                {  # new file case
                    "bad_file3.h": """\n+#include <stdlib.h>\n+char* Do() { return setenv("xxx", "xxx", 1);}\n"""
                },
                {
                    "bad_file3.h": "M"
                },
                {'BadCppFunctions': '+char* Do() { return setenv("xxx", "xxx", 1);}'}
            ),
            CaseItem(
                {
                    "good_file1.cpp": """\n+char* Do() { return SetEnv("xxx", y);}\n""",
                    "good_file2.py": """\n+def x(): return sys.setenv("xxx", "fff")\n"""
                },
                {
                    "good_file1.cpp": "M",
                    "good_file2.py": "M"
                },
                None
            ),
        ],
        10
    ),
    Case(
        {},
        [
            CaseItem(
                {
                    "some_good_file.h": """\n+#include <util/stream/out.h>\n+\n+void Do() { Cout << "Do" << Endl;}\n"""
                },
                {
                    "some_good_file.h": "M"
                },
                None
            ),
            CaseItem(
                {
                    "some_good_file.h": """\n+#include <util/stream/out.h>\n+\n+ void Do() { Cout << "Do" << Endl;}\n""",  # noqa
                    "some_bad_file.h": """\n+#include <unistd.h>\n+\n+void Do() { write(0, "Do\n");}\n"""
                },
                {
                    "some_good_file.h": "M",
                    "some_bad_file.h": "M"
                },
                {'BadHeaders': "+#include <unistd.h>"}
            ),
        ],
        123456
    ),
    Case(
        {
            "path/to/py_library/ya.make": {
                123455: """\n+PY_LIBRARY\ntext\n"""
            },
            "path/to/py23_library/ya.make": {
                123455: """\n+PY23_LIBRARY\ntext\n"""
            },
        },
        [
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY23_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY3_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PROTO_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+LIBRARY\ntext\nPY_SRCS(file.py)\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+LIBRARY\ntext\nUSE_PYTHON2()\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
#            CaseItem(
#                {
#                    "some/path/ya.make": """\n+SANDBOX_TASK\ntext\n"""
#                },
#                {
#                    "some/path/ya.make": "A"
#                },
#                {'Py2Project': None}
#            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\ntext\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_LIBRARY\ntext\n"""
                },
                {
                    "some/path/ya.make": "M"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR()\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR(\n)\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR(path/to/py_library)\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR(\npath/to/py_library\n)\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR(path/to/py23_library)\n"""
                },
                {
                    "some/path/ya.make": "A"
                },
                {'Py2Project': None}
            ),
            CaseItem(
                {
                    "some/path/ya.make": """\n+PY_PROGRAM\nPEERDIR(\n    path/to/py_library\n    path/to/py23_library)\n"""  # noqa
                },
                {
                    "some/path/ya.make": "A"
                },
                None
            ),
        ],
        123456
    ),
    Case(
        {},
        [
            CaseItem(
                {
                    "data-ui/README.md": "documentation",
                    "data-ui/ya.make": "something",
                    "groups/data-ui": "group content",
                },
                {
                    "data-ui/README.md": "A",
                    "data-ui/ya.make": "A",
                    "data-ui": "A",
                    "groups/data-ui": "A",
                },
                {'NewTopLevelProjectApprove': None, 'NewTopLevelProjectDocumentation': None}
            ),
            CaseItem(
                {
                    "data-ui/ya.make": "something",
                    "groups/data-ui": "group content",
                },
                {
                    "data-ui/ya.make": "A",
                    "data-ui": "A",
                    "groups/data-ui": "A",
                },
                {'NewTopLevelProjectApprove': None, 'NewTopLevelProjectDocumentation': None}
            ),
            CaseItem(
                {
                    "data-ui/README.md": "documentation",
                    "data-ui/ya.make": "OWNER(w100)",
                    "groups/data-ui": "group content",
                },
                {
                    "data-ui/README.md": "A",
                    "data-ui/ya.make": "A",
                    "data-ui": "A",
                    "groups/data-ui": "A",
                },
                {'NewTopLevelProjectApprove': None}
            ),
            CaseItem(
                {
                    "folder/data-ui/README.md": "documentation",
                    "folder/data-ui/ya.make": "OWNER(w100)",
                    "groups/data-ui": "group content",
                },
                {
                    "folder/data-ui/README.md": "A",
                    "folder/data-ui/ya.make": "A",
                    "folder/data-ui": "A",
                    "groups/data-ui": "A",
                },
                None
            ),
        ],
        123456
    ),
    Case(
        {
            "library/cpp/lib1/README.md": {
                5000000: """documentation"""
            },
        },
        [
            CaseItem(
                {
                    "library/cpp/some_lib/ya.make": "something",
                },
                {
                    "library/cpp/some_lib/ya.make": "A",
                },
                {'NewLibraryDoc': None}
            ),
            CaseItem(
                {
                    "library/cpp/some_lib/ya.make": "something",
                    "library/cpp/some_lib/README.md": "documentation",
                },
                {
                    "library/cpp/some_lib/ya.make": "A",
                    "library/cpp/some_lib/README.md": "A"
                },
                None
            ),
            CaseItem(
                {
                    "library/cpp/some_lib/ya.make": "something",
                    "library/cpp/some_another_lib/README.md": "documentation",
                },
                {
                    "library/cpp/some_lib/ya.make": "A",
                    "library/cpp/some_another_lib/README.md": "A"
                },
                {'NewLibraryDoc': None}
            ),
            CaseItem(
                {
                    "library/cpp/lib1/ya.make": "something",
                },
                {
                    "library/cpp/lib1/ya.make": "A",
                },
                None
            ),
        ],
        5000001
    ),
]


def get_file_content_getter(path_2_revision_2_content):
    def file_content_getter(path, revision):
        if path not in path_2_revision_2_content:
            return None
        assert revision in path_2_revision_2_content[path]
        return path_2_revision_2_content[path][revision]
    return file_content_getter


def test_all_rules():
    assert rules.RULES

    for rule in rules.RULES:
        assert rule.name()
        assert rule.owners
        assert rule.message

    for case in _CASES:
        file_content_getter = get_file_content_getter(case.path_2_revision_2_content)

        for item in case.items:
            rule_name_2_match = {}
            for rule in rules.RULES:
                diff_context = diff_parse.DiffContext(item.file_2_diff, item.path_2_status)
                match = rule.function(file_content_getter, diff_context, case.current_revision)
                if match:
                    rule_name_2_match[rule.name()] = match

            if not item.rule_name_2_match_line:
                assert not rule_name_2_match, item
            else:
                assert set(item.rule_name_2_match_line.keys()) == set(rule_name_2_match.keys())
                for rule_name, match_line in item.rule_name_2_match_line.items():
                    assert match_line == rule_name_2_match[rule_name].line, (item, rule_name)


_DIFF1 = '''Index: sandbox/projects/SuspiciousCommits/__init__.py
===================================================================
--- sandbox/projects/SuspiciousCommits/__init__.py	(revision 7110807)
+++ sandbox/projects/SuspiciousCommits/__init__.py	(revision 7110808)
@@ -87,7 +83,7 @@
         messages = []
         for rule in rules.RULES:
             try:
-                match = rule.function(diff, context, revision)
+                match = rule.function(_file_content_getter, diff, context, revision)

                 if match is None:
                     logger.debug("Rule %s has no matches, skipped", rule.name())'''

_DIFF2 = '''Index: sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py
===================================================================
--- sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py	(nonexistent)
+++ sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py	(revision 7110808)
@@ -0,0 +1,64 @@
+import logging
+
'''

_DIFF = _DIFF1 + '\n' + _DIFF2

_DIFF_SUMMARY = '''M       svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/projects/SuspiciousCommits/__init__.py
A       svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py
A       svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/projects/SuspiciousCommits/rules
'''


def test_diff_parser():
    diff_context = diff_parse.parse_diff(_DIFF, _DIFF_SUMMARY)

    files_2_expected_diff = {
        'sandbox/projects/SuspiciousCommits/__init__.py': _DIFF1,
        'sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py': _DIFF2
    }

    path_2_expected_status = {
        'sandbox/projects/SuspiciousCommits/__init__.py': 'M',
        'sandbox/projects/SuspiciousCommits/rules/BadCppFunctions.py': 'A',
        'sandbox/projects/SuspiciousCommits/rules': 'A',
    }

    assert diff_context.file_2_diff == files_2_expected_diff
    assert diff_context.path_2_status == path_2_expected_status
